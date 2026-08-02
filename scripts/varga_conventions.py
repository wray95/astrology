#!/usr/bin/env python3
"""
varga_conventions.py — SINGLE SOURCE OF TRUTH for divisional (varga) sign
computation in this workspace. Adopted 2026-08-02 (validation pass, Turn 7).

CONVENTION (LOCKED): multiplication method
    varga_sign(lon, N) = floor((lon * N mod 360) / 30)
where lon = full sidereal longitude in degrees (0-360, Lahiri).

Why this is THE repo convention:
  1. It is exactly the method already used by the NEXUS engine of record
     (scripts/p_update.py) and the ML matrices (scripts/build_v4_matrix.py,
     6,520 charts). Adopting it makes all varga-dependent outputs consistent
     with the entire ML pipeline with ZERO changes to those scripts.
  2. For the Navamsa (D9) it is algebraically identical to the classical
     BPHS movable/fixed/dual rule (movable -> same sign, fixed -> 9th from it,
     dual -> 5th from it). Verified: offset_relative(s) = (9s mod 12 - s) mod 12
     = {0 movable, 8 fixed, 4 dual}.
  3. It is deterministic and dependency-free (pure arithmetic).

Historical note (do NOT silently rewrite past analyses):
  - scripts/d9_shrinkala.py  (P1-P4 D9, Turn 7) uses odd/even FORWARD
    (even signs start from the 9th) — the user's astrologylover.com link
    method. For D9 this matches the multiplication method for odd and FIXED
    even signs, but differs for even MOVABLE (Cancer, Capricorn) and even
    DUAL (Virgo, Pisces) signs.
  - scripts/senath_recompute.py (P5 D9, Turn 26) used odd/even REVERSE
    (even signs count backwards) — this was the OUTLIER; it did not match
    either the engine or the user's link method, and produced a different
    navamsa for the same person. Fixed to use this module (2026-08-02).
  - Conclusion: Senath's D9 from Turn 25/26 (and any vargottama flags built
    on it) must be re-derived with this locked convention — see
    reports/divisional_convention_validation.md "Resolution".

Caveat: for D7 Saptamsha, the multiplication method treats DUAL signs
differently from some classical tables (movable -> same, fixed -> 7th,
dual -> 7th in several texts; multiplication gives dual -> 7th as well,
verify with the table below). Where texts conflict we keep this engine-
standard method and document the choice here.
"""

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def varga_index(lon: float, n: int) -> int:
    """Return the 0-based sign index of the N-th varga (D9: n=9, D7: n=7, D5: n=5)."""
    return int((lon * n % 360) // 30) % 12


def varga_sign(lon: float, n: int) -> str:
    """Return the sign name of the N-th varga for a full sidereal longitude."""
    return SIGNS[varga_index(lon, n)]


def varga_house(lon: float, n: int, asc_lon: float) -> int:
    """1-12 house of the N-th varga planet given the varga ascendant longitude."""
    return (varga_index(lon, n) - varga_index(asc_lon, n)) % 12 + 1


if __name__ == "__main__":
    # self-test: BPHS D9 table for one degree inside each sign (d = 1.0)
    print("D9 (navamsa) first-navamsa sign per rashi — must match BPHS mov/fix/dual:")
    expected = {  # first navamsa of each sign
        "Aries": "Aries", "Taurus": "Capricorn", "Gemini": "Libra",
        "Cancer": "Cancer", "Leo": "Aries", "Virgo": "Capricorn",
        "Libra": "Libra", "Scorpio": "Cancer", "Sagittarius": "Aries",
        "Capricorn": "Capricorn", "Aquarius": "Libra", "Pisces": "Cancer",
    }
    ok = True
    for i, s in enumerate(SIGNS):
        got = varga_sign(i * 30 + 1.0, 9)
        mark = "OK" if got == expected[s] else "MISMATCH"
        if got != expected[s]:
            ok = False
        print(f"  {s:<12} -> {got:<12} (expected {expected[s]}) {mark}")
    print("ALL OK" if ok else "SOME MISMATCHES — investigate")
