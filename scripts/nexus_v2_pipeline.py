#!/usr/bin/env python3
"""
COMPREHENSIVE BENCHMARK PIPELINE
1. Compute 112 celebrity charts via Swiss Ephemeris
2. NEXUS yoga detection with VRY × dusthana-lord interaction
3. Cross-validate against known categories (12 labeled charts)
4. Save all results
"""
import swisseph as swe
import json, sys, os
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

# ============================================================
# CONSTANTS
# ============================================================
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

def parse_iso(s):
    s = s.replace('Z','+00:00')
    try:
        return datetime.fromisoformat(s)
    except:
        base = s[:19]
        tz = s[19:] if len(s)>19 else '+00:00'
        dt = datetime.strptime(base, '%Y-%m-%dT%H:%M:%S')
        sign = 1 if tz[0]=='+' else -1
        h, m = int(tz[1:3]), int(tz[4:6])
        return dt.replace(tzinfo=timezone(timedelta(hours=sign*h, minutes=sign*m)))

def compute_chart(name, iso, lat, lon):
    dt = parse_iso(iso)
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
            "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)}}


# ============================================================
# NEXUS YOGA DETECTION v2.1 — WITH VRY INTERACTION
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
    
    # --- DHANA ---
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
    
    # --- RAJA (Kendra-Kona lord pairs) ---
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
    
    # --- MAHAPURUSHA ---
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    for pl, yname in mp_map.items():
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            yogas['mahapurusha'].append(f"{yname}:{pl} H{p[pl]['house']} {p[pl]['sign']}")
    
    # --- NBRY ---
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
    
    # --- VRY (Vipareeta Raj Yoga) ---
    dusthana_lords = {6: h6l, 8: h8l, 12: h12l}
    for dh, dhl in dusthana_lords.items():
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            yogas['vry'].append(f"{dhl}(L{dh}) in H{p[dhl]['house']}")
    
    # --- Key dignities ---
    dignities = {
        'll': {'planet': ll, 'house': p[ll]['house'] if ll in p else 0, 'dignity': p[ll]['dignity'] if ll in p else 0},
        '9l': {'planet': h9l, 'house': p[h9l]['house'] if h9l in p else 0, 'dignity': p[h9l]['dignity'] if h9l in p else 0},
        '11l': {'planet': h11l, 'house': p[h11l]['house'] if h11l in p else 0, 'dignity': p[h11l]['dignity'] if h11l in p else 0},
    }
    
    return yogas, dignities


def nexus_score_v2(yogas, dignities, key_pos):
    """
    NEXUS v2.1 — VRY × dusthana-lord interaction scoring.
    
    Channels:
    - Wealth: Dhana yogas + 11L/9L dignity + 2/11 benefics
    - Power: Raja yogas + Mahapurusha
    - Obstruction removal: VRY (with interaction boost) + NBRY
    """
    s = 0
    y = yogas
    d = dignities
    
    # --- WEALTH CHANNEL ---
    s += min(len(y['dhana']), 3) * 1.5  # Dhana yogas: max 4.5
    
    # 11L quality
    d11 = d['11l']['dignity']
    h11 = d['11l']['house']
    if d11 == 100: s += 2.5
    elif d11 == 75: s += 1.5
    if h11 in [2,5,9,11]: s += 1
    elif h11 in [6,8,12]: s -= 1
    
    # 9L quality
    d9 = d['9l']['dignity']
    h9 = d['9l']['house']
    if d9 == 100: s += 2.5
    elif d9 == 75: s += 1.5
    if h9 in [1,4,5,7,9,10]: s += 1
    elif h9 in [6,8,12]: s -= 0.5
    
    # Benefics in wealth houses
    for benefic in ['Jupiter','Venus']:
        if benefic in key_pos:
            bh = key_pos[benefic]['house']
            bd = key_pos[benefic]['dignity']
            if bh in [2,11] and bd >= 0: s += 1.5
            elif bh in [1,4,7,10] and bd >= 75: s += 2
    
    # --- POWER CHANNEL ---
    s += len(y['raja']) * 1.5  # Each Raja yoga: 1.5
    s += len(y['mahapurusha']) * 2.5  # Each MP: 2.5
    
    # LL quality
    if d['ll']['dignity'] >= 75: s += 1
    if d['ll']['house'] in [1,4,7,10]: s += 1
    
    # --- OBSTRUCTION REMOVAL ---
    # VRY interaction: count²-like boost for multiple dusthana lords cooperating
    vry_count = len(y['vry'])
    if vry_count > 0:
        unique_lords = len(set(v.split('(')[1].split(')')[0] for v in y['vry']))
        vry_score = vry_count * (1 + unique_lords) * 0.75  # Interaction term
        s += vry_score
    
    # NBRY
    s += len(y['nbry']) * 1.5
    
    return round(s, 1)


