"""Inkrementalni update WU podataka: dopunjava raw_5min.csv od zadnjeg
zabiljezenog dana do danas i regenerise merged_observations.csv."""

import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

from wu_scraper import scrape_day, OUTPUT_DIR
from wu_aggregation import resample_to_hourly

RAW_FILE = os.path.join(OUTPUT_DIR, "raw_5min.csv")
HOURLY_FILE = os.path.join(OUTPUT_DIR, "merged_observations.csv")
SLEEP_S = 2


def main():
    raw = pd.read_csv(RAW_FILE)
    raw['datetime'] = pd.to_datetime(raw['datetime'])
    last = raw['datetime'].max()
    print(f"Postojeci raw: {len(raw)} redova, zadnji {last}")

    # Zadnji dan je vjerojatno nepotpun -> ponovo ga skidamo.
    start = last.date()
    end = datetime.now().date()
    dates = []
    d = start
    while d <= end:
        dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    print(f"Skidam {len(dates)} dana: {dates[0]} .. {dates[-1]}")

    session = requests.Session()
    chunks = []
    failed = []
    for i, ds in enumerate(dates, 1):
        print(f"[{i}/{len(dates)}] {ds}...", end=" ", flush=True)
        df = scrape_day(ds, session)
        if df is not None and not df.empty:
            chunks.append(df)
            print(f"{len(df)} redova")
        else:
            failed.append(ds)
            print("nema podataka")
        time.sleep(SLEEP_S)

    if not chunks:
        print("Nista novo skinuto.")
        return 1

    new = pd.concat(chunks, ignore_index=True)
    new['datetime'] = pd.to_datetime(new['datetime'])
    merged = pd.concat([raw, new], ignore_index=True)
    merged = merged.drop_duplicates(subset=['datetime'], keep='last').sort_values('datetime')
    added = len(merged) - len(raw)

    out = merged.copy()
    out['datetime'] = out['datetime'].dt.strftime("%Y-%m-%d %H:%M:%S")
    out.to_csv(RAW_FILE, index=False)
    print(f"\nraw_5min.csv: {len(merged)} redova (+{added}), do {merged['datetime'].max()}")

    hourly = resample_to_hourly(merged)
    hourly.to_csv(HOURLY_FILE, index=False)
    print(f"merged_observations.csv: {len(hourly)} sati, do {hourly['datetime'].max()}")

    if failed:
        print(f"Neuspjesni dani ({len(failed)}): {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
