"""Replay the SKALA rain-arrival signal and ITALIAMETEO on the DGMR archive.

The prepared WebDataset shards deliberately retain every tile-rainy window but
only a configured fraction of completely dry windows.  This verifier rebuilds
the deterministic selection and applies inverse-probability weights to dry
windows, so point-event POD/FAR/CSI/HSS reflect the source archive rather than
the training sample mix.

This is a CPU + sequential-storage workload.  It does not import TensorFlow,
CUDA, or the DGMR inference plugin.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import random
import sys
import tarfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np


BUDVA_LAT = 42.2864
BUDVA_LON = 18.84
TILE_CENTER = 128
RADAR_DISC_KM = 5.0
DBZ_EVENT_THRESHOLD = 20.0
RAIN_RATE_EVENT_THRESHOLD = (
    10.0 ** (DBZ_EVENT_THRESHOLD / 10.0) / 200.0
) ** (1.0 / 1.6)
ITALIA_THRESHOLD_MM = 0.1
ITALIA_ARCHIVE_START = datetime(2025, 4, 13, tzinfo=timezone.utc)

CASE_FIELDS = [
    "shard", "key", "origin_utc", "selection_weight", "tile_n_wet_frames",
    "current_rain", "observed_15", "observed_30", "observed_60",
    "skala_pred60", "skala_p15", "skala_p30", "skala_p60", "skala_p120",
    "italia_mm60", "italia_pred01",
]


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path(r"F:\dgmr_train_s11"))
    parser.add_argument("--radar-repo", type=Path,
                        default=Path(r"C:\Users\Matija\Documents\GitHub\budva-radar"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent / "analysis_output")
    parser.add_argument("--output-stem", default="dgmr_archive_replay_20260814")
    parser.add_argument("--start-shard", type=int, default=0)
    parser.add_argument("--end-shard", type=int, default=None,
                        help="inclusive shard index; default processes every shard")
    parser.add_argument("--limit", type=int, default=0,
                        help="global sample cap for a bounded smoke run; 0 means all")
    return parser.parse_args()


def _gap_free_windows(times: list[int], win: int, stride: int,
                      cadence_s: int, tolerance_s: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    i = 0
    while i <= len(times) - win:
        deltas = np.diff(times[i:i + win])
        if np.all(np.abs(deltas - cadence_s) <= tolerance_s):
            result.append((i, i + win))
            i += stride
        else:
            i += 1
    return result


def _rebuild_kept_windows(frames: list[dict], manifest: dict) -> list[dict]:
    window_cfg = manifest["window"]
    times = [int(row["unixts"]) for row in frames]
    wet_fraction = {int(row["unixts"]): float(row["wet_fraction"]) for row in frames}
    windows = _gap_free_windows(
        times,
        int(window_cfg["frames"]),
        int(window_cfg["stride"]),
        int(window_cfg["cadence_s"]),
        int(window_cfg["tol_s"]),
    )
    dry_keep = float(manifest.get("dry_keep", 0.0))
    keep_fraction = float(manifest["keep_frac"])
    kept = []
    for start, end in windows:
        window_times = times[start:end]
        n_wet = sum(wet_fraction[t] >= keep_fraction for t in window_times)
        keep = n_wet >= 1
        if not keep and dry_keep > 0:
            keep = random.Random(f"42-dry-{window_times[0]}").random() < dry_keep
        if keep:
            kept.append({
                "start": start,
                "end": end,
                "origin_ts": times[start + 3],
                "n_wet": n_wet,
                "weight": 1.0 if n_wet else 1.0 / dry_keep,
            })
    expected = int(manifest["counts"]["kept_windows"])
    if len(kept) != expected:
        raise RuntimeError(f"rebuilt {len(kept)} kept windows, expected {expected}")
    return kept


def _fetch_italia(start: datetime, end: datetime) -> dict[datetime, float | None]:
    start = max(start, ITALIA_ARCHIVE_START)
    params = {
        "latitude": BUDVA_LAT,
        "longitude": BUDVA_LON,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "hourly": "precipitation",
        "models": "italia_meteo_arpae_icon_2i",
        "timezone": "UTC",
    }
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    print(f"Fetching ITALIAMETEO {params['start_date']}..{params['end_date']} ...", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        payload = json.load(response)
    return {
        datetime.fromisoformat(label).replace(tzinfo=timezone.utc): value
        for label, value in zip(payload["hourly"]["time"], payload["hourly"]["precipitation"])
    }


def _italia_next_60(origin_ts: int, hourly: dict[datetime, float | None]) -> float | None:
    origin = datetime.fromtimestamp(origin_ts, timezone.utc)
    first_end = origin.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    first_fraction = (first_end - origin).total_seconds() / 3600.0
    first = hourly.get(first_end)
    second = hourly.get(first_end + timedelta(hours=1))
    if first is None or second is None:
        return None
    return float(first) * first_fraction + float(second) * (1.0 - first_fraction)


def _pixel_to_latlon(x: float, y: float) -> tuple[float, float]:
    lat = BUDVA_LAT - (y - TILE_CENTER) / 110.57
    lon = BUDVA_LON + (x - TILE_CENTER) / (111.32 * math.cos(math.radians(lat)))
    return lat, lon


def _rainrate_to_dbz(rain_rate: np.ndarray) -> np.ndarray:
    dbz = np.full(rain_rate.shape, -99.0, dtype=np.float32)
    wet = rain_rate > 0
    dbz[wet] = 10.0 * np.log10(200.0 * np.power(rain_rate[wet], 1.6))
    return dbz


def _weighted_metrics(records: list[dict], prediction_field: str) -> dict:
    hits = misses = false_alarms = correct_rejections = 0.0
    for row in records:
        weight = float(row["selection_weight"])
        observed = bool(row["observed_60"])
        predicted = bool(row[prediction_field])
        if predicted and observed:
            hits += weight
        elif predicted:
            false_alarms += weight
        elif observed:
            misses += weight
        else:
            correct_rejections += weight
    n = hits + misses + false_alarms + correct_rejections
    pod = hits / (hits + misses) if hits + misses else None
    far = false_alarms / (hits + false_alarms) if hits + false_alarms else None
    csi = hits / (hits + misses + false_alarms) if hits + misses + false_alarms else None
    expected = (
        ((hits + misses) * (hits + false_alarms)
         + (correct_rejections + misses) * (correct_rejections + false_alarms)) / n
        if n else None
    )
    hss = ((hits + correct_rejections - expected) / (n - expected)
           if expected is not None and n != expected else None)
    return {
        "weighted_n": round(n, 3),
        "hits": round(hits, 3),
        "misses": round(misses, 3),
        "false_alarms": round(false_alarms, 3),
        "correct_rejections": round(correct_rejections, 3),
        "POD": None if pod is None else round(pod, 5),
        "FAR": None if far is None else round(far, 5),
        "CSI": None if csi is None else round(csi, 5),
        "HSS": None if hss is None else round(hss, 5),
    }


def _probability_metrics(records: list[dict], probability_field: str) -> dict:
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

    truth = np.asarray([bool(row["observed_60"]) for row in records], dtype=int)
    probability = np.asarray([float(row[probability_field]) for row in records])
    weights = np.asarray([float(row["selection_weight"]) for row in records])
    if len(np.unique(truth)) < 2:
        return {"n": len(records), "note": "only one observed class"}
    return {
        "n_unweighted": len(records),
        "ROC_AUC": round(float(roc_auc_score(truth, probability, sample_weight=weights)), 5),
        "average_precision": round(float(average_precision_score(
            truth, probability, sample_weight=weights)), 5),
        "Brier": round(float(brier_score_loss(
            truth, probability, sample_weight=weights)), 5),
    }


def _summary(all_records: list[dict], processed_shards: list[str], elapsed_s: float,
             errors: int, partial: bool) -> dict:
    dry_origins = [row for row in all_records if not row["current_rain"]]
    head_to_head = [row for row in dry_origins if row["italia_mm60"] not in (None, "")]
    for row in head_to_head:
        row["both_pred60"] = bool(row["skala_pred60"] and row["italia_pred01"])
        row["either_pred60"] = bool(row["skala_pred60"] or row["italia_pred01"])
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "partial": partial,
        "processed_shards": processed_shards,
        "elapsed_seconds": round(elapsed_s, 2),
        "sample_errors": errors,
        "cases_total": len(all_records),
        "dry_origin_cases": len(dry_origins),
        "head_to_head_cases": len(head_to_head),
        "assumptions": {
            "radar_truth": "any >=20 dBZ-equivalent echo within 5 km during next 60 minutes",
            "dry_origin_only": True,
            "dry_window_inverse_weight": 20.0,
            "italiameteo_threshold_mm": ITALIA_THRESHOLD_MM,
            "skala_replay": "2-D object tracking; no live RHOHV, Doppler, volume products, or scene-motion fallback",
        },
        "SKALA_all_archive": _weighted_metrics(dry_origins, "skala_pred60"),
        "SKALA_probability_all_archive": _probability_metrics(dry_origins, "skala_p60"),
    }
    if head_to_head:
        result["head_to_head"] = {
            "SKALA": _weighted_metrics(head_to_head, "skala_pred60"),
            "ITALIAMETEO": _weighted_metrics(head_to_head, "italia_pred01"),
            "AND": _weighted_metrics(head_to_head, "both_pred60"),
            "OR": _weighted_metrics(head_to_head, "either_pred60"),
            "SKALA_probability": _probability_metrics(head_to_head, "skala_p60"),
        }
    return result


def main() -> int:
    args = _args()
    sys.path.insert(0, str(args.radar_repo))
    import nowcast
    import tracking

    manifest = json.loads((args.archive / "dataset_manifest.json").read_text())
    frames = json.loads((args.archive / "frames_manifest.json").read_text())
    kept = _rebuild_kept_windows(frames, manifest)
    print(f"Rebuilt {len(kept)} deterministic archive sequences.", flush=True)

    shards = sorted(args.archive.glob("budva-*.tar"))
    if args.end_shard is None:
        args.end_shard = len(shards) - 1
    shards = [path for path in shards
              if args.start_shard <= int(path.stem.split("-")[-1]) <= args.end_shard]
    if not shards:
        raise RuntimeError("no shards selected")

    first_origin = datetime.fromtimestamp(kept[0]["origin_ts"], timezone.utc)
    last_origin = datetime.fromtimestamp(kept[-1]["origin_ts"], timezone.utc) + timedelta(days=1)
    italia = _fetch_italia(first_origin, last_origin)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases_path = args.output_dir / f"{args.output_stem}_cases.csv"
    summary_path = args.output_dir / f"{args.output_stem}_summary.json"
    all_records: list[dict] = []
    processed_shards: list[str] = []
    errors = 0
    started = time.perf_counter()

    yy, xx = np.ogrid[:256, :256]
    radar_disc = ((xx - TILE_CENTER) ** 2 + (yy - TILE_CENTER) ** 2
                  <= (RADAR_DISC_KM ** 2))

    with cases_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CASE_FIELDS)
        writer.writeheader()
        for shard_path in shards:
            shard_index = int(shard_path.stem.split("-")[-1])
            shard_started = time.perf_counter()
            shard_cases = 0
            print(f"[{shard_index + 1}/{len(shards)}] {shard_path.name}", flush=True)
            with tarfile.open(shard_path, "r") as archive:
                for member in archive:
                    if not member.isfile() or not member.name.endswith(".seq.npy"):
                        continue
                    key = int(member.name.split(".")[0])
                    if key >= len(kept):
                        errors += 1
                        continue
                    try:
                        extracted = archive.extractfile(member)
                        if extracted is None:
                            raise RuntimeError("tar member has no data")
                        sequence = np.load(io.BytesIO(extracted.read())).astype(np.float32)
                        window = kept[key]

                        current_rain = bool(np.max(sequence[3][radar_disc])
                                            >= RAIN_RATE_EVENT_THRESHOLD)
                        future_disc = np.max(sequence[4:16][:, radar_disc], axis=1)
                        observed_15 = bool(np.any(future_disc[:3] >= RAIN_RATE_EVENT_THRESHOLD))
                        observed_30 = bool(np.any(future_disc[:6] >= RAIN_RATE_EVENT_THRESHOLD))
                        observed_60 = bool(np.any(future_disc[:12] >= RAIN_RATE_EVENT_THRESHOLD))

                        summaries = []
                        for frame in sequence[:4]:
                            dbz = _rainrate_to_dbz(frame)
                            cells = tracking.cells_from_dbz(
                                dbz, dbz >= DBZ_EVENT_THRESHOLD,
                                _pixel_to_latlon, TILE_CENTER, TILE_CENTER, 1.0,
                            )
                            summaries = tracking.update_summaries(
                                cells, summaries, None, dt_min=5.0,
                            )
                        skala = nowcast.arrival_nowcast(summaries, BUDVA_LAT, BUDVA_LON)
                        p_by_lead = skala["p_by_lead"]
                        italia_mm = _italia_next_60(window["origin_ts"], italia)
                        record = {
                            "shard": shard_index,
                            "key": key,
                            "origin_utc": datetime.fromtimestamp(
                                window["origin_ts"], timezone.utc).isoformat(),
                            "selection_weight": window["weight"],
                            "tile_n_wet_frames": window["n_wet"],
                            "current_rain": current_rain,
                            "observed_15": observed_15,
                            "observed_30": observed_30,
                            "observed_60": observed_60,
                            "skala_pred60": bool(skala["approaching"]),
                            "skala_p15": float(p_by_lead["15"]),
                            "skala_p30": float(p_by_lead["30"]),
                            "skala_p60": float(p_by_lead["60"]),
                            "skala_p120": float(p_by_lead["120"]),
                            "italia_mm60": italia_mm,
                            "italia_pred01": (None if italia_mm is None
                                               else italia_mm >= ITALIA_THRESHOLD_MM),
                        }
                        writer.writerow(record)
                        all_records.append(record)
                        shard_cases += 1
                    except Exception as error:
                        errors += 1
                        if errors <= 10:
                            print(f"  sample {member.name} failed: {type(error).__name__}: {error}",
                                  flush=True)
                    if args.limit and len(all_records) >= args.limit:
                        break
            handle.flush()
            processed_shards.append(shard_path.name)
            elapsed = time.perf_counter() - started
            partial = bool(args.limit and len(all_records) >= args.limit)
            summary_path.write_text(json.dumps(
                _summary(all_records, processed_shards, elapsed, errors, partial),
                indent=2,
            ), encoding="utf-8")
            print(f"  {shard_cases} cases in {time.perf_counter() - shard_started:.1f}s; "
                  f"total={len(all_records)}, errors={errors}", flush=True)
            if partial:
                break

    elapsed = time.perf_counter() - started
    final = _summary(all_records, processed_shards, elapsed, errors,
                     bool(args.limit and len(all_records) >= args.limit))
    summary_path.write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(json.dumps(final, indent=2), flush=True)
    print(f"Cases: {cases_path}", flush=True)
    print(f"Summary: {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
