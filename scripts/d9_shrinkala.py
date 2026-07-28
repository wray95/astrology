#!/usr/bin/env python3
"""
D9 (Navamsa) derivation + Parivartana/Shrinkala closed-loop + dignity analysis.
METHOD (link-derived, NOT self-computed ephemeris):
  D1 longitudes = Drik Panchang (user-provided links), verbatim.
  D9 sign = standard Vedic navamsa division (astrologylover.com/how-to-read-navamsa-chart):
    each 30deg sign -> 9 navamsas of 3deg20min; odd signs start from same sign,
    even signs start from the 9th sign.
  D9 Lagna from user Lagna + Drik degree (absolute longitude) where degree known;
  P4 Taurus = Vargottama (user) => D9 Lagna Taurus.
  Dignity in D9 (own/exalt/debil) per astrologylover: "planet exalted in birth but
    debilitated in D9 gives debilitation result; debilitated in D1 but exalted in D9
    gives exaltation result." Vargottama (same sign D1&D9) = very strong.
  Repetition rule (scribd D-9 doc): a Parivartana present in BOTH D1 and D9 is strengthened.
Only the 7 grahas are sign-lords (Rahu/Ketu excluded as lords, per Parashari).
"""
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
LORD = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",
        6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
OWN = {"Sun":[4],"Moon":[3],"Mars":[0,7],"Mercury":[2,5],"Jupiter":[8,11],
       "Venus":[1,6],"Saturn":[9,10]}
EXALT = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
DEBIL = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

