#!/usr/bin/env python3
"""
SENSITIVITY ANALYSIS — birth-time jitter (±10m / ±30m) on the 111 exact-time charts.
====================================================================================
Addresses review item #12 / risk #2 ("birth-time error dominates signal"):
how often does a plausible birth-time error FLIP a planet's sign (and hence
loops/vargas) in the real charted dataset?

Method: Swiss Ephemeris (Lahiri), same engine as p_update.py. For each chart in
astrodb_out/chart_houses.json (n=112), recompute the 7 planet sidereal signs at
jd, jd±10min, jd±30min. A "flip" = sign differs from baseline. Only planets
matter for loops (Lagna is location-dependent, excluded per standing rule).
"""
import json, sys
sys.path.insert(0, "scripts")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
PLANETS = [("Sun",0),("Moon",1),("Mars",4),("Mercury",2),("Jupiter",5),("Venus",3),("Saturn",6)]
P7 = [p for p,_ in PLANETS]
MIN10 = 10/1440.0
MIN30 = 30/1440.0

charts = json.load(open("astrodb_out/chart_houses.json"))
print(f"charts: {len(charts)}")

def signs_at(jd):
    ayan = swe.get_ayanamsa(jd)
    out = {}
    for pn, pid in PLANETS:
        lt, _ = swe.calc_ut(jd, pid)
        out[pn] = int(((lt[0]-ayan) % 360) // 30)
    return out

stats = {pn: {"10m": 0, "30m": 0} for pn in P7}
chart_flips = {10: 0, 30: 0}
per_chart = []
for c in charts:
    jd = c.get("jd_ut")
    if jd is None:
        print(f"  (skip {c['name']}: no jd_ut)")
        continue
    base = signs_at(jd)
    flips10, flips30 = {}, {}
    for jd2, tag in ((jd+MIN10,"10m"), (jd-MIN10,"10m"), (jd+MIN30,"30m"), (jd-MIN30,"30m")):
        s2 = signs_at(jd2)
        d = {pn: (base[pn], s2[pn]) for pn in P7 if s2[pn] != base[pn]}
        if tag == "10m":
            for pn in d: flips10[pn] = d[pn]
        else:
            for pn in d: flips30[pn] = d[pn]
    if flips10: chart_flips[10] += 1
    if flips30: chart_flips[30] += 1
    for pn in P7:
        if pn in flips10: stats[pn]["10m"] += 1
        if pn in flips30: stats[pn]["30m"] += 1
    per_chart.append({"name": c["name"], "flips_10m": flips10, "flips_30m": flips30})

n = len(charts)
print("\n=== CHARTS WITH ≥1 PLANET SIGN FLIP ===")
print(f"  ±10 min: {chart_flips[10]}/{n} ({chart_flips[10]*100/n:.0f}%)")
print(f"  ±30 min: {chart_flips[30]}/{n} ({chart_flips[30]*100/n:.0f}%)")
print("\n=== PER-PLANET FLIP RATES ===")
print(f"  {'planet':<10}{'±10m':>6}{'±30m':>6}")
for pn in P7:
    print(f"  {pn:<10}{stats[pn]['10m']:>6}{stats[pn]['30m']:>6}")
worst = sorted(per_chart, key=lambda c: -(len(c["flips_30m"])))
print("\n=== MOST SENSITIVE CHARTS (±30m, >1 planet) ===")
for c in worst[:8]:
    if len(c["flips_30m"]) > 1:
        fl = "; ".join(f"{p}:{a}->{b}" for p,(a,b) in c["flips_30m"].items())
        print(f"  {c['name']:<28} {fl}")

json.dump({"n": n, "chart_flips_10m": chart_flips[10], "chart_flips_30m": chart_flips[30],
           "planet_stats": stats, "per_chart": per_chart},
          open("dataset/birthtime_jitter_sensitivity.json","w"), indent=1)
print("\nWrote dataset/birthtime_jitter_sensitivity.json")