# ============================================================
# MAIN
# ============================================================
print("="*100)
print("NEXUS v2.1 — 112 CELEBRITY CHARTS + 12 LABELED BENCHMARK")
print("="*100)

# --- LOAD 112 celebrity charts ---
with open('astrodb_out/chart_houses.json') as f:
    celeb_charts = json.load(f)

print(f"\nLoaded {len(celeb_charts)} celebrity charts")

# Compute all 112
computed_112 = []
for i, c in enumerate(celeb_charts):
    if i % 20 == 0: print(f"  Computing {i+1}/{len(celeb_charts)}...")
    try:
        ch = compute_chart(c['name'], c['birth_local'], c['lat'], c['lon'])
        # Preserve original fields
        ch['city'] = c.get('city','')
        ch['country'] = c.get('country','')
        ch['loop_len'] = c.get('loop_len',0)
        ch['bond'] = c.get('bond',0)
        # Run yoga detection
        key_pos = {pl: {'house': ch['planets'][pl]['house'], 
                        'sign': ch['planets'][pl]['sign'],
                        'dignity': ch['planets'][pl]['dignity']} 
                   for pl in ['Jupiter','Venus','Saturn','Mars'] if pl in ch['planets']}
        yogas, dignities = detect_yogas(ch)
        score = nexus_score_v2(yogas, dignities, key_pos)
        ch['yogas'] = yogas
        ch['nexus_score_v2'] = score
        ch['dignities'] = dignities
        computed_112.append(ch)
    except Exception as e:
        print(f"  ERROR {c['name']}: {e}")

print(f"\nComputed {len(computed_112)}/{len(celeb_charts)} celebrity charts")

