#!/usr/bin/env python3
"""
LAYER 1 — Chart Strength Score (pre-specified, transparent)
===========================================================
Per the external reviewer's test: define a chart-strength score from
classical dignities/yogas ONLY (no outcomes), then test Spearman rho vs
real-world outcome ratings. Bar: rho > 0.35 (reviewer's threshold).

SCORE DEFINITION (weights fixed BEFORE looking at outcomes — pre-registered):
  strength = 0.30 * bond_norm        # jyotishvidya bond / 100 (2=100,3=50,4=33,5=25)
           + 0.20 * exalt_own        # (exalted + own-sign) count / 7
           + 0.15 * mahapurusha      # kendra-own/exalt yogas (Ruchaka/Malavya/etc) / 2
           + 0.15 * benefic_kendra   # natural benefics (Jup,Ven,Mer,exalt Moon) in kendra / 4
           + 0.10 * kendra_lord_own  # kendra lords in dignity (own/exalt) / 4
           + 0.10 * no_debil         # 1 - (debilitated count / 7)

Data: astrodb_out/astrodb_loops.json (signs/degrees/loops/bond/achievement)
      astrodb_out/chart_houses.json (whole-sign houses + lagna)
Outcome: achievement (1-10) as recorded in the dataset (proxy for
real-world prominence; the only outcome-like variable available).
"""
import json, sys, random, math
sys.path.insert(0, "scripts")

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
BENEFIC = ["Jupiter","Venus","Mercury"]
P7 = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

loops = json.load(open("astrodb_out/astrodb_loops.json"))
houses = json.load(open("astrodb_out/chart_houses.json"))
by_name = {c["name"]: c for c in houses}

def strength(rec):
    signs = rec["signs"]; degs = rec.get("degrees", {})
    h = by_name.get(rec["name"], {})
    hs = h.get("houses", {})
    lagna = h.get("lagna_sign")
    bond = rec.get("bond", 0)
    ex_own = 0; deb = 0
    for p in P7:
        s = signs.get(p)
        if not s: continue
        if s == EXALT.get(p) or s in OWN.get(p, []): ex_own += 1
        if s == DEBIL.get(p): deb += 1
    # mahapurusha: own/exalt in kendra (1,4,7,10)
    mah = 0
    for p in P7:
        s = signs.get(p); hh = hs.get(p)
        if s and hh in (1,4,7,10) and (s == EXALT.get(p) or s in OWN.get(p, [])):
            mah += 1
    # benefic kendra
    bk = sum(1 for p in BENEFIC if hs.get(p) in (1,4,7,10))
    # kendra lords in dignity
    if lagna:
        li = SIGNS.index(lagna)
        kendra_signs = [SIGNS[(li+k) % 12] for k in (0,3,6,9)]
        kendra_lords = []
        for ks in kendra_signs:
            lord = next((p for p in P7 if ks in OWN.get(p, [])), None)
            if lord: kendra_lords.append(lord)
        kl_own = sum(1 for p in kendra_lords
                     if signs.get(p) == EXALT.get(p) or signs.get(p) in OWN.get(p, []))
    else:
        kl_own = 0
    score = (0.30 * (bond/100.0) + 0.20 * (ex_own/7.0) + 0.15 * min(mah,2)/2.0
             + 0.15 * min(bk,4)/4.0 + 0.10 * kl_own/4.0 + 0.10 * (1 - deb/7.0))
    return score * 100, {"bond": bond, "ex_own": ex_own, "mah": mah, "bk": bk, "kl_own": kl_own, "deb": deb}

def spearman(xs, ys):
    def rank(v):
        r = {x: i+1 for i, x in enumerate(sorted(v))}
        # tie handling: average ranks
        from collections import defaultdict
        groups = defaultdict(list)
        for i, x in enumerate(v): groups[x].append(i)
        avg = {}
        for x, idxs in groups.items():
            a = sum(i+1 for i in idxs)/len(idxs)
            for i in idxs: avg[i] = a
        return [avg[i] for i in range(len(v))]
    rx, ry = rank(xs), rank(ys)
    n = len(xs); mx = sum(rx)/n; my = sum(ry)/n
    cov = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    vx = sum((a-mx)**2 for a in rx); vy = sum((b-my)**2 for b in ry)
    return cov/math.sqrt(vx*vy) if vx and vy else 0.0

# ---- compute on the 111 joinable charts ----
data = []
for rec in loops:
    if rec["name"] not in by_name: continue
    s, parts = strength(rec)
    data.append({"name": rec["name"], "score": s, "ach": rec.get("achievement", 0), "parts": parts})

xs = [d["score"] for d in data]; ys = [d["ach"] for d in data]
rho = spearman(xs, ys)
n = len(data)
# permutation p
rng = random.Random(42)
perm = 0
for _ in range(10000):
    ys2 = ys[:]; rng.shuffle(ys2)
    if abs(spearman(xs, ys2)) >= abs(rho): perm += 1
p = perm/10000

print(f"LAYER 1 — n={n} charted (joinable) charts")
print(f"Spearman rho (chart strength vs achievement) = {rho:.4f}  (permutation p={p})")
print(f"Reviewer bar: rho > 0.35 -> {'PASSED' if rho > 0.35 else 'NOT MET'}")
print()
print("Top 8 scores:")
for d in sorted(data, key=lambda x: -x["score"])[:8]:
    print(f"  {d['name']:<26} score={d['score']:5.1f} ach={d['ach']} {d['parts']}")
print("Bottom 5 scores:")
for d in sorted(data, key=lambda x: x["score"])[:5]:
    print(f"  {d['name']:<26} score={d['score']:5.1f} ach={d['ach']} {d['parts']}")

json.dump({"n": n, "rho": rho, "permutation_p": p, "bar": 0.35, "passed": rho > 0.35,
           "rows": data}, open("dataset/layer1_strength_test.json", "w"), indent=1)
print("\nWrote dataset/layer1_strength_test.json")
