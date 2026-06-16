"""Probabilistic post-processing toolbox — monograph-2 (PDF2).

Contents:
  Verification (Pogl. 8):   dm_test_hln, moving_block_bootstrap_ci
  Diagnostics (Pogl. 3.4):  corp_reliability (PAV / MCB-DSC-UNC), coverage_width
  EMOS baseline (Pogl. 1):  gaussian_crps, fit_emos, emos_predict
  Thresholds (Pogl. 4.4):   threshold_for_max_sedi, threshold_for_max_csi
  Quantiles+CQR (Pogl. 3):  train_quantile_models, cqr_calibrate, predict_quantiles,
                            pinball_loss, crps_from_quantiles, exceedance_from_quantiles
  ECC (Pogl. 5.2):          ecc_scenarios, rain_episode_stats
  CSG (Pogl. 4.1, gated):   fit_csg, csg_sample_crps

Standalone module: no import of forecast_48h_v3 (so fetch/eval scripts can use
it without dragging in the whole pipeline).
"""
import json

import numpy as np
import pandas as pd
from scipy import optimize, stats
from sklearn.isotonic import IsotonicRegression

DEFAULT_ALPHAS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


# ============================================================================
# Verification statistics (PDF2 §8.1–8.2)
# ============================================================================

def dm_test_hln(loss_a, loss_b, h=24):
    """Diebold–Mariano test with HAC (uniform-kernel) variance over h-1 lags and
    the Harvey–Leybourne–Newbold small-sample correction.

    loss_a/loss_b: per-time losses of the two systems on the SAME cases.
    Returns (dm_stat, p_value). dm_stat < 0 -> system A has lower loss.
    """
    d = np.asarray(loss_a, dtype=float) - np.asarray(loss_b, dtype=float)
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 10:
        return np.nan, np.nan
    dbar = d.mean()
    dc = d - dbar
    gamma0 = np.mean(dc * dc)
    var = gamma0
    for k in range(1, min(h, n - 1)):
        gk = np.mean(dc[k:] * dc[:-k])
        var += 2.0 * gk
    var = max(var, 1e-12) / n
    dm = dbar / np.sqrt(var)
    # HLN correction
    hln = np.sqrt(max((n + 1 - 2 * h + h * (h - 1) / n) / n, 1e-12))
    dm_c = dm * hln
    p = 2 * stats.t.sf(abs(dm_c), df=n - 1)
    return float(dm_c), float(p)


