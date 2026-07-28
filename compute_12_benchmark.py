#!/usr/bin/env python3
"""Compute 12 AA-rated benchmark charts + cross-validate against known outcomes"""
import swisseph as swe
import json, sys
from datetime import datetime, timezone, timedelta

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
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
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
    s = iso.replace('Z','+00:00')
    # Handle odd offsets
    try:
        dt = datetime.fromisoformat(s)
    except:
        base = s[:19]
        tz = s[19:] if len(s)>19 else '+00:00'
        dt = datetime.strptime(base, '%Y-%m-%dT%H:%M:%S')
        sign = 1 if tz[0]=='+' else -1
        h, m = int(tz[1:3]), int(tz[4:6])
        offset = timedelta(hours=sign*h, minutes=sign*m)
        dt = dt.replace(tzinfo=timezone(offset))
    
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)
    asc_trop, _ = swe.houses_ex(jd, lat, lon, b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0] - ayan) % 360
    asc_sign = SIGNS[int(asc_sid//30)]
    asc_idx = int(asc_sid//30)
    
    planets = {}
    for pn, pid in PLANETS_MAP.items():
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
    
    ms = planets["Moon"]["sidereal"]
    ml = mn = "?"; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + NAK_SPAN:
            elapsed = (ms - s) / NAK_SPAN
            bal = VIM_YRS[l] * (1.0 - elapsed)
            ml = l; mn = n; break
    
    return {"name": name, "ascendant": {"sign": asc_sign, "deg": round(asc_sid%30,4), "sidereal": round(asc_sid,4)},
            "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)},
            "houses": {h: SIGNS[(asc_idx+h-1)%12] for h in range(1,13)}}

# --- LOAD CHARTS ---
CHARTS = [
    {"name":"A. A. Gill","occupation":"Journalist/Author","category":"Creative/Success","iso":"1954-06-26T19:55:00+01:00","lat":55.95,"lon":-3.188},
    {"name":"A. J. Antoon","occupation":"Theatre Director","category":"Creative/Success","iso":"1944-12-07T13:55:00-04:00","lat":42.708,"lon":-71.162},
    {"name":"A. J. Cronin","occupation":"Physician/Novelist","category":"Creative/Success","iso":"1896-07-19T03:45:00+00:00","lat":55.963,"lon":-4.653},
    {"name":"A. J. Foyt","occupation":"Racing Driver","category":"Athlete","iso":"1935-01-16T01:25:00-06:00","lat":29.761,"lon":-95.37},
    {"name":"Aaron Eckhart","occupation":"Actor","category":"Actor","iso":"1968-03-12T18:50:00-08:00","lat":37.445,"lon":-122.16},
    {"name":"Aaron Spelling","occupation":"Producer","category":"Creative/Success","iso":"1923-04-22T12:30:00-06:00","lat":32.778,"lon":-96.796},
    {"name":"Abbe Pierre","occupation":"Priest/Humanitarian","category":"Religious","iso":"1932-08-05T11:00:00+00:00","lat":45.767,"lon":4.834},
    {"name":"Abel Gance","occupation":"Filmmaker","category":"Creative/Success","iso":"1889-10-25T14:00:00+00:09","lat":48.857,"lon":2.351},
    {"name":"Abigail Folger","occupation":"Heiress","category":"Wealth/Inherited","iso":"1943-08-11T17:27:00-07:00","lat":37.78,"lon":-122.42},
    {"name":"Abigail Johnson","occupation":"CEO Fidelity","category":"Billionaire","iso":"1961-12-19T14:45:00-05:00","lat":42.359,"lon":-71.059},
    {"name":"Adolf Hitler","occupation":"Dictator","category":"Power/Historical","iso":"1889-04-20T18:30:00+01:05","lat":48.259,"lon":13.035},
    {"name":"Adolf Eichmann","occupation":"Nazi Officer","category":"Military/Criminal","iso":"1906-03-19T19:30:00+01:00","lat":51.172,"lon":7.084},
]

results = []
for c in CHARTS:
    print(f"Computing {c['name']}...", end=" ")
    try:
        out = compute(c['name'], c['iso'], c['lat'], c['lon'])
        out['occupation'] = c['occupation']
        out['category'] = c['category']
        results.append(out)
        print(f"{out['ascendant']['sign']} Lagna, Moon {out['planets']['Moon']['sign']} {out['planets']['Moon']['nakshatra']}")
    except Exception as e:
        print(f"ERROR: {e}")
        results.append({"name": c['name'], "error": str(e)})

# --- ANALYSIS ---
print("\n" + "="*100)
print("12-CHART BENCHMARK: Wealth & Power Yogas vs Known Categories")
print("="*100)

def detect_key_yogas(chart):
    """Detect wealth/power yogas: Dhana, Raja, Mahapurusha, NBRY, etc."""
    p = chart['planets']
    asc = chart['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    yogas = []
    
    # Lords
    ll = SL[asc]  # Lagna lord
    h2l = SL[SIGNS[(asc_idx+1)%12]]  # 2L
    h5l = SL[SIGNS[(asc_idx+4)%12]]  # 5L
    h9l = SL[SIGNS[(asc_idx+8)%12]]  # 9L
    h10l = SL[SIGNS[(asc_idx+9)%12]]  # 10L
    h11l = SL[SIGNS[(asc_idx+10)%12]]  # 11L
    
    # --- DHANA YOGAS (Wealth) ---
    # 1. 2L + 11L conjunction or mutual aspect
    if h2l in p and h11l in p:
        h2h, h11h = p[h2l]['house'], p[h11l]['house']
        same_house = (h2h == h11h)
        # Check mutual aspect via house positions
        if same_house:
            yogas.append(f"DHANA: 2L({h2l})+11L({h11l}) conj H{h2h}")
        else:
            yogas.append(f"DHANA: 2L({h2l})H{h2h} + 11L({h11l})H{h11h}")
    
    # 2. LL + 5L/9L connection
    for xl, xname in [(h5l,'5L'),(h9l,'9L')]:
        if ll in p and xl in p:
            if p[ll]['house'] == p[xl]['house']:
                yogas.append(f"DHANA: LL({ll})+{xname}({xl}) conj H{p[ll]['house']}")
    
    # 3. 5L + 9L connection
    if h5l in p and h9l in p and p[h5l]['house'] == p[h9l]['house']:
        yogas.append(f"DHANA: 5L({h5l})+9L({h9l}) conj — Lakshmi Yoga")
    
    # --- RAJA YOGAS (Power/Status) ---
    # Kendra-Kona lord conjunction
    kendras = [1,4,7,10]
    konas = [1,5,9]
    kendra_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in kendras]
    kona_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in konas]
    
    for kh, kl in kendra_lords:
        for ch, cl in kona_lords:
            if kl == cl: continue  # same planet handling separately
            if kl in p and cl in p and p[kl]['house'] == p[cl]['house']:
                yogas.append(f"RAJA: {kl}(L{kh})+{cl}(L{ch}) conj H{p[kl]['house']}")
    
    # Kendra-Kona lord in mutual kendras
    for kh, kl in kendra_lords:
        for ch, cl in kona_lords:
            if kl == cl: continue
            if kl in p and cl in p:
                if p[kl]['house'] in kendras and p[cl]['house'] in kendras:
                    if f"RAJA: {kl}(L{kh})+{cl}(L{ch})" not in [y[:30] for y in yogas]:
                        yogas.append(f"RAJA-MUTUAL: {kl}(L{kh})H{p[kl]['house']} + {cl}(L{ch})H{p[cl]['house']}")
    
    # --- MAHAPURUSHA YOGAS ---
    mp_map = {
        'Mars': ('Ruchaka', [1,4,7,10]),
        'Mercury': ('Bhadra', [1,4,7,10]),
        'Jupiter': ('Hamsa', [1,4,7,10]),
        'Venus': ('Malavya', [1,4,7,10]),
        'Saturn': ('Sasa', [1,4,7,10]),
    }
    for pl, (yname, req_houses) in mp_map.items():
        if pl in p:
            own_or_exalted = (p[pl]['dignity'] >= 75)
            in_kendra = (p[pl]['house'] in req_houses)
            if own_or_exalted and in_kendra:
                yogas.append(f"MAHAPURUSHA: {yname} ({pl} in H{p[pl]['house']} {p[pl]['sign']})")
    
    # --- NEECH BHANGA RAJ YOGA ---
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in p and p[pl]['dignity'] == -100:
            nb_conditions = []
            # Condition: deb lord in kendra from Moon or Lagna
            deb_sign = DEBIL[pl]
            deb_lord = SL[deb_sign]
            if deb_lord in p:
                if p[deb_lord]['house'] in [1,4,7,10]:
                    nb_conditions.append(f"deblord({deb_lord}) in kendra")
                if (p[deb_lord]['sign_idx'] - p['Moon']['sign_idx']) % 12 in [0,3,6,9]:
                    nb_conditions.append(f"deblord({deb_lord}) in kendra fm Moon")
            # Condition: exalted lord aspects deb planet
            exalt_sign = EXALT[pl]
            ex_lord = SL[exalt_sign]
            if ex_lord in p:
                exh = p[ex_lord]['house']
                debh = p[pl]['house']
                if exh in [debh, (debh+6)%12+1, (debh-2)%12+1]:  # rough aspect
                    nb_conditions.append(f"exlord({ex_lord}) aspects deb {pl}")
            if nb_conditions:
                yogas.append(f"NBRY: {pl} deb in {deb_sign} H{p[pl]['house']} | {'; '.join(nb_conditions)}")
    
    # --- VIPAREETA RAJ YOGA (Dusthana lord in dusthana) ---
    for dh in [6,8,12]:
        dhl = SL[SIGNS[(asc_idx+dh-1)%12]]
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            yogas.append(f"VRY: {dhl}(L{dh}) in H{p[dhl]['house']}")
    
    # --- 11L DIGNITY ---
    if h11l in p:
        dig = p[h11l]['dignity']
        h = p[h11l]['house']
        note = ""
        if dig == 100: note = "EXALTED"
        elif dig == 75: note = "OWN"
        yogas.append(f"11L({h11l}): H{h} {note} (dig={dig})")
    
    # --- JUPITER/VENUS POSITION ---
    for benefic in ['Jupiter','Venus']:
        if benefic in p:
            h = p[benefic]['house']
            dig = p[benefic]['dignity']
            tag = ""
            if h in [1,4,7,10]: tag = "KEN"
            elif h in [5,9]: tag = "KON"
            elif h in [2,11]: tag = "WEALTH"
            yogas.append(f"{benefic}: H{h} {tag} {p[benefic]['sign']}(dig={dig})")
    
    return yogas

def wealth_score(yogas):
    """Crude count-based wealth score"""
    score = 0
    for y in yogas:
        if y.startswith('DHANA'): score += 2
        if y.startswith('MAHAPURUSHA'): score += 3
        if y.startswith('RAJA'): score += 2
        if y.startswith('NBRY'): score += 2
        if y.startswith('VRY'): score += 1
        if 'WEALTH' in y: score += 1
        if 'EXALTED' in y and '11L' in y: score += 2
        if 'OWN' in y and '11L' in y: score += 1
    return score

# Known category to expected band
CAT_BANDS = {
    'Billionaire': (4,5),
    'Wealth/Inherited': (3,5),
    'Creative/Success': (2,4),
    'Actor': (2,4),
    'Athlete': (2,3),
    'Religious': (1,3),
    'Power/Historical': (3,5),
    'Military/Criminal': (2,4),
}

print(f"\n{'Name':<22} {'Category':<20} {'Lagna':<10} {'Moon':<22} {'Yogas':>3} {'W$':>3} {'Match':>6}")
print("-"*105)

total = 0
hits = 0
for r in results:
    if 'error' in r: continue
    yogas = detect_key_yogas(r)
    ws = wealth_score(yogas)
    cat = r['category']
    band = CAT_BANDS.get(cat, (1,5))
    match = "✓" if band[0] <= ws <= band[1] else ("↑HI" if ws > band[1] else "↓LO")
    if match == "✓": hits += 1
    total += 1
    
    asc = r['ascendant']['sign']
    moon = r['planets']['Moon']
    moon_str = f"{moon['sign'][:4]} {moon['nakshatra']}"
    
    print(f"{r['name']:<22} {cat:<20} {asc:<10} {moon_str:<22} {len(yogas):>3} {ws:>3} {match:>6}")

print(f"\nAccuracy: {hits}/{total} ({100*hits/total:.0f}%) match within expected band")

# --- DETAILED YOGA LIST ---
print("\n" + "="*100)
print("PER-CHART YOGA DETAIL")
print("="*100)
for r in results:
    if 'error' in r: continue
    yogas = detect_key_yogas(r)
    print(f"\n--- {r['name']} ({r['category']}) ---")
    print(f"  Lagna: {r['ascendant']['sign']} {r['ascendant']['deg']:.2f}°")
    for y in yogas:
        print(f"  • {y}")

# Save
with open('/home/user/dataset/benchmark_12_computed.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to /home/user/dataset/benchmark_12_computed.json")
