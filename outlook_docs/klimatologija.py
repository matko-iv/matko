# -*- coding: utf-8 -*-
"""Računa sve ERA5 brojke koje se navode u dokumentima u docs/20_VIII_MMXXVI_*.pdf.

Podaci se povlače iz Open-Meteo arhive (ERA5) i keširaju u era5_<mjesto>.json.
Pokretanje: python klimatologija.py
"""

import collections
import json
import os
import statistics as st
import sys
import time
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TACKE = {"budva": (42.28, 18.84), "podgorica": (42.44, 19.26)}
KRAJ = "2026-08-18"


def ucitaj(mjesto):
    put = os.path.join(HERE, "era5_%s.json" % mjesto)
    if not os.path.exists(put):
        lat, lon = TACKE[mjesto]
        url = ("https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s"
               "&start_date=1950-01-01&end_date=%s"
               "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
               "precipitation_sum&timezone=Europe%%2FPodgorica" % (lat, lon, KRAJ))
        for pokusaj in range(6):
            try:
                json.dump(json.load(urllib.request.urlopen(url, timeout=180)),
                          open(put, "w"))
                break
            except Exception as greska:
                print("  ponavljam (%s)" % greska)
                time.sleep(45)
    d = json.load(open(put))["daily"]
    return list(zip(d["time"], d["temperature_2m_max"], d["temperature_2m_min"],
                    d["temperature_2m_mean"], d["precipitation_sum"]))


def godisnji_pokazatelji(dani):
    srednja, padavine = collections.defaultdict(list), collections.defaultdict(float)
    vreli, veoma_vreli, tropske = (collections.defaultdict(int) for _ in range(3))
    for datum, tmax, tmin, tsr, pad in dani:
        g = int(datum[:4])
        srednja[g].append(tsr)
        padavine[g] += pad or 0
        if tmax is not None and tmax >= 30:
            vreli[g] += 1
        if tmax is not None and tmax >= 35:
            veoma_vreli[g] += 1
        if tmin is not None and tmin >= 20:
            tropske[g] += 1
    return srednja, padavine, vreli, veoma_vreli, tropske


def zimski_pokazatelji(dani):
    """Zima je označena godinom januara (DJF)."""
    zime = collections.defaultdict(lambda: {"t": [], "p": 0.0, "d50": 0, "d100": 0, "mraz": 0})
    for datum, tmax, tmin, tsr, pad in dani:
        g, m = int(datum[:4]), int(datum[5:7])
        if m not in (12, 1, 2):
            continue
        z = zime[g + 1 if m == 12 else g]
        z["t"].append(tsr)
        z["p"] += pad or 0
        if pad and pad >= 50:
            z["d50"] += 1
        if pad and pad >= 100:
            z["d100"] += 1
        if tmin is not None and tmin < 0:
            z["mraz"] += 1
    return zime


def prośek(d, od, do):
    return st.mean([d[g] for g in range(od, do + 1)])


def trend(d, od, do):
    godine = list(range(od, do + 1))
    return np.polyfit(godine, [d[g] for g in godine], 1)[0] * 10


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for mjesto in TACKE:
        dani = ucitaj(mjesto)
        srednja, padavine, vreli, veoma_vreli, tropske = godisnji_pokazatelji(dani)
        srednja_g = {g: st.mean(v) for g, v in srednja.items()}
        print("\n== %s ==" % mjesto.upper())
        print("trend godišnje temperature 1951–2025: %+.2f °C/dek" % trend(srednja_g, 1951, 2025))
        for naziv, d in [("srednja T", srednja_g), ("dani ≥ 30 °C", vreli),
                         ("dani ≥ 35 °C", veoma_vreli), ("tropske noći", tropske),
                         ("padavine", padavine)]:
            print("  %-14s 1961–1990 %7.1f | 1991–2020 %7.1f | 2011–2025 %7.1f"
                  % (naziv, prośek(d, 1961, 1990), prośek(d, 1991, 2020), prośek(d, 2011, 2025)))

        if mjesto != "budva":
            continue

        zime = zimski_pokazatelji(dani)
        osnova = list(range(1991, 2021))
        t_norma = st.mean([st.mean(zime[g]["t"]) for g in osnova])
        p_norma = st.mean([zime[g]["p"] for g in osnova])
        print("  zimska norma 1991–2020: T %.2f °C, padavine %.0f mm" % (t_norma, p_norma))
        print("  analogne zime (odstupanje T, %% normale padavina):")
        for g in (1983, 1998, 2010, 2016, 2026):
            print("    %d/%d  %+.2f °C  %3.0f %%"
                  % (g - 1, g, st.mean(zime[g]["t"]) - t_norma, 100 * zime[g]["p"] / p_norma))
        udio = lambda uslov: round(100 * sum(1 for g in osnova if uslov(zime[g])) / len(osnova))
        print("  klimatološke učestalosti (udio zima 1991–2020):")
        print("    dan ≥ 50 mm: %d %% | tri dana ≥ 50 mm: %d %% | dan ≥ 100 mm: %d %%"
              % (udio(lambda z: z["d50"] >= 1), udio(lambda z: z["d50"] >= 3),
                 udio(lambda z: z["d100"] >= 1)))
        print("    T iznad +1 °C: %d %% | padavine > 120 %%: %d %% | padavine < 80 %%: %d %%"
              % (udio(lambda z: st.mean(z["t"]) - t_norma > 1),
                 udio(lambda z: z["p"] > 1.2 * p_norma), udio(lambda z: z["p"] < 0.8 * p_norma)))

        ljeto = {g: st.mean([t for datum, _, _, t, _ in dani
                             if "%d-06-01" % g <= datum <= "%d-08-18" % g])
                 for g in range(1950, 2027)}
        top = sorted(ljeto.items(), key=lambda par: -par[1])[:3]
        print("  najtoplije ljeto (1.6–18.8): " +
              ", ".join("%d %.2f °C" % (g, v) for g, v in top))


if __name__ == "__main__":
    main()
