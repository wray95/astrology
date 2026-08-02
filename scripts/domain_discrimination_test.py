#!/usr/bin/env python3
"""
10-CHART DOMAIN DISCRIMINATION TEST
Venture Capitalists vs Academics vs Corporate Fraudsters
Tests whether NEXUS can separate domain of expression
"""
import swisseph as swe
import json, math
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

def parse_coords(s):
    """Parse '50.1109° N, 8.6821° E' or '1.2921° S, 36.8219° E'"""
    parts = s.split(',')
    lat_str = parts[0].strip()
    lon_str = parts[1].strip()
    
    lat_val = float(lat_str.replace('°','').replace('N','').replace('S','').strip())
    if 'S' in lat_str: lat_val = -lat_val
    
    lon_val = float(lon_str.replace('°','').replace('E','').replace('W','').strip())
    if 'W' in lon_str: lon_val = -lon_val
    
    return lat_val, lon_val

# Timezone mapping (UTC offset in hours for each birth date/location)
TZ_MAP = {
    "Peter Thiel": 1,          # Frankfurt, Oct 1967: CET (UTC+1)
    "Marc Andreessen": -5,     # Cedar Falls IA, Jul 1971: CDT (UTC-5)
    "Vinod Khosla": 5.5,       # Delhi, Jan 1955: IST (UTC+5:30)
    "Paul Graham": 0,          # Weymouth UK, Nov 1964: GMT (UTC+0)
    "Noam Chomsky": -5,        # Philadelphia, Dec 1928: EST (UTC-5)
    "Carl Sagan": -5,          # Brooklyn NY, Nov 1934: EST (UTC-5)
    "Richard Dawkins": 3,      # Nairobi, Mar 1941: EAT (UTC+3)
    "Bernard Madoff": -4,      # Queens NY, Apr 29 1938: EDT (UTC-4, DST started Apr 24)
    "Elizabeth Holmes": -5,    # Washington DC, Feb 1984: EST (UTC-5)
    "Sam Bankman-Fried": -8,   # Stanford CA, Mar 1992: PST (UTC-8)
}

CHARTS_RAW = [
    {"name":"Peter Thiel","category":"Venture Capitalist","birthday":"1967-10-11","birth_time":"04:15:00","location":"Frankfurt, Germany","coordinates":"50.1109° N, 8.6821° E"},
    {"name":"Marc Andreessen","category":"Venture Capitalist","birthday":"1971-07-09","birth_time":"15:22:00","location":"Cedar Falls, Iowa, USA","coordinates":"42.5275° N, 92.4455° W"},
    {"name":"Vinod Khosla","category":"Venture Capitalist","birthday":"1955-01-28","birth_time":"11:45:00","location":"Delhi, India","coordinates":"28.6139° N, 77.2090° E"},
    {"name":"Paul Graham","category":"Venture Capitalist / Academic","birthday":"1964-11-13","birth_time":"08:12:00","location":"Weymouth, England, UK","coordinates":"50.6144° N, 2.4576° W"},
    {"name":"Noam Chomsky","category":"Academic / Professor","birthday":"1928-12-07","birth_time":"07:15:00","location":"Philadelphia, Pennsylvania, USA","coordinates":"39.9526° N, 75.1652° W"},
    {"name":"Carl Sagan","category":"Academic / Professor","birthday":"1934-11-09","birth_time":"17:05:00","location":"Brooklyn, New York, USA","coordinates":"40.6782° N, 73.9442° W"},
    {"name":"Richard Dawkins","category":"Academic / Professor","birthday":"1941-03-26","birth_time":"06:15:00","location":"Nairobi, Kenya","coordinates":"1.2921° S, 36.8219° E"},
    {"name":"Bernard Madoff","category":"Corporate Bankruptcy / Fraud","birthday":"1938-04-29","birth_time":"07:35:00","location":"Queens, New York, USA","coordinates":"40.7282° N, 73.7949° W"},
    {"name":"Elizabeth Holmes","category":"Corporate Bankruptcy / Fraud","birthday":"1984-02-03","birth_time":"14:10:00","location":"Washington, D.C., USA","coordinates":"38.9072° N, 77.0369° W"},
    {"name":"Sam Bankman-Fried","category":"Corporate Bankruptcy / Fraud","birthday":"1992-03-06","birth_time":"10:14:00","location":"Stanford, California, USA","coordinates":"37.4241° N, 122.1661° W"},
]

