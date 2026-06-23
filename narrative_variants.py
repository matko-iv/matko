"""Phrasing pools for the rule-based daily narrative (forecast_48h_v3._daily_narrative).

Variable-weather days previously had a single fixed phrasing each; this gives
each weather pattern a small POOL of equivalent Montenegrin phrasings. The picker
is DETERMINISTIC per day (keyed on the day's weather signature) so a given day's
wording is stable across runs (no forecast-JSON churn / Gemini-cache thrash) while
DIFFERENT days get different wording.

Every variant is faithful to the SAME classified weather, so the output still
passes the gemini_narrative.validate() guardrail. Entry 0 of each pool is the
original canonical phrasing, so nothing is lost. EDIT/EXTEND freely — add more
phrasings to any pool (a native-speaker pass is welcome).

Stdlib only, so it is importable + unit-testable without the heavy forecast deps.
"""

VARIANTS = {
    # --- dry days, sky transitions through the day (the "variable weather" the
    #     selection felt slim for) ------------------------------------------
    "sun_to_cloud": [
        "Sunčano prije podne, oblaci od podneva",
        "Vedro ujutru, naoblačenje od podneva",
        "Sunčano prijepodne, sve više oblaka poslije podne",
        "Vedro prije podne, oblačnije poslije podne",
    ],
    "cloud_to_sun": [
        "Oblačno prije podne, sunce od podneva",
        "Oblačno ujutru, razvedravanje od podneva",
        "Tmurnije prijepodne, sunčanije poslije podne",
        "Oblaci prije podne, sunce preovlađuje od podneva",
    ],
    "sun_to_partly": [
        "Sunčano sa ponešto oblaka od podneva",
        "Vedro ujutru, poneki oblak od podneva",
        "Sunčano prijepodne, ponegdje oblaci poslije podne",
    ],
    "partly_to_sun": [
        "Više oblaka prijepodna, sunčano od podneva",
        "Oblačnije ujutru, razvedravanje od podneva",
        "Poneki oblak prijepodne, sunčano poslije podne",
    ],
    "increasing_cloud": [
        "Sve oblačnije kako dan odmiče",
        "Postepeno naoblačenje tokom dana",
        "Sve više oblaka kako dan odmiče",
    ],
    "cloud_to_partly": [
        "Oblačno prijepodne, ponešto sunca od podneva",
        "Oblaci ujutru, malo sunca od podneva",
        "Tmurnije prijepodne, ponegdje sunce poslije podne",
    ],
    "variable": [
        "Promjenljivo oblačno",
        "Promjenljivo, smjena sunca i oblaka",
        "Naoblačenja i razvedravanja tokom dana",
        "Sunce i oblaci naizmjenično",
    ],
    # steady "partly cloudy" all day (variable-ish but no clear AM/PM trend)
    "partly_steady": [
        "Oblačno sa sunčanim periodima",
        "Smjena sunca i oblaka tokom dana",
        "Promjenljivo oblačno, uz sunčane periode",
    ],
    # appended to the end when the evening sky differs from the day
    "eve_clouding": [
        ". Oblaci predveče",
        ". Naoblačenje predveče",
        ". Više oblaka predveče",
    ],
    "eve_clearing": [
        ". Vedrije predveče",
        ". Razvedravanje predveče",
        ". Sunčanije predveče",
    ],
}


def variant(key, seed):
    """Deterministically pick one phrasing from the pool named `key`, keyed on
    `seed` (the day's weather signature). Stable for a given day, varied across
    days. An unknown key is returned as a literal string (safe fallback), so
    callers can pass either a pool name or a one-off sentence."""
    pool = VARIANTS.get(key)
    if not pool:
        return key
    # Stable rolling hash (NOT Python's hash(), which is per-process randomized).
    # Mixing the key in decorrelates pools that share a length.
    s = f"{key}|{seed}"
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return pool[h % len(pool)]
