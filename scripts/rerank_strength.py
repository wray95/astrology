#!/usr/bin/env python3
"""
Re-rank the four horoscopes by the user's strength rubric:
  - a planet in its OWN SIGN  -> top tier (strong)
  - a planet in a 2/3/4/5-LOOP yoga (Parivartana/Shrinkala) -> top tier ("exalted")
INPUT = Drik Panchang longitudes (link) + user Lagnas. D9 via standard navamsa
division (astrologylover.com/Scribd method, Turns 6-7). No Swiss-Ephemeris.
"""
SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
OWN={"Sun":[4],"Moon":[3],"Mars":[0,7],"Mercury":[2,5],"Jupiter":[8,11],"Venus":[1,6],"Saturn":[9,10]}
LORD={0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
PLANETS=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

def navamsa(lon):
    s=int(lon//30); p=lon-s*30; n=int(p//(30.0/9.0))
    return (s+n)%12 if s%2==0 else (s+8+n)%12

# Drik longitudes (absolute degrees) -- re-read from report data
P1={"Mars":5+6/60,"Sun":30+11+49/60,"Mercury":30+27+2/60,"Venus":60+11+25/60,"Rahu":90+18+57/60,
    "Saturn":270+18+2/60,"Moon":300+13+29/60,"Jupiter":300+17+18/60,"Ketu":270+18+57/60}
P2={"Venus":300+24.9,"Jupiter":270+17.8,"Moon":30+8.5,"Saturn":330+14.3,"Sun":300+29.8,
    "Mars":150+4.1,"Mercury":330+2.4,"Rahu":150+5.4,"Ketu":330+5.4}
P3={"Jupiter":210+11.8,"Saturn":330+0,"Rahu":180+6.4,"Ketu":6.4,"Sun":90+20.9,"Moon":240+8,
    "Mars":150+16.6,"Mercury":120+1.9,"Venus":90+17.2}
P4={"Venus":30+19,"Jupiter":90+2,"Saturn":330+13,"Mars":150+27,"Mercury":330+24,"Sun":11,
    "Moon":180+19+28/60,"Rahu":13+52/60,"Ketu":180+13+52/60}
DATA={"P1":P1,"P2":P2,"P3":P3,"P4":P4}
NAMES={"P1":"Polgahawela Bappa (1962 M, Aries)","P2":"Upulakshi (1997 F, Aries)",
       "P3":"Senith (1995 M, Pisces)","P4":"Niromi (1967 F, Taurus*)"}

def signs(c): return {p:int(v//30) for p,v in c.items()}
def d9signs(c): return {p:navamsa(v) for p,v in c.items()}

def find_cycles(d):
    f={p:LORD[d[p]] for p in PLANETS}
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
    members=set()
    for c in uniq: members|=set(c)
    return uniq, members

def own_set(d): return {p for p in PLANETS if d[p] in OWN[p]}

print("="*78)
print("STRENGTH RE-RANK  (own-sign = strong; 2/3/4/5-loop = 'exalted')  [link-only]")
print("="*78)
rows=[]
for k in DATA:
    d1=signs(DATA[k]); d9=d9signs(DATA[k])
    c1,m1=find_cycles(d1); c9,m9=find_cycles(d9)
    own1=own_set(d1); own9=own_set(d9)
    own_u=own1|own9
    loop_u=m1|m9
    toptier=own_u|loop_u
    rows.append((k,own1,own9,own_u,c1,m1,c9,m9,loop_u,toptier))
    print(f"\n### {k} — {NAMES[k]}")
    print(f"  Own-sign D1 : {sorted(own1) or 'none'}")
    print(f"  Own-sign D9 : {sorted(own9) or 'none'}")
    print(f"  D1 loops    : { [list(c) for c in c1] or 'none' }  -> members {sorted(m1) or 'none'}")
    print(f"  D9 loops    : { [list(c) for c in c9] or 'none' }  -> members {sorted(m9) or 'none'}")
    print(f"  >>> OWN(D1∪D9)={sorted(own_u)}  LOOP(D1∪D9)={sorted(loop_u)}  TOP-TIER={sorted(toptier)}  COUNT={len(toptier)}")

print("\n"+"="*78)
print("RANKING")
print("="*78)
# D1-only top-tier
def score(d1,d9,c1,c9,own1,own9,m1,m9):
    return len((own1|own9)|(m1|m9))
print("\n(A) D1-ONLY  (own-sign D1 ∪ loop D1):")
d1scores=[]
for k,own1,own9,own_u,c1,m1,c9,m9,loop_u,toptier in rows:
    s=len(own1|m1); d1scores.append((k,s,own1,m1))
for k,s,o,lo in sorted(d1scores,key=lambda x:-x[1]):
    print(f"   {k}: {s}  (own D1={sorted(o)} loop D1={sorted(lo)})")
order_d1=[k for k,s,o,lo in sorted(d1scores,key=lambda x:-x[1])]

print("\n(B) D1+D9 COMBINED  (own-sign D1∪D9 ∪ loop D1∪D9):")
combos=[]
for k,own1,own9,own_u,c1,m1,c9,m9,loop_u,toptier in rows:
    s=len(toptier)
    combos.append((k,s,len(own_u),len(loop_u),sorted(own_u),sorted(loop_u)))
for k,s,no,nl,ou,lu in sorted(combos,key=lambda x:-x[1]):
    print(f"   {k}: {s}  (own={no} {ou} | loop={nl} {lu})")
order_combo=[k for k,s,no,nl,ou,lu in sorted(combos,key=lambda x:-x[1])]

print("\n>>> D1-only rank   :", " > ".join(order_d1))
print(">>> D1+D9 rank     :", " > ".join(order_combo))
print("(Tie at 4 in D1+D9: P1=3own+2loop, P2=0own+4loop, P4=4own+0loop -> see composition notes)")
