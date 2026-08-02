#!/usr/bin/env python3
"""
ALL-PLANET EVENT PREDICTION ENGINE
Matches biography events to Saturn/Jupiter/Rahu transits + retrogrades
Extends to all planets in Q-series
"""
import csv, json
from collections import Counter, defaultdict
from datetime import datetime

print("="*100)
print("ALL-PLANET EVENT-BIOGRAPHY MATCH & PREDICTION ENGINE")
print("="*100)

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
# Saturn transit screen (biography events with transit data)
with open('outputs/saturn_transit_event_screen.csv') as f:
    saturn_events = list(csv.DictReader(f))

# Saturn same-sign passages (45,657 records)
with open('outputs/saturn_same_sign_passages/all_passages.csv') as f:
    passages = list(csv.DictReader(f))

# Q-series returns
with open('outputs/saturn_returns_q_series/q_saturn_returns.csv') as f:
    q_returns = list(csv.DictReader(f))

# Q-series events with movements
with open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv') as f:
    q_events = list(csv.DictReader(f))

# All planet positions
with open('outputs/all_planets_q_series/q_all_planet_positions.csv') as f:
    q_planets_all = list(csv.DictReader(f))

# 200 biographies
with open('outputs/requested_200_biographies/biographies_200.json') as f:
    bios = json.load(f)

print(f"Loaded: {len(saturn_events)} Saturn-screened events | {len(passages):,} same-sign passages | {len(q_returns):,} Q returns | {len(q_events):,} Q events | {len(q_planets_all):,} all-planet records | {len(bios)} biographies")

# ============================================================
# 2. SATURN TRANSIT SCREEN — EVENT ANALYSIS
# ============================================================
print(f"\n{'='*100}")
print("SATURN TRANSIT EVENT SCREEN — 11 Biography Events")
print('='*100)

for ev in saturn_events:
    name = ev['name']
    event_date = ev['event_date']
    event_type = ev['event_type']
    event_desc = ev['event_description']
    sat_sign = ev['saturn_sign']
    sat_deg = float(ev['saturn_degree'])
    sat_retro = ev['saturn_retrograde_midpoint']
    md = ev.get('ruling_mahadasha','?')
    ad = ev.get('ruling_antardasha','?')
    
    print(f"\n  {name} — {event_date}")
    print(f"    Event: {event_type} — {event_desc}")
    print(f"    Saturn: {sat_sign} {sat_deg:.1f}° | Retrograde: {sat_retro} | Dasha: {md}/{ad}")

# ============================================================
# 3. SATURN EVENT PATTERN SUMMARY
# ============================================================
print(f"\n{'='*100}")
print("SATURN PATTERN SUMMARY — What Saturn Sign/Retrograde Correlates With What Event")
print('='*100)

# By event type
event_saturn = defaultdict(list)
for ev in saturn_events:
    event_saturn[ev['event_type']].append({
        'sign': ev['saturn_sign'],
        'retro': ev['saturn_retrograde_midpoint'],
        'person': ev['name'],
        'date': ev['event_date'],
    })

for ev_type, evs in event_saturn.items():
    signs = Counter(e['sign'] for e in evs)
    retros = sum(1 for e in evs if e['retro'] == 'True')
    print(f"\n  {ev_type} ({len(evs)} events):")
    print(f"    Saturn signs: {dict(signs)}")
    print(f"    Saturn retrograde: {retros}/{len(evs)} ({retros/len(evs)*100:.0f}%)")
    print(f"    People: {', '.join(e['person'] for e in evs)}")

# ============================================================
# 4. P1-P9 PREDICTION USING SATURN WINDOW DATA
# ============================================================
print(f"\n{'='*100}")
print("P1-P9 PREDICTION — Match Saturn Windows Against Q-Series Patterns")
print('='*100)

# P1-P9 Saturn data from earlier computation
p_saturns = {
    'P1': {'name': 'Polgahawela Bappa', 'natal_saturn': 'Capricorn', 'birth_year': 1962},
    'P2': {'name': 'Upulakshi', 'natal_saturn': 'Pisces', 'birth_year': 1997},
    'P3': {'name': 'Senith', 'natal_saturn': 'Pisces', 'birth_year': 1995},
    'P4': {'name': 'Niromi', 'natal_saturn': 'Pisces', 'birth_year': 1967},
    'P5': {'name': 'Senath', 'natal_saturn': 'Taurus', 'birth_year': 2001},
    'P6': {'name': 'Dewli', 'natal_saturn': 'Cancer', 'birth_year': 2005},
    'P7': {'name': 'Sineth', 'natal_saturn': 'Gemini', 'birth_year': 2005},
    'P8': {'name': 'Lakshi Amma', 'natal_saturn': 'Capricorn', 'birth_year': 1963},
    'P9': {'name': 'Lalith Uncle', 'natal_saturn': 'Aries', 'birth_year': 1970},
}