# --- 12 LABELED BENCHMARK ---
LABELED = [
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

print(f"\n--- 12 LABELED BENCHMARK ---")
labeled_results = []
for c in LABELED:
    ch = compute_chart(c['name'], c['iso'], c['lat'], c['lon'])
    ch['occupation'] = c['occupation']
    ch['category'] = c['category']
    key_pos = {pl: {'house': ch['planets'][pl]['house'], 
                    'sign': ch['planets'][pl]['sign'],
                    'dignity': ch['planets'][pl]['dignity']} 
               for pl in ['Jupiter','Venus','Saturn','Mars'] if pl in ch['planets']}
    yogas, dignities = detect_yogas(ch)
    score = nexus_score_v2(yogas, dignities, key_pos)
    ch['yogas'] = yogas
    ch['nexus_score_v2'] = score
    ch['dignities'] = dignities
    labeled_results.append(ch)

CAT_BANDS = {
    'Billionaire': (5, 12), 'Wealth/Inherited': (4, 10),
    'Creative/Success': (3, 9), 'Actor': (2, 8),
    'Athlete': (2, 7), 'Religious': (1, 6),
    'Power/Historical': (5, 12), 'Military/Criminal': (3, 10),
}

WEALTH_RANK = {
    'Billionaire': 5, 'Wealth/Inherited': 4, 'Power/Historical': 4,
    'Creative/Success': 3, 'Actor': 3, 'Military/Criminal': 2,
    'Athlete': 2, 'Religious': 1,
}

labeled_results.sort(key=lambda x: -x['nexus_score_v2'])

print(f"\n{'#':<3} {'Name':<22} {'Cat':<20} {'Asc':<8} {'MoonNak':<16} {'Dha':>3} {'Raj':>3} {'MP':>3} {'VRY':>3} {'NBRY':>3} {'Score':>6} {'Band':>8}")
print("-"*120)

hits = 0
scores_pred = []
scores_known = []
for i, c in enumerate(labeled_results, 1):
    y = c['yogas']
    sc = c['nexus_score_v2']
    cat = c['category']
    band = CAT_BANDS.get(cat, (0,20))
    match = "✓" if band[0] <= sc <= band[1] else ("↑" if sc > band[1] else "↓")
    if match == "✓": hits += 1
    scores_pred.append(sc)
    scores_known.append(WEALTH_RANK.get(cat, 2))
    moon = c['planets']['Moon']
    print(f"{i:<3} {c['name']:<22} {cat:<20} {c['ascendant']['sign']:<8} {moon['nakshatra']:<16} "
          f"{len(y['dhana']):>3} {len(y['raja']):>3} {len(y['mahapurusha']):>3} {len(y['vry']):>3} {len(y['nbry']):>3} {sc:>6.1f} {band[0]}-{band[1]:<3} {match}")

# Spearman
n = len(scores_pred)
pred_ranks = [sorted(scores_pred, reverse=True).index(x)+1 for x in scores_pred]
known_ranks = [sorted(scores_known, reverse=True).index(x)+1 for x in scores_known]
d2 = sum((a-b)**2 for a,b in zip(pred_ranks, known_ranks))
rho = 1 - (6*d2)/(n*(n**2-1))

print(f"\nNEXUS v2.1 Results: {hits}/{n} in-band ({100*hits/n:.0f}%) | Spearman ρ = {rho:.3f}")

# --- TOP/BOTTOM 10 from 112 ---
print(f"\n{'='*100}")
print("TOP 20 CELEBRITY CHARTS BY NEXUS v2.1 SCORE")
print(f"{'='*100}")
computed_112.sort(key=lambda x: -x['nexus_score_v2'])
for i, c in enumerate(computed_112[:20], 1):
    y = c['yogas']
    sc = c['nexus_score_v2']
    asc = c['ascendant']['sign']
    moon = c['planets']['Moon']['nakshatra']
    print(f"{i:>3}. {c['name']:<28} {sc:>5.1f} | {asc:<8} Moon {moon:<14} | "
          f"D:{len(y['dhana'])} R:{len(y['raja'])} MP:{len(y['mahapurusha'])} V:{len(y['vry'])} N:{len(y['nbry'])} | "
          f"{c.get('country','')}")

print(f"\nBOTTOM 10:")
for i, c in enumerate(computed_112[-10:], 1):
    y = c['yogas']
    sc = c['nexus_score_v2']
    asc = c['ascendant']['sign']
    moon = c['planets']['Moon']['nakshatra']
    print(f"{i:>3}. {c['name']:<28} {sc:>5.1f} | {asc:<8} Moon {moon:<14} | "
          f"D:{len(y['dhana'])} R:{len(y['raja'])} MP:{len(y['mahapurusha'])} V:{len(y['vry'])} N:{len(y['nbry'])}")

# --- SAVE ALL ---
out_112 = 'dataset/celebrity_112_nexus_v2.json'
out_12 = 'dataset/benchmark_12_nexus_v2.json'

with open(out_112, 'w') as f:
    json.dump(computed_112, f, indent=2)
print(f"\nSaved 112 charts → {out_112}")

with open(out_12, 'w') as f:
    json.dump(labeled_results, f, indent=2)
print(f"Saved 12 labeled → {out_12}")

# Summary stats
scores_112 = [c['nexus_score_v2'] for c in computed_112]
print(f"\n112-chart distribution: min={min(scores_112):.1f} max={max(scores_112):.1f} "
      f"mean={sum(scores_112)/len(scores_112):.1f} median={sorted(scores_112)[len(scores_112)//2]:.1f}")
