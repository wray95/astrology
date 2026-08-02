#!/usr/bin/env python3
"""
PHASE 1 — D10 (Dasamsa) strength vs achievement (gochara plan H1)
=================================================================
Pre-specified D10 strength score (weights fixed BEFORE looking at outcomes):
  +30  D10 10th-lord dignified (exalt/own)
  +20  D10 10th-lord in kendra (1,4,7,10)
  +15  D10 10th-lord in 10th house
  +15  Sun in D10 dignified
  +10  Sun in D10 kendra
  +10  D10 lagna-lord dignified in D10
  -10  Saturn in D10 10th house
  -10  10th-lord debilitated in D10
clamp 0-100.

10th lord = lord of the 10th sign from D1 lagna (career significator),
evaluated in the D10 (multiplication convention = locked repo convention).

Data: 111 exact-time charts (astrodb_out/chart_houses.json: jd_ut, lat, lon)
      + astrodb_out/astrodb_loops.json (achievement, rodden).
Test: Spearman rho(D10_score, achievement). Bar per plan: rho > 0.35.
"""
import json, math, random, sys
sys.path.insert(0, "scripts")
import swisseph as swe
from varga_conventions import SIGNS

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
P7 = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
PL_IDS = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
KENDRA = (1,4,7,10)

def chart_at(jd, lat, lon):
    ayan = swe.get_ayanamsa(jd)
    asc_trop = swe.houses_ex(jd, lat, lon, b"A")[0][0]
    asc = (asc_trop - ayan) % 360
    li = int(asc // 30)
    pl = {}
    for pn in P7:
        lt,_ = swe.calc_ut(jd, PL_IDS[pn])
        lon_p = (lt[0] - ayan) % 360
        pl[pn] = {"lon": lon_p, "sign": SIGNS[int(lon_p // 30)],
                  "house": (int(lon_p // 30) - li) % 12 + 1}
    return {"lagna_idx": li, "asc_lon": asc, "planets": pl}

def varga(ch, n):
    from varga_conventions import varga_index
    ai = varga_index(ch["asc_lon"], n)
    v = {"asc_idx": ai}
    for pn in P7:
        idx = varga_index(ch["planets"][pn]["lon"], n)
        v[pn] = {"sign": SIGNS[idx], "idx": idx,
                 "house": (idx - ai) % 12 + 1}
    return v

def dign(pn, sign):
    if sign == EXALT.get(pn): return 100
    if sign in OWN.get(pn, []): return 75
    if sign == DEBIL.get(pn): return -100
    return 0

def d10_strength(ch):
    li = ch["lagna_idx"]
    d10 = varga(ch, 10)
    # D1 10th sign lord (career significator) evaluated in D10
    s10_sign = SIGNS[(li + 9) % 12]
    s10l = next(p for p in P7 if s10_sign in OWN.get(p, []))
    d10_asc_sign = SIGNS[d10["asc_idx"]]
    asc_lord = next(p for p in P7 if d10_asc_sign in OWN.get(p, []))
    sc = 0
    if dign(s10l, d10[s10l]["sign"]) >= 75: sc += 30
    if d10[s10l]["house"] in KENDRA: sc += 20
    if d10[s10l]["house"] == 10: sc += 15
    if dign("Sun", d10["Sun"]["sign"]) >= 75: sc += 15
    if d10["Sun"]["house"] in KENDRA: sc += 10
    if dign(asc_lord, d10[asc_lord]["sign"]) >= 75: sc += 10
    if d10["Saturn"]["house"] == 10: sc -= 10
    if dign(s10l, d10[s10l]["sign"]) <= -100: sc -= 10
    return max(0, min(100, sc))

def spearman(xs, ys):
    from collections import defaultdict
    def ranks(v):
        grp = defaultdict(list)
        for i, x in enumerate(v): grp[x].append(i)
        avg = {}
        for x, idxs in grp.items():
            a = sum(i+1 for i in idxs)/len(idxs)
            for i in idxs: avg[i] = a
        return [avg[i] for i in range(len(v))]
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs); mx, my = sum(rx)/n, sum(ry)/n
    cov = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    vx = sum((a-mx)**2 for a in rx); vy = sum((b-my)**2 for b in ry)
    return cov/math.sqrt(vx*vy) if vx and vy else 0.0

# ---- load data ----
houses = json.load(open("astrodb_out/chart_houses.json"))
loops = json.load(open("astrodb_out/astrodb_loops.json"))
ach = {c["name"]: c.get("achievement", 0) for c in loops}
rod = {c["name"]: c.get("rodden", "") for c in loops}

rows = []
for c in houses:
    jd = c.get("jd_ut"); nm = c.get("name")
    if jd is None or nm not in ach: continue
    ch = chart_at(jd, c["lat"], c["lon"])
    sc = d10_strength(ch)
    rows.append({"name": nm, "d10_strength": sc, "achievement": ach[nm],
                 "rodden": rod.get(nm, ""), "career": loops[[i for i,x in enumerate(loops) if x["name"]==nm][0]].get("profession","") if any(x["name"]==nm for x in loops) else ""})

xs = [r["d10_strength"] for r in rows]
ys = [r["achievement"] for r in rows]
rho = spearman(xs, ys)
rng = random.Random(42)
perm = sum(1 for _ in range(10000) if abs(spearman(xs, rng.sample(ys, len(ys)))) >= abs(rho))
p = perm/10000

print(f"D10 TEST — n={len(rows)} timed charts (rodden: { {k: sum(1 for r in rows if r['rodden']==k) for k in set(r['rodden'] for r in rows)} })")
print(f"Spearman rho(D10 strength, achievement) = {rho:.4f}  (permutation p={p:.4f})")
print(f"Plan bar rho > 0.35 -> {'PASSED' if rho > 0.35 else 'NOT MET'}")
print(f"Achievement range: {min(ys)}-{max(ys)} (range-restricted?) -> {'YES, all famous' if max(ys)-min(ys) <= 3 else 'no'}")
print("\nTop 5 D10 scores:")
for r in sorted(rows, key=lambda x: -x["d10_strength"])[:5]:
    print(f"  {r['name']:<26} D10={r['d10_strength']:>3} ach={r['achievement']} rodden={r['rodden']}")
print("Bottom 5 D10 scores:")
for r in sorted(rows, key=lambda x: x["d10_strength"])[:5]:
    print(f"  {r['name']:<26} D10={r['d10_strength']:>3} ach={r['achievement']} rodden={r['rodden']}")

json.dump({"n": len(rows), "rho": rho, "permutation_p": p, "bar": 0.35, "passed": rho > 0.35,
           "rows": rows}, open("dataset/d10_strength.json", "w"), indent=1)
print("\nWrote dataset/d10_strength.json")
