"""Factual-only Montenegrin weather narratives: Gemini as a rephraser.

The rule-based `_daily_narrative()` already produces a correct sentence.
Letting Gemini generate from the hourly table hallucinates phantom
rain/wind/thunder, so Gemini gets the correct sentence and is asked only for
a stylistic paraphrase; a deterministic guardrail rejects anything unfaithful
and falls back to the rule-based sentence. The guardrail, not the LLM, is
the factual guarantee.

  daily_narrative_ai(correct_sentence, ds)
      -> rephrase(correct_sentence) -> validate(candidate, ds) -> candidate
      -> else: correct_sentence  (safe fallback)

stdlib + lazily-imported `requests`; the guardrail itself needs only stdlib,
so it tests without a network.
"""

import os
import re

# Gemini 3.x GA Flash model. Pinned so output doesn't drift when
# Google changes defaults.
MODEL = "gemini-3.5-flash"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# WMO weather codes, matching forecast_48h_v3._daily_narrative.
SNOW_CODES = {71, 73, 75, 77, 85, 86}
THUNDER_CODES = {95, 96, 99}
FOG_CODES = {45, 48}

RAIN_PRECIP_MIN_MM = 0.1   # precip at/above which a rain mention is supported
STRONG_WIND_MS = 8.0       # wind_max for a "jak vjetar" claim
STRONG_GUST_MS = 13.0      # gust_max for a "udari" claim
MAX_WORDS = 22             # complex days give long rule-based sentences; only
                           # reject genuine rambling, not faithful long rephrases


def _num(ds, key, default=0.0):
    try:
        v = (ds or {}).get(key)
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def _wmo(ds):
    try:
        v = (ds or {}).get("weather_code")
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


# Zero-tolerance phantom phenomena: stemmed Montenegrin token -> predicate
# over the daily summary `ds`. A rephrase mentioning one the data doesn't
# support is rejected.
_PHANTOM = {
    "kiš":     lambda d: _num(d, "precip_total") >= RAIN_PRECIP_MIN_MM,
    "pljus":   lambda d: _num(d, "precip_total") >= RAIN_PRECIP_MIN_MM,
    "grmljav": lambda d: _wmo(d) in THUNDER_CODES,
    "snij":    lambda d: _wmo(d) in SNOW_CODES,
    "snjež":   lambda d: _wmo(d) in SNOW_CODES,
    "magl":    lambda d: _wmo(d) in FOG_CODES,
}

# Strong-wind claims (jak [smjer] vjetar / olujno / orkansko / udari) are
# gated on speed; bare "vjetar" / "slab vjetar" stays lenient. The regex
# allows one wind-direction word between "jak" and "vjetar", but not two, so
# "jaka kiša, slab vjetar" is not mis-flagged.
_STRONG_WIND_RE = re.compile(r"jak\w*\s+(?:\w+\s+)?vjet|oluj|orkan|udar")


def validate(text, ds):
    """True iff `text` is a faithful rephrase: no phantom rain/thunder/snow/
    fog the data `ds` lacks, no strong-wind claim without the speed. Sky and
    wind descriptors are otherwise lenient so faithful rephrases aren't
    false-rejected. On failure the caller falls back to the rule-based
    sentence, which is the real factual guarantee."""
    if not text or not text.strip():
        return False
    t = text.lower()

    for token, supported in _PHANTOM.items():
        if token in t and not supported(ds):
            return False

    if _STRONG_WIND_RE.search(t):
        if not (_num(ds, "wind_max") >= STRONG_WIND_MS
                or _num(ds, "gust_max") >= STRONG_GUST_MS):
            return False

    n = len(text.split())
    if n < 1 or n > MAX_WORDS or len(text.strip()) < 3:
        return False
    return True


SYSTEM = (
    "Ti si jezički uređivač za vremenske prognoze na crnogorskom jeziku. "
    "Dobićeš jednu TAČNU rečenicu o vremenu. Tvoj JEDINI zadatak je da je "
    "preformulišeš da zvuči prirodno i tečno. "
    "STROGA PRAVILA: "
    "1) Ne dodaji NIJEDNU novu informaciju (nikakvu kišu, vjetar, grmljavinu, "
    "maglu, snijeg, temperaturu ili vrijeme koje nije u originalu). "
    "2) Ne mijenjaj nijednu brojku, smjer vjetra, niti vremenski period. "
    "3) Ako nešto nije u originalnoj rečenici, NE smije se pojaviti. "
    "4) Vrati rečenicu slične dužine kao original; ne izostavljaj nijednu "
    "informaciju i bez ikakvih objašnjenja."
)

# Few-shot pairs teach the rephrase transform, not fact generation.
FEWSHOT = [
    ("Sunčano prije podne, kiša od podneva; jak SZ vjetar.",
     "Prijepodne sunčano, a od podneva kiša uz jak sjeverozapadni vjetar."),
    ("Pretežno oblačno cijeli dan, bez padavina; slab vjetar.",
     "Tokom dana pretežno oblačno i bez padavina, vjetar slab."),
]


def _build_contents(correct_sentence):
    contents = []
    for src, tgt in FEWSHOT:
        contents.append({"role": "user", "parts": [{"text": f"Rečenica: {src}"}]})
        contents.append({"role": "model", "parts": [{"text": tgt}]})
    contents.append({"role": "user",
                     "parts": [{"text": f"Rečenica: {correct_sentence}"}]})
    return contents


