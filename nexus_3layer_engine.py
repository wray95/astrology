#!/usr/bin/env python3
"""
NEXUS 3-LAYER CAREER & WEALTH ENGINE
Layer 1: Planetary Archetype (Engine) — dominant planets by dignity
Layer 2: Routing Circuits (Houses + Nakshatra) — where energy discharges
Layer 3: Interaction Multipliers (Yogas × D9 × D10 × Shrinkhala)
"""
import swisseph as swe, json, os, math
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN = 360.0/27
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
VIM = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

# ============================================================
# ARCHETYPE MAPS
# ============================================================
PLANET_ARCHETYPES = {
    'Sun': ('Power/Authority', 'Executive & Leadership', 'Fire'),
    'Moon': ('Public Resonance', 'Creative & Mass Impact', 'Water'),
    'Mars': ('Execution/Action', 'Executive & Operations', 'Fire'),
    'Mercury': ('Logic/Data/Commerce', 'Systems & Analytics', 'Air'),
    'Jupiter': ('Wisdom/Expansion', 'Healing & Advisory', 'Ether'),
    'Venus': ('Aesthetics/Arts/Wealth', 'Creative & Media', 'Water'),
    'Saturn': ('Institutional Control', 'Engineering & Governance', 'Earth'),
    'Rahu': ('Innovation/Disruption', 'Tech & Mass Media', 'Air'),
    'Ketu': ('Research/Specialization', 'Healing & Deep Analysis', 'Fire'),
}

SIGN_MODALITY = {
    'Aries':'Fire','Taurus':'Earth','Gemini':'Air','Cancer':'Water',
    'Leo':'Fire','Virgo':'Earth','Libra':'Air','Scorpio':'Water',
    'Sagittarius':'Fire','Capricorn':'Earth','Aquarius':'Air','Pisces':'Water',
}

INDUSTRY_VECTORS = {
    'Executive & Leadership': ['Government','Politics','Military','Defense','Aerospace','Corporate Leadership','C-Suite'],
    'Systems & Analytics': ['Software','AI','Data Science','Engineering','Logistics','Finance','Quantitative Analytics'],
    'Creative & Media': ['Film','Music','Entertainment','Design','Architecture','Public Relations','Mass Communications'],
    'Healing & Advisory': ['Medicine','Surgery','Law','Ethics','Compliance','Philanthropy','Social Impact'],
    'Tech & Mass Media': ['Internet','Social Media','Blockchain','Venture Capital','Advertising','Broadcasting'],
}

WEALTH_VECTORS = {
    'Capital Accumulation': {'circuit': 'Shrinkhala + Dhana (2-9-11)', 'multiplier': 3.0},
    'Entrepreneurship': {'circuit': '7H + 11H + Mercury/Rahu', 'multiplier': 2.0},
    'Windfalls/Asymmetric': {'circuit': '8H + Rahu/Jupiter', 'multiplier': 2.5},
    'Institutional/Earned': {'circuit': '10L Kendra + Sasa/Ruchaka', 'multiplier': 2.0},
}

# ============================================================
# P1-P9 BIRTH DATA
# ============================================================
P_CHARTS = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"note":"⚠️ PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"note":"⚠️ Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5},
]

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l,(lon-s)/13.334
    return "Revati","Mercury",0

def dg(p,s):
    if p in EXALT and EXALT[p]==s: return 100
    if p in OWN and s in OWN[p]: return 75
    if p in DEBIL and DEBIL[p]==s: return -100
    return 0

