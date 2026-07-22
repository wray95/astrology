SEQ=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
YEARS={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
def antar(md, s, e):
    total=e-s; si=SEQ.index(md); cur=s; out=[]
    for k in range(9):
        lord=SEQ[(si+k)%9]; dur=total*YEARS[lord]/120.0
        out.append((lord,round(cur,2),round(cur+dur,2))); cur+=dur
    return out
def y2d(x):
    y=int(x); d=(x-y)*365.25; import datetime as dt
    return (dt.date(y,1,1)+dt.timedelta(days=int(d))).isoformat()
print("=== P4 (1967, Taurus Lagna) : Ketu MD 2019.7-2026.7 ===")
print("  Money lords: Venus(Lagna/1st&6th, in Lagna Malavya), Mercury(2nd&5th), Jupiter(11th)")
for l,a,b in antar("Ketu",2019.7,2026.7):
    fav=" <== MONEY" if l in("Venus","Mercury","Jupiter") else ""
    print(f"  Ketu/{l:8} {a}-{b}  ({y2d(a)} -> {y2d(b)}){fav}")
print("  NEXT MAHA: Venus MD 2026.7-2046.7 -> Venus/Venus bhukti ~2026.7-2028.7 = PEAK MONEY")
print("\n=== P2 (1997, Aries Lagna) : Rahu MD 2014.9-2032.9 ===")
print("  Money lords: Venus(2nd&7th, in 11th), Saturn(11th), Moon(4th exalted in 2nd)")
for l,a,b in antar("Rahu",2014.9,2032.9):
    fav=" <== MONEY" if l in("Venus","Saturn","Moon") else ""
    print(f"  Rahu/{l:8} {a}-{b}  ({y2d(a)} -> {y2d(b)}){fav}")
print("  TODAY ~ 2026-07-22")
