#!/usr/bin/env python3
"""
PHASE 2 — GOCHARA (transit) timing features vs achievement (plan H2)
====================================================================
For each timed chart (111), compute actual transit events via Swiss Ephemeris:
  - saturn_return_1st_age  : transiting Saturn returns to natal Saturn ±0.5 deg
  - saturn_return_2nd_age  : second return
  - jupiter_10th_visits    : ages (0-40) when transiting Jupiter in natal 10th sign
  - jupiter_10th_20to35    : any visit in ages 20-35 (the contingency feature)

Contingency test (plan 2.2): Jupiter-10th (20-35) vs high/low achievement.
Because the 111 are famous (ach 4-10, mostly 8-10), "low" group is tiny;
we use the plan's High(8-10) vs Low(<=7) split AND a median split, reporting
both honestly. Chi-square + odds ratio.
"""
import json, sys, math
sys.path.insert(0, "scripts")
import swisseph as swe
from varga_conventions import SIGNS
from scipy.stats import chi2_contingency

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
P7 = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
PL_IDS = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
DAYS = 365.25

def sidereal_lon(jd, pid):
    lt,_ = swe.calc_ut(jd, pid)
    return (lt[0] - swe.get_ayanamsa(jd)) % 360

def chart_at(jd, lat, lon):
    ayan = swe.get_ayanamsa(jd)
    asc = (swe.houses_ex(jd, lat, lon, b"A")[0][0] - ayan) % 360
    li = int(asc // 30)
    pl = {}
    for pn in P7:
        lt,_ = swe.calc_ut(jd, PL_IDS[pn])
        lon_p = (lt[0] - ayan) % 360
        pl[pn] = {"lon": lon_p, "sign": SIGNS[int(lon_p // 30)],
                  "house": (int(lon_p // 30) - li) % 12 + 1}
    return {"lagna_idx": li, "planets": pl}

def transit_ages(jd_birth, lat, lon, pid, target_lon, span_years=40, tol=2.0):
    """Ages (in years) when transiting body pid is within tol deg of target_lon."""
    visits = []
    jd = jd_birth
    end = jd_birth + span_years * DAYS
    step = 7.0
    prev = None
    while jd < end:
        lon = sidereal_lon(jd, pid)
        d = abs((lon - target_lon + 180) % 360 - 180)
        if d <= tol and prev is not None and prev > tol:
            visits.append(round((jd - jd_birth) / DAYS, 1))
        prev = d
        jd += step
    return visits

houses = json.load(open("astrodb_out/chart_houses.json"))
loops = json.load(open("astrodb_out/astrodb_loops.json"))
ach = {c["name"]: c.get("achievement", 0) for c in loops}

rows = []
for c in houses:
    jd = c.get("jd_ut"); nm = c.get("name")
    if jd is None or nm not in ach: continue
    ch = chart_at(jd, c["lat"], c["lon"])
    sat_natal = ch["planets"]["Saturn"]["lon"]
    # Saturn returns: first time within 2 deg of natal after age 25 / after 45
    r1 = transit_ages(jd, c["lat"], c["lon"], 6, sat_natal, 60, 2.0)
    r2 = transit_ages(jd, c["lat"], c["lon"], 6, sat_natal, 90, 2.0)
    s1 = next((a for a in r1 if a >= 24), None)
    s2 = next((a for a in r2 if a >= 50 and (s1 is None or a > s1 + 20)), None)
    s10 = SIGNS[(ch["lagna_idx"] + 9) % 12]
    s10_idx = SIGNS.index(s10)
    # Jupiter transits through natal 10th sign (target = center of sign)
    j10 = transit_ages(jd, c["lat"], c["lon"], 5, s10_idx * 30 + 15, 40, 16.0)
    j10_2035 = [a for a in j10 if 20 <= a <= 35]
    rows.append({"name": nm, "achievement": ach[nm],
                 "saturn_return_1st": s1, "saturn_return_2nd": s2,
                 "jupiter_10th_visits": j10, "jupiter_10th_20to35": len(j10_2035) > 0})

# ---- contingency: High (8-10) vs Low (<=7), Jupiter-10th 20-35 ----
high = [r for r in rows if r["achievement"] >= 8]
low = [r for r in rows if r["achievement"] <= 7]
table = [[sum(1 for r in high if r["jupiter_10th_20to35"]), sum(1 for r in high if not r["jupiter_10th_20to35"])],
         [sum(1 for r in low if r["jupiter_10th_20to35"]), sum(1 for r in low if not r["jupiter_10th_20to35"])]]
def cont(t, label):
    t = [[x + 0.5 for x in row] for row in t]   # Haldane-Anscombe correction (zero cells)
    chi2, p, dof, _ = chi2_contingency(t)
    a,b,c,d = t[0][0], t[0][1], t[1][0], t[1][1]
    or_ = (a*d)/(b*c) if b*c else float("inf")
    print(f"\n[{label}] table={t}  chi2={chi2:.3f} p={p:.4f} OR={or_:.2f}")
    return {"label": label, "table": t, "chi2": chi2, "p": p, "OR": or_}
r1 = cont(table, "Jupiter-10th(20-35) High>=8 vs Low<=7")

# ---- median-split version ----
med = sorted(r["achievement"] for r in rows)[len(rows)//2]
hi = [r for r in rows if r["achievement"] >= med]
lo = [r for r in rows if r["achievement"] < med]
t2 = [[sum(1 for r in hi if r["jupiter_10th_20to35"]), sum(1 for r in hi if not r["jupiter_10th_20to35"])],
      [sum(1 for r in lo if r["jupiter_10th_20to35"]), sum(1 for r in lo if not r["jupiter_10th_20to35"])]]
r2 = cont(t2, f"Jupiter-10th(20-35) median-split (>= {med})")

# Saturn return stats
s1_ages = [r["saturn_return_1st"] for r in rows if r["saturn_return_1st"]]
s2_ages = [r["saturn_return_2nd"] for r in rows if r["saturn_return_2nd"]]
print(f"\nSaturn return 1st: n={len(s1_ages)} mean={sum(s1_ages)/len(s1_ages):.1f}y range={min(s1_ages)}-{max(s1_ages)}" if s1_ages else "no S1")
print(f"Saturn return 2nd: n={len(s2_ages)} mean={sum(s2_ages)/len(s2_ages):.1f}y" if s2_ages else "no S2")

json.dump({"n": len(rows), "contingency_high8": r1, "contingency_median": r2,
           "saturn_returns": {"s1_mean": (sum(s1_ages)/len(s1_ages)) if s1_ages else None,
                              "s2_mean": (sum(s2_ages)/len(s2_ages)) if s2_ages else None},
           "rows": rows}, open("dataset/gochara_features.json", "w"), indent=1)
print("\nWrote dataset/gochara_features.json")