def navamsa(lon):
    s = int(lon // 30); p = lon - s*30; n = int(p // (30.0/9.0))
    return (s+n)%12 if s%2==0 else (s+8+n)%12

def dms(deg):
    d=int(deg); m=int(round((deg-d)*60))
    if m==60: d+=1; m=0
    return f"{d}\u00b0{m:02d}\u2032"

# D1 absolute longitudes (Drik Panchang, link-derived)
P1 = {"Mars":5+6/60,"Sun":30+11+49/60,"Mercury":30+27+2/60,"Venus":60+11+25/60,
      "Rahu":90+18+57/60,"Saturn":270+18+2/60,"Moon":300+13+29/60,"Jupiter":300+17+18/60,"Ketu":270+18+57/60}
P2 = {"Venus":300+24.9,"Jupiter":270+17.8,"Moon":30+8.5,"Saturn":330+14.3,"Sun":300+29.8,
      "Mars":150+4.1,"Mercury":330+2.4,"Rahu":150+5.4,"Ketu":330+5.4}
P3 = {"Jupiter":210+11.8,"Saturn":330+0,"Rahu":180+6.4,"Ketu":6.4,"Sun":90+20.9,"Moon":240+8,
      "Mars":150+16.6,"Mercury":120+1.9,"Venus":90+17.2}
P4 = {"Venus":30+19,"Jupiter":90+2,"Saturn":330+13,"Mars":150+27,"Mercury":330+24,"Sun":11,
      "Moon":180+19+28/60,"Rahu":13+52/60,"Ketu":180+13+52/60}

# Lagna as ABSOLUTE longitude (deg within sign -> +30*sign_index)
LAGNA_ABS = {"P1":9+26/60, "P2":None, "P3":330+6.0, "P4":1}  # P4 vargottama => D9 lagna Taurus(1)
D9_LAGNA = {}
for k,ab in LAGNA_ABS.items():
    D9_LAGNA[k] = 1 if k=="P4" else (navamsa(ab) if ab is not None else None)

DATA = {"P1":P1,"P2":P2,"P3":P3,"P4":P4}
NAMES = {"P1":"Polgahawela Bappa (1962, M, Aries)",
         "P2":"Upulakshi (1997, F, Aries)","P3":"Senith (1995, M, Pisces)",
         "P4":"Niromi (1967, F, Taurus*)"}

def d1_signs(c): return {p:int(v//30) for p,v in c.items()}
def d9_signs(c): return {p:navamsa(v) for p,v in c.items()}

def find_cycles(d9s):
    f={p:LORD[d9s[p]] for p in PLANETS}
    visited=set(); cycles=[]
    for start in PLANETS:
        if start in visited: continue
        path=[]; cur=start
        while cur not in visited:
            visited.add(cur); path.append(cur); cur=f[cur]
        if cur in path:
            cyc=path[path.index(cur):]
            if 2<=len(cyc)<=5: cycles.append(tuple(cyc))
    uniq=[]; seen=set()
    for c in cycles:
        best=c
        for i in range(len(c)):
            rot=tuple(c[(i+j)%len(c)] for j in range(len(c)))
            if rot<best: best=rot
        if best not in seen: seen.add(best); uniq.append(best)
    out={}
    for c in uniq: out.setdefault(len(c),[]).append(c)
    return out,f

def dignity(p,sign):
    if sign in OWN[p]: return "OWN"
    if sign==EXALT[p]: return "EXALT"
    if sign==DEBIL[p]: return "DEBIL"
    return "neut"

# ---- SANITY: reproduce prior D1 loops ----
print("SANITY D1 loops (must match prior Section 13):")
for k in DATA:
    cyc,_=find_cycles(d1_signs(DATA[k]))
    print(" ",k,{L:['->'.join(c) for c in cyc.get(L,[])] for L in cyc})

# ---- D9 full analysis ----
print("\n"+"="*78+f"\nD9 (NAVAMSA) — derived from Drik longitudes via standard navamsa division\n"+"="*78)
out={}
for k in DATA:
    d1s=d1_signs(DATA[k]); d9s=d9_signs(DATA[k])
    cyc,f=find_cycles(d9s)
    varg=[p for p in PLANETS if d1s[p]==d9s[p]]
    print(f"\n### {k} — {NAMES[k]}")
    print(f"D9 Lagna: {SIGNS[D9_LAGNA[k]] if D9_LAGNA[k] is not None else 'UNKNOWN (no Lagna degree)'}")
    print(f"{'Planet':<8}{'D1 sign':<14}{'D9 sign':<14}{'Dignity':<8}{'Varg'}")
    for p in PLANETS:
        dg=dignity(p,d9s[p])
        v="VARG" if p in varg else ""
        print(f"{p:<8}{SIGNS[d1s[p]]:<14}{SIGNS[d9s[p]]:<14}{dg:<8}{v}")
    print("  Vargottama (7 grahas):", varg or "none")
    print("  D9 closed-loops:")
    if cyc:
        for L in sorted(cyc):
            for c in cyc[L]:
                if D9_LAGNA[k] is not None:
                    hs="/".join(str((d9s[p]-D9_LAGNA[k])%12+1) for p in c)
                    ht=f" D9 houses {hs}"
                else: ht=" (D9 houses pending Lagna deg)"
                print(f"    {L}-loop: {' -> '.join(c)} -> {c[0]}  | signs {[SIGNS[d9s[p]] for p in c]}{ht}")
    else: print("    NONE")
    out[k]={"d1s":d1s,"d9s":d9s,"cyc":cyc,"varg":varg,"dl":D9_LAGNA[k]}

# ---- D1 vs D9 repetition ----
print("\n"+"="*78+"\nD1 vs D9 — REPEATED (strengthened) / NEW / broken loops\n"+"="*78)
for k in DATA:
    c1,_=find_cycles(d1_signs(DATA[k])); c9=out[k]["cyc"]
    print(f"\n{k} {NAMES[k]}")
    rep=[]
    for L1 in c1:
        for z1 in c1[L1]:
            for L9 in c9:
                for z9 in c9[L9]:
                    if set(z1)==set(z9): rep.append((z1,L1,L9))
    if rep:
        for z1,L1,L9 in rep:
            print(f"  >>> REPEATED/STRENGTHENED: {L1}-loop {z1} in BOTH D1 & D9")
    else:
        print("  >>> No identical planet-loop repeats D1<->D9")
    # list new D9-only loops and broken D1-only loops
    d9only=[]; d1only=[]
    for L9 in c9:
        for z9 in c9[L9]:
            if not any(set(z9)==set(z1) for L1 in c1 for z1 in c1[L1]): d9only.append((L9,z9))
    for L1 in c1:
        for z1 in c1[L1]:
            if not any(set(z1)==set(z9) for L9 in c9 for z9 in c9[L9]): d1only.append((L1,z1))
    for L9,z9 in d9only: print(f"  + NEW in D9 only: {L9}-loop {z9}")
    for L1,z1 in d1only: print(f"  - D1-only (NOT in D9): {L1}-loop {z1}")

print("\nDONE")
