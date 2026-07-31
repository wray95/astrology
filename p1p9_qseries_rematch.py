#!/usr/bin/env python3
"""P1-P9 REMATCHED AGAINST 5,000 Q-SERIES BIRTHDAYS"""
import swisseph as swe, csv, json
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

P_CHARTS = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"note":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"note":"Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5},
]

def compute_p_planets(c):
    dt=datetime.strptime(f"{c['birthday']}T{c['birth_time']}","%Y-%m-%dT%H:%M:%S")
    dt=dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    asc_trop,_=swe.houses_ex(jd,c['lat'],c['lon'],b'A')
    ayan=swe.get_ayanamsa(jd)
    asc_sid=(asc_trop[0]-ayan)%360; asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    planets={}
    for pn,pid in PLANETS_MAP.items():
        lt,_=swe.calc_ut(jd,pid); lt=lt[0]
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30)
        dig=100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
        planets[pn]={"sign":sgn,"sign_idx":si,"dignity":dig,"house":(si-asc_idx)%12+1}
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360
    planets["Rahu"]={"sign":SIGNS[int(rh//30)],"house":(int(rh//30)-asc_idx)%12+1}
    return {"asc":asc_sign,"id":c['id'],"name":c['name'],"note":c.get('note',''),"planets":planets}

# Compute P1-P9
p_charts = [compute_p_planets(c) for c in P_CHARTS]

# Load Q-series
with open('outputs/saturn_returns_q_series/q_saturn_returns.csv') as f:
    q_data = list(csv.DictReader(f))

# Load all planet positions for Q-series
with open('outputs/all_planets_q_series/q_all_planet_positions.csv') as f:
    q_planets = list(csv.DictReader(f))

q_lookup = {r['q_id']: r for r in q_planets}

print("="*110)
print("P1-P9 REMATCHED AGAINST 5,000 Q-SERIES BIRTHDAYS")
print("="*110)
print(f"P-charts: {len(p_charts)} | Q-series: {len(q_data):,} records, {len(set(r['name'] for r in q_data)):,} unique names")
print(f"Q-series with full planet data: {len(q_planets):,}")

# For each P-chart, find closest Q-series matches
print(f"\n{'='*110}")
print("P-CHART → Q-SERIES MATCHES (closest Saturn + planet-sign overlap)")
print("="*110)

for pc in p_charts:
    pid = pc['id']
    pname = pc['name']
    psat = pc['planets']['Saturn']['sign']
    
    # Find Q-series with same Saturn sign
    same_sat = [r for r in q_data if r['natal_saturn_sign'] == psat]
    
    # Find closest Saturn degree match
    sat_deg = pc['planets']['Saturn'].get('sidereal', 0) % 30 if 'sidereal' in pc['planets']['Saturn'] else 0
    
    # Find exact birthday match
    exact_match = [r for r in q_data if r['birth_date'] == pc.get('birthday','')]
    
    # Now do full planet-sign overlap
    best_matches = []
    for qr in q_data[:500]:  # Sample first 500 for speed
        qid = qr['q_id']
        if qid not in q_lookup: continue
        qp = q_lookup[qid]
        overlap = 0
        for pn in P7:
            p_sign = pc['planets'][pn]['sign']
            q_sign = qp.get(f'{pn}_sign','?')
            if p_sign == q_sign: overlap += 1
        if overlap >= 3:
            best_matches.append((qr['name'], overlap, qr['natal_saturn_sign'], qr.get('occupation','?')))
    
    best_matches.sort(key=lambda x: -x[1])
    
    tier = "[REF ONLY]" if pc.get('note') else ""
    print(f"\n{pid} {pname} {tier}")
    print(f"  Natal Saturn: {psat} | Q-series same-sign: {len(same_sat):,} people")
    if exact_match:
        print(f"  ★ EXACT BIRTHDAY MATCH in Q-series: {exact_match[0]['name']} ({exact_match[0].get('occupation','?')})")
    
    # Top 5 planet-sign matches
    top5 = best_matches[:5]
    if top5:
        print(f"  Top planet-sign overlaps (≥3 signs):")
        for name, ov, ns, occ in top5:
            print(f"    {name:<30} {ov}/7 signs | Saturn:{ns} | {occ[:50]}")
    
    # Q-series career distribution for same Saturn sign
    careers = Counter(r.get('occupation','?') for r in same_sat if r.get('occupation'))
    top_careers = careers.most_common(5)
    if top_careers:
        print(f"  Q-series careers with Saturn in {psat}:")
        for occ, n in top_careers:
            print(f"    {occ[:55]:<55} {n}")

# Cross-reference: P-chart career prediction vs Q-series Saturn-sign career distribution
print(f"\n{'='*110}")
print("CAREER PREDICTION CROSS-REFERENCE")
print("="*110)

for pc in p_charts:
    pid = pc['id']
    psat = pc['planets']['Saturn']['sign']
    same_sat = [r for r in q_data if r['natal_saturn_sign'] == psat and r.get('occupation')]
    
    # Occupations of Q-series with same Saturn sign
    occs = Counter(r['occupation'] for r in same_sat)
    
    print(f"\n{pid} {pc['name']} — Saturn in {psat}")
    print(f"  Q-series sample: {len(same_sat):,} people share this Saturn sign")
    print(f"  Top occupations: {', '.join(f'{o}({n})' for o,n in occs.most_common(5))}")

# Save
with open('outputs/p1p9_q_series_rematch.json','w') as f:
    json.dump({
        'p_charts': [{'id':pc['id'],'name':pc['name'],'saturn':pc['planets']['Saturn']['sign']} for pc in p_charts],
        'q_series_total': len(q_data),
    }, f, indent=2)
print(f"\nSaved → outputs/p1p9_q_series_rematch.json")