def moving_block_bootstrap_ci(x, block_len=48, n_boot=1000, alpha=0.10, seed=0):
    """CI for the mean of an autocorrelated series via moving-block bootstrap
    (PDF2 §8.1: without block structure hourly CIs are falsely tight)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < block_len * 2:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_len))
    starts_max = n - block_len
    means = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, starts_max + 1, size=n_blocks)
        sample = np.concatenate([x[s:s + block_len] for s in starts])[:n]
        means[b] = sample.mean()
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


# ============================================================================
# Diagnostics (PDF2 §3.4)
# ============================================================================

def corp_reliability(y, p):
    """CORP (Dimitriadis–Gneiting–Jordan 2021): PAV-recalibrated reliability with
    the Brier decomposition BS = MCB − DSC + UNC. Returns a dict."""
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    ok = ~(np.isnan(y) | np.isnan(p))
    y, p = y[ok], p[ok]
    if len(y) < 20:
        return {'brier': np.nan, 'mcb': np.nan, 'dsc': np.nan, 'unc': np.nan, 'n': int(len(y))}
    iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds='clip')
    p_hat = iso.fit_transform(p, y)
    bs = float(np.mean((p - y) ** 2))
    bs_c = float(np.mean((p_hat - y) ** 2))
    ybar = float(y.mean())
    unc = ybar * (1 - ybar)
    return {'brier': bs, 'mcb': bs - bs_c, 'dsc': unc - bs_c, 'unc': unc, 'n': int(len(y))}


def coverage_width(y, q_lo, q_hi):
    """Empirical coverage + mean width of an interval forecast."""
    y = np.asarray(y, dtype=float)
    q_lo = np.asarray(q_lo, dtype=float)
    q_hi = np.asarray(q_hi, dtype=float)
    ok = ~(np.isnan(y) | np.isnan(q_lo) | np.isnan(q_hi))
    if ok.sum() == 0:
        return np.nan, np.nan
    cov = float(np.mean((y[ok] >= q_lo[ok]) & (y[ok] <= q_hi[ok])))
    width = float(np.mean(q_hi[ok] - q_lo[ok]))
    return cov, width


# ============================================================================
# EMOS / NGR baseline (PDF2 Pogl. 1 hierarchy)
# ============================================================================

def gaussian_crps(y, mu, sigma):
    """Closed-form CRPS of N(mu, sigma) at y (Gneiting et al. 2005)."""
    sigma = np.clip(np.asarray(sigma, dtype=float), 1e-6, None)
    z = (np.asarray(y, dtype=float) - np.asarray(mu, dtype=float)) / sigma
    return sigma * (z * (2 * stats.norm.cdf(z) - 1)
                    + 2 * stats.norm.pdf(z) - 1.0 / np.sqrt(np.pi))


def fit_emos(ens_mean, ens_std, y):
    """NGR: mu = a + b*ens_mean, sigma^2 = c^2 + d^2*ens_std^2, min mean CRPS."""
    ens_mean = np.asarray(ens_mean, dtype=float)
    ens_std = np.asarray(ens_std, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = ~(np.isnan(ens_mean) | np.isnan(ens_std) | np.isnan(y))
    em, es, yy = ens_mean[ok], ens_std[ok], y[ok]
    if len(yy) < 100:
        return None
    resid_sd = float(np.std(yy - em)) or 1.0

    def loss(theta):
        a, b, c, d = theta
        mu = a + b * em
        sig = np.sqrt(np.clip(c * c + d * d * es * es, 1e-6, None))
        return float(np.mean(gaussian_crps(yy, mu, sig)))

    res = optimize.minimize(loss, x0=[0.0, 1.0, resid_sd, 1.0], method='Nelder-Mead',
                            options={'maxiter': 2000, 'xatol': 1e-4, 'fatol': 1e-5})
    a, b, c, d = res.x
    return {'a': float(a), 'b': float(b), 'c': float(c), 'd': float(d),
            'crps_train': float(res.fun)}


def emos_predict(params, ens_mean, ens_std):
    mu = params['a'] + params['b'] * np.asarray(ens_mean, dtype=float)
    sig = np.sqrt(np.clip(params['c'] ** 2
                          + params['d'] ** 2 * np.asarray(ens_std, dtype=float) ** 2,
                          1e-6, None))
    return mu, sig


# ============================================================================
# Decision thresholds (PDF2 §4.4)
# ============================================================================

def _contingency(y, pred):
    hits = int(np.sum((pred == 1) & (y == 1)))
    misses = int(np.sum((pred == 0) & (y == 1)))
    fas = int(np.sum((pred == 1) & (y == 0)))
    cns = int(np.sum((pred == 0) & (y == 0)))
    return hits, misses, fas, cns


def sedi_score(y, pred):
    hits, misses, fas, cns = _contingency(np.asarray(y), np.asarray(pred))
    H = hits / max(hits + misses, 1)
    F = fas / max(fas + cns, 1)
    H = min(max(H, 1e-6), 1 - 1e-6)
    F = min(max(F, 1e-6), 1 - 1e-6)
    num = np.log(F) - np.log(H) - np.log(1 - F) + np.log(1 - H)
    den = np.log(F) + np.log(H) + np.log(1 - F) + np.log(1 - H)
    return float(num / den) if den != 0 else 0.0


def csi_score(y, pred):
    hits, misses, fas, _ = _contingency(np.asarray(y), np.asarray(pred))
    den = hits + misses + fas
    return hits / den if den > 0 else 0.0


def far_score(y, pred):
    hits, _, fas, _ = _contingency(np.asarray(y), np.asarray(pred))
    den = hits + fas
    return fas / den if den > 0 else 0.0


def threshold_for_max_sedi(y, p, grid=None, far_cap=None):
    """Probability threshold maximizing SEDI (optionally subject to FAR <= cap)."""
    y = np.asarray(y).astype(int)
    p = np.asarray(p, dtype=float)
    if grid is None:
        grid = np.unique(np.round(np.quantile(p, np.linspace(0.02, 0.98, 97)), 4))
    best_t, best_s = 0.5, -np.inf
    for t in grid:
        pred = (p >= t).astype(int)
        if pred.sum() == 0:
            continue
        if far_cap is not None and far_score(y, pred) > far_cap:
            continue
        s = sedi_score(y, pred)
        if s > best_s:
            best_s, best_t = s, float(t)
    return best_t, best_s


def threshold_for_max_csi(y, p, grid=None):
    y = np.asarray(y).astype(int)
    p = np.asarray(p, dtype=float)
    if grid is None:
        grid = np.unique(np.round(np.quantile(p, np.linspace(0.02, 0.98, 97)), 4))
    best_t, best_s = 0.5, -np.inf
    for t in grid:
        pred = (p >= t).astype(int)
        if pred.sum() == 0:
            continue
        s = csi_score(y, pred)
        if s > best_s:
            best_s, best_t = s, float(t)
    return best_t, best_s


# ============================================================================
# Multi-quantile models + CQR (PDF2 §3.1–3.3)
# ============================================================================

def pinball_loss(y, q, alpha):
    y = np.asarray(y, dtype=float)
    q = np.asarray(q, dtype=float)
    diff = y - q
    return float(np.nanmean(np.maximum(alpha * diff, (alpha - 1) * diff)))


def train_quantile_models(X_tr, y_tr, X_cal, y_cal, alphas=DEFAULT_ALPHAS,
                          lgb_params=None):
    """One LightGBM per quantile (pinball objective), early-stopped on the
    calibration fold. Returns {alpha: booster-like model}."""
    import lightgbm as lgb
    params = {
        'n_estimators': 600, 'learning_rate': 0.05, 'num_leaves': 63,
        'min_child_samples': 40, 'subsample': 0.8, 'subsample_freq': 1,
        'colsample_bytree': 0.7, 'reg_alpha': 0.1, 'reg_lambda': 1.0,
        'random_state': 42, 'verbose': -1, 'n_jobs': -1,
    }
    if lgb_params:
        params.update(lgb_params)
    models = {}
    for a in alphas:
        m = lgb.LGBMRegressor(objective='quantile', alpha=a, **params)
        m.fit(X_tr, y_tr, eval_set=[(X_cal, y_cal)],
              callbacks=[lgb.early_stopping(50, verbose=False)])
        models[a] = m
    return models


def predict_quantiles(models, X, offsets=None, lower_bound=None):
    """Predict all quantiles; apply CQR offsets (per symmetric pair), then a
    non-crossing sort per row. Returns DataFrame with q{alpha*100:02.0f} cols."""
    alphas = sorted(models.keys())
    preds = np.column_stack([models[a].predict(X) for a in alphas])
    if offsets:
        for (lo, hi), e in offsets.items():
            if lo in alphas:
                preds[:, alphas.index(lo)] -= e
            if hi in alphas:
                preds[:, alphas.index(hi)] += e
    preds = np.sort(preds, axis=1)  # non-crossing
    if lower_bound is not None:
        preds = np.clip(preds, lower_bound, None)
    cols = [f"q{int(round(a * 100)):02d}" for a in alphas]
    return pd.DataFrame(preds, columns=cols)


def cqr_calibrate(models, X_cal, y_cal,
                  pairs=((0.05, 0.95), (0.10, 0.90), (0.25, 0.75))):
    """Conformalized Quantile Regression (Romano et al. 2019): per interval pair,
    the (1-alpha_mis)(1+1/n) empirical quantile of s = max(q_lo - y, y - q_hi).
    Returns {(lo, hi): offset}."""
    y = np.asarray(y_cal, dtype=float)
    offsets = {}
    for lo, hi in pairs:
        q_lo = models[lo].predict(X_cal)
        q_hi = models[hi].predict(X_cal)
        s = np.maximum(q_lo - y, y - q_hi)
        s = s[~np.isnan(s)]
        n = len(s)
        if n < 50:
            offsets[(lo, hi)] = 0.0
            continue
        alpha_mis = 1.0 - (hi - lo)
        level = min((1 - alpha_mis) * (1 + 1.0 / n), 1.0)
        offsets[(lo, hi)] = float(np.quantile(s, level))
    return offsets


def crps_from_quantiles(y, qdf, alphas=DEFAULT_ALPHAS):
    """Mean-pinball CRPS approximation: CRPS ≈ 2 * mean_alpha pinball_alpha."""
    losses = []
    for a in alphas:
        col = f"q{int(round(a * 100)):02d}"
        losses.append(pinball_loss(y, qdf[col].values, a))
    return 2.0 * float(np.mean(losses))


def exceedance_from_quantiles(qdf, alphas, threshold):
    """P(Y > threshold) per row from the quantile-encoded CDF. Handles ties
    (e.g. many zero precip quantiles): P(Y <= v) at a tied value = highest alpha."""
    alphas = np.asarray(sorted(alphas), dtype=float)
    cols = [f"q{int(round(a * 100)):02d}" for a in alphas]
    V = qdf[cols].values.astype(float)
    n = len(qdf)
    out = np.empty(n)
    for i in range(n):
        v = V[i]
        if np.isnan(v).any():
            out[i] = np.nan
            continue
        if threshold < v[0]:
            cdf = alphas[0] * (threshold / v[0] if v[0] > 0 else 1.0)
        elif threshold >= v[-1]:
            cdf = alphas[-1]
        else:
            below = v <= threshold
            k = int(np.max(np.nonzero(below)))
            base = alphas[k]
            if v[k + 1] > v[k]:
                frac = (threshold - v[k]) / (v[k + 1] - v[k])
                cdf = base + frac * (alphas[k + 1] - base)
            else:
                cdf = base
        out[i] = 1.0 - float(np.clip(cdf, 0.0, 1.0))
    return out


def save_quantile_bundle(models, offsets, path_prefix):
    """Persist LightGBM quantile models + CQR offsets next to MODEL_DIR files."""
    meta = {'alphas': sorted(models.keys()),
            'offsets': {f"{lo}-{hi}": e for (lo, hi), e in offsets.items()}}
    for a, m in models.items():
        m.booster_.save_model(f"{path_prefix}_q{int(round(a * 100)):02d}.txt")
    with open(f"{path_prefix}_cqr.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f)


def load_quantile_bundle(path_prefix):
    """Reload bundle saved by save_quantile_bundle; returns (models, offsets)
    where models are lightgbm.Booster wrapped to expose .predict."""
    import os
    import lightgbm as lgb
    meta_path = f"{path_prefix}_cqr.json"
    if not os.path.exists(meta_path):
        return None, None
    with open(meta_path, encoding='utf-8') as f:
        meta = json.load(f)
    models = {}
    for a in meta['alphas']:
        mp = f"{path_prefix}_q{int(round(a * 100)):02d}.txt"
        if not os.path.exists(mp):
            return None, None
        models[float(a)] = lgb.Booster(model_file=mp)
    offsets = {}
    for k, e in meta['offsets'].items():
        lo, hi = k.split('-')
        offsets[(float(lo), float(hi))] = float(e)
    return models, offsets


# ============================================================================
# ECC — Ensemble Copula Coupling (PDF2 §5.2)
# ============================================================================

def ecc_scenarios(qdf, alphas, raw_members):
    """Reorder samples from the calibrated marginals by the rank structure of
    the raw ensemble (Schefzik et al. 2013). raw_members: (n_hours, m) array.
    Returns (n_hours, m) of temporally coherent member trajectories."""
    alphas = np.asarray(sorted(alphas), dtype=float)
    cols = [f"q{int(round(a * 100)):02d}" for a in alphas]
    V = qdf[cols].values.astype(float)
    raw = np.asarray(raw_members, dtype=float)
    n, m = raw.shape
    probs = (np.arange(m) + 0.5) / m
    out = np.full((n, m), np.nan)
    for i in range(n):
        v = V[i]
        if np.isnan(v).any():
            continue
        samples = np.interp(probs, alphas, v)  # sorted by construction
        row = raw[i].copy()
        med = np.nanmedian(row)
        row[np.isnan(row)] = med if not np.isnan(med) else 0.0
        ranks = stats.rankdata(row, method='ordinal') - 1  # 0..m-1
        out[i] = samples[ranks]
    return out


def rain_episode_stats(scenarios, wet_thresh=0.1, windows=((0, 12), (12, 24), (24, 48))):
    """From ECC scenario trajectories: P(any rain in window) + expected number
    and mean duration of wet episodes over the full horizon."""
    sc = np.asarray(scenarios, dtype=float)
    n, m = sc.shape
    stats_out = {}
    for (a, b) in windows:
        b = min(b, n)
        if a >= n:
            continue
        any_rain = np.nansum(sc[a:b] >= wet_thresh, axis=0) > 0
        stats_out[f"p_rain_{a}_{b}h"] = float(np.mean(any_rain))
    counts, durs = [], []
    for j in range(m):
        wet = sc[:, j] >= wet_thresh
        runs = []
        run = 0
        for w in wet:
            if w:
                run += 1
            elif run:
                runs.append(run)
                run = 0
        if run:
            runs.append(run)
        counts.append(len(runs))
        if runs:
            durs.extend(runs)
    stats_out['expected_episodes'] = float(np.mean(counts))
    stats_out['mean_episode_hours'] = float(np.mean(durs)) if durs else 0.0
    return stats_out


# ============================================================================
# CSG — censored shifted Gamma (PDF2 §4.1; gated experiment)
# ============================================================================

def fit_csg(ens_mean, ens_stat, y, n_starts=2):
    """Censored-shifted-Gamma (Scheuerer & Hamill 2015, simplified): the
    uncensored Gamma has mean mu = exp(a + b*log1p(ens_mean)), constant shape k,
    shift delta; observed Y = max(0, G - delta). Fit by censored MLE."""
    em = np.log1p(np.clip(np.asarray(ens_mean, dtype=float), 0, None))
    yy = np.asarray(y, dtype=float)
    ok = ~(np.isnan(em) | np.isnan(yy))
    em, yy = em[ok], yy[ok]
    if len(yy) < 500:
        return None

    def nll(theta):
        a, b, log_k, log_delta = theta
        k = np.exp(np.clip(log_k, -3, 3))
        delta = np.exp(np.clip(log_delta, -5, 2))
        mu = np.exp(np.clip(a + b * em, -5, 4))
        theta_scale = mu / k
        wet = yy > 0
        ll = np.zeros(len(yy))
        # wet: density of Gamma at y + delta
        ll[wet] = stats.gamma.logpdf(yy[wet] + delta, k, scale=theta_scale[wet])
        # dry: P(G <= delta)
        ll[~wet] = stats.gamma.logcdf(delta, k, scale=theta_scale[~wet])
        ll[~np.isfinite(ll)] = -30.0
        return -float(np.mean(ll))

    best = None
    for x0 in ([np.log(0.5), 1.0, 0.0, -1.0], [np.log(0.2), 0.8, -0.5, 0.0])[:n_starts]:
        res = optimize.minimize(nll, x0=x0, method='Nelder-Mead',
                                options={'maxiter': 3000})
        if best is None or res.fun < best.fun:
            best = res
    a, b, log_k, log_delta = best.x
    return {'a': float(a), 'b': float(b), 'k': float(np.exp(np.clip(log_k, -3, 3))),
            'delta': float(np.exp(np.clip(log_delta, -5, 2))), 'nll': float(best.fun)}


def csg_sample_crps(params, ens_mean, y, n_samples=400, seed=0):
    """Sample-based CRPS of the fitted CSG (good enough for the gated A/B)."""
    rng = np.random.default_rng(seed)
    em = np.log1p(np.clip(np.asarray(ens_mean, dtype=float), 0, None))
    yy = np.asarray(y, dtype=float)
    mu = np.exp(np.clip(params['a'] + params['b'] * em, -5, 4))
    k, delta = params['k'], params['delta']
    crps = np.empty(len(yy))
    n = n_samples
    # E|X-X'| for sorted samples in O(n): 2/n^2 * sum_i (2i - n + 1) * x_(i)
    coef = (2.0 * np.arange(n) - n + 1)
    for i in range(len(yy)):
        g = rng.gamma(k, mu[i] / k, size=n)
        x = np.clip(g - delta, 0, None)
        x.sort()
        term1 = np.mean(np.abs(x - yy[i]))
        term2 = 2.0 / (n * n) * float(np.dot(coef, x))
        crps[i] = term1 - 0.5 * term2
    return crps
