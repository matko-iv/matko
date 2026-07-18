"""Probabilistic post-processing toolbox.

Contents:
  Verification:   dm_test_hln, moving_block_bootstrap_ci
  Diagnostics:    corp_reliability (PAV / MCB-DSC-UNC), coverage_width
  EMOS baseline:  gaussian_crps, fit_emos, emos_predict
  Thresholds:     threshold_for_max_sedi, threshold_for_max_csi
  Quantiles+CQR:  train_quantile_models, cqr_calibrate, predict_quantiles,
                  pinball_loss, crps_from_quantiles, exceedance_from_quantiles
  ECC:            ecc_scenarios, rain_episode_stats
  CSG (gated):    fit_csg, csg_sample_crps

Standalone: no import of forecast_48h_v3, so fetch/eval scripts can use it
without dragging in the whole pipeline.
"""
import json

import numpy as np
import pandas as pd
from scipy import optimize, stats
from sklearn.isotonic import IsotonicRegression

DEFAULT_ALPHAS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


# Verification statistics.

def dm_test_hln(loss_a, loss_b, h=24):
    """Diebold–Mariano test with Bartlett/Newey-West HAC variance over h-1 lags and
    the Harvey–Leybourne–Newbold small-sample correction.

    loss_a/loss_b: per-time losses of the two systems on the SAME cases.
    Returns (dm_stat, p_value). dm_stat < 0 -> system A has lower loss.
    """
    d = np.asarray(loss_a, dtype=float) - np.asarray(loss_b, dtype=float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 10:
        return np.nan, np.nan
    dbar = d.mean()
    dc = d - dbar
    gamma0 = np.mean(dc * dc)
    # Newey-West / Bartlett HAC weights keep distant, noisy autocovariances
    # from dominating the variance estimate (the former uniform kernel could
    # produce a negative variance and then an enormous fabricated DM score).
    max_lag = min(max(int(h) - 1, 0), n - 1)
    var = gamma0
    for k in range(1, max_lag + 1):
        gk = np.mean(dc[k:] * dc[:-k])
        var += 2.0 * (1.0 - k / (max_lag + 1.0)) * gk
    if not np.isfinite(var) or var <= 1e-12:
        return np.nan, np.nan
    var /= n
    dm = dbar / np.sqrt(var)
    # HLN correction
    h_eff = min(max(int(h), 1), n - 1)
    correction = (n + 1 - 2 * h_eff + h_eff * (h_eff - 1) / n) / n
    if correction <= 0:
        return np.nan, np.nan
    hln = np.sqrt(correction)
    dm_c = dm * hln
    p = 2 * stats.t.sf(abs(dm_c), df=n - 1)
    return float(dm_c), float(p)


def moving_block_bootstrap_ci(x, block_len=48, n_boot=1000, alpha=0.10, seed=0):
    """CI for the mean of an autocorrelated series via moving-block bootstrap."""
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


# Diagnostics.

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


# EMOS / NGR baseline.

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


# Decision thresholds.

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


# Multi-quantile models + CQR.

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
    """Calibrate CQR intervals with a split-conformal finite-sample quantile.

    For nominal coverage ``hi - lo``, the offset is the empirical quantile of
    ``max(q_lo - y, y - q_hi)`` at
    ``ceil((n + 1) * coverage) / n``, capped at one and selected with NumPy's
    conservative ``method='higher'`` rule.  A negative offset is intentional:
    standard CQR can shrink an over-wide base interval as well as expand an
    under-covering one.  Returns ``{(lo, hi): offset}``.
    """
    y = np.asarray(y_cal, dtype=float).reshape(-1)
    offsets = {}
    for lo, hi in pairs:
        if not (0.0 <= lo < hi <= 1.0):
            raise ValueError(f"Invalid CQR quantile pair ({lo}, {hi})")
        q_lo = np.asarray(models[lo].predict(X_cal), dtype=float).reshape(-1)
        q_hi = np.asarray(models[hi].predict(X_cal), dtype=float).reshape(-1)
        if q_lo.shape != y.shape or q_hi.shape != y.shape:
            raise ValueError("CQR predictions and calibration targets must have equal length")
        s = np.maximum(q_lo - y, y - q_hi)
        s = s[np.isfinite(s)]
        n = len(s)
        if n == 0:
            offsets[(lo, hi)] = 0.0
            continue
        coverage = hi - lo
        level = min(np.ceil((n + 1) * coverage) / n, 1.0)
        offsets[(lo, hi)] = float(np.quantile(s, level, method='higher'))
    return offsets


def crps_from_quantiles(y, qdf, alphas=DEFAULT_ALPHAS):
    """Approximate mean CRPS by integrating pinball loss over quantile level.

    The supplied (possibly nonuniform) alpha grid is integrated case-by-case
    with the trapezoidal rule.  Outside the supplied grid, the lowest and
    highest predicted quantiles are held constant to alpha 0 and 1; endpoint
    pinball losses are evaluated under that explicit finite-tail convention.
    Rows missing the target or any requested quantile are excluded.
    """
    alphas = np.asarray(alphas, dtype=float)
    if alphas.ndim != 1 or alphas.size == 0:
        raise ValueError("alphas must be a non-empty one-dimensional sequence")
    if not np.isfinite(alphas).all() or np.any((alphas <= 0.0) | (alphas >= 1.0)):
        raise ValueError("alphas must be finite and strictly between 0 and 1")
    order = np.argsort(alphas)
    alphas = alphas[order]
    if np.any(np.diff(alphas) <= 0.0):
        raise ValueError("alphas must be unique")

    y = np.asarray(y, dtype=float).reshape(-1)
    cols = [f"q{int(round(a * 100)):02d}" for a in alphas]
    if len(set(cols)) != len(cols):
        raise ValueError("alphas must map to distinct quantile column names")
    q = qdf[cols].to_numpy(dtype=float)
    if q.shape[0] != y.size:
        raise ValueError("Quantile predictions and targets must have equal length")
    valid = np.isfinite(y) & np.isfinite(q).all(axis=1)
    if not valid.any():
        return np.nan

    yy = y[valid, None]
    q = q[valid]
    diff = yy - q
    losses = np.maximum(alphas[None, :] * diff,
                        (alphas[None, :] - 1.0) * diff)

    # Constant-quantile extrapolation supplies the otherwise unobserved tails:
    # rho_0(y - q_min) on the left and rho_1(y - q_max) on the right.
    left_loss = np.maximum(q[:, 0] - yy[:, 0], 0.0)
    right_loss = np.maximum(yy[:, 0] - q[:, -1], 0.0)
    grid = np.concatenate(([0.0], alphas, [1.0]))
    losses = np.column_stack((left_loss, losses, right_loss))
    case_crps = 2.0 * np.trapezoid(losses, grid, axis=1)
    return float(np.mean(case_crps))


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
            # Exponential upper-tail extrapolation anchored by the last two
            # quantiles. A flat CDF above q95 incorrectly returned exactly 5%
            # exceedance for every larger threshold, however extreme.
            tail_last = 1.0 - alphas[-1]
            if threshold == v[-1]:
                out[i] = tail_last
                continue
            # Repeated upper quantiles are common for zero-inflated targets.
            # Anchor to the nearest *distinct* lower quantile so the survival
            # curve stays continuous instead of dropping 5% -> 0 immediately.
            distinct = np.flatnonzero(v[:-1] < v[-1])
            previous = int(distinct[-1]) if distinct.size else -1
            width = v[-1] - v[previous] if previous >= 0 else 0.0
            tail_prev = 1.0 - alphas[previous] if previous >= 0 else tail_last
            if width > 0 and tail_prev > tail_last > 0:
                scale = width / np.log(tail_prev / tail_last)
                out[i] = float(tail_last * np.exp(-(threshold - v[-1]) / scale))
            else:
                out[i] = 0.0
            continue
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


# ECC — Ensemble Copula Coupling.

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
        # scipy.stats.rankdata returns floating-point ranks even for the
        # ordinal method; NumPy requires integers for positional indexing.
        ranks = (stats.rankdata(row, method='ordinal') - 1).astype(np.intp)
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


# CSG — censored shifted Gamma.

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
