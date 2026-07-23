#!/usr/bin/env python3
"""Senath RECOMPUTE from the live Drik link (14/05/2001 16:08:40, Lahiri).
The cached senath_parsed.json was WRONG (Moon 24.3 Dhanishta vs link 20.87 Shravana).
This uses the LINK's actual data and runs the SAME battery as P1-P4:
  Lagna+houses, Navamsa/vargottama, Vimshottari MD (Moon-start), loop/bond, P1234 rules.
"""
import sys, os, json, datetime
sys.path.insert(0, "/home/user/astrology/scripts")
import math

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
RULER = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
         "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
         "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
BOND = {2:100, 3:50, 4:33, 5:25}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

# ---- LINK DATA (parsed from live fetch_page of the Drik link) ----
def D(deg, m, s): return deg + m/60.0 + s/3600.0
LINK = {
    "Lagna":  ("Virgo",     D(5,44,16)),
    "Sun":    ("Aries",     D(29,57,3)),
    "Moon":   ("Capricorn", D(20,52,23)),
    "Mars":   ("Sagittarius",D(5,6,49)),
    "Mercury":("Taurus",    D(20,21,23)),
    "Jupiter":("Taurus",    D(22,34,13)),
    "Venus":  ("Pisces",    D(17,4,8)),
    "Saturn": ("Taurus",    D(9,3,54)),
    "Rahu":   ("Gemini",    D(14,43,58)),
    "Ketu":   ("Sagittarius",D(14,43,58)),
}
# Moon nakshatra from link: Shravana (Capricorn 10deg..23d20), pada 4, lord = Moon
MOON_TOTAL = 9*30 + LINK["Moon"][1]   # Capricorn index 9 -> 270 + deg
SHRAVANA_START = 280.0                # Capricorn 10deg = 280.0
NAKSH_MOON = "Shravana"; NAKSH_LORD = "Moon"