def compute_d1(c):
    dt = datetime.strptime(f"{c['birthday']}T{c['birth_time']}","%Y-%m-%dT%H:%M:%S")
    dt = dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0]-ayan)%360
    asc_sign = SIGNS[int(asc_sid//30)]; asc_idx = int(asc_sid//30)
    planets = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt-ayan)%360; sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        planets[pn] = {"sidereal":round(sid,4),"sign":sgn,"sign_idx":si,"deg_in_sign":round(sid%30,4),"dignity":dg(pn,sgn),"nakshatra":nk,"nakshatra_lord":nl}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    for pn, rl in [("Rahu",rh),("Ketu",kh)]:
        sgn=SIGNS[int(rl//30)]; si=int(rl//30); nk,nl,_=gn(rl)
        planets[pn]={"sidereal":round(rl,4),"sign":sgn,"sign_idx":si,"deg_in_sign":round(rl%30,4),"dignity":0,"nakshatra":nk,"nakshatra_lord":nl}
    for pn in planets: planets[pn]["house"]=(planets[pn]["sign_idx"]-asc_idx)%12+1
    ms=planets["Moon"]["sidereal"]; ml=mn="?"; bal=0
    for n,s,l in NAKS:
        if s <= ms < s+NAK_SPAN:
            bal=VIM_YRS[l]*(1-(ms-s)/13.334); ml=l; mn=n; break
    return {"ascendant":{"sign":asc_sign,"deg":round(asc_sid%30,4),"sidereal":round(asc_sid,4)},"planets":planets,"moon_nakshatra":{"name":mn,"lord":ml,"balance_yrs":round(bal,2)},"birthday":c['birthday'],"birth_time":c['birth_time'],"tz":c['tz']}

def compute_varga(d1, division):
    p=d1['planets']; asc_sid=d1['ascendant']['sidereal']
    vp={}
    for pn in p: vlon=(p[pn]['sidereal']*division)%360; vp[pn]={"sign":SIGNS[int(vlon//30)],"sidereal":vlon}
    vl=SIGNS[int((asc_sid*division)%360//30)]; vli=SIGNS.index(vl)
    for pn in vp: vp[pn]['house']=(SIGNS.index(vp[pn]['sign'])-vli)%12+1
    return {"lagna":vl,"planets":vp}

def detect_shrinkhala(p):
    signs_of={pn: p[pn]['sign'] for pn in P7 if pn in p and p[pn].get('sign')}
    in_sign_of={}
    for pn, sign in signs_of.items():
        lord=SL.get(sign)
        if lord and lord!=pn: in_sign_of[pn]=lord
    all_loops=[]
    def dfs(start, current, path):
        if len(path)>7: return
        if current==start and len(path)>=2: all_loops.append(path[:]); return
        if current in path[:-1]: return
        nxt=in_sign_of.get(current)
        if nxt and nxt not in path[1:-1]: dfs(start,nxt,path+[nxt])
    for start in P7:
        if start in in_sign_of: dfs(start,in_sign_of[start],[start,in_sign_of[start]])
    unique=[]; seen=set()
    for loop in all_loops:
        mi=min(range(len(loop)),key=lambda i:loop[i])
        rot=tuple(loop[mi:]+loop[:mi])
        if rot not in seen: seen.add(rot); unique.append(list(rot))
    return unique

# ============================================================
# 3-LAYER ANALYSIS ENGINE
# ============================================================
def analyze_chart(d1, chart_meta):
    p = d1['planets']; asc = d1['ascendant']['sign']; ai = SIGNS.index(asc)
    houses = {h: SL[SIGNS[(ai+h-1)%12]] for h in range(1,13)}
    ll = houses[1]; h2l = houses[2]; h7l = houses[7]; h9l = houses[9]; h10l = houses[10]; h11l = houses[11]
    
    result = {'id': chart_meta.get('id','?'), 'name': chart_meta.get('name','?')}
    
    # ================================================================
    # LAYER 1: THE ENGINE — Planetary Archetypes (top 3 by dignity)
    # ================================================================
    planet_strengths = []
    for pn in P7:
        if pn not in p: continue
        dig = p[pn]['dignity']
        house = p[pn]['house']
        nak = p[pn]['nakshatra']
        sign = p[pn]['sign']
        modality = SIGN_MODALITY.get(sign,'?')
        archetype, domain, element = PLANET_ARCHETYPES.get(pn, ('?','?','?'))
        
        # Strength score: dignity + kendra bonus + own/exalt bonus
        score = abs(dig) + (5 if house in [1,4,7,10] else (3 if house in [5,9] else 1))
        if dig == 100: score += 10
        elif dig == 75: score += 7
        
        planet_strengths.append((pn, score, dig, house, sign, modality, nak, archetype, domain))
    
    planet_strengths.sort(key=lambda x: -x[1])
    top3 = planet_strengths[:3]
    
    result['layer1_engine'] = []
    for i, (pn, score, dig, house, sign, modality, nak, archetype, domain) in enumerate(top3, 1):
        digname = "EXALTED" if dig==100 else ("OWN" if dig==75 else ("DEBIL" if dig==-100 else "neutral"))
        result['layer1_engine'].append({
            'rank': i, 'planet': pn, 'score': score, 'dignity': digname,
            'sign': sign, 'modality': modality, 'house': house,
            'nakshatra': nak, 'archetype': archetype, 'domain': domain
        })
    
    # Dominant archetype from #1 engine
    result['dominant_archetype'] = top3[0][7] if top3 else 'Unknown'
    result['dominant_domain'] = top3[0][8] if top3 else 'Unknown'
    
    # ================================================================
    # LAYER 2: ROUTING CIRCUITS — Where does the energy discharge?
    # ================================================================
    circuits = []
    
    # 2H/11H Nexus: Wealth Generation
    wealth_planets = []
    for hnum in [2, 11]:
        lord = houses[hnum]
        if lord in p:
            wealth_planets.append((lord, hnum, p[lord]['house']))
    if wealth_planets or h2l in p or h11l in p:
        circuits.append({
            'circuit': 'Wealth Generation (2H-11H Nexus)',
            'mechanism': 'Capital accumulation through asset-gain circuit',
            'planets': [f"{lp}(L{hnum} in H{ph})" for lp, hnum, ph in wealth_planets],
            'strength': 'Strong' if len(wealth_planets) >= 2 else 'Moderate'
        })
    
    # 7H/10H Nexus: Public Commerce & Career
    career_planets = []
    for hnum in [7, 10]:
        lord = houses[hnum]
        if lord in p:
            career_planets.append((lord, hnum, p[lord]['house']))
    if career_planets:
        circuits.append({
            'circuit': 'Career & Public Commerce (7H-10H Nexus)',
            'mechanism': 'Public-facing career or business partnership channel',
            'planets': [f"{lp}(L{hnum} in H{ph})" for lp, hnum, ph in career_planets],
            'strength': 'Strong' if len(career_planets) >= 2 else 'Moderate'
        })
    
    # 3H/10H Nexus: Media/Communication
    comm_planets = [pn for pn in P7 if pn in p and p[pn]['house'] in [3, 10]]
    if comm_planets:
        circuits.append({
            'circuit': 'Media & Communication (3H-10H Nexus)',
            'mechanism': 'Expression, media, broadcasting, writing',
            'planets': [f"{pn}(H{p[pn]['house']})" for pn in comm_planets[:4]],
            'strength': 'Strong' if len(comm_planets) >= 3 else 'Moderate'
        })
    
    # 6H/10H Nexus: Service/Operations
    service_planets = [pn for pn in P7 if pn in p and p[pn]['house'] in [6, 10]]
    if service_planets:
        circuits.append({
            'circuit': 'Service & Operations (6H-10H Nexus)',
            'mechanism': 'Organizational execution, systems, health services',
            'planets': [f"{pn}(H{p[pn]['house']})" for pn in service_planets[:4]],
            'strength': 'Strong' if len(service_planets) >= 3 else 'Moderate'
        })
    
    result['layer2_circuits'] = circuits
    
    # ================================================================
    # LAYER 3: INTERACTION MULTIPLIERS
    # ================================================================
    multipliers = {}
    
    # Mahapurusha count
    mp_count = 0
    mp_list = []
    for pl, yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            mp_count += 1; mp_list.append(f"{yn}({pl} H{p[pl]['house']})")
    multipliers['mahapurusha_count'] = mp_count
    multipliers['mahapurusha_list'] = mp_list
    multipliers['mp_multiplier'] = mp_count * 4.0
    
    # Shrinkhala presence
    loops = detect_shrinkhala(p)
    multipliers['has_shrinkhala'] = len(loops) > 0
    multipliers['shrinkhala_count'] = len(loops)
    multipliers['shrinkhala_multiplier'] = 2.0 if len(loops) > 0 else 0
    
    # D10 10L position
    d10 = compute_varga(d1, 10); d10p = d10['planets']; d10i = SIGNS.index(d10['lagna'])
    d10_10l = SL[SIGNS[(d10i+9)%12]]
    d10_10l_house = d10p[d10_10l]['house'] if d10_10l in d10p else 0
    multipliers['d10_10l_house'] = d10_10l_house
    if d10_10l_house in [1,4,7,10]:
        multipliers['d10_10l_multiplier'] = 2.5
    elif d10_10l_house in [6,8,12]:
        multipliers['d10_10l_multiplier'] = -2.5
    else:
        multipliers['d10_10l_multiplier'] = 0
    
    # D9 Venus
    d9 = compute_varga(d1, 9); d9p = d9['planets']
    d9_venus_sign = d9p['Venus']['sign'] if 'Venus' in d9p else '?'
    multipliers['d9_venus'] = d9_venus_sign
    if d9_venus_sign in ['Taurus','Libra','Pisces']:
        multipliers['d9_venus_multiplier'] = 2.0
    elif d9_venus_sign == 'Virgo':
        multipliers['d9_venus_multiplier'] = -2.0
    else:
        multipliers['d9_venus_multiplier'] = 0
    
    # Raja yoga count
    raja = 0; seen = set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            kl = houses[kh]; cl = houses[ch]
            if kl == cl: continue
            key = tuple(sorted([kl, cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house'] == p[cl]['house']:
                seen.add(key); raja += 1
    multipliers['raja_count'] = raja
    
    # NBRY condition count
    nbr_max = 0
    for pl in P7:
        if pl not in p or p[pl]['dignity'] != -100: continue
        conds = 0
        dl = SL[DEBIL[pl]]
        if dl in p and p[dl]['house'] in [1,4,7,10]: conds += 1
        el = SL[EXALT[pl]]
        if el in p:
            eh, dh = p[el]['house'], p[pl]['house']
            if (eh+6)%12+1==dh or ((eh+4)%12+1==dh) or ((eh+7)%12+1==dh) or ((eh+8)%12+1==dh):
                conds += 1
        if p[pl]['house'] in [1,4,7,10]: conds += 1
        nbr_max = max(nbr_max, conds)
    multipliers['nbr_max_conds'] = nbr_max
    if nbr_max >= 4: multipliers['nbry_multiplier'] = 3.0
    elif nbr_max >= 2: multipliers['nbry_multiplier'] = 1.0
    else: multipliers['nbry_multiplier'] = 0
    
    # Composite score
    result['layer3_multipliers'] = multipliers
    result['composite_wealth_score'] = round(
        multipliers['mp_multiplier'] + multipliers['shrinkhala_multiplier'] +
        multipliers['d10_10l_multiplier'] + multipliers['d9_venus_multiplier'] +
        raja * 1.0 + multipliers['nbry_multiplier'], 1
    )
    
    # ================================================================
    # CAREER & WEALTH PREDICTION
    # ================================================================
    # Dominant archetype → industries
    predicted_industries = []
    dom_domain = result['dominant_domain']
    for domain, industries in INDUSTRY_VECTORS.items():
        if domain == dom_domain or any(pn['archetype'] == domain for pn in result['layer1_engine'][:2]):
            predicted_industries.extend(industries[:3])
    result['predicted_industries'] = list(set(predicted_industries))[:4]
    
    # Wealth mechanism
    wealth_mechanisms = []
    # Check Shrinkhala + Dhana
    if multipliers['has_shrinkhala'] and any('2H' in str(c) for c in circuits if 'Wealth' in c.get('circuit','')):
        wealth_mechanisms.append(('Capital Accumulation & Scale', 3.0))
    # Check 7H + 11H
    if any('7H' in str(c) for c in circuits) and any('11H' in str(c) for c in circuits):
        wealth_mechanisms.append(('Entrepreneurship & Commerce', 2.0))
    # Check 8H
    for pn in ['Rahu','Jupiter']:
        if pn in p and p[pn]['house'] == 8:
            wealth_mechanisms.append(('Windfalls & Asymmetric Gains', 2.5))
            break
    # Check 10L kendra
    if d10_10l_house in [1,4,7,10]:
        wealth_mechanisms.append(('Institutional / Earned Wealth', 2.0))
    
    # If no mechanism, infer from top circuits
    if not wealth_mechanisms:
        for c in circuits:
            if 'Wealth' in c.get('circuit',''):
                wealth_mechanisms.append(('Capital Accumulation', 1.5))
                break
    
    result['wealth_mechanisms'] = wealth_mechanisms
    
    return result

# ============================================================
# RUN P1-P9
# ============================================================
print("="*100)
print("NEXUS 3-LAYER CAREER & WEALTH ENGINE")
print("="*100)

results = []
for c in P_CHARTS:
    d1 = compute_d1(c)
    d1['name'] = c['name']; d1['id'] = c['id']; d1['note'] = c.get('note','')
    analysis = analyze_chart(d1, c)
    results.append(analysis)

results.sort(key=lambda x: -x['composite_wealth_score'])

for i, r in enumerate(results, 1):
    tier = '(REF ONLY)' if any(n in r['name'] for n in ['Upulakshi','Sineth']) else ''
    print(f"\n{'='*100}")
    print(f"#{i} {r['id']} {r['name']} — Composite Wealth Score: {r['composite_wealth_score']} {tier}")
    print(f"{'='*100}")
    
    # Layer 1
    print(f"\n  LAYER 1: THE ENGINE")
    for e in r['layer1_engine']:
        print(f"    #{e['rank']} {e['planet']:<10} {e['dignity']:<10} {e['sign']:<12} {e['modality']:<8} H{e['house']:<4} {e['nakshatra']:<16} → {e['archetype']}")
    print(f"  Dominant Archetype: {r['dominant_archetype']} → {r['dominant_domain']}")
    
    # Layer 2
    print(f"\n  LAYER 2: ROUTING CIRCUITS")
    for c in r['layer2_circuits']:
        print(f"    [{c['strength']}] {c['circuit']}")
        print(f"    {c['mechanism']}")
        print(f"    Planets: {', '.join(c['planets'])}")
    
    # Layer 3
    m = r['layer3_multipliers']
    print(f"\n  LAYER 3: INTERACTION MULTIPLIERS")
    print(f"    Mahapurusha: {m['mahapurusha_count']} ({', '.join(m['mahapurusha_list']) if m['mahapurusha_list'] else 'none'}) × +{m['mp_multiplier']:.0f}")
    print(f"    Shrinkhala:  {'✓' if m['has_shrinkhala'] else '✗'} ({m['shrinkhala_count']} loops) × {m['shrinkhala_multiplier']:+.0f}")
    print(f"    D10 10L:     H{m['d10_10l_house']} × {m['d10_10l_multiplier']:+.1f}")
    print(f"    D9 Venus:    {m['d9_venus']} × {m['d9_venus_multiplier']:+.1f}")
    print(f"    Raja Yogas:  {m['raja_count']} × +1.0")
    print(f"    NBRY (max):  {m['nbr_max_conds']} conditions × {m['nbry_multiplier']:+.1f}")
    
    # Prediction
    print(f"\n  PREDICTED INDUSTRIES: {', '.join(r['predicted_industries']) if r['predicted_industries'] else 'No clear routing — check D9/D10'}")
    print(f"  WEALTH MECHANISM:")
    for mech, weight in r['wealth_mechanisms']:
        print(f"    {mech} (weight={weight})")

# Save
with open('dataset/p1p9_3layer_analysis.json','w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved → dataset/p1p9_3layer_analysis.json")
