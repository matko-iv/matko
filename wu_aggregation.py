"""Aggregacija sirovih 5-min WU opservacija u satne redove."""

import numpy as np
import pandas as pd

DIR_DEG = {
    'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
    'East': 90, 'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
    'South': 180, 'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
    'West': 270, 'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5,
    'North': 0,
}

HOURLY_COLUMNS = [
    'datetime', 'temp_c', 'dewpoint_c', 'humidity_pct', 'pressure_hpa',
    'wind_ms', 'precip_rate_mm', 'solar_wm2', 'uv', 'gust_ms', 'gust_ms_p95',
    'wind_ms_max', 'wind_ms_p95', 'precip_rate_max', 'solar_wm2_max',
    'precip_accum_mm', 'wind_dir_deg',
]


def _p95(s):
    return s.quantile(0.95) if s.notna().any() else np.nan


def _vector_dir(group):
    deg = group['wind_dir'].map(DIR_DEG)
    spd = group['wind_ms']
    mask = deg.notna() & spd.notna()
    if not mask.any():
        return np.nan
    rad = np.radians(deg[mask].to_numpy(dtype=float))
    w = spd[mask].to_numpy(dtype=float)
    if w.sum() == 0:
        w = np.ones_like(w)
    ang = np.degrees(np.arctan2((w * np.sin(rad)).sum(), (w * np.cos(rad)).sum()))
    return ang % 360


def resample_to_hourly(df):
    """5-min redovi -> satni redovi (label = pocetak sata)."""
    if df is None or df.empty:
        return None

    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    df['hour'] = df['datetime'].dt.floor('h')

    out = []
    for hour, g in df.groupby('hour'):
        row = {
            'datetime': hour.strftime('%Y-%m-%d %H:%M:%S'),
            'temp_c': g['temp_c'].mean(),
            'dewpoint_c': g['dewpoint_c'].mean(),
            'humidity_pct': g['humidity_pct'].mean(),
            'pressure_hpa': g['pressure_hpa'].mean(),
            'wind_ms': g['wind_ms'].mean(),
            'precip_rate_mm': g['precip_rate_mm'].mean(),
            'solar_wm2': g['solar_wm2'].mean(),
            'uv': g['uv'].mean(),
            'gust_ms': g['gust_ms'].max(),
            'gust_ms_p95': _p95(g['gust_ms']),
            'wind_ms_max': g['wind_ms'].max(),
            'wind_ms_p95': _p95(g['wind_ms']),
            'precip_rate_max': g['precip_rate_mm'].max(),
            'solar_wm2_max': g['solar_wm2'].max(),
            'precip_accum_mm': g['precip_accum_mm'].max(),
            'wind_dir_deg': _vector_dir(g),
        }
        out.append(row)

    if not out:
        return None
    return pd.DataFrame(out, columns=HOURLY_COLUMNS)
