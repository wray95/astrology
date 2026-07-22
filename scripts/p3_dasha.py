SEQ=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
YEARS={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
import datetime as dt
def y2d(x):
    y=int(x); d=(x-y)*365.25
    return (dt.date(y,1,1)+dt.timedelta(days=int(d))).isoformat()
def sub(md,s,e):
    total=e-s; si=SEQ.index(md); cur=s; out=[]
    for k in range(9):
        lord=SEQ[(si+k)%9]; dur=total*YEARS[lord]/120.0
        out.append((lord,round(cur,3),round(cur+dur,3))); cur+=dur
    return out
# P3 (1995) Moon in Mula -> Ketu start. Moon MD = 2023.8 - 2033.8
print("P3 (1995, M, Pisces Lagna) — Vimshottari (method per sites)")
print("Moon MD: 2023.8 - 2033.8  (Moon = 5th lord in 10th; MD favorable)")
print("\nANTARDASHA inside Moon MD:")
for l,a,b in sub("Moon",2023.8,2033.8):
    print(f"  Moon/{l:8} {y2d(a)} -> {y2d(b)}")
# current date
print("\nTODAY 2026-07-22  -> in Moon/Rahu antar (ends ~2026-09)")
print("\nPRATYANTAR (current Moon/Rahu antar 2025.22-2026.72):")
for l,a,b in sub("Rahu",2025.22,2026.72):
    print(f"  Moon/Rahu/{l:8} {y2d(a)} -> {y2d(b)}")
print("\nNEAR-FUTURE LUCK WINDOW -> Moon/Jupiter antar (Jupiter = Lagna+10th lord in 9th fortune):")
for l,a,b in sub("Jupiter",2026.72,2028.05):
    print(f"  Moon/Jupiter/{l:8} {y2d(a)} -> {y2d(b)}")
print("\nAlso favorable later: Moon/Moon antar would be 5th-lord; Moon/Saturn (2032.9?) no.")
