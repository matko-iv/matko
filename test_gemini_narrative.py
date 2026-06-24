"""Tests for gemini_narrative.py — the deterministic guardrail that keeps Gemini
factual (PDF: rephrase-and-validate). The guardrail is the ACTUAL guarantee: it
hard-gates the zero-tolerance phantoms (kiša/pljusak, grmljavina, snijeg, magla)
against the structured daily summary `ds`, and any failure falls back to the
rule-based sentence. Sky/wind descriptors are lenient so faithful rephrases like
"Sunčano ujutru, kiša od podneva" are not false-rejected.

Run from repo root:  python test_gemini_narrative.py   (exit 0 = pass)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import gemini_narrative as gn  # noqa: E402

DRY = {"precip_total": 0.0, "weather_code": 1, "wind_max": 2.0,
       "gust_max": 4.0, "cloud_cover_day": 30}
RAINY = {"precip_total": 5.0, "weather_code": 63, "wind_max": 4.0,
         "gust_max": 7.0, "cloud_cover_day": 80}


def test_rejects_phantom_rain():
    assert gn.validate("Kiša poslije podne", DRY) is False


def test_accepts_supported_rain():
    assert gn.validate("Povremena kiša tokom dana", RAINY) is True


def test_rejects_phantom_thunder():
    assert gn.validate("Grmljavina predveče", DRY) is False


def test_accepts_supported_thunder():
    assert gn.validate("Grmljavina od podneva", {"precip_total": 8.0,
                       "weather_code": 95, "wind_max": 5, "gust_max": 9}) is True


def test_rejects_phantom_snow():
    assert gn.validate("Snijeg ujutru", DRY) is False


def test_accepts_supported_snow():
    assert gn.validate("Snijeg tokom dana", {"precip_total": 4.0,
                       "weather_code": 73, "wind_max": 3, "gust_max": 6}) is True


def test_rejects_phantom_fog():
    assert gn.validate("Magla ujutru", DRY) is False


def test_accepts_supported_fog():
    assert gn.validate("Magla ujutru, sunčano od podneva",
                       {"precip_total": 0.0, "weather_code": 45,
                        "wind_max": 2, "gust_max": 3, "cloud_cover_day": 20}) is True


def test_lenient_sun_plus_rain_not_false_rejected():
    # The rule-based sentence legitimately combines sun + rain across periods;
    # rain is supported by data, sun is a lenient descriptor -> must pass.
    ds = {"precip_total": 3.0, "weather_code": 61, "wind_max": 4,
          "gust_max": 7, "cloud_cover_day": 45}
    assert gn.validate("Sunčano ujutru, kiša od podneva", ds) is True


def test_rejects_phantom_strong_wind():
    assert gn.validate("Jak vjetar tokom dana", DRY) is False


def test_accepts_supported_strong_wind():
    assert gn.validate("Jak vjetar tokom dana", {"precip_total": 0.0,
                       "weather_code": 1, "wind_max": 12.0, "gust_max": 18.0,
                       "cloud_cover_day": 30}) is True


def test_bare_light_wind_is_lenient():
    assert gn.validate("Pretežno vedro uz umjeren vjetar",
                       {"precip_total": 0.0, "weather_code": 1, "wind_max": 6.0,
                        "gust_max": 9.0, "cloud_cover_day": 40}) is True


def test_long_faithful_rephrase_not_rejected_by_length():
    # Complex days give long rule-based sentences; a faithful ~17-word rephrase
    # (rain + strong NW wind + gusts, all supported) must NOT be length-rejected.
    ds = {"precip_total": 3.5, "weather_code": 61, "wind_max": 11.0,
          "gust_max": 18.0, "cloud_cover_day": 50}
    text = ("Jača kiša prijepodne, suvo i vedrije od podneva, uz jak "
            "sjeverozapadni vjetar i udare do osamnaest metara")
    assert gn.validate(text, ds) is True


def test_strong_wind_with_direction_infix_is_gated():
    # "jak <smjer> vjetar" must still be treated as a strong-wind claim.
    assert gn.validate("Jak sjeverozapadni vjetar tokom dana", DRY) is False


def test_length_and_sanity():
    assert gn.validate("a", DRY) is False                      # too short
    assert gn.validate(" ".join(["riječ"] * 25), DRY) is False  # rambling (>22)


def test_daily_narrative_ai_keeps_valid_rephrase(monkeypatch=None):
    gn.rephrase = lambda s: "Tokom dana povremena kiša"          # valid paraphrase
    out = gn.daily_narrative_ai("Povremena kiša", RAINY)
    assert out == "Tokom dana povremena kiša", out


def test_daily_narrative_ai_falls_back_on_phantom():
    gn.rephrase = lambda s: "Sunčano, ali grmljavina uveče"      # phantom thunder
    out = gn.daily_narrative_ai("Pretežno vedro", DRY)
    assert out == "Pretežno vedro", out                         # fell back


def test_daily_narrative_ai_falls_back_on_api_failure():
    gn.rephrase = lambda s: None                                # API returned nothing
    out = gn.daily_narrative_ai("Pretežno vedro", DRY)
    assert out == "Pretežno vedro", out


class _FakeResp:
    def __init__(self, status, payload):
        self.status_code = status
        self._p = payload

    def json(self):
        return self._p

    def raise_for_status(self):
        pass


def test_rephrase_rejects_truncated_output():
    # finishReason MAX_TOKENS -> the sentence was cut off -> reject so the caller
    # falls back to the complete rule-based one (the "opisi se ne završe" bug).
    gn._http_post = lambda url, payload, timeout: _FakeResp(200, {
        "candidates": [{"finishReason": "MAX_TOKENS",
                        "content": {"parts": [{"text": "Tokom dana ved"}]}}]})
    assert gn.rephrase("Vedro i sunčano tokom dana", api_key="x") is None


def test_rephrase_accepts_complete_output():
    gn._http_post = lambda url, payload, timeout: _FakeResp(200, {
        "candidates": [{"finishReason": "STOP",
                        "content": {"parts": [{"text": "Tokom dana vedro i sunčano."}]}}]})
    assert gn.rephrase("Vedro i sunčano tokom dana", api_key="x") == "Tokom dana vedro i sunčano."


def test_rephrase_disables_thinking_and_has_room():
    # Guard the regression: thinking must be disabled and the token budget ample,
    # else gemini-3.5-flash spends the budget thinking and truncates the sentence.
    captured = {}
    def _cap(url, payload, timeout):
        captured.update(payload.get("generationConfig", {}))
        return _FakeResp(200, {"candidates": [{"finishReason": "STOP",
                         "content": {"parts": [{"text": "ok."}]}}]})
    gn._http_post = _cap
    gn.rephrase("Vedro", api_key="x")
    assert captured.get("thinkingConfig", {}).get("thinkingBudget") == 0, captured
    assert captured.get("maxOutputTokens", 0) >= 200, captured


def test_generate_uses_hourly_prompt_and_legacy_model():
    cap = {}
    def _cap(url, payload, timeout):
        cap['url'] = url
        cap['prompt'] = payload['contents'][0]['parts'][0]['text']
        return _FakeResp(200, {"candidates": [{"finishReason": "STOP",
                         "content": {"parts": [{"text": "Sunčano prije podne"}]}}]})
    gn._http_post = _cap
    rows = [{"hour": 8, "temperature_2m": 20, "cloud_cover": 80, "precipitation": 0}]
    out = gn.generate("2026-06-24", rows, {0: {"icon": "sun"}}, api_key="x")
    assert out == "Sunčano prije podne", out
    assert "gemini-3-flash-preview" in cap['url'], cap['url']
    assert "Satni podaci za Budvu" in cap['prompt']
    assert "Maksimalno 6-7 riječi" in cap['prompt']


def test_generate_rejects_truncation():
    gn._http_post = lambda u, p, t: _FakeResp(200, {"candidates": [
        {"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "Sunčano pri"}]}}]})
    assert gn.generate("2026-06-24", [{"hour": 8}], {}, api_key="x") is None


def test_daily_narrative_ai_generate_path_is_validated():
    # hourly_rows present -> uses generate(); phantom rain on a dry day -> fallback
    gn.generate = lambda date, rows, wmo, **k: "Kiša poslije podne"
    out = gn.daily_narrative_ai("Vedro i sunčano", DRY,
                                hourly_rows=[{"hour": 8}], wmo_codes={})
    assert out == "Vedro i sunčano", out
    # valid generated text on a dry day -> kept
    gn.generate = lambda date, rows, wmo, **k: "Vedro tokom dana"
    out2 = gn.daily_narrative_ai("Vedro i sunčano", DRY,
                                 hourly_rows=[{"hour": 8}], wmo_codes={})
    assert out2 == "Vedro tokom dana", out2


def main():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = []
    for fn in fns:
        # restore the real rephrase between tests that monkeypatch it
        import importlib
        importlib.reload(gn)
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            fails.append(f"{fn.__name__}: {e}")
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            fails.append(f"{fn.__name__}: {type(e).__name__}: {e}")
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
    if fails:
        print(f"\n{len(fails)} failure(s).")
        return 1
    print("\nPASS — Gemini rephrase-and-validate guardrail OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
