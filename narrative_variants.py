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
        "Vedro jutro, popodne porast oblačnosti",
        "Sunčano do podneva, potom naoblačenje",
        "Vedro prijepodne, oblaci se skupljaju poslije podne",
    ],
    "cloud_to_sun": [
        "Oblačno prije podne, sunce od podneva",
        "Oblačno ujutru, razvedravanje od podneva",
        "Tmurnije prijepodne, sunčanije poslije podne",
        "Oblaci prije podne, sunce preovlađuje od podneva",
        "Oblačno jutro, popodne sunčanije",
        "Tmurno do podneva, potom razvedravanje",
        "Oblaci ujutru, sunce probija od podneva",
    ],
    "sun_to_partly": [
        "Sunčano sa ponešto oblaka od podneva",
        "Vedro ujutru, poneki oblak od podneva",
        "Sunčano prijepodne, ponegdje oblaci poslije podne",
        "Vedro jutro, malo oblaka poslije podne",
        "Sunčano, popodne uz poneki oblak",
    ],
    "partly_to_sun": [
        "Više oblaka prijepodna, sunčano od podneva",
        "Oblačnije ujutru, razvedravanje od podneva",
        "Poneki oblak prijepodne, sunčano poslije podne",
        "Malo oblaka ujutru, popodne sunčano",
        "Oblačnije jutro, vedrije poslije podne",
    ],
    "increasing_cloud": [
        "Sve oblačnije kako dan odmiče",
        "Postepeno naoblačenje tokom dana",
        "Sve više oblaka kako dan odmiče",
        "Naoblačenje koje jača tokom dana",
        "Oblaci se zgušnjavaju kako dan odmiče",
    ],
    "cloud_to_partly": [
        "Oblačno prijepodne, ponešto sunca od podneva",
        "Oblaci ujutru, malo sunca od podneva",
        "Tmurnije prijepodne, ponegdje sunce poslije podne",
        "Oblačno jutro, popodne uz poneki sunčani period",
        "Tmurno do podneva, potom djelimično razvedravanje",
    ],
    "variable": [
        "Promjenljivo oblačno",
        "Promjenljivo, smjena sunca i oblaka",
        "Naoblačenja i razvedravanja tokom dana",
        "Sunce i oblaci naizmjenično",
        "Promjenljiva oblačnost tokom dana",
        "Čas sunce, čas oblaci",
    ],
    # steady "partly cloudy" all day (variable-ish but no clear AM/PM trend)
    "partly_steady": [
        "Oblačno sa sunčanim periodima",
        "Smjena sunca i oblaka tokom dana",
        "Promjenljivo oblačno, uz sunčane periode",
        "Sunčani periodi uz povremene oblake",
        "Djelimično oblačno tokom dana",
    ],
    # appended to the end when the evening sky differs from the day
    "eve_clouding": [
        ". Oblaci predveče",
        ". Naoblačenje predveče",
        ". Više oblaka predveče",
        ". Naoblačenje u večernjim satima",
    ],
    "eve_clearing": [
        ". Vedrije predveče",
        ". Razvedravanje predveče",
        ". Sunčanije predveče",
        ". Razvedravanje u večernjim satima",
    ],

    # --- variable RAIN timing (rain branches; all mention rain, which the data
    #     supports, so they pass the guardrail) ------------------------------
    "rain_intermittent": [
        "Povremena kiša",
        "Mjestimična kiša",
        "Kiša s prekidima",
        "Povremene padavine",
        "Kiša u više navrata",
    ],
    "rain_light_intermittent": [
        "Povremena slaba kiša",
        "Mjestimično slaba kiša",
        "Slaba kiša s prekidima",
        "Povremena sitna kiša",
    ],
    "rain_all_day": [
        "Kiša cijeli dan",
        "Kiša tokom cijelog dana",
        "Kišovito cijeli dan",
        "Kiša gotovo cijeli dan",
    ],
    "rain_sun_then_rain": [
        "Sunčano ujutru, kiša od podneva",
        "Vedro prijepodne, kiša poslije podne",
        "Sunčano ujutru, naoblačenje i kiša od podneva",
        "Suvo i sunčano do podneva, potom kiša",
        "Vedro jutro, kiša od popodneva",
    ],
    "rain_sun_then_rain_pm": [
        "Sunčano ujutru, kiša od podneva do kasno poslijepodne",
        "Vedro prijepodne, kiša poslije podne",
        "Suvo do podneva, kiša poslije podne",
    ],
    "rain_cloud_then_rain_pm": [
        "Oblačno, kiša od podneva do kasno poslijepodne",
        "Oblačno prijepodne, kiša poslije podne",
        "Tmurno, kiša od podneva",
    ],
    "rain_morn_then_dry": [
        "Kiša prijepodne, suvo od podneva",
        "Kiša ujutru, razvedravanje od podneva",
        "Padavine prijepodne, suvo poslije podne",
        "Jutarnja kiša, suvo i vedrije od podneva",
        "Kiša do podneva, potom suvo",
    ],
    "rain_dry_then_eve": [
        "Suvo tokom dana, kiša predveče",
        "Suvo danju, kiša u večernjim satima",
        "Pretežno suvo, kiša predveče",
        "Suvo do večeri, potom kiša",
    ],
    "rain_morn_eve": [
        "Kiša ujutru i predveče, suvo od podneva do večeri",
        "Kiša jutrom i uveče, suvo sredinom dana",
        "Padavine ujutru i predveče, suvo tokom dana",
    ],
    "rain_night_then_sun": [
        "Kiša tokom noći, sunčano tokom dana",
        "Noćna kiša, danju sunčano",
        "Kiša preko noći, vedro tokom dana",
    ],
    "rain_night_then_dry": [
        "Kiša tokom noći, suvo tokom dana",
        "Noćna kiša, danju suvo",
        "Kiša preko noći, suvo tokom dana",
    ],
    "rain_day_then_dry_eve": [
        "Kiša tokom dana do kasno poslijepodne, suvo predveče",
        "Kiša danju, suvo predveče",
        "Padavine tokom dana, suvo u večernjim satima",
    ],

    # --- temperature tails (appended after the sky/rain part) ---------------
    "temp_hot": [
        "vruće",
        "toplo i sparno",
        "veoma toplo",
    ],
    "temp_very_hot": [
        "izuzetno vruće",
        "veoma vruće",
        "pripeka",
    ],
    "temp_frost": [
        "mraz",
        "jutarnji mraz",
        "uz mraz",
    ],
    "temp_hard_frost": [
        "jak mraz",
        "jak jutarnji mraz",
        "oštar mraz",
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
