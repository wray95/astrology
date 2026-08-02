#!/usr/bin/env python3
"""
H2 TEST (v2, pre-registered) — first career event vs Saturn transit of natal
Saturn sign. Birth-date only. Swiss Ephemeris Lahiri.

Windows: A = [entry into natal Saturn sign → entry into next sign] (~2.5y)
         B = exact Saturn return ±1y (subset of A)
         C = 2.5y before A (control) and 2.5y after A (control)
Chance: P(event in A) ≈ 2.5/29.46 ≈ 8.5% (binomial, one-sided).
Events: career_active start year (n≈910) + debut (n≈34).
"""
import json, sys, math, datetime, re, gzip, csv
from collections import Counter
sys.path.insert(0, "scripts")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
DAYS = 365.25
SATURN_PID = 6

def jd_of(y, m, d):
    return swe.julday(y, m, d, 12.0)

def saturn_lon(jd):
    lt, _ = swe.calc_ut(jd, SATURN_PID)
    return (lt[0] - swe.get_ayanamsa(jd)) % 360

def natal_saturn_sign(y, m, d):
    return int(saturn_lon(jd_of(y, m, d)) // 30)

def parse_birth(s):
    """Accept YYYY-MM-DD or '1 January 1918' or YYYY."""
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return tuple(map(int, m.groups()))
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
    if m:
        mon = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
               "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
        return int(m.group(3)), mon.get(m.group(2)[:3].capitalize(), 1), int(m.group(1))
    m = re.match(r"^(\d{4})$", s)
    if m:
        return int(m.group(1)), 6, 15
    return None

def global_sign_entries(from_year=1900, to_year=2105):
    """All Saturn sidereal sign-entry JDs, computed ONCE (universal table)."""
    entries = []
    jd = jd_of(from_year, 1, 1)
    end = jd_of(to_year, 12, 31)
    prev = None
    step = 4.0
    while jd <= end:
        s = int(saturn_lon(jd) // 30)
        if prev is not None and s != prev:
            lo, hi = jd - step, jd
            for _ in range(20):
                mid = (lo + hi) / 2
                if int(saturn_lon(mid) // 30) == s:
                    hi = mid
                else:
                    lo = mid
            entries.append((hi, s))
        prev = s
        jd += step
    return entries

GLOBAL_ENTRIES = None

def windows_for(natal_idx, birth_jd, age_max=80):
    """Windows A/B/C for each transit cycle of the natal sign (global table)."""
    global GLOBAL_ENTRIES
    if GLOBAL_ENTRIES is None:
        GLOBAL_ENTRIES = global_sign_entries()
    out = []
    natal_lon = saturn_lon(birth_jd)
    end_jd = birth_jd + age_max * DAYS
    for i, (e, s) in enumerate(GLOBAL_ENTRIES):
        if s != natal_idx or e < birth_jd or e > end_jd:
            continue
        nxt = GLOBAL_ENTRIES[i+1][0] if i+1 < len(GLOBAL_ENTRIES) else e + 2.55 * DAYS
        a = (e, nxt)                      # Window A
        # exact return within A: bisect on crossing natal longitude
        lo, hi = e, nxt
        ret = None
        for _ in range(24):
            mid = (lo + hi) / 2
            if saturn_lon(mid) > natal_lon:
                hi = mid
            else:
                lo = mid
        if abs((saturn_lon(lo) - natal_lon + 180) % 360 - 180) < 0.5:
            ret = lo
        b = (ret - DAYS, ret + DAYS) if ret else (None, None)
        c_before = (e - 2.55 * DAYS, e)
        c_after = (nxt, nxt + 2.55 * DAYS)
        out.append({"A": a, "B": b, "C": (c_before, c_after)})
    return out

def in_window(jd, w):
    return w[0] is not None and w[0] <= jd <= w[1]

def event_jd(y_ev):
    return jd_of(y_ev, 7, 1)   # mid-year approximation for year-only events

def binomial_p(k, n, p0, alt="greater"):
    # one-sided binomial
    import math as m
    s = 0.0
    for i in range(k, n+1):
        s += m.comb(n, i) * (p0**i) * ((1-p0)**(n-i))
    return s

# ============ load events ============
events = []   # (name, birth_ymd_tuple, event_year, source)
def parse_reg_birth(s):
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s.strip())
    if m:
        return (int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return None

# registry (clean MM/DD/YYYY) joined with q_biographical career/debut
reg = {}
with gzip.open("data/famous_people_birth_data.csv.gz", "rt", errors="ignore") as f:
    for row in csv.DictReader(f):
        nm = (row.get("name") or "").strip()
        bd = (row.get("birth_date") or "").strip()
        if nm and bd:
            reg[nm] = bd
qa = {}
with gzip.open("outputs/q_biographical_wikipedia/q_biographical_details.csv.gz", "rt", errors="ignore") as f:
    for row in csv.DictReader(f):
        nm = (row.get("name") or "").strip()
        ca = (row.get("career_active") or "").strip()
        db = (row.get("debut") or "").strip()
        if nm and (ca or db):
            qa[nm] = (ca, db)
for nm, (ca, db) in qa.items():
    if nm not in reg: continue
    b = parse_reg_birth(reg[nm])
    if not b: continue
    m = re.match(r"^(\d{4})", ca)          # "1985–present", "1939–1992"
    if not m:
        m = re.search(r"(\d{4})", ca)      # "1997 | 2013"
    if m and b:
        events.append((nm, b, int(m.group(1)), "career_active"))
    m = re.match(r"^([A-Za-z]+)?\s*(\d{4})", db)
    if m and b:
        events.append((nm, b, int(m.group(2)), "debut"))
# dedupe by (name, source)
seen = set(); evs = []
for e in events:
    k = (e[0], e[3])
    if k not in seen:
        seen.add(k); evs.append(e)

# ============ run ============
results = []
n_A = n_ev = n_B = n_C = 0
for name, b, ev_y, src in evs:
    y, mo, d = b
    if not (1850 <= y <= 2010 and y <= ev_y <= y + 80):
        continue
    ns = natal_saturn_sign(y, mo, d)
    wins = windows_for(ns, jd_of(y, mo, d))
    ej = event_jd(ev_y)
    inA = any(in_window(ej, w["A"]) for w in wins)
    inB = any(w["B"][0] and in_window(ej, w["B"]) for w in wins)
    inC = any(in_window(ej, c) for w in wins for c in w["C"])
    results.append({"name": name, "birth": f"{y}-{mo:02d}-{d:02d}", "event_year": ev_y,
                    "natal_saturn": SIGNS[ns], "in_A": inA, "in_B": inB, "in_C": inC, "src": src})
    n_ev += 1; n_A += inA; n_B += inB; n_C += inC

p0 = 2.5 / 29.46
kA = n_A; n = n_ev
print(f"H2 TEST — n={n} events (career_active + debut)")
print(f"Expected in Window A by chance: {p0*100:.1f}%  (~{p0*n:.0f} events)")
print(f"Observed in Window A: {kA} ({kA/n*100:.1f}%)   binomial p (one-sided) = {binomial_p(kA, n, p0):.4f}")
print(f"Observed in Window B (±1y of exact return): {n_B} ({n_B/n*100:.1f}%)  (chance ~{2/29.46*100:.1f}%)")
print(f"Observed in Window C (controls, 2×2.5y): {n_C} ({n_C/n*100:.1f}%)   (chance ~{2*p0*100:.1f}%)")
print(f"Rate A vs C: {kA/n*100:.1f}% vs {n_C/n*100:.1f}%  -> {'A>C' if kA > n_C else 'A<=C'}")
print(f"\nPre-registered threshold: p<0.05 and rate_A > rate_C  -> {'PASSED' if (binomial_p(kA,n,p0) < 0.05 and kA/n > n_C/n) else 'NOT MET'}")

# natal sign distribution sanity (should be ~uniform)
dist = Counter(r["natal_saturn"] for r in results)
print("\nNatal Saturn sign distribution (sanity):", dict(dist))

json.dump({"n_events": n, "p0": p0, "in_A": n_A, "in_B": n_B, "in_C": n_C,
           "binom_p_A": binomial_p(n_A, n, p0),
           "threshold_met": binomial_p(n_A, n, p0) < 0.05 and n_A/n > n_C/n,
           "natal_saturn_dist": dict(dist), "rows": results},
          open("dataset/h2_saturn_window_test.json", "w"), indent=1)
print("\nWrote dataset/h2_saturn_window_test.json")
