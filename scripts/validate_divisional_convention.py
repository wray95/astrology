#!/usr/bin/env python3
"""
VALIDATE DIVISIONAL CHART CONVENTIONS (D9 / D7 / D5) in the P-series engine.
================================================================================
The P-series engine (scripts/p_update.py) computes all vargas with the
MULTIPLICATION method:  varga_sign = floor((lon * N) mod 360 / 30).

This script compares that against the classical conventions used elsewhere in
this repo and by the user's source links:
  - senath_recompute.py / navamsa_senath.py  → odd/even, even signs REVERSE
  - astrologylover.com (Turn-7 user link)     → odd signs from same sign,
                                               even signs from 9th (FORWARD)
  - BPHS movable/fixed/dual rule              → the multiplication method is
                                               algebraically equivalent to it
Output: for each P-series person, which planets' varga SIGNS differ between
methods, and whether the P-series marriage/children scores change.
"""
import json, sys
sys.path.insert(0, "scripts")
import swisseph as swe
from p_update import PD, P7, S, EX, OW, DB, SL, marriage_score, children_score, compute

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

def mult(lon, n):
    return int((lon * n % 360) // 30)          # p_update.py method

def odd_even_reverse(lon, n, off_even):
    """senath_recompute.py style: odd sign forward from same; even sign
    from (sign - n) [reverse] OR from (sign + off_even + n) [forward]."""
    s = int(lon // 30) % 12
    d = lon % 30
    k = int(d // (30.0 / n))
    if s % 2 == 0:
        return (s + k) % 12
    if off_even is None:
        return (s - k) % 12
    return (s + off_even + k) % 12

def bphs_movfixdual(lon, n, off_fixed, off_dual):
    """BPHS movable/fixed/dual: movable→same, fixed→+off_fixed, dual→+off_dual.
    (Equivalent to multiplication method; included for clarity.)"""
    s = int(lon // 30) % 12
    d = lon % 30
    k = int(d // (30.0 / n))
    off = {0: 0, 1: off_fixed, 2: off_dual}[s % 3]
    return (s + off + k) % 12

CONV = {
    "D9": {"mult": (9, None, None, "mult"),
           "oer": (9, None, None, "odd/even REVERSE (senath_recompute)"),
           "oef": (9, 8, None, "odd/even FORWARD from 9th (Turn-7 link)"),
           "mfd": (9, 8, 4, "BPHS mov/fix/dual (=mult)")},
    "D7": {"mult": (7, None, None, "mult"),
           "oer": (7, None, None, "odd/even REVERSE"),
           "oef": (7, 6, None, "odd/even FORWARD from 7th (=mult)")},
    "D5": {"mult": (5, None, None, "mult"),
           "oer": (5, None, None, "odd/even REVERSE"),
           "oef": (5, 4, None, "odd/even FORWARD from 5th"),
           "mfd": (5, 4, 8, "BPHS mov/fix/dual (=mult)")},
}

def varga_sign(lon, n, mode):
    s = int(lon // 30) % 12
    d = lon % 30
    k = int(d // (30.0 / n))
    if mode == "mult":
        return int((lon * n % 360) // 30)
    if mode == "oer":
        return (s + k) % 12 if s % 2 == 0 else (s - k) % 12
    if mode == "oef":
        return (s + k) % 12 if s % 2 == 0 else (s + (n // 2 + 1) + k) % 12 if n == 5 else (s + 8 + k) % 12
    # mfd
    off = {9: {0: 0, 1: 8, 2: 4}, 7: {0: 0, 1: 6, 2: 6}, 5: {0: 0, 1: 4, 2: 8}}[n]
    return (s + off[s % 3] + k) % 12

report = {}
for person in PD:
    ch = compute(person)
    asc_sid = ch["asc_deg"] + S.index(ch["lagna"]) * 30
    for varga in ("D9", "D7", "D5"):
        n = {"D9": 9, "D7": 7, "D5": 5}[varga]
        base = "mult"
        rows = []
        for pn in P7:
            lon = ch["planets"][pn]["sid"]
            m = varga_sign(lon, n, "mult")
            diffs = {}
            for name, (nn, off, off2, label) in CONV[varga].items():
                if name == "mult":
                    continue
                v = varga_sign(lon, n, name)
                if v != m:
                    diffs[name] = (S[v], S[m])
            if diffs:
                rows.append({"planet": pn, "mult": S[m],
                             "diffs": {k: {"conv_sign": v[0], "mult_sign": v[1]} for k, v in diffs.items()}})
        report.setdefault(varga, {})[person] = rows

# score impact: does any convention change marriage/children raw scores?
score_impact = {}
for person in PD:
    ch = compute(person)
    m_mar = marriage_score(ch)
    m_chi = children_score(ch)
    score_impact[person] = {"marriage_raw": m_mar, "children_raw": m_chi,
                            "marriage_pct": ch.get("marriage_pct", None)}

print("=" * 78)
print("VARGAS CONVENTION COMPARISON — planets whose varga SIGN differs from")
print("the multiplication method used in p_update.py")
print("=" * 78)
total_diff = 0
for varga in ("D9", "D7", "D5"):
    print(f"\n--- {varga} ---")
    for person, rows in report[varga].items():
        if rows:
            total_diff += len(rows)
            for r in rows:
                print(f"  {person:>4} {r['planet']:<9} mult={r['mult']:<10} " +
                      "; ".join(f"{k}->{v['conv_sign']}" for k, v in r["diffs"].items()))
print(f"\nTOTAL planets with divergent varga sign vs mult method: {total_diff}")

json.dump({"report": report, "score_impact": score_impact},
          open("dataset/divisional_convention_audit.json", "w"), indent=1)
print("Wrote dataset/divisional_convention_audit.json")
