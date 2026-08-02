#!/usr/bin/env python3
"""Export date-only natal reference positions for every Q-series person.
No birth time, Ascendant, houses, D1 or D9. Uses existing date-only charts.
"""
import csv,json,os
from collections import Counter
BASE='outputs/date_only_nexus_5010'; QBASE='outputs/saturn_returns_q_series'; OUT='outputs/all_planets_q_series'
os.makedirs(OUT,exist_ok=True)
charts=json.load(open(os.path.join(BASE,'reference_charts_by_date.json'),encoding='utf8'))
q=list(csv.DictReader(open(os.path.join(QBASE,'q_saturn_returns.csv'),encoding='utf8')))
PLANETS=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Rahu_mean','Ketu']
rows=[]
for p in q:
    c=charts[p['birth_date']]; mp=c['midpoint_planets']; row={'q_id':p['q_id'],'source_person_id':p['source_person_id'],'name':p['name'],'birth_date':p['birth_date'],'birth_time_used':False}
    for pl in PLANETS:
        x=mp[pl]
        for key in ['longitude','sign','degree','speed_deg_day','retrograde','nakshatra']:
            row[f'{pl}_{key}']=x[key]
    rows.append(row)
fields=list(rows[0])
with open(os.path.join(OUT,'q_all_planet_positions.csv'),'w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
summary={'people':len(rows),'planets':PLANETS,'method':'UTC-noon midpoint date-only Lahiri sidereal reference position','birth_time_used':False,'forbidden':['Ascendant','houses','D1','D9'] ,'sign_counts':{}}
for pl in PLANETS:
 summary['sign_counts'][pl]=dict(Counter(r[f'{pl}_sign'] for r in rows))
summary['retrograde_midpoint_counts']={pl:sum(str(r[f'{pl}_retrograde']).lower()=='true' for r in rows) for pl in PLANETS}
with open(os.path.join(OUT,'run_summary.json'),'w',encoding='utf8') as f: json.dump(summary,f,indent=2)
with open(os.path.join(OUT,'planet_cycle_reference.json'),'w',encoding='utf8') as f: json.dump({'cycles':{'Sun':'~1 year','Moon':'~27.3 days sidereal','Mercury':'~1 year, variable due retrograde','Venus':'~1 year, variable due retrograde','Mars':'~1.88 years','Jupiter':'~11.86 years','Saturn':'~29.46 years','Uranus':'~84 years','Neptune':'~164.8 years','Pluto':'~248 years','Rahu_mean':'~18.6 years retrograde node','Ketu':'~18.6 years retrograde node'},'interpretation':'These are approximate astronomical cycle lengths, not event predictions. A date-only return requires interval/sensitivity analysis and a verified event timeline.'},f,indent=2)
print(json.dumps({'people':len(rows),'planets':len(PLANETS),'output':OUT},indent=2))
