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

    # --- snow (snow branches; every phrasing mentions snijeg/snježno) --------
    "snow_all_day": [
        "Snijeg tokom cijelog dana",
        "Snijeg gotovo cijeli dan",
        "Snježne padavine tokom dana",
        "Snijeg s prekidima cijeli dan",
        "Snijeg tokom čitavog dana",
    ],
    "snow_morn_then_dry": [
        "Snijeg prije podne, prestanak od podneva",
        "Snijeg ujutru, suvo od podneva",
        "Jutarnji snijeg, potom prestanak",
        "Snijeg do podneva, zatim suvo",
    ],
    "snow_dry_then_pm": [
        "Suvo ujutru, snijeg od podneva",
        "Suvo prijepodne, snijeg poslije podne",
        "Vedrije ujutru, snijeg od podneva",
    ],
    "snow_dry_then_eve": [
        "Suvo tokom dana, snijeg predveče",
        "Suvo danju, snijeg u večernjim satima",
        "Pretežno suvo, snijeg predveče",
    ],
    "snow_intermittent": [
        "Povremeni snijeg",
        "Mjestimično snijeg",
        "Snijeg s prekidima",
        "Povremene snježne padavine",
    ],
    "snow_heavy_intermittent": [
        "Povremeni obilniji snijeg",
        "Mjestimično jači snijeg",
        "Obilniji snijeg s prekidima",
    ],

    # --- thunder (grmljavina branches) --------------------------------------
    "thunder_sun_then_storm": [
        "Sunčano prije podne, grmljavinska kiša od podneva",
        "Vedro prijepodne, grmljavina od podneva",
        "Sunčano ujutru, pljuskovi s grmljavinom poslije podne",
        "Vedro jutro, grmljavinski pljuskovi od podneva",
    ],
    "thunder_morn_then_calm": [
        "Grmljavina prije podne, smirivanje od podneva",
        "Grmljavina ujutru, mirnije od podneva",
        "Jutarnja grmljavina, potom smirivanje",
    ],
    "thunder_eve": [
        "Pretežno suvo, grmljavina predveče",
        "Suvo danju, grmljavina predveče",
        "Pretežno suvo, grmljavina u večernjim satima",
    ],
    "thunder_day": [
        "Oblačno uz povremenu grmljavinu tokom dana",
        "Nestabilno uz grmljavinu tokom dana",
        "Oblačno uz pljuskove i grmljavinu",
    ],
    "thunder_night": [
        "Grmljavina tokom noći, mirnije tokom dana",
        "Noćna grmljavina, danju mirnije",
        "Grmljavina preko noći, smirivanje danju",
    ],
    "thunder_unstable": [
        "Nestabilno uz povremenu grmljavinu",
        "Nestabilno vrijeme uz grmljavinu",
        "Promjenljivo i nestabilno, moguća grmljavina",
    ],

    # --- fog ----------------------------------------------------------------
    "fog_then_sun": [
        "Magla ujutru, sunčano od podneva",
        "Jutarnja magla, potom sunčano",
        "Magla ujutru, razvedravanje od podneva",
        "Magla prije podne, sunčano poslije podne",
    ],
    "fog_then_partly": [
        "Magla ujutru, oblaci i sunce od podneva",
        "Jutarnja magla, potom promjenljivo",
        "Magla ujutru, sunce i oblaci od podneva",
    ],
    "fog_then_cloud": [
        "Magla ujutru, oblačno od podneva",
        "Jutarnja magla, potom oblačno",
        "Magla ujutru, tmurno od podneva",
    ],

    # --- steady sky all day (no AM/PM trend) --------------------------------
    "clear_all_day": [
        "Vedro i sunčano tokom dana",
        "Sunčano cijeli dan",
        "Vedro i sunčano cijelog dana",
        "Pretežno vedro i sunčano",
        "Sunčano i vedro tokom čitavog dana",
    ],
    "mostly_clear_all_day": [
        "Pretežno sunčano, poneki oblak",
        "Pretežno vedro uz poneki oblak",
        "Sunčano uz malo oblaka",
        "Pretežno sunčano tokom dana",
    ],
    "mostly_cloudy_all_day": [
        "Pretežno oblačno, malo sunca",
        "Pretežno oblačno tokom dana",
        "Više oblaka, malo sunca",
        "Uglavnom oblačno uz malo sunca",
    ],
    "cloudy_all_day": [
        "Oblačno tokom cijelog dana bez padavina",
        "Oblačno cijeli dan, bez padavina",
        "Tmurno tokom dana, bez padavina",
        "Oblačno čitav dan",
    ],
    # short sky labels (used when only part of the day is sampled)
    "sky_clear_short": ["Vedro", "Vedro i sunčano", "Sunčano"],
    "sky_mostly_clear_short": ["Pretežno vedro", "Pretežno sunčano", "Uglavnom vedro"],
    "sky_partly_short": ["Po koji oblak", "Promjenljivo oblačno", "Djelimično oblačno"],
    "sky_mostly_cloudy_short": ["Pretežno oblačno", "Uglavnom oblačno"],
    "sky_cloudy_short": ["Oblačno", "Tmurno", "Potpuno oblačno"],

    # --- wind adjectives (composed as "<adj> <smjer> vjetar") ---------------
    "wind_strong_adj": ["jak", "snažan", "izražen"],
    "wind_moderate_adj": ["umjeren", "osjetan", "umjeren do svjež"],
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