def _http_post(url, payload, timeout):
    """Single POST seam (so the call can be stubbed in tests). Lazy `requests`
    import keeps the guardrail importable without the dependency."""
    import requests
    return requests.post(url, json=payload, timeout=timeout)


def rephrase(correct_sentence, *, api_key=None, timeout=15, retries=4):
    """Ask Gemini to paraphrase the already-correct sentence into natural
    Montenegrin. Returns the candidate, or None on any failure (the caller
    validates and falls back). Raw REST, no SDK.

    Thinking must stay disabled: gemini-3.5-flash defaults to medium
    thinking, which spends the output-token budget reasoning and returns the
    sentence truncated mid-word ("opisi se ne završe"). `thinkingBudget: 0`
    turns it off, `maxOutputTokens` sits well above the longest sentence, and
    any response with finishReason != STOP is rejected as a backstop, so a
    half sentence never ships. temperature/top_p/top_k stay unset, as Google
    discourages them on Gemini 3.x.
    """
    key = api_key if api_key is not None else GEMINI_API_KEY
    if not key or not correct_sentence:
        return None
    import time
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={key}")
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": _build_contents(correct_sentence),
        "generationConfig": {
            "maxOutputTokens": 256,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    for attempt in range(retries):
        try:
            resp = _http_post(url, payload, timeout)
            if resp.status_code == 429:                 # free-tier rate limit
                time.sleep(2 ** attempt * 5)            # 5/10/20/40 s backoff
                continue
            resp.raise_for_status()
            cand = (resp.json().get("candidates") or [{}])[0]
            # Reject anything cut off (MAX_TOKENS) or not finished cleanly, so a
            # truncated half-sentence never ships — fall back to rule-based.
            if cand.get("finishReason") not in (None, "STOP"):
                return None
            text = cand["content"]["parts"][0]["text"].strip()
            return text.strip('"').strip()
        except Exception:
            return None
    return None


def generate(date_str, hourly_rows, wmo_codes, *, api_key=None, timeout=15, retries=4):
    """Full Gemini narrative from hourly data — the legacy
    forecast_48h_v3._gemini_narrative prompt verbatim, on
    gemini-3-flash-preview. Returns the text, or None on failure/truncation.
    `wmo_codes` is passed in to avoid a circular import; the caller must
    validate() the output before use."""
    key = api_key if api_key is not None else GEMINI_API_KEY
    if not key or not hourly_rows:
        return None
    import time

    def _ok(x):                       # not None and not NaN (avoid a pandas dep)
        return x is not None and x == x

    lines = []
    for h in hourly_rows:
        hour = h.get('hour', 0)
        temp = h.get('temperature_2m', h.get('temperature_2m_ensemble', '?'))
        hum = h.get('relative_humidity_2m', h.get('relative_humidity_2m_ensemble', '?'))
        wind = h.get('wind_speed_10m', h.get('wind_speed_10m_ensemble', '?'))
        press = h.get('surface_pressure', h.get('pressure_msl', '?'))
        cloud = h.get('cloud_cover', '?')
        precip_raw = h.get('precipitation', h.get('precipitation_ensemble', 0))
        precip = precip_raw if _ok(precip_raw) else 0
        wc_raw = h.get('weather_code', h.get('weather_code_raw', 0))
        wc = int(wc_raw) if _ok(wc_raw) else 0
        icon = (wmo_codes or {}).get(wc, {}).get('icon', 'unknown')
        emoji = h.get('weather_emoji', '')
        lines.append(
            f"  {date_str} {hour:02d}:00 {icon} {emoji}  {temp}°   {hum}%   {wind}   {press}   {cloud}%   {precip}"
        )
    hourly_text = "\n".join(lines)

    prompt = (
        f"Satni podaci za Budvu, {date_str} (sat  ikonica  temp  vlažnost  vjetar_m/s  pritisak_hPa  oblačnost  padavine_mm):\n"
        f"{hourly_text}\n\n"
        "Na osnovu ovih satnih podataka za Budvu, napiši kratak izvještaj.\n\nPravila:\n1. Maksimalno 6-7 riječi.\n2. Fokusiraj se na glavnu promjenu vremena (npr. prelaz iz oblačnog u sunčano).\n3. Navedi doba dana kada se promjena dešava.\n4.Ako nema kiše ili vjetra, ne spominji ih."
    )

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-3-flash-preview:generateContent?key={key}")
    payload = {"contents": [{"parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.3, "maxOutputTokens": 200,
                                    "thinkingConfig": {"thinkingBudget": 0}}}
    for attempt in range(retries):
        try:
            resp = _http_post(url, payload, timeout)
            if resp.status_code == 429:
                time.sleep(2 ** attempt * 5)
                continue
            resp.raise_for_status()
            cand = (resp.json().get("candidates") or [{}])[0]
            if cand.get("finishReason") not in (None, "STOP"):
                return None
            text = cand["content"]["parts"][0]["text"].strip()
            return text.strip('"').strip()
        except Exception:
            return None
    return None


def daily_narrative_ai(correct_sentence, ds, hourly_rows=None, wmo_codes=None):
    """Gemini narrative behind the guardrail, with `correct_sentence` as the
    fallback. With hourly data Gemini generates via the legacy prompt;
    otherwise it rephrases the rule-based sentence. Either way the candidate
    must pass validate() against `ds`, so a phantom or truncation never
    reaches the output."""
    if hourly_rows:
        candidate = generate(ds.get("date", ""), hourly_rows, wmo_codes)
    else:
        candidate = rephrase(correct_sentence) if correct_sentence else None
    if candidate and validate(candidate, ds):
        return candidate
    return correct_sentence
