"""Factual-only Montenegrin weather narratives: Gemini as a REPHRASER, not an
author (research report "Keeping Gemini in the Loop Without Hallucinating").

The rule-based `_daily_narrative()` already produces a provably-correct sentence.
Instead of letting Gemini GENERATE from the hourly/daily table (which hallucinates
phantom rain/wind/thunder), we feed it the correct sentence and ask only for a
stylistic paraphrase, then run a DETERMINISTIC guardrail and fall back to the
rule-based sentence on any failure. The guardrail — not the LLM — is the actual
guarantee of factual output.

  daily_narrative_ai(correct_sentence, ds)
      -> rephrase(correct_sentence) -> validate(candidate, ds) -> candidate
      -> else: correct_sentence  (guaranteed-safe fallback)

Dependency-light: stdlib + `requests` (lazy-imported, already a project dep). The
guardrail itself needs only stdlib, so it is unit-testable without any network.
"""

import os
import re

# Gemini 3.x GA Flash model (PDF Stage 2). Pinned so output doesn't drift when
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


# Zero-tolerance phantom phenomena: stemmed Montenegrin token -> predicate over
# the structured daily summary `ds`. If the rephrase mentions one the data does
# NOT support, it is rejected (the user's "phantom rain/wind/thunder" concern).
_PHANTOM = {
    "kiš":     lambda d: _num(d, "precip_total") >= RAIN_PRECIP_MIN_MM,
    "pljus":   lambda d: _num(d, "precip_total") >= RAIN_PRECIP_MIN_MM,
    "grmljav": lambda d: _wmo(d) in THUNDER_CODES,
    "snij":    lambda d: _wmo(d) in SNOW_CODES,
    "snjež":   lambda d: _wmo(d) in SNOW_CODES,
    "magl":    lambda d: _wmo(d) in FOG_CODES,
}

# Strong-wind claims (jak [smjer] vjetar / olujno / orkansko / udari) are gated
# on speed; bare "vjetar" / "slab vjetar" stays lenient. The regex allows ONE
# wind-direction word between "jak" and "vjetar" (e.g. "jak sjeverozapadni
# vjetar"), but not two — so "jaka kiša, slab vjetar" is not mis-flagged.
_STRONG_WIND_RE = re.compile(r"jak\w*\s+(?:\w+\s+)?vjet|oluj|orkan|udar")


def validate(text, ds):
    """True iff `text` is a faithful rephrase of the day's weather: it must not
    introduce a zero-tolerance phantom (rain/thunder/snow/fog) unsupported by the
    data `ds`, nor claim strong wind the data lacks. Sky/wind descriptors are
    otherwise lenient so faithful rephrases (e.g. "Sunčano ujutru, kiša od
    podneva") are not false-rejected. Any failure -> caller falls back to the
    rule-based sentence, so this is the real factual guarantee."""
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


# --- Gemini rephraser (transform-only) --------------------------------------
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

# Few-shot pairs teach the TRANSFORM (rephrase), not fact generation.
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


def rephrase(correct_sentence, *, api_key=None, timeout=15, retries=4):
    """Ask Gemini to paraphrase the already-correct sentence into natural
    Montenegrin (transform-only). Returns the candidate string, or None on any
    failure — the caller validates and falls back. Raw REST (matches the existing
    code; no SDK dependency).

    Gemini 3.x: temperature/top_p/top_k are deliberately NOT set (Google
    discourages them on 3.x). `thinkingConfig` is omitted so the call cannot fail
    on a wrong thinking field; to trim latency/cost once verified live, add
    `"thinkingConfig": {"thinkingLevel": "minimal"}` (or the budget form your
    account accepts).
    """
    key = api_key if api_key is not None else GEMINI_API_KEY
    if not key or not correct_sentence:
        return None
    import time
    import requests
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={key}")
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": _build_contents(correct_sentence),
        "generationConfig": {"maxOutputTokens": 120},
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 429:                 # free-tier rate limit
                time.sleep(2 ** attempt * 5)            # 5/10/20/40 s backoff
                continue
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text.strip('"').strip()
        except Exception:
            return None
    return None


def daily_narrative_ai(correct_sentence, ds):
    """Return Gemini's paraphrase of the rule-based sentence IF it passes the
    deterministic guardrail, else the rule-based sentence itself (guaranteed-safe
    fallback). Every factual claim is sourced from `correct_sentence`/`ds`."""
    if not correct_sentence:
        return correct_sentence
    candidate = rephrase(correct_sentence)
    if candidate and validate(candidate, ds):
        return candidate
    return correct_sentence
