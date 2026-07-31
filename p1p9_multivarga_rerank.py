#!/usr/bin/env python3
"""
P1-P9 COMPREHENSIVE RERANK — Using all discoveries from 22 benchmark charts
- D1 + D2 + D9 + D10 + D24 + D60 vargas
- D9 Venus dignity (fraud/ethics signal)
- D10 10L position (career destruction risk)
- D60 D1-LL karmic position
- Vimshottari dasha window analysis
- NEXUS v2.1 yoga scoring
- Rank correlation with known archetypes
"""
import swisseph as swe
import json
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
NAK_SPAN = 360.0/27
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),
        ("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),
        ("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),
        ("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),
        ("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),
        ("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),
        ("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

# P1-P9 birth data (verified from research)
CHARTS_P = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5,"place":"Polgahawela, SL","archetype":"Self-Made Warlord","edu":"Engineering→MBA","career":"Industrial CEO"},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"place":"Colombo, SL","archetype":"Enigma ⚠️","edu":"Intl Business→MBA","career":"MNC Manager","note":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5,"place":"Colombo, SL","archetype":"Sage","edu":"PhD→Jyotish","career":"Academic Researcher"},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5,"place":"Colombo, SL","archetype":"Luxe Empire Builder","edu":"Business→Real Estate","career":"Luxury/Beauty Founder"},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5,"place":"Colombo, SL","archetype":"Slow-Motion Titan","edu":"CS→Finance→Law","career":"Tech/Quant Finance"},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5,"place":"Sri Jayawardenepura Kotte, SL","archetype":"Fighter","edu":"Business→Law","career":"Strategy Consultant"},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"place":"Colombo, SL","archetype":"Phoenix","edu":"Finance→CS→PhD","career":"Quant Finance","note":"Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5,"place":"Kurunegala, SL","archetype":"Oracle of Depth","edu":"Psychology→Finance","career":"Psychologist/Analyst"},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5,"place":"Kandy, SL","archetype":"Magnetic Partner","edu":"Accounting→Eng→Law","career":"Audit/Govt Director"},
]

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

def compute_d1(c):
    dt_local = datetime.strptime(f"{c['birthday']}T{c['birth_time']}", "%Y-%m-%dT%H:%M:%S")
    tz = timezone(timedelta(hours=c['tz']))
    dt_local = dt_local.replace(tzinfo=tz)
    dt_utc = dt_local.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                     dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
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
                       "deg_in_sign": round(rl%30,4), "dignity": 0, "nakshatra": nk, "nakshatra_lord": nl}
    
    for pn in planets:
        planets[pn]["house"] = (planets[pn]["sign_idx"] - asc_idx) % 12 + 1
    
    ms = planets["Moon"]["sidereal"]
    ml = mn = "?"; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + NAK_SPAN:
            elapsed = (ms - s) / NAK_SPAN
            bal = VIM_YRS[l] * (1.0 - elapsed)
            ml = l; mn = n; break
    
    return {"name": c['name'],"id": c['id'],
            "ascendant": {"sign": asc_sign, "deg": round(asc_sid%30,4), "sidereal": round(asc_sid,4)},
            "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)},
            "birthday": c['birthday'], "birth_time": c['birth_time'], "tz": c['tz']}

