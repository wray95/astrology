import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI)
SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
PLAN=[("Sun",swe.SUN),("Moon",swe.MOON),("Mars",swe.MARS),("Mercury",swe.MERCURY),("Jupiter",swe.JUPITER),("Venus",swe.VENUS),("Saturn",swe.SATURN)]
def jd(Y,M,D,H,MI,SEC): return swe.julday(Y,M,D,0)+(H-5.5+MI/60+SEC/3600)/24.0
# Lagnas TAKEN FROM YOUR SITE (not computed): P2=Aries, P3=Pisces
data={"P2":(1997,3,14,9,38,0,"Aries"),"P3":(1995,8,7,21,18,41,"Pisces")}
for name,(Y,M,D,H,MI,SEC,lagna) in data.items():
    j=jd(Y,M,D,H,MI,SEC); li=SIGNS.index(lagna)
    print(f"\n=== {name}  LAGNA (your site) = {lagna} ===  [longitudes = Lahiri/Drik Panchang]")
    for p,ipl in PLAN:
        lo=swe.calc_ut(j,ipl,swe.FLG_SIDEREAL)[0][0]
        print(f"  {p:8} {SIGNS[int(lo//30)]:11} {lo%30:6.2f}  -> House {(int(lo//30)-li)%12+1}")
    rahu=swe.calc_ut(j,swe.MEAN_NODE,swe.FLG_SIDEREAL)[0][0]; ketu=(rahu+180)%360
    for p,lo in [("Rahu",rahu),("Ketu",ketu)]:
        print(f"  {p:8} {SIGNS[int(lo//30)]:11} {lo%30:6.2f}  -> House {(int(lo//30)-li)%12+1}")
