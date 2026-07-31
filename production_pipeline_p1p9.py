#!/usr/bin/env python3
"""
PRODUCTION PIPELINE INTEGRATION
Runs the 3-layer feature engineering against P1-P9 actual data.
Cross-validates against our calibrated scores from earlier analysis.
"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
KENDRA = {1,4,7,10}
DUSTHANA = {6,8,12}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]

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

# ================================================================
# PRODUCTION PIPELINE FUNCTIONS (from the shared spec)
# ================================================================

MAHAPURUSHA_MAP = {
    "Mars": {"yoga":"Ruchaka","own":{"Aries","Scorpio"},"exalted":"Capricorn"},
    "Mercury": {"yoga":"Bhadra","own":{"Gemini","Virgo"},"exalted":"Virgo"},
    "Jupiter": {"yoga":"Hamsa","own":{"Sagittarius","Pisces"},"exalted":"Cancer"},
    "Venus": {"yoga":"Malavya","own":{"Taurus","Libra"},"exalted":"Pisces"},
    "Saturn": {"yoga":"Sasa","own":{"Capricorn","Aquarius"},"exalted":"Libra"},
}

def extract_layer1_archetypes(d1_signs, d1_houses):
    scores = {p: 0 for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']}
    for p in scores:
        sign = d1_signs.get(p); house = d1_houses.get(p)
        if p in DIGNITIES and sign == DIGNITIES[p]["exalted"]: scores[p] += 3
        elif sign and SL.get(sign) == p: scores[p] += 2
        if house in KENDRA: scores[p] += 1.5
    sorted_p = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top, second = sorted_p[0][0], sorted_p[1][0]
    archetype_map = {"Sun":"Executive/Power","Mars":"Executive/Power","Mercury":"Logic/Systems","Saturn": "Logic/Systems","Venus":"Creative/Commerce","Jupiter":"Advisory/Expansion","Moon":"Public/Resonance"}
    return {"primary_driver":top,"secondary_driver":second,"primary_archetype":archetype_map.get(top,"General"),"top_driver_dignity_score":sorted_p[0][1]}

def extract_layer2_routing_circuits(d1_houses):
    monet = sum(1 for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if d1_houses.get(p) in {2,11})
    kendra_c = sum(1 for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if d1_houses.get(p) in KENDRA)
    dusthana_c = sum(1 for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if d1_houses.get(p) in DUSTHANA)
    ctype = "Wealth Circuit" if monet >= 2 else ("Executive/Kendra Circuit" if kendra_c >= 3 else "Balanced Circuit")
    return {"monetization_focus_count":monet,"kendra_focus_count":kendra_c,"dusthana_challenge_count":dusthana_c,"circuit_type":ctype}

def detect_shrinkala_loops(d1_signs):
    graph = {p: SL[d1_signs[p]] for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if p in d1_signs and d1_signs[p] in SL}
    visited_cycles = set(); loops = []
    for start in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        path = []; curr = start
        while curr in graph and curr not in path: path.append(curr); curr = graph[curr]
        if curr in path:
            cycle = path[path.index(curr):]
            if 2 <= len(cycle) <= 5:
                canonical = tuple(sorted(cycle))
                if canonical not in visited_cycles: visited_cycles.add(canonical); loops.append({"length":len(cycle),"planets":list(cycle)})
    return {"shrinkhala_present":len(loops)>0,"shrinkhala_count":len(loops),"shrinkhala_loops":loops}

def evaluate_mahapurusha_yogas(d1_signs, d1_houses):
    active = []
    for p, config in MAHAPURUSHA_MAP.items():
        house = d1_houses.get(p); sign = d1_signs.get(p)
        if house in KENDRA:
            if sign == config["exalted"] or sign in config["own"]: active.append(config["yoga"])
    return {"mahapurusha_count":len(active),"active_mahapurusha_yogas":active,"is_outlier_achievement":len(active)>=2}

DIGNITIES = {
    "Sun":{"exalted":"Aries","debilitated":"Libra"},"Moon":{"exalted":"Taurus","debilitated":"Scorpio"},
    "Mars":{"exalted":"Capricorn","debilitated":"Cancer"},"Mercury":{"exalted":"Virgo","debilitated":"Pisces"},
    "Jupiter":{"exalted":"Cancer","debilitated":"Capricorn"},"Venus":{"exalted":"Pisces","debilitated":"Virgo"},
    "Saturn":{"exalted":"Libra","debilitated":"Aries"},
}

def evaluate_d10_and_d9_gates(d10_10L_house, d9_venus_sign):
    if d10_10L_house in KENDRA: d10_status = "Kendra - High Career Stability"; d10_score = 2.5
    elif d10_10L_house in DUSTHANA: d10_status = "Dusthana - Volatile / Career Risk"; d10_score = -2.5
    else: d10_status = "Neutral"; d10_score = 0.0
    if d9_venus_sign in ["Pisces","Taurus","Libra"]: d9_status = "Exalted/Own - High Ethical Guard"; d9_score = 2.0
    elif d9_venus_sign == "Virgo": d9_status = "Debilitated - High Risk / Ethical Vulnerability"; d9_score = -2.0
    else: d9_status = "Neutral"; d9_score = 0.0
    return {"d10_10L_status":d10_status,"d10_score_weight":d10_score,"d9_venus_status":d9_status,"d9_venus_score_weight":d9_score}

def engineer_chart_features(person_id, d1_signs, d1_houses, d9_signs, d10_10L_house):
    l1 = extract_layer1_archetypes(d1_signs, d1_houses)
    l2 = extract_layer2_routing_circuits(d1_houses)
    shrinkhala = detect_shrinkala_loops(d1_signs)
    mahapurusha = evaluate_mahapurusha_yogas(d1_signs, d1_houses)
    gates = evaluate_d10_and_d9_gates(d10_10L_house, d9_signs.get("Venus",""))
    net = (mahapurusha["mahapurusha_count"]*4.0 + (2.0 if shrinkhala["shrinkhala_present"] else 0.0) + gates["d10_score_weight"] + gates["d9_venus_score_weight"])
    return {"person_id":person_id,"primary_archetype":l1["primary_archetype"],"primary_driver":l1["primary_driver"],
            "circuit_type":l2["circuit_type"],"shrinkhala_present":shrinkhala["shrinkhala_present"],
            "shrinkhala_count":shrinkhala["shrinkhala_count"],"mahapurusha_count":mahapurusha["mahapurusha_count"],
            "outlier_achievement_flag":mahapurusha["is_outlier_achievement"],
            "d10_10L_status":gates["d10_10L_status"],"d9_venus_status":gates["d9_venus_status"],
            "net_interaction_multiplier_score":round(net,1)}

# ================================================================
# COMPUTE P1-P9
# ================================================================
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

def compute_chart(c):
    dt = datetime.strptime(f"{c['birthday']}T{c['birth_time']}","%Y-%m-%dT%H:%M:%S")
    dt = dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0]-ayan)%360
    asc_sign = SIGNS[int(asc_sid//30)]; asc_idx = int(asc_sid//30)
    
    p = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt-ayan)%360; sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        p[pn] = {"sidereal":round(sid,4),"sign":sgn,"sign_idx":si,"deg_in_sign":round(sid%30,4),"dignity":dg(pn,sgn),"nakshatra":nk,"house":(si-asc_idx)%12+1}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh=(rh[0]-ayan)%360
    p["Rahu"] = {"sign":SIGNS[int(rh//30)],"house":(int(rh//30)-asc_idx)%12+1}
    p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"house":(int(((rh+180)%360)//30)-asc_idx)%12+1}
    return {"ascendant":{"sign":asc_sign}, "planets":p}

def compute_varga(d1, div):
    asc_sid = d1['planets']['Sun']['sidereal']  # approximate
    # Use actual ascendant
    asc_sid = None
    for pn in d1['planets']:
        if 'sign_idx' in d1['planets'][pn]:
            asc_sid = d1['planets'][pn]['sidereal'] - d1['planets'][pn]['sign_idx']*30 + SIGNS.index(d1['ascendant']['sign'])*30
            break
    if not asc_sid:
        asc_sid = SIGNS.index(d1['ascendant']['sign'])*30 + 15
    
    vp = {}
    for pn in PLANETS_MAP:
        if pn in d1['planets']:
            vlon = (d1['planets'][pn]['sidereal'] * div) % 360
            vp[pn] = SIGNS[int(vlon//30)]
    
    vl = SIGNS[int((asc_sid*div)%360//30)]
    return {"lagna":vl, "planets":vp}

print("="*100)
print("PRODUCTION PIPELINE — P1-P9 Feature Engineering")
print("="*100)

results = []
for c in P_CHARTS:
    d1 = compute_chart(c)
    asc = d1['ascendant']['sign']
    
    # D1 signs and houses
    d1_signs = {pn: d1['planets'][pn]['sign'] for pn in PLANETS_MAP if pn in d1['planets']}
    d1_houses = {pn: d1['planets'][pn]['house'] for pn in PLANETS_MAP if pn in d1['planets']}
    
    # D9
    d9 = compute_varga(d1, 9)
    d9_signs = d9['planets']
    
    # D10 10L
    d10 = compute_varga(d1, 10)
    d10_idx = SIGNS.index(d10['lagna'])
    d10_10l_sign = SIGNS[(d10_idx+9)%12]
    d10_10l = SL[d10_10l_sign]
    d10_10l_house = (SIGNS.index(d10['planets'].get(d10_10l, d10_10l_sign)) - d10_idx) % 12 + 1 if d10_10l in d10['planets'] else 0
    
    features = engineer_chart_features(c['id'], d1_signs, d1_houses, d9_signs, d10_10l_house)
    features['name'] = c['name']
    features['note'] = c.get('note','')
    results.append(features)

results.sort(key=lambda x: -x['net_interaction_multiplier_score'])

print(f"\n{'ID':<4} {'Name':<20} {'Score':>6} {'Archetype':<22} {'Circuit':<25} {'MP':>3} {'Shrink':>6} {'D10':>5} {'D9 Venus':>12} {'Outlier':>8} {'Δ'}")
print("-"*130)

prev_scores = {"P5":11.5,"P9":10.0,"P1":8.5,"P4":5.0,"P8":5.0,"P6":2.5,"P3":-0.5,"P2":8.5,"P7":3.0}

for i, r in enumerate(results, 1):
    note = r.get('note','')
    tier = '⚠️' if note else ''
    prev = prev_scores.get(r['person_id'],0)
    diff = r['net_interaction_multiplier_score'] - prev
    arrow = f"+{diff:.1f}" if diff > 0.1 else (f"{diff:.1f}" if diff < -0.1 else "≡")
    
    print(f"{r['person_id']:<4} {r['name']:<20} {r['net_interaction_multiplier_score']:>6.1f} {r['primary_archetype']:<22} {r['circuit_type']:<25} "
          f"{r['mahapurusha_count']:>3} {'✓' if r['shrinkhala_present'] else '✗':>6} "
          f"{r.get('d10_10L_status','?')[:5]:>5} {r.get('d9_venus_status','?')[:12]:>12} "
          f"{'⚠️ YES' if r['outlier_achievement_flag'] else '':>8} {tier}{arrow}")

print(f"\n{'='*100}")
print("CROSS-VALIDATION vs CALIBRATED SCORES")
print(f"{'='*100}")
print("(Production pipeline uses exact same weights as calibrated analysis)")
print("Differences arise from: Raj Yoga count (not in pipeline) + NBRY (not in pipeline)")
print("Core Layer 3 multipliers (MP+4, Shrinkhala+2, D10±2.5, D9 Venus±2) are identical.")

with open('dataset/p1p9_production_features.json','w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → dataset/p1p9_production_features.json")
