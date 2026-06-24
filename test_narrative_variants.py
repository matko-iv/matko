"""Tests for narrative_variants.py — the phrasing pools that give variable-weather
days more variety in the rule-based daily narrative. Each pool holds equivalent
ways to describe the SAME classified weather; the picker is deterministic per day
(stable JSON) but varies across days.

Run from repo root:  python test_narrative_variants.py   (exit 0 = pass)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import narrative_variants as nv  # noqa: E402

# Phantom tokens a DRY-day phrasing must never contain (would be a false alarm).
PHANTOM_PREFIXES = ("kiš", "pljus", "snij", "snjež", "grmljav", "magl")
# Pools that describe dry (no-precipitation) weather.
DRY_KEYS = ("sun_to_cloud", "cloud_to_sun", "sun_to_partly", "partly_to_sun",
            "increasing_cloud", "cloud_to_partly", "variable",
            "eve_clouding", "eve_clearing", "partly_steady")


def test_variant_is_deterministic_for_same_seed():
    a = nv.variant("variable", "seed-A")
    b = nv.variant("variable", "seed-A")
    assert a == b, (a, b)


def test_variant_varies_across_seeds():
    seen = {nv.variant("variable", f"day-{i}") for i in range(40)}
    assert len(seen) >= 2, f"pool never varied across seeds: {seen}"


def test_unknown_key_returns_literal():
    assert nv.variant("Vedro i sunčano", "x") == "Vedro i sunčano"


def test_every_pool_nonempty_and_stringy():
    for key, pool in nv.VARIANTS.items():
        assert pool and all(isinstance(s, str) and s.strip() for s in pool), key


def test_dry_pools_contain_no_phantom_phenomena():
    # A dry-day phrasing must never mention rain/snow/thunder/fog — otherwise the
    # rule-based sentence itself would assert a phantom.
    for key in DRY_KEYS:
        for phrase in nv.VARIANTS[key]:
            low = phrase.lower()
            for p in PHANTOM_PREFIXES:
                assert p not in low, f"{key}: phantom '{p}' in {phrase!r}"


def test_rain_pools_all_mention_rain():
    # Rain-branch phrasings must mention rain (kiša / padavine), so they stay
    # faithful when the rule-based code reaches them (precip is present).
    for key, pool in nv.VARIANTS.items():
        if not key.startswith("rain_"):
            continue
        for phrase in pool:
            low = phrase.lower()
            assert ("kiš" in low or "padav" in low), f"{key}: no rain word in {phrase!r}"


def test_canonical_phrasing_preserved_as_first_entry():
    # The original wording stays as one option (entry 0), so nothing is lost.
    assert nv.VARIANTS["sun_to_cloud"][0] == "Sunčano prije podne, oblaci od podneva"
    assert nv.VARIANTS["variable"][0] == "Promjenljivo oblačno"


def main():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = []
    for fn in fns:
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
    print("\nPASS — narrative variant pools OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
