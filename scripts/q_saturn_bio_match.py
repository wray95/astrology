#!/usr/bin/env python3
"""Q-Series Saturn-Biography Year-by-Year Match"""
import csv, json
from collections import Counter, defaultdict

with open('outputs/saturn_returns_q_series/q_saturn_returns.csv') as f:
    q = list(csv.DictReader(f))
with open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv') as f:
    events = list(csv.DictReader(f))
with open('outputs/requested_200_biographies/biographies_200.json') as f:
    bios = json.load(f)

print('='*85)
print(f'Q-SERIES SATURN-BIOGRAPHY YEAR-BY-YEAR MATCH')
print('='*85)
print(f'People: {len(q):,} | Events: {len(events):,} | Biographies: {len(bios)}')

# Build lookups
q_lookup = {r['q_id']: r for r in q}
saturn_events = defaultdict(list)
for ev in events:
    saturn_events[ev['q_id']].append(ev)

# TOP PEOPLE BY EVENT COUNT
print(f'\n{"="*85}')
print('TOP 25 PEOPLE — SATURN TRANSIT EVENTS')
print('='*85)
top = sorted(saturn_events.items(), key=lambda x:-len(x[1]))[:25]
for i,(qid,evs) in enumerate(top,1):
    r = q_lookup.get(qid,{})
    name = r.get('name','?')
    natal_sat = r.get('natal_saturn_sign','?')
    by = int(r.get('birth_date','0')[:4]) if r.get('birth_date') else 0
    ev_types = Counter(e['event_type'] for e in evs)
    print(f'{i:>2}. {name:<35} Sat:{natal_sat:<12} Born:{by} Events:{len(evs)}')
    for t,n in ev_types.most_common(3):
        print(f'    {t}: {n}')

# SATURN SIGN → EVENT DENSITY
print(f'\n{"="*85}')
print('SATURN SIGN → EVENT DENSITY')
print('='*85)
sign_events = defaultdict(list)
sign_count = Counter()
for r in q:
    ns = r['natal_saturn_sign']
    sign_count[ns] += 1
    qid = r['q_id']
    if qid in saturn_events:
        sign_events[ns].extend(saturn_events[qid])

for sign in sorted(sign_count.keys(), key=lambda s:-sign_count[s]):
    n_people = sign_count[sign]
    n_events = len(sign_events[sign])
    rate = n_events / n_people if n_people > 0 else 0
    bar = 'X' * int(rate * 5)
    print(f'  {sign:<12} People:{n_people:>4} Events:{n_events:>4} Rate:{rate:.2f}/person {bar}')

# SATURN RETURN — EVENT PEAKS
print(f'\n{"="*85}')
print('SATURN RETURN — EVENT PEAKS (+/-2yr window)')
print('='*85)
return_events = defaultdict(list)
for r in q:
    by = int(r['birth_date'][:4])
    qid = r['q_id']
    for age, label in [(29,'1st Return'), (59,'2nd Return'), (89,'3rd Return')]:
        ry = by + age
        if qid in saturn_events:
            for ev in saturn_events[qid]:
                ey = int(ev['event_date'][:4])
                if abs(ey - ry) <= 2:
                    return_events[label].append(ev)

for label in ['1st Return','2nd Return','3rd Return']:
    evs = return_events[label]
    print(f'  {label} (age ~29/59/89): {len(evs)} events')
    if evs:
        types = Counter(e['event_type'] for e in evs)
        for t,n in types.most_common():
            print(f'    {t}: {n}')

# YEAR-BY-YEAR: Saturn sign passages
print(f'\n{"="*85}')
print('YEAR-BY-YEAR: Saturn transit sign vs event frequency')
print('='*85)
year_sign_events = defaultdict(Counter)
for ev in events:
    ey = int(ev['event_date'][:4])
    sat_sign = ev.get('saturn_sign','?')
    if sat_sign != '?':
        year_sign_events[ey][sat_sign] += 1

# Peak years
peak_years = sorted(year_sign_events.items(), key=lambda x:-sum(x[1].values()))[:15]
for y, signs in peak_years:
    total = sum(signs.values())
    top_sign = signs.most_common(1)[0] if signs else ('?',0)
    print(f'  {y}: {total:>4} events — Top sign: {top_sign[0]} ({top_sign[1]})')

# BIOGRAPHY MATCH
print(f'\n{"="*85}')
print('200 BIOGRAPHIES — Saturn Sign Distribution')
print('='*85)
bio_saturn = defaultdict(list)
for b in bios:
    bname = b.get('name','')
    for r in q:
        if r.get('name','').lower() == bname.lower():
            bio_saturn[r['natal_saturn_sign']].append(b)
            break

for sign in sorted(bio_saturn.keys()):
    names = [b.get('name','?')[:25] for b in bio_saturn[sign][:4]]
    print(f'  {sign:<12}: {len(bio_saturn[sign])} bios — {", ".join(names)}')

# SAVE
with open('outputs/q_saturn_biography_match.json','w') as f:
    json.dump({
        'total_people': len(q), 'total_events': len(events), 'total_bios': len(bios),
        'top_people': [(q_lookup.get(qid,{}).get('name','?'), len(evs)) for qid,evs in top],
        'sign_event_rates': {s: round(len(sign_events[s])/max(sign_count[s],1),2) for s in sign_count},
        'return_events': {k: len(v) for k,v in return_events.items()},
    }, f, indent=2)
print(f'\nSaved to outputs/q_saturn_biography_match.json')