def compute_varga(d1, division):
    p = d1['planets']
    asc_sid = d1['ascendant']['sidereal']
    varga_planets = {}
    for pn in p:
        vlon = (p[pn]['sidereal'] * division) % 360
        vsgn = SIGNS[int(vlon // 30)]
        varga_planets[pn] = {"sign": vsgn, "sidereal": vlon}
    vlagna_lon = (asc_sid * division) % 360
    vlagna = SIGNS[int(vlagna_lon // 30)]
    vlagna_idx = SIGNS.index(vlagna)
    for pn in varga_planets:
        si = SIGNS.index(varga_planets[pn]['sign'])
        varga_planets[pn]['house'] = (si - vlagna_idx) % 12 + 1
    return {"lagna": vlagna, "lagna_idx": vlagna_idx, "planets": varga_planets}

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

def detect_yogas(d1):
    p = d1['planets']
    asc = d1['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    ll = SL[asc]
    h2l, h5l, h9l, h10l, h11l = [SL[SIGNS[(asc_idx+h-1)%12]] for h in [2,5,9,10,11]]
    
    yogas = {'dhana': [], 'raja': [], 'mahapurusha': [], 'nbry': [], 'vry': []}
    
    if h2l in p and h11l in p:
        if p[h2l]['house'] == p[h11l]['house']:
            yogas['dhana'].append(f"2L({h2l})+11L({h11l}) conj H{p[h2l]['house']}")
        elif aspect_each_other(p, h2l, h11l):
            yogas['dhana'].append(f"2L({h2l})+11L({h11l}) aspect")
    if h5l in p and h9l in p and p[h5l]['house'] == p[h9l]['house']:
        yogas['dhana'].append(f"LAKSHMI:5L({h5l})+9L({h9l})")
    if ll in p and h9l in p and p[ll]['house'] == p[h9l]['house']:
        yogas['dhana'].append(f"LL({ll})+9L({h9l})")
    if ll in p and h5l in p and p[ll]['house'] == p[h5l]['house']:
        yogas['dhana'].append(f"LL({ll})+5L({h5l})")
    
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
    
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    for pl, yname in mp_map.items():
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            yogas['mahapurusha'].append(f"{yname}:{pl} H{p[pl]['house']} {p[pl]['sign']}")
    
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
    
    dusthana = {6: SL[SIGNS[(asc_idx+5)%12]], 8: SL[SIGNS[(asc_idx+7)%12]], 12: SL[SIGNS[(asc_idx+11)%12]]}
    for dh, dhl in dusthana.items():
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            yogas['vry'].append(f"{dhl}(L{dh}) in H{p[dhl]['house']}")
    
    return yogas

# ============================================================
# MULTI-DIMENSIONAL SCORING (informed by 22 benchmark discoveries)
# ============================================================
def score_wealth(d1, yogas, vargas):
    """Wealth score: D1 yogas + D2 strength + D9 Venus"""
    s = 0
    p = d1['planets']; asc = d1['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    ll = SL[asc]; h11l = SL[SIGNS[(asc_idx+10)%12]]; h9l = SL[SIGNS[(asc_idx+8)%12]]
    
    # D1 Dhana yogas
    s += min(len(yogas['dhana']), 3) * 1.5
    
    # 11L dignity
    if h11l in p:
        d11 = p[h11l]['dignity']
        h11 = p[h11l]['house']
        if d11 == 100: s += 3
        elif d11 == 75: s += 1.5
        if h11 in [2,5,9,11]: s += 1
        elif h11 in [6,8,12]: s -= 1.5
    
    # 9L dignity
    if h9l in p:
        d9 = p[h9l]['dignity']
        h9 = p[h9l]['house']
        if d9 == 100: s += 3
        elif d9 == 75: s += 1.5
        if h9 in [1,4,5,7,9,10]: s += 1
        elif h9 in [6,8,12]: s -= 1
    
    # D2 Hora analysis
    d2 = vargas['D2']
    d2_p = d2['planets']
    d2_asc = d2['lagna']; d2_idx = SIGNS.index(d2_asc)
    d2_11l = SL[SIGNS[(d2_idx+10)%12]]
    if d2_11l in d2_p and d2_p[d2_11l]['house'] in [1,2,5,9,11]:
        s += 1.5
    
    # D9 Venus — CRITICAL from fraud discovery
    d9 = vargas['D9']
    d9_p = d9['planets']
    if 'Venus' in d9_p:
        d9_venus_sign = d9_p['Venus']['sign']
        if DEBIL.get('Venus') == d9_venus_sign:
            s -= 2  # Debilitated Venus in D9 = compromised wealth ethics
        elif EXALT.get('Venus') == d9_venus_sign:
            s += 2  # Exalted Venus = clean wealth channel
        elif d9_venus_sign in OWN.get('Venus', []):
            s += 1
    
    # Benefics in D1 2/11
    for b in ['Jupiter','Venus']:
        if b in p and p[b]['house'] in [2,11] and p[b]['dignity'] >= 0:
            s += 1.5
        elif b in p and p[b]['house'] in [1,4,7,10] and p[b]['dignity'] >= 75:
            s += 2
    
    return max(0, s)

def score_power(d1, yogas, vargas):
    """Power/Status: D1 Raja + Mahapurusha + D10 10L"""
    s = 0
    p = d1['planets']; asc = d1['ascendant']['sign']
    asc_idx = SIGNS.index(asc); ll = SL[asc]
    
    # Raja yogas
    s += len(yogas['raja']) * 1.5
    
    # Mahapurusha — BUT penalize if 3+ (Cronin effect)
    mp_count = len(yogas['mahapurusha'])
    if mp_count == 1: s += 3
    elif mp_count == 2: s += 5
    elif mp_count >= 3: s += 6  # Diminishing returns
    
    # LL dignity
    if ll in p:
        if p[ll]['dignity'] >= 75: s += 1.5
        if p[ll]['house'] in [1,4,7,10]: s += 1.5
    
    # VRY interaction
    vry_count = len(yogas['vry'])
    if vry_count > 0:
        unique = len(set(v.split('(')[1].split(')')[0] for v in yogas['vry']))
        s += vry_count * (1 + unique) * 0.5
    
    # NBRY
    s += len(yogas['nbry']) * 1.5
    
    # D10 10L — CRITICAL from fraud discovery
    d10 = vargas['D10']
    d10_p = d10['planets']
    d10_idx = SIGNS.index(d10['lagna'])
    d10_10l = SL[SIGNS[(d10_idx+9)%12]]
    if d10_10l in d10_p:
        h10l_d10_house = d10_p[d10_10l]['house']
        if h10l_d10_house in [1,4,7,10]:
            s += 2
        elif h10l_d10_house in [6,8,12]:
            s -= 2  # Career destruction risk
    
    # D10 planets in 10H
    for pl in d10_p:
        if d10_p[pl]['house'] == 10:
            s += 1
    
    return max(0, s)

def score_karma(vargas):
    """Karmic debt score from D60"""
    d60 = vargas['D60']
    d60_p = d60['planets']
    d60_idx = SIGNS.index(d60['lagna'])
    
    s = 0
    d60_ll = SL[d60['lagna']]
    
    # D60 LL in kendra = good karma
    if d60_ll in d60_p and d60_p[d60_ll]['house'] in [1,4,7,10]:
        s += 2
    elif d60_ll in d60_p and d60_p[d60_ll]['house'] in [6,8,12]:
        s -= 2
    
    # D60 9L
    d60_9l = SL[SIGNS[(d60_idx+8)%12]]
    if d60_9l in d60_p and d60_p[d60_9l]['house'] in [1,5,9]:
        s += 2
    elif d60_9l in d60_p and d60_p[d60_9l]['house'] in [6,8,12]:
        s -= 1
    
    # Benefics in D60 lagna or 9H
    for pl in ['Jupiter','Venus']:
        if pl in d60_p and d60_p[pl]['house'] in [1,9]:
            s += 1
    
    return s

def score_education(d1, vargas):
    """Education/Learning from D24"""
    d24 = vargas['D24']
    d24_p = d24['planets']
    d24_idx = SIGNS.index(d24['lagna'])
    s = 0
    
    d24_5l = SL[SIGNS[(d24_idx+4)%12]]
    if d24_5l in d24_p:
        h = d24_p[d24_5l]['house']
        if h in [1,5,9]: s += 2
        elif h in [6,8,12]: s -= 1
    
    d24_9l = SL[SIGNS[(d24_idx+8)%12]]
    if d24_9l in d24_p:
        h = d24_p[d24_9l]['house']
        if h in [1,5,9]: s += 2
        elif h in [6,8,12]: s -= 1
    
    for pl in ['Mercury','Jupiter']:
        if pl in d24_p and d24_p[pl]['house'] in [1,5,9]:
            s += 1
    
    return s

def get_current_dasha(d1, ref_year=2026):
    """Get current and upcoming MD"""
    ml = d1['moon_nakshatra']['lord']
    balance = d1['moon_nakshatra']['balance_yrs']
    birth_dt = datetime.strptime(f"{d1['birthday']}T{d1['birth_time']}", "%Y-%m-%dT%H:%M:%S")
    birth_dt = birth_dt.replace(tzinfo=timezone(timedelta(hours=d1['tz'])))
    ref_dt = datetime(ref_year, 6, 15, tzinfo=timezone(timedelta(hours=0)))
    yrs_from_birth = (ref_dt - birth_dt).total_seconds() / (365.25 * 86400)
    
    ml_idx = VIM_ORDER.index(ml)
    elapsed = 0; remaining = balance
    
    while elapsed + remaining <= yrs_from_birth:
        elapsed += remaining
        ml_idx = (ml_idx + 1) % 9
        remaining = VIM_YRS[VIM_ORDER[ml_idx]]
    
    current_md = VIM_ORDER[ml_idx]
    next_md = VIM_ORDER[(ml_idx + 1) % 9]
    md_elapsed = yrs_from_birth - elapsed
    md_total = VIM_YRS[current_md]
    
    # AD
    ad_idx = VIM_ORDER.index(current_md)
    ad_elapsed = 0
    for ad_i in range(9):
        ad_lord = VIM_ORDER[(ad_idx + ad_i) % 9]
        ad_dur = VIM_YRS[ad_lord] / 120 * md_total
        if ad_elapsed + ad_dur > md_elapsed:
            current_ad = ad_lord
            break
        ad_elapsed += ad_dur
    
    return current_md, current_ad, next_md, round(md_elapsed/md_total * 100, 1)


# ============================================================
# MAIN
# ============================================================
print("="*120)
print("P1-P9 COMPREHENSIVE RERANK — Multi-Varga + Dasha Analysis")
print("="*120)

all_p = []
for c in CHARTS_P:
    print(f"Computing {c['id']} {c['name']}...")
    d1 = compute_d1(c)
    d1['archetype'] = c['archetype']
    d1['career'] = c['career']
    d1['edu'] = c['edu']
    d1['note'] = c.get('note','')
    
    # Vargas
    vargas = {}
    for vn, vd in [('D2',2),('D9',9),('D10',10),('D24',24),('D60',60)]:
        vargas[vn] = compute_varga(d1, vd)
    
    # Yogas
    yogas = detect_yogas(d1)
    
    # Multi-dimensional scores
    w = score_wealth(d1, yogas, vargas)
    pwr = score_power(d1, yogas, vargas)
    k = score_karma(vargas)
    e = score_education(d1, vargas)
    composite = w * 0.35 + pwr * 0.30 + k * 0.15 + e * 0.20
    
    # Current dasha
    cm, ca, nm, pct = get_current_dasha(d1)
    
    d1['vargas'] = vargas
    d1['yogas'] = yogas
    d1['scores'] = {'wealth': round(w,1), 'power': round(pwr,1), 'karma': round(k,1),
                    'education': round(e,1), 'composite': round(composite,1)}
    d1['dasha'] = {'current_md': cm, 'current_ad': ca, 'next_md': nm, 'md_pct': pct}
    
    # D9 Venus check
    d9v = vargas['D9']['planets'].get('Venus', {})
    d9_venus_sign = d9v.get('sign', '?') if d9v else '?'
    d1['d9_venus'] = d9_venus_sign
    
    # D10 10L check
    d10 = vargas['D10']
    d10_idx = SIGNS.index(d10['lagna'])
    d10_10l = SL[SIGNS[(d10_idx+9)%12]]
    d10_10l_house = d10['planets'][d10_10l]['house'] if d10_10l in d10['planets'] else 0
    d1['d10_10l_house'] = d10_10l_house
    
    all_p.append(d1)

# Sort by composite
all_p.sort(key=lambda x: -x['scores']['composite'])

print(f"\n{'='*120}")
print(f"FINAL RANKED TABLE — Multi-Dimensional Scoring")
print(f"{'='*120}")
print(f"{'Rank':<5} {'ID':<4} {'Name':<20} {'Lagna':<10} {'Moon(Nak)':<18} {'Dha':>3} {'Raj':>3} {'MP':>3} {'W$':>5} {'Pwr':>5} {'Kar':>5} {'Edu':>5} {'Comp':>6} {'D9♀':<10} {'D10 10L':<12} {'Dasha':<16} {'Note'}")
print("-"*150)

prev_rank = {}
for i, c in enumerate(all_p, 1):
    s = c['scores']
    y = c['yogas']
    moon = c['planets']['Moon']
    moon_str = f"{moon['nakshatra'][:14]}"
    asc = c['ascendant']['sign']
    d9v = c['d9_venus']
    d10_10l_h = c['d10_10l_house']
    d10_tag = ""
    if d10_10l_h in [6,8,12]: d10_tag = "⚠️"
    elif d10_10l_h in [1,4,7,10]: d10_tag = "✓"
    
    dasha_str = f"{c['dasha']['current_md']}/{c['dasha']['current_ad']}"
    note = c.get('note','')[:20]
    if note: note = f"[{note}]"
    
    print(f"{i:<5} {c['id']:<4} {c['name']:<20} {asc:<10} {moon_str:<18} "
          f"{len(y['dhana']):>3} {len(y['raja']):>3} {len(y['mahapurusha']):>3} "
          f"{s['wealth']:>5.1f} {s['power']:>5.1f} {s['karma']:>5.1f} {s['education']:>5.1f} "
          f"{s['composite']:>6.1f} "
          f"{d9v:<10} {d10_10l_h}:{d10_tag:<10} {dasha_str:<16} {note}")

# --- RANK SHIFT vs OLD ---
old_ranks = {"P4":1,"P9":2,"P5":3,"P8":4,"P1":5,"P2":6,"P7":7,"P6":8,"P3":9}
print(f"\n{'='*120}")
print("RANK SHIFT vs PREVIOUS RANKING")
print(f"{'='*120}")
print(f"{'ID':<4} {'Name':<20} {'Old Rk':>6} {'New Rk':>6} {'Shift':>6} {'Key Driver'}")
print("-"*65)
for i, c in enumerate(all_p, 1):
    old = old_ranks.get(c['id'], 99)
    shift = old - i
    arrow = "↑" if shift > 0 else ("↓" if shift < 0 else "—")
    
    # What drove the shift?
    s = c['scores']
    drivers = []
    if s['wealth'] >= 8: drivers.append("strong wealth")
    if s['power'] >= 8: drivers.append("strong power")
    if s['karma'] >= 3: drivers.append("good karma")
    if s['education'] >= 3: drivers.append("education")
    if c['d9_venus'] in ['Taurus','Libra','Pisces']: drivers.append("D9♀ strong")
    if c['d9_venus'] == 'Virgo': drivers.append("D9♀ debil")
    if c['d10_10l_house'] in [6,8,12]: drivers.append("D10 10L⚠️")
    
    print(f"{c['id']:<4} {c['name']:<20} {old:>6} {i:>6} {arrow}{abs(shift):>4}  {', '.join(drivers[:3])}")

# --- GROUP SUMMARY ---
print(f"\n{'='*120}")
print("DIMENSION LEADERS")
print(f"{'='*120}")
for dim, label in [('wealth','💰 Wealth'),('power','👑 Power'),('karma','🕉️ Karma'),('education','📚 Education'),('composite','⭐ Composite')]:
    sorted_dim = sorted(all_p, key=lambda x: -x['scores'][dim])
    top3 = sorted_dim[:3]
    print(f"  {label}: " + " > ".join(f"{c['id']} {c['name']}({c['scores'][dim]:.1f})" for c in top3))

# --- D9 VENUS AUDIT ---
print(f"\n{'='*120}")
print("D9 VENUS AUDIT — Ethics/Wealth Relationship")
print(f"{'='*120}")
for c in all_p:
    d9v = c['d9_venus']
    d9v_status = ""
    if d9v == 'Virgo': d9v_status = "⛔ DEBILITATED — compromised wealth ethics"
    elif d9v == 'Pisces': d9v_status = "✓ EXALTED — clean wealth channel"
    elif d9v in ['Taurus','Libra']: d9v_status = "✓ OWN — stable wealth relationship"
    else: d9v_status = "— neutral"
    print(f"  {c['id']} {c['name']:<20} D9 Venus: {d9v:<12} {d9v_status}")

# --- D10 10L AUDIT ---
print(f"\n{'='*120}")
print("D10 10L AUDIT — Career Destruction Risk")
print(f"{'='*120}")
for c in all_p:
    h = c['d10_10l_house']
    risk = ""
    if h in [6,8,12]: risk = f"⚠️ DUSTHANA H{h} — career collapse risk"
    elif h in [1,4,7,10]: risk = f"✓ KENDRA H{h} — stable career foundation"
    else: risk = f"— neutral H{h}"
    print(f"  {c['id']} {c['name']:<20} D10 10L: H{h} {risk}")

# --- DASHA WINDOWS ---
print(f"\n{'='*120}")
print("CURRENT DASHA WINDOWS (July 2026)")
print(f"{'='*120}")
for c in all_p:
    d = c['dasha']
    next_info = f"→ {d['next_md']} MD next"
    print(f"  {c['id']} {c['name']:<20} {d['current_md']} MD / {d['current_ad']} AD ({d['md_pct']}% thru) {next_info}")

# Save
with open('dataset/p1p9_multivarga_reranked.json', 'w') as f:
    json.dump(all_p, f, indent=2)
print(f"\nSaved → dataset/p1p9_multivarga_reranked.json")
