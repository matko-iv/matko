"""Fit lead-aware ITALIAMETEO rain probabilities against DGMR radar truth.

This reuses the completed replay case CSV, so it does not reread the 30 GB
WebDataset archive. Open-Meteo Previous Runs supplies forecasts made roughly
0, 24 and 48 hours before each valid radar hour. A chronological 2025 fit /
calibration and 2026 test prevents future leakage.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


LAT = 42.2864
LON = 18.84
MODEL = "italia_meteo_arpae_icon_2i"
API = "https://previous-runs-api.open-meteo.com/v1/forecast"
ITALIA_ARCHIVE_START = datetime(2025, 4, 13, tzinfo=timezone.utc)
ANCHORS = {
    "lead_0h": "precipitation",
    "lead_24h": "precipitation_previous_day1",
    "lead_48h": "precipitation_previous_day2",
}


def _args() -> argparse.Namespace:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        default=base / "analysis_output" / "dgmr_archive_replay_20260814_cases.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "analysis_output" / "italiameteo_dgmr_lead_calibration.json",
    )
    parser.add_argument("--chunk-days", type=int, default=60)
    return parser.parse_args()


def _fetch_chunk(start: datetime, end: datetime) -> dict[str, dict[datetime, float | None]]:
    requested = [
        "precipitation_previous_day0",
        "precipitation_previous_day1",
        "precipitation_previous_day2",
    ]
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "hourly": ",".join(requested),
        "models": MODEL,
        "timezone": "UTC",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    print(f"Fetching {params['start_date']}..{params['end_date']}", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        payload = json.load(response)
    hourly = payload["hourly"]
    times = [
        datetime.fromisoformat(label).replace(tzinfo=timezone.utc)
        for label in hourly["time"]
    ]
    result: dict[str, dict[datetime, float | None]] = {}
    for field in ANCHORS.values():
        values = hourly.get(field, [None] * len(times))
        result[field] = dict(zip(times, values))
    return result


def _fetch_archive(start: datetime, end: datetime, chunk_days: int) -> dict[str, dict]:
    result = {field: {} for field in ANCHORS.values()}
    cursor = start.replace(hour=0, minute=0, second=0, microsecond=0)
    final = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    while cursor < final:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), final - timedelta(days=1))
        chunk = _fetch_chunk(cursor, chunk_end)
        for field in result:
            result[field].update(chunk[field])
        cursor = chunk_end + timedelta(days=1)
    return result


def _next_60(origin: datetime, hourly: dict[datetime, float | None]) -> float | None:
    first_end = origin.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    first_fraction = (first_end - origin).total_seconds() / 3600.0
    first = hourly.get(first_end)
    second = hourly.get(first_end + timedelta(hours=1))
    if first is None or second is None:
        return None
    return float(first) * first_fraction + float(second) * (1.0 - first_fraction)


def _contingency(y: np.ndarray, predicted: np.ndarray, weight: np.ndarray) -> dict:
    hit = float(weight[(predicted == 1) & (y == 1)].sum())
    miss = float(weight[(predicted == 0) & (y == 1)].sum())
    false = float(weight[(predicted == 1) & (y == 0)].sum())
    reject = float(weight[(predicted == 0) & (y == 0)].sum())
    return {
        "weighted_n": round(hit + miss + false + reject, 3),
        "hits": round(hit, 3), "misses": round(miss, 3),
        "false_alarms": round(false, 3), "correct_rejections": round(reject, 3),
        "POD": round(hit / (hit + miss), 5) if hit + miss else None,
        "FAR": round(false / (hit + false), 5) if hit + false else None,
        "CSI": round(hit / (hit + miss + false), 5) if hit + miss + false else None,
    }


def _probability_metrics(y: np.ndarray, probability: np.ndarray,
                         weight: np.ndarray) -> dict:
    return {
        "ROC_AUC": round(float(roc_auc_score(y, probability, sample_weight=weight)), 5),
        "average_precision": round(float(average_precision_score(
            y, probability, sample_weight=weight)), 5),
        "Brier": round(float(brier_score_loss(y, probability, sample_weight=weight)), 5),
    }


def _choose_threshold(y: np.ndarray, probability: np.ndarray,
                      weight: np.ndarray) -> tuple[float, dict]:
    candidates = np.unique(np.r_[np.arange(0.01, 0.501, 0.005), probability])
    scored = []
    for threshold in candidates:
        metrics = _contingency(y, probability >= threshold, weight)
        metrics["threshold"] = float(threshold)
        scored.append(metrics)
    # Precision-first onset signal: optimize threat score while preventing a
    # degenerate ultra-high threshold that catches almost no real events.
    feasible = [row for row in scored if (row["POD"] or 0.0) >= 0.25]
    pool = feasible or scored
    best = max(pool, key=lambda row: (
        row["CSI"] if row["CSI"] is not None else -1.0,
        -(row["FAR"] if row["FAR"] is not None else 1.0),
        row["POD"] if row["POD"] is not None else -1.0,
    ))
    return float(best["threshold"]), best


def _fit_anchor(rows: list[dict], anchor: str) -> dict:
    usable = [row for row in rows if row[anchor] is not None]
    fit = [row for row in usable if row["origin"].year == 2025]
    test = [row for row in usable if row["origin"].year >= 2026]
    fit.sort(key=lambda row: row["origin"])
    split = max(1, int(len(fit) * 0.75))
    train, calibration = fit[:split], fit[split:]
    if min(len(train), len(calibration), len(test)) < 50:
        return {"usable": len(usable), "error": "insufficient chronological coverage"}

    def arrays(part: list[dict]):
        amount = np.asarray([row[anchor] for row in part], dtype=float)
        X = np.log1p(amount).reshape(-1, 1)
        y = np.asarray([row["observed"] for row in part], dtype=int)
        w = np.asarray([row["weight"] for row in part], dtype=float)
        return amount, X, y, w

    _, X_train, y_train, w_train = arrays(train)
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000)
    model.fit(X_train, y_train, sample_weight=w_train)
    _, X_cal, y_cal, w_cal = arrays(calibration)
    p_cal = model.predict_proba(X_cal)[:, 1]
    threshold, selection = _choose_threshold(y_cal, p_cal, w_cal)
    threshold_logit = np.log(threshold / (1.0 - threshold))
    equivalent_mm = float(np.expm1(
        (threshold_logit - model.intercept_[0]) / model.coef_[0, 0]
    ))

    amount_test, X_test, y_test, w_test = arrays(test)
    p_test = model.predict_proba(X_test)[:, 1]
    calibrated_signal = _contingency(y_test, p_test >= threshold, w_test)
    raw_signal = _contingency(y_test, amount_test >= 0.1, w_test)
    csi_gain = float(calibrated_signal["CSI"] - raw_signal["CSI"])
    return {
        "coverage": {
            "usable": len(usable), "fit": len(train),
            "calibration": len(calibration), "test": len(test),
            "test_start": min(row["origin"] for row in test).isoformat(),
            "test_end": max(row["origin"] for row in test).isoformat(),
        },
        "model": {
            "transform": "log1p_mm", "coef": float(model.coef_[0, 0]),
            "intercept": float(model.intercept_[0]),
            "probability_threshold": threshold,
            "equivalent_amount_threshold_mm": equivalent_mm,
        },
        "selection_2025_tail": selection,
        "test_2026": {
            "calibrated_probability": _probability_metrics(y_test, p_test, w_test),
            "calibrated_signal": calibrated_signal,
            "raw_amount_ge_0_1mm": raw_signal,
            "calibrated_minus_raw_CSI": round(csi_gain, 5),
        },
        "deployment_recommendation": (
            "candidate" if csi_gain >= 0.01 else "do_not_deploy"
        ),
    }


def main() -> int:
    args = _args()
    raw = []
    with args.cases.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            origin = datetime.fromisoformat(row["origin_utc"])
            if origin.tzinfo is None:
                origin = origin.replace(tzinfo=timezone.utc)
            if row["current_rain"].lower() == "true":
                continue
            raw.append({
                "origin": origin,
                "observed": int(row["observed_60"].lower() == "true"),
                "weight": float(row["selection_weight"]),
            })
    start = max(min(row["origin"] for row in raw), ITALIA_ARCHIVE_START)
    end = max(row["origin"] for row in raw) + timedelta(hours=2)
    archive = _fetch_archive(start, end, args.chunk_days)
    for row in raw:
        for anchor, field in ANCHORS.items():
            row[anchor] = _next_60(row["origin"], archive[field])

    result = {
        "artifact_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target": "any >=20 dBZ-equivalent DGMR echo within 5 km in next 60 minutes",
        "population": "dry-origin replay cases with inverse-probability dry weights",
        "model": MODEL,
        "anchors": {anchor: _fit_anchor(raw, anchor) for anchor in ANCHORS},
        "deployment_note": (
            "Anchors are approximately 0/24/48-hour forecast age. Interpolate "
            "calibration coefficients by live lead only after reviewing held-out scores."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(args.output)
    print(json.dumps(result, indent=2), flush=True)
    print(f"Saved {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