def compute_chart(name, birthday, birth_time, lat, lon, tz_offset):
    """Compute chart from date+time+timezone"""
    dt_local = datetime.strptime(f"{birthday}T{birth_time}", "%Y-%m-%dT%H:%M:%S")
    tz = timezone(timedelta(hours=tz_offset))
    dt_local = dt_local.replace(tzinfo=tz)
    dt_utc = dt_local.astimezone(timezone.utc).replace(tzinfo=None)
    
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                     dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
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
    
    return {"name": name, "ascendant": {"sign": asc_sign, "deg": round(asc_sid%30,4)},
            "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)}}

# ============================================================
# YOGA DETECTION (same as v2.1)
# ============================================================
def aspect_each_other(p, a, b):
    if a not in p or b not in p: return False
    ah, bh = p[a]['house'], p[b]['house']
    if (ah + 6) % 12 + 1 == bh: return True
    if (bh + 6) % 12 + 1 == ah: return True
    special = {'Mars': [4,7,8], 'Jupiter': [5,7,9], 'Saturn': [3,7,10]}
    for pl, aspects in special.items():
        if a == pl:
            for asp in aspects:
                if (ah + asp - 1) % 12 + 1 == bh: return True
        if b == pl:
            for asp in aspects:
                if (bh + asp - 1) % 12 + 1 == ah: return True
    return False

def detect_yogas(chart):
    p = chart['planets']
    asc = chart['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    
    ll = SL[asc]
    h2l, h5l, h9l, h10l, h11l = [SL[SIGNS[(asc_idx+h-1)%12]] for h in [2,5,9,10,11]]
    h6l, h8l, h12l = [SL[SIGNS[(asc_idx+h-1)%12]] for h in [6,8,12]]
    
    yogas = {'dhana': [], 'raja': [], 'mahapurusha': [], 'nbry': [], 'vry': []}
    
    # DHANA
    if h2l in p and h11l in p:
        if p[h2l]['house'] == p[h11l]['house']:
            yogas['dhana'].append(f"2L({h2l})+11L({h11l}) conj H{p[h2l]['house']}")
        elif aspect_each_other(p, h2l, h11l):
            yogas['dhana'].append(f"2L({h2l})+11L({h11l}) aspect")
    if h5l in p and h9l in p and p[h5l]['house'] == p[h9l]['house']:
        yogas['dhana'].append(f"LAKSHMI:5L({h5l})+9L({h9l}) conj")
    if ll in p and h9l in p and p[ll]['house'] == p[h9l]['house']:
        yogas['dhana'].append(f"LL({ll})+9L({h9l}) conj")
    if ll in p and h5l in p and p[ll]['house'] == p[h5l]['house']:
        yogas['dhana'].append(f"LL({ll})+5L({h5l}) conj")
    
    # RAJA
    k_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in [1,4,7,10]]
    c_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in [1,5,9]]
    seen = set()
    for kh, kl in k_lords:
        for ch, cl in c_lords:
            if kl == cl: continue
            key = tuple(sorted([kl, cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house'] == p[cl]['house']:
                seen.add(key)
                yogas['raja'].append(f"{kl}(L{kh})+{cl}(L{ch}) conj H{p[kl]['house']}")
    
    # MAHAPURUSHA
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    for pl, yname in mp_map.items():
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            yogas['mahapurusha'].append(f"{yname}:{pl} H{p[pl]['house']} {p[pl]['sign']}")
    
    # NBRY
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in p and p[pl]['dignity'] == -100:
            conds = []
            deb_lord = SL[DEBIL[pl]]
            if deb_lord in p and p[deb_lord]['house'] in [1,4,7,10]:
                conds.append(f"deblord({deb_lord}) kendra")
            ex_lord = SL[EXALT[pl]]
            if ex_lord in p and aspect_each_other(p, pl, ex_lord):
                conds.append(f"exlord({ex_lord}) aspects")
            if conds:
                yogas['nbry'].append(f"{pl} deb {DEBIL[pl]} H{p[pl]['house']}: " + ";".join(conds))
    
    # VRY
    dusthana_lords = {6: h6l, 8: h8l, 12: h12l}
    for dh, dhl in dusthana_lords.items():
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            yogas['vry'].append(f"{dhl}(L{dh}) in H{p[dhl]['house']}")
    
    # Dignities
    dignities = {
        'll': {'planet': ll, 'house': p[ll]['house'] if ll in p else 0, 'dignity': p[ll]['dignity'] if ll in p else 0},
        '9l': {'planet': h9l, 'house': p[h9l]['house'] if h9l in p else 0, 'dignity': p[h9l]['dignity'] if h9l in p else 0},
        '11l': {'planet': h11l, 'house': p[h11l]['house'] if h11l in p else 0, 'dignity': p[h11l]['dignity'] if h11l in p else 0},
    }
    return yogas, dignities

def nexus_score_v2(yogas, dignities, key_pos):
    s = 0
    y = yogas; d = dignities
    
    s += min(len(y['dhana']), 3) * 1.5
    
    d11 = d['11l']['dignity']; h11 = d['11l']['house']
    if d11 == 100: s += 2.5
    elif d11 == 75: s += 1.5
    if h11 in [2,5,9,11]: s += 1
    elif h11 in [6,8,12]: s -= 1
    
    d9 = d['9l']['dignity']; h9 = d['9l']['house']
    if d9 == 100: s += 2.5
    elif d9 == 75: s += 1.5
    if h9 in [1,4,5,7,9,10]: s += 1
    elif h9 in [6,8,12]: s -= 0.5
    
    for benefic in ['Jupiter','Venus']:
        if benefic in key_pos:
            bh = key_pos[benefic]['house']; bd = key_pos[benefic]['dignity']
            if bh in [2,11] and bd >= 0: s += 1.5
            elif bh in [1,4,7,10] and bd >= 75: s += 2
    
    s += len(y['raja']) * 1.5
    s += len(y['mahapurusha']) * 2.5
    
    if d['ll']['dignity'] >= 75: s += 1
    if d['ll']['house'] in [1,4,7,10]: s += 1
    
    vry_count = len(y['vry'])
    if vry_count > 0:
        unique_lords = len(set(v.split('(')[1].split(')')[0] for v in y['vry']))
        s += vry_count * (1 + unique_lords) * 0.75
    
    s += len(y['nbry']) * 1.5
    return round(s, 1)

# ============================================================
# FRAUD SIGNATURES — specific patterns for rise-then-fall
# ============================================================
def detect_fraud_signatures(chart):
    """Detect patterns associated with catastrophic financial collapse"""
    p = chart['planets']
    asc = chart['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    fraud_flags = []
    
    # 1. Rahu-Ketu axis on 2-8 (wealth-destruction axis)
    if 'Rahu' in p and 'Ketu' in p:
        if p['Rahu']['house'] == 2 or p['Ketu']['house'] == 2:
            fraud_flags.append(f"Node on 2H (wealth)")
        if p['Rahu']['house'] == 8 or p['Ketu']['house'] == 8:
            fraud_flags.append(f"Node on 8H (destruction)")
        if {p['Rahu']['house'], p['Ketu']['house']} == {2,8}:
            fraud_flags.append("⛔ RAHU-KETU 2-8 AXIS — classical fraud/collapse")
    
    # 2. 8L in lagna or 12H (secret destruction)
    h8l = SL[SIGNS[(asc_idx+7)%12]]
    if h8l in p:
        if p[h8l]['house'] == 1:
            fraud_flags.append(f"8L({h8l}) in Lagna — carries destruction in self")
        if p[h8l]['house'] == 12:
            fraud_flags.append(f"8L({h8l}) in 12H — hidden losses")
    
    # 3. Rahu + 2L/11L conjunction (illusory wealth)
    h2l = SL[SIGNS[(asc_idx+1)%12]]
    h11l = SL[SIGNS[(asc_idx+10)%12]]
    for lord, lname in [(h2l,'2L'),(h11l,'11L')]:
        if lord in p and 'Rahu' in p and p[lord]['house'] == p['Rahu']['house']:
            fraud_flags.append(f"⛔ Rahu+{lname}({lord}) conj H{p[lord]['house']} — illusory wealth")
    
    # 4. 12L with Venus/Jupiter (hidden expenses consuming wealth)
    h12l = SL[SIGNS[(asc_idx+11)%12]]
    for benefic in ['Venus','Jupiter']:
        if h12l in p and benefic in p and p[h12l]['house'] == p[benefic]['house']:
            fraud_flags.append(f"12L({h12l})+{benefic} conj H{p[h12l]['house']}")
    
    # 5. Saturn aspects on 2H or 11H
    if 'Saturn' in p:
        sh = p['Saturn']['house']
        # Saturn aspects 3,7,10 from itself
        for asp_offset in [3,7,10]:
            asp_house = (sh + asp_offset - 1) % 12 + 1
            if asp_house == 2:
                fraud_flags.append(f"Saturn(H{sh}) aspects 2H — restricts wealth")
            if asp_house == 11:
                fraud_flags.append(f"Saturn(H{sh}) aspects 11H — restricts gains")
    
    # 6. Debilitated 2L or 11L
    for lord, lname in [(h2l,'2L'),(h11l,'11L')]:
        if lord in p and p[lord]['dignity'] == -100:
            fraud_flags.append(f"⛔ {lname}({lord}) DEBILITATED in {p[lord]['sign']} H{p[lord]['house']}")
    
    # 7. Strong yoga count + fraud marker = rise-then-fall
    return fraud_flags

# ============================================================
# MAIN
# ============================================================
print("="*120)
print("10-CHART DOMAIN DISCRIMINATION: VCs vs Academics vs Fraudsters")
print("="*120)

results = []
for c in CHARTS_RAW:
    lat, lon = parse_coords(c['coordinates'])
    tz = TZ_MAP[c['name']]
    ch = compute_chart(c['name'], c['birthday'], c['birth_time'], lat, lon, tz)
    ch['category'] = c['category']
    ch['location'] = c['location']
    
    key_pos = {pl: {'house': ch['planets'][pl]['house'],
                    'sign': ch['planets'][pl]['sign'],
                    'dignity': ch['planets'][pl]['dignity']}
               for pl in ['Jupiter','Venus','Saturn','Mars'] if pl in ch['planets']}
    yogas, dignities = detect_yogas(ch)
    score = nexus_score_v2(yogas, dignities, key_pos)
    fraud_flags = detect_fraud_signatures(ch)
    
    ch['yogas'] = yogas
    ch['nexus_score_v2'] = score
    ch['dignities'] = dignities
    ch['fraud_flags'] = fraud_flags
    results.append(ch)

# --- SORTED TABLE ---
results.sort(key=lambda x: -x['nexus_score_v2'])

print(f"\n{'#':<3} {'Name':<22} {'Category':<30} {'Asc':<8} {'Moon':<20} "
      f"{'Dha':>3} {'Raj':>3} {'MP':>3} {'VRY':>3} {'NBR':>3} {'Score':>6} {'Fraud':>4}")
print("-"*130)

DOMAIN = {
    'Venture Capitalist': '💰',
    'Venture Capitalist / Academic': '💰📚',
    'Academic / Professor': '📚',
    'Corporate Bankruptcy / Fraud': '💀',
}

for i, c in enumerate(results, 1):
    y = c['yogas']
    sc = c['nexus_score_v2']
    ff = c['fraud_flags']
    ff_count = len([f for f in ff if '⛔' in f])  # Critical fraud markers only
    moon = c['planets']['Moon']
    moon_str = f"{moon['nakshatra'][:16]}"
    emoji = DOMAIN.get(c['category'], '?')
    print(f"{i:<3} {c['name']:<22} {emoji} {c['category']:<27} {c['ascendant']['sign']:<8} {moon_str:<20} "
          f"{len(y['dhana']):>3} {len(y['raja']):>3} {len(y['mahapurusha']):>3} "
          f"{len(y['vry']):>3} {len(y['nbry']):>3} {sc:>6.1f} {ff_count:>4}")

# --- GROUP STATS ---
print(f"\n{'='*120}")
print("GROUP STATISTICS")
print(f"{'='*120}")

groups = {}
for c in results:
    grp = c['category']
    if grp not in groups: groups[grp] = []
    groups[grp].append(c)

for grp, charts in groups.items():
    scores = [c['nexus_score_v2'] for c in charts]
    fraud_critical = [len([f for f in c['fraud_flags'] if '⛔' in f]) for c in charts]
    print(f"\n{grp} (n={len(charts)})")
    print(f"  Score: mean={sum(scores)/len(scores):.1f}  range=[{min(scores):.1f}, {max(scores):.1f}]")
    print(f"  Critical fraud flags: mean={sum(fraud_critical)/len(fraud_critical):.1f}  total={sum(fraud_critical)}")
    # Common yogas
    all_yoga_types = []
    for c in charts:
        for ytype in ['dhana','raja','mahapurusha','vry','nbry']:
            all_yoga_types.extend([ytype] * len(c['yogas'][ytype]))
    from collections import Counter
    yc = Counter(all_yoga_types)
    print(f"  Yoga profile: " + " | ".join(f"{k}={v}" for k,v in yc.most_common()))

# --- FRAUD vs NON-FRAUD DISCRIMINATION ---
print(f"\n{'='*120}")
print("FRAUD DISCRIMINATION SIGNAL")
print(f"{'='*120}")

fraud_charts = [c for c in results if 'Fraud' in c['category']]
non_fraud = [c for c in results if 'Fraud' not in c['category']]

print(f"\nFraud group (n={len(fraud_charts)}):")
for c in fraud_charts:
    print(f"\n  {c['name']} | Score={c['nexus_score_v2']} | {c['ascendant']['sign']} Lagna | Moon {c['planets']['Moon']['nakshatra']}")
    for f in c['fraud_flags']:
        print(f"    {f}")

print(f"\nNon-fraud group (n={len(non_fraud)}):")
for c in non_fraud:
    critical = [f for f in c['fraud_flags'] if '⛔' in f]
    if critical:
        print(f"  ⚠ {c['name']} (should NOT be fraud): {', '.join(critical)}")

# Separate by domain scores
print(f"\n--- FRAUD SCORE vs NON-FRAUD SCORE ---")
fraud_scores = [c['nexus_score_v2'] for c in fraud_charts]
nf_scores = [c['nexus_score_v2'] for c in non_fraud]
print(f"  Fraud mean score: {sum(fraud_scores)/len(fraud_scores):.1f}")
print(f"  Non-fraud mean score: {sum(nf_scores)/len(nf_scores):.1f}")
print(f"  Fraud critical flags avg: {sum(len([f for f in c['fraud_flags'] if '⛔' in f]) for c in fraud_charts)/len(fraud_charts):.1f}")
print(f"  Non-fraud critical flags avg: {sum(len([f for f in c['fraud_flags'] if '⛔' in f]) for c in non_fraud)/len(non_fraud):.1f}")

# Save
with open('dataset/benchmark_10_domain.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → dataset/benchmark_10_domain.json")
