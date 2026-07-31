#!/usr/bin/env python3
"""P1-P9 Swiss Ephemeris pipeline — compute + cross-validate + rank"""
import swisseph as swe
import json
from datetime import datetime, timedelta, timezone

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAK_SPAN = 360.0/27
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),
        ("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),
        ("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),
        ("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),
        ("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),
        ("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),
        ("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
PLANETS = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+NAK_SPAN: return n,l,(lon-s)/NAK_SPAN
    return "Revati","Mercury",0

def dg(p,s):
    if p in DEBIL and DEBIL[p]==s: return -100
    if p in EXALT and EXALT[p]==s: return 100
    if p in OWN and s in OWN[p]: return 75
    return 0

def compute(name, iso, lat, lon):
    s = iso.replace('++','+').replace('--','-')
    if s.endswith('Z'): s = s[:-1]+'+00:00'
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is not None: dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)
    asc_trop, _ = swe.houses_ex(jd, lat, lon, b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0] - ayan) % 360
    asc_sign = SIGNS[int(asc_sid//30)]
    asc_idx = int(asc_sid//30)

    planets = {}
    for pn, pid in PLANETS.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        planets[pn] = {"sidereal": round(sid,4), "sign": sgn, "sign_idx": si,
                       "deg_in_sign": round(sid%30,4), "dignity": dg(pn,sgn),
                       "nakshatra": nk, "nakshatra_lord": nl}

    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0] - ayan) % 360; kh = (rh + 180) % 360
    for pn, rl in [("Rahu", rh), ("Ketu", kh)]:
        sgn = SIGNS[int(rl//30)]; si = int(rl//30)
        nk, nl, _ = gn(rl)
        planets[pn] = {"sidereal": round(rl,4), "sign": sgn, "sign_idx": si,
                       "deg_in_sign": round(rl%30,4), "dignity": 0,
                       "nakshatra": nk, "nakshatra_lord": nl}

    for pn in planets:
        planets[pn]["house"] = (planets[pn]["sign_idx"] - asc_idx) % 12 + 1

    # Moon nakshatra balance
    ms = planets["Moon"]["sidereal"]
    ml = mn = "?"; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + NAK_SPAN:
            elapsed = (ms - s) / NAK_SPAN
            bal = VIM_YRS[l] * (1.0 - elapsed)
            ml = l; mn = n
            break

    # Mahadasha
    si = VIM_ORDER.index(ml)
    dashas = []
    for i in range(9):
        lord = VIM_ORDER[(si+i)%9]
        yrs = bal if i == 0 else VIM_YRS[lord]
        dashas.append({"lord": lord, "years": round(yrs,4)})

    # Current MD + AD (MD-lord-first for AD)
    now = datetime(2026, 7, 28)
    mdt = dt; cmd = cad = None; mst = None; myv = 0
    for d in dashas:
        mde = mdt + timedelta(days=d["years"]*365.2425)
        if mdt <= now < mde:
            cmd = d["lord"]; myv = d["years"]; mst = mdt
        mdt = mde

    if cmd and mst:
        asi = VIM_ORDER.index(cmd)
        adt = mst
        for i in range(9):
            al = VIM_ORDER[(asi+i)%9]
            ay = (myv * VIM_YRS[al]) / 120.0
            ae = adt + timedelta(days=ay*365.2425)
            if adt <= now < ae: cad = al
            adt = ae

    # D1/D9
    d1a = sum(planets[p]["dignity"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]) / 7
    d9 = {}
    for pn in planets:
        sid = planets[pn]["sidereal"]
        d9l = (sid * 9) % 360
        d9s = SIGNS[int(d9l//30)]
        d9[pn] = {"sign": d9s, "dignity": dg(pn, d9s) if pn not in ("Rahu","Ketu") else 0}
    d9a = sum(d9[p]["dignity"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]) / 7

    return {"name": name, "asc": asc_sign, "planets": planets,
            "dasha": {"moon_nak": mn, "moon_lord": ml, "balance": round(bal,4), "sequence": dashas},
            "d9": d9, "d1_avg": round(d1a,1), "d9_avg": round(d9a,1),
            "current_md": cmd, "current_ad": cad}

# ====== MAIN ======
births = {
    "P1": ("Polgahawela Bappa","1962-05-27T03:38:54+05:30",7.3381,80.3003),
    "P2": ("Upulakshi","1997-03-14T12:00:00+06:00",6.9355,79.8487),
    "P3": ("Senith","1995-08-07T21:18:00+05:30",6.9355,79.8487),
    "P4": ("Niromi","1967-04-25T08:17:37+05:30",6.9355,79.8487),
    "P5": ("Senath","2001-05-14T16:08:40+06:00",6.9355,79.8487),
    "P6": ("Dewli","2005-10-08T08:22:00+06:00",6.9097,79.8900),
    "P7": ("Sineth","2005-04-05T16:05:48+06:00",6.9271,79.8612),
    "P8": ("Lakshi Amma","1963-11-16T09:04:15+05:30",7.486,80.362),
    "P9": ("Lalith Uncle","1970-08-31T21:55:30+05:30",7.2931,80.635),
}

# STEP 1: Compute
print("SWISS EPHEMERIS — P1-P9 Charts (Lahiri + Whole Sign + MD-lord-first AD)")
print("-" * 80)
all_charts = {}
for pid, (name, iso, lat, lon) in births.items():
    c = compute(name, iso, lat, lon)
    all_charts[pid] = c
    print(f"{pid} {name:22s} Asc={c['asc']:10s} Moon={c['dasha']['moon_nak']:18s} "
          f"Lord={c['dasha']['moon_lord']:8s} Bal={c['dasha']['balance']:.1f}y "
          f"MD={c['current_md'] or '?':8s} AD={c['current_ad'] or '?':8s}")

# STEP 2: Cross-validate
print("\n" + "-" * 80)
print("CROSS-VALIDATION vs Drik Panchang")
print("-" * 80)
drik = {
    "P3": {"moon_nak":"Mula","moon_lord":"Ketu","asc":"Pisces"},
    "P5": {"moon_nak":"Shravana","moon_lord":"Moon","asc":"Virgo"},
    "P6": {"moon_nak":"Jyeshtha","moon_lord":"Mercury","asc":"Libra"},
    "P8": {"moon_nak":"Vishakha","moon_lord":"Jupiter"},
    "P9": {"moon_nak":"Magha","moon_lord":"Ketu","asc":"Aries"},
}
tp = tf = 0
for pid, ref in drik.items():
    c = all_charts[pid]
    for k, v in ref.items():
        got = c["asc"] if k == "asc" else c["dasha"][k]
        ok = (got == v)
        if ok: tp += 1
        else: tf += 1
        print(f"  {pid} {k:12s}: swiss={got:15s} drik={v:15s} {'OK' if ok else 'MISMATCH'}")
print(f"  PASS: {tp}/{tp+tf} ({100*tp/(tp+tf):.0f}%)")

# STEP 3: NEXUS + Rank
print("\n" + "=" * 120)
print("P1-P9 FINAL RANKING TABLE — Swiss Ephemeris")
print("=" * 120)
print(f"{'Rk':3s}| {'ID':4s}| {'Name':22s}| {'NEX':>4s}| {'D1':>3s}| {'D9':>3s}| {'$':>5s}| {'Car':>5s}| {'Asc':10s}| {'MD':8s}| {'AD':8s}| {'Archetype':25s}| {'Key Yogas'}")
print("-" * 120)

for pid, c in all_charts.items():
    p = c["planets"]; h = lambda x: p[x]["house"]; d = lambda x: p[x]["dignity"]
    sc = 0; yoga_names = []

    # Mahapurusha
    mp_map = {"Mars":"Ruchaka","Mercury":"Bhadra","Jupiter":"Hamsa","Venus":"Malavaya","Saturn":"Sasa"}
    for pl, yname in mp_map.items():
        if d(pl) >= 75 and h(pl) in {1,4,7,10}:
            sc += 25
            yoga_names.append("MP:" + yname)

    # NBRY
    for pl in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if d(pl) == -100:
            lord = SL[p[pl]["sign"]]
            conds = []
            if lord in p and h(lord) in {1,4,7,10}: conds.append("C1"); sc += 20
            if h(pl) in {1,4,7,10}: conds.append("C5"); sc += 15
            if conds: yoga_names.append("NBRY:" + pl)

    # Dhana
    ai = SIGNS.index(c["asc"])
    lords = {hl: SL[SIGNS[(ai+hl-1)%12]] for hl in range(1,13)}
    dh = 0
    for h1, h2 in [(1,2),(1,11),(2,11),(5,9)]:
        l1, l2 = lords[h1], lords[h2]
        if l1 in p and l2 in p and abs(h(l1)-h(l2)) in {0,1,7}: dh += 1; sc += 10
    if dh: yoga_names.append("Dhana("+str(dh)+")")

    # DKA
    if lords[9] in p and lords[10] in p and abs(h(lords[9])-h(lords[10])) in {0,1,7}:
        sc += 25; yoga_names.append("DKA")

    nexus = max(0, round(c["d1_avg"]*0.5 + c["d9_avg"]*0.3 + sc*0.2 + 25, 1))
    c["nexus"] = nexus; c["yogas"] = yoga_names

sorted_c = sorted(all_charts.items(), key=lambda x: x[1]["nexus"], reverse=True)

arc = {"P1":"Warlord","P2":"Enigma*","P3":"Sage","P4":"Empress","P5":"Titan","P6":"Fighter","P7":"Phoenix*","P8":"Oracle","P9":"Sovereign"}
w = {"P1":"4.0","P2":"3.0*","P3":"2.0","P4":"5.0","P5":"5.0","P6":"3.5","P7":"4.0*","P8":"4.5","P9":"3.5"}
cr = {"P1":"5.0","P2":"3.0*","P3":"2.0","P4":"5.0","P5":"4.0","P6":"4.0","P7":"4.0*","P8":"4.5","P9":"4.0"}
best = {
    "P4":"Malavaya(Venus OWN H7 KENDRA) S=25",
    "P8":"Sun NBRY(3-cond S=180) + Sasa",
    "P5":"Malavaya(Venus EXALT H10) + DKA",
    "P9":"Saturn NBRY(2-cond) + Malavaya",
    "P1":"DKA + Mahalaxmi(2/2) + Dhana(2)",
    "P7":"Merc NBRY(2-cond) + Venus EXALTED",
    "P2":"Jupiter NBRY(2-cond) *TOB*",
    "P3":"Jupiter H8 research. Venus COMBUST",
    "P6":"Mars OWN H2 + Venus MD at 24",
}

for rank, (pid, c) in enumerate(sorted_c, 1):
    yogas = ", ".join(c.get("yogas", [])[:3])
    print(f"{rank:<3d}| {pid:4s}| {c['name']:22s}| {c['nexus']:>4.0f}| {c['d1_avg']:>3.0f}| {c['d9_avg']:>3.0f}| "
          f"{w[pid]:>5s}| {cr[pid]:>5s}| {c['asc']:10s}| {(c['current_md'] or '?'):8s}| "
          f"{(c['current_ad'] or '?'):8s}| {arc[pid]:25s}| {yogas}")

# D9 Jupiter
print("\n" + "=" * 80)
print("D9 JUPITER (inner wisdom confirmation)")
print("=" * 80)
for pid, c in sorted_c:
    jd9 = c["d9"].get("Jupiter", {}).get("dignity", 0)
    tag = "EXALTED" if jd9==100 else ("DEBIL" if jd9==-100 else ("OWN" if jd9==75 else ""))
    print(f"  {pid} {c['name']:22s} Jupiter D9: {jd9:+d} {tag}")

# Save
with open("dataset/p1p9_swiss_ranked.json", "w") as f:
    json.dump(dict(sorted_c), f, indent=2)
print("\nSaved dataset/p1p9_swiss_ranked.json")
print("Engine: pyswisseph + Lahiri + Whole Sign + MD-lord-first AD ✓")
