import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI)
SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAK=["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORD=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
SEQ=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
YEARS={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
def nav_sign(lon):
    si=int(lon//30); dis=lon%30; ni=int(dis//(30/9)); return (si*9+ni)%12
def nak_of(lon):
    i=int(lon//(360/27)); return NAK[i], i, lon%(360/27)
def dasha(Y,moon):
    ni=nak_of(moon)[1]; start=NAK_LORD[ni]; frac=nak_of(moon)[2]/(360/27); rem=YEARS[start]*(1-frac)
    cur=float(Y); tl=[]; si=SEQ.index(start)
    for k in range(9):
        lord=SEQ[(si+k)%9]; dur=rem if k==0 else YEARS[lord]
        s=cur; e=cur+dur; tl.append((lord,round(s,1),round(e,1))); cur=e
    cd=[t for t in tl if t[1]<=2026.0<t[2]]
    return tl, (cd[0] if cd else None)
people=[("P1",1962,5,27,3,38,0,6.85,79.87),("P2",1997,3,14,9,38,0,6.9271,79.8603),
        ("P3",1995,8,7,21,18,41,6.9271,79.8603),("P4",1967,4,25,8,17,37,6.9271,79.8603)]
print("==== ALL 4 ON SRI LANKAN (Colombo) COORDS ====")
for name,Y,M,D,H,MI,SEC,lat,lon in people:
    jd=swe.julday(Y,M,D,0)+(H-5.5+MI/60+SEC/3600)/24
    h=swe.houses(jd,lat,lon,b'W'); asc=h[1][0]%360
    moon=swe.calc_ut(jd,swe.MOON,swe.FLG_SIDEREAL)[0][0]
    nk,ni,nd=nak_of(moon); d1s=SIGNS[int(asc//30)]; d9s=SIGNS[nav_sign(asc)]
    tl,cd=dasha(Y,moon)
    print(f"\n{name} {Y}-{M:02d}-{D} {H}:{MI:02d} SLT  Lagna={d1s} {asc%30:.2f}  D9={d9s}  {'VARGOTTAMA' if d1s==d9s else ''}")
    print(f"  Moon {SIGNS[int(moon//30)]} {moon%30:.2f}  {nk}({ni}) lord={NAK_LORD[ni]}")
    print(f"  Dasha: "+" ".join(f"{l[0][:3]}{l[1]}-{l[2]}" for l in tl))
    print(f"  CURRENT(2026): {cd}")
print("\n==== P4: what Colombo birth TIME gives TAURUS VARGOTTAMA? ====")
Y,M,D=1967,4,25; lat,lon=6.9271,79.8603
for hh in range(0,24):
    for mm in [0,30]:
        jd=swe.julday(Y,M,D,0)+(hh-5.5+mm/60)/24
        h=swe.houses(jd,lat,lon,b'W'); asc=h[1][0]%360
        d1=SIGNS[int(asc//30)]; d9=SIGNS[nav_sign(asc)]
        if d1=="Taurus" and d9=="Taurus":
            print(f"  SLT {hh:02d}:{mm:02d} -> Lagna Taurus {asc%30:.2f}  VARGOTTAMA")