def d9_sign(lon):
    s = int(lon//30) % 12; d = lon % 30
    n = int(d // (30.0/9.0))
    if s % 2 == 0:   # odd sign (Aries=0): forward
        return (s + n) % 12, n
    else:            # even sign: reverse
        return (s - n) % 12, n

def lon_of(sign, deg): return SIGNS.index(sign)*30 + deg

# ----- 1. Lagna + whole-sign houses (Virgo Lagna) -----
lagna_sign = LINK["Lagna"][0]; lagna_idx = SIGNS.index(lagna_sign)
houses = {}
for p,(sg,deg) in LINK.items():
    if p == "Lagna": continue
    si = SIGNS.index(sg)
    houses[p] = ((si - lagna_idx) % 12) + 1

# ----- 2. Navamsa / vargottama -----
nav = {}
for p,(sg,deg) in LINK.items():
    lon = lon_of(sg,deg); d9,n = d9_sign(lon)
    nav[p] = (sg, round(deg,2), n+1, SIGNS[d9], (sg==SIGNS[d9]))

# ----- 3. Vimshottari MAHADASHA from Moon's nakshatra (Shravana -> Moon) -----
VIM = [("Ketu",7),("Venus",20),("Sun",6),("Moon",10),("Mars",7),("Rahu",18),
       ("Jupiter",16),("Saturn",19),("Mercury",17)]
def md_sequence(birth_lord):
    i = [p for p,_ in VIM].index(birth_lord)
    return VIM[i:] + VIM[:i]
birth = datetime.datetime(2001,5,14,16,8,40)
frac = (MOON_TOTAL - SHRAVANA_START)/30.0   # portion of Moon MD elapsed at birth
seq = md_sequence(NAKSH_LORD)
mds = []
cur = birth
# first (birth) lord partial
bperiod = dict(VIM)[NAKSH_LORD]
rem = (1-frac)*bperiod
end = cur + datetime.timedelta(days=rem*365.25)
mds.append((NAKSH_LORD, cur.date().isoformat(), end.date().isoformat(), round(rem,2)))
cur = end
for lord,per in seq[1:]:
    end = cur + datetime.timedelta(days=per*365.25)
    mds.append((lord, cur.date().isoformat(), end.date().isoformat(), per))
    cur = end

# ----- 4. Loop / bond (same algorithm as astrodatabank_loop_batch) -----
def cycles(signs):
    disp = {p: RULER[signs[p]] for p in PLANETS if p in signs}
    found, visited = [], {}
    for start in PLANETS:
        if start not in disp: continue
        path, cur = [], start
        while cur in disp:
            if cur in visited:
                if cur in path:
                    cyc = path[path.index(cur):]
                    if len(cyc) >= 2: found.append(tuple(cyc))
                break
            visited[cur] = len(path); path.append(cur); cur = disp[cur]
    uniq = []
    for c in found:
        if not any(set(u)==set(c) for u in uniq): uniq.append(c)
    return uniq
def classify(cycs):
    lens = [len(c) for c in cycs]
    if not lens: return 0, [], 0
    longest = max(lens); return longest, [list(c) for c in cycs], BOND.get(longest,0)
signs_only = {p:v[0] for p,v in LINK.items() if p!="Lagna"}
cycs = cycles(signs_only)
loop_len, loops, bond = classify(cycs)

# ----- 5. P1234 rule engine (import) -----
import p1234_validate as P
chart = {
    "name":"Senath (Drik-link)",
    "signs": signs_only,
    "houses": houses,
    "lagna_index": lagna_idx,
    "lagna_sign": lagna_sign,
    "loops": loops,
    "loop_len": loop_len,
    "bond": bond,
    "achievement": "",
}
present = []
for rule in P.RULES:
    r = P.eval_rule(chart, rule)
    if r == "TRUE": present.append(rule["id"])
p4 = P.classify_p1234(chart, present)

# ===== OUTPUT =====
print("="*70)
print("SENATH RECOMPUTE (from LIVE Drik link, Lahiri)")
print("="*70)
print("\n[1] LINK PLANET DATA (sidereal)")
for p,(sg,deg) in LINK.items():
    print(f"  {p:7} {sg:11} {deg:7.3f}  nakshatra-total={lon_of(sg,deg):.2f}")
print(f"  Moon nakshatra = {NAKSH_MOON} (lord {NAKSH_LORD}); frac-through = {frac:.4f}")

print("\n[2] LAGNA + HOUSES (whole-sign, Virgo Lagna)")
print(f"  Lagna = {lagna_sign} (idx {lagna_idx})")
for p in PLANETS:
    print(f"  {p:7} {LINK[p][0]:11} -> house {houses[p]}")

print("\n[3] NAVAMSA (D9) + vargottama")
for p,(sg,deg,n,d9,vg) in nav.items():
    print(f"  {p:7} D1 {sg:11}({deg:5.2f})  nav#{n}  D9 {d9:11}  {'VARGOTTAMA' if vg else '-'}")

print("\n[4] VIMSHOTTARI MAHADASHA (Moon-start, Shravana)")
for lord,s,e,per in mds:
    flag = "  <<< RAHU MD (current focus)" if lord=="Rahu" else ""
    print(f"  {lord:8} {s} -> {e}  ({per}y){flag}")

print("\n[5] LOOP / BOND")
print(f"  loops={loops}  loop_len={loop_len}  bond={bond}")

print("\n[6] P1234 RULES PRESENT (TRUE):")
print("  ", present)
print("\n[6b] P1234 CLASSIFICATION:")
print("  status =", p4["status"], "| role =", p4.get("role"),
      "| matched =", p4.get("matched_hallmarks"))

# dump machine-readable
out = {
  "link_data": {p:{"sign":v[0],"deg":round(v[1],3)} for p,v in LINK.items()},
  "moon_nakshatra": NAKSH_MOON, "moon_nakshatra_lord": NAKSH_LORD,
  "lagna_sign": lagna_sign, "houses": houses,
  "navamsa": {p:{"d1":v[0],"d1deg":v[1],"nav#":v[2],"d9":v[3],"vargottama":v[4]} for p,v in nav.items()},
  "mahadasha": [{"lord":l,"start":s,"end":e,"years":y} for l,s,e,y in mds],
  "loop_len": loop_len, "loops": loops, "bond": bond,
  "p1234_present": present, "p1234_status": p4["status"],
  "p1234_matched": p4.get("matched_hallmarks"),
}
json.dump(out, open("/home/user/astrology/astrodb_out/senath_recomputed.json","w"), indent=2)
print("\nWrote astrodb_out/senath_recomputed.json")