# Build Q-series passage lookup by person
passage_by_person = defaultdict(list)
for p in passages:
    passage_by_person[p['person_id']].append(p)

for pid, pdata in p_saturns.items():
    ns = pdata['natal_saturn']
    by = pdata['birth_year']
    
    # Saturn return years
    sat_return_1 = by + 29
    sat_return_2 = by + 59
    
    # Find Q-series people with same natal Saturn and find their passage patterns
    same_sat_q = [r for r in q_returns if r['natal_saturn_sign'] == ns]
    
    # Career events during Saturn return for same-sign people
    career_at_return = 0
    for qr in same_sat_q[:100]:
        qid = qr['q_id']
        if qid in passage_by_person:
            for psg in passage_by_person[qid][:10]:
                # Check if any event near these passage dates
                for ev in q_events:
                    if ev['q_id'] == qid:
                        try:
                            ev_year = int(ev['event_date'][:4])
                            psg_year = int(psg['saturn_ingress'][:4]) if psg['saturn_ingress'] else 0
                            if abs(ev_year - psg_year) <= 2 and 'career' in ev.get('event_type',''):
                                career_at_return += 1
                        except: pass
    
    print(f"\n  {pid} {pdata['name']} — Saturn {ns}")
    print(f"    1st Return: ~{sat_return_1} | 2nd Return: ~{sat_return_2}")
    print(f"    Q-series same-sign: {len(same_sat_q)} people")
    print(f"    Predicted: career shift at Saturn return (same-sign Q career events near passage: {career_at_return})")

# ============================================================
# 5. ALL-PLANET CROSS-REFERENCE
# ============================================================
print(f"\n{'='*100}")
print("ALL-PLANET EVENT CROSS-REFERENCE — Jupiter, Mars, Venus, Rahu at Events")
print('='*100)

# For each of the 11 Saturn-screened events, what were the other planets doing?
PLANETS = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Rahu_mean']
for ev in saturn_events:
    name = ev['name']
    event_date = ev['event_date']
    event_type = ev['event_type']
    
    # Find matching event in q_events by date
    matching = [qe for qe in q_events if qe.get('event_date') == event_date]
    
    print(f"\n  {name} — {event_date} ({event_type})")
    print(f"    Saturn: {ev['saturn_sign']} {float(ev['saturn_degree']):.1f}° | Retro: {ev['saturn_retrograde_midpoint']}")
    
    # Other planets at event date (from all-planets Q data)
    for qp in q_planets_all[:50]:
        # Match by name or birth date
        if qp.get('name','').lower() in name.lower():
            for pl in PLANETS:
                pl_sign = qp.get(f'{pl}_sign','?')
                pl_retro = qp.get(f'{pl}_retrograde','?')
                if pl_sign != '?':
                    retro_tag = '⟲' if pl_retro.lower() == 'true' else ''
                    print(f"    {pl:<12} {pl_sign:<12} {retro_tag}")

# ============================================================
# 6. COUNTS & SAVE
# ============================================================
print(f"\n{'='*100}")
print("DATASET INVENTORY")
print('='*100)
print(f"  Saturn-screened biography events: {len(saturn_events)}")
print(f"  Saturn same-sign passages: {len(passages):,}")
print(f"  Q-series returns (5,010): {len(q_returns):,}")
print(f"  Q-series events with movements: {len(q_events):,}")
print(f"  All-planet positions (Q-series): {len(q_planets_all):,}")
print(f"  200 biographies: {len(bios)}")

# Save cross-reference
with open('outputs/all_planet_event_prediction.json','w') as f:
    json.dump({
        'saturn_screened_events': len(saturn_events),
        'saturn_patterns': {et: {
            'count': len(evs),
            'signs': dict(Counter(e['sign'] for e in evs)),
            'retro_rate': sum(1 for e in evs if e['retro']=='True')/max(len(evs),1)
        } for et, evs in event_saturn.items()},
        'p_predictions': {pid: {
            'natal_saturn': pdata['natal_saturn'],
            'first_return': pdata['birth_year']+29,
            'second_return': pdata['birth_year']+59,
        } for pid, pdata in p_saturns.items()},
    }, f, indent=2)
print(f"\nSaved → outputs/all_planet_event_prediction.json")
