#!/usr/bin/env python3
"""Quantify how D7/D5 convention choice changes P-series marriage/children scores."""
import json, sys
sys.path.insert(0, "scripts")
import swisseph as swe
from p_update import PD, P7, S, SL, marriage_score, children_score, compute

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

def varga_sign(lon, n, mode):
    s = int(lon // 30) % 12
    d = lon % 30
    k = int(d // (30.0 / n))
    if mode == "mult":
        return int((lon * n % 360) // 30)
    if mode == "oer":           # odd/even reverse (senath_recompute.py)
        return (s + k) % 12 if s % 2 == 0 else (s - k) % 12
    if mode == "oef":           # odd/even forward from Nth (user Turn-7 link style)
        off = {9: 8, 7: 6, 5: 4}[n]
        return (s + k) % 12 if s % 2 == 0 else (s + off + k) % 12

def rebuild_varga(ch, n, mode):
    asc_lon = S.index(ch["lagna"]) * 30 + ch["asc_deg"]
    vl = varga_sign(asc_lon, n, mode)
    v = {"asc": S[vl]}
    for pn in P7:
        lon = ch["planets"][pn]["sid"]
        vs = S[varga_sign(lon, n, mode)]
        vh = (S.index(vs) - vl) % 12 + 1
        dgn = 100 if (pn in {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"} and {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}[pn]==vs) else \
              (75 if (pn in {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]} and vs in {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}[pn]) else \
              (-100 if (pn in {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"} and {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}[pn]==vs) else 0))
        v[pn] = {"sign": vs, "house": vh, "dignity": dgn}
    return v

results = {}
for person in PD:
    ch = compute(person)
    base_mar, base_chi = marriage_score(ch), children_score(ch)
    ch_oer = dict(ch, d7=rebuild_varga(ch, 7, "oer"), d5=rebuild_varga(ch, 5, "oer"))
    ch_oef = dict(ch, d7=rebuild_varga(ch, 7, "oef"), d5=rebuild_varga(ch, 5, "oef"))
    mar_oer, chi_oer = marriage_score(ch_oer), children_score(ch_oer)
    mar_oef, chi_oef = marriage_score(ch_oef), children_score(ch_oef)
    results[person] = {"base": [base_mar, base_chi],
                       "oer": [mar_oer, chi_oer],
                       "oef": [mar_oef, chi_oef]}
    print(f"{person:>14}: marriage mult={base_mar:>3} oer={mar_oer:>3} oef={mar_oef:>3}  |  children mult={base_chi:>3} oer={chi_oer:>3} oef={chi_oef:>3}")

# ranking shifts
def rank(d):
    return sorted(d, key=lambda p: -d[p])
base_r = rank({p: r["base"][0] for p, r in results.items()})
oer_r = rank({p: r["oer"][0] for p, r in results.items()})
oef_r = rank({p: r["oef"][0] for p, r in results.items()})
print("\nMARRIAGE ranking: mult:", base_r)
print("                  oer:", oer_r)
print("                  oef:", oef_r)
print("MARRIAGE rank differs mult vs oer:", base_r != oer_r, "| mult vs oef:", base_r != oef_r)

base_c = rank({p: r["base"][1] for p, r in results.items()})
oer_c = rank({p: r["oer"][1] for p, r in results.items()})
oef_c = rank({p: r["oef"][1] for p, r in results.items()})
print("\nCHILDREN ranking: mult:", base_c)
print("                  oer:", oer_c)
print("                  oef:", oef_c)
print("CHILDREN rank differs mult vs oer:", base_c != oer_c, "| mult vs oef:", base_c != oef_c)

json.dump(results, open("dataset/divisional_score_impact.json", "w"), indent=1)
print("\nWrote dataset/divisional_score_impact.json")
