#!/usr/bin/env python3
"""Run a transparent event-date planetary-movement screen on available events.
Does not invent events or map reference events onto Q people.
"""
import csv,json,os,sys
from collections import Counter
sys.path.insert(0,os.path.dirname(__file__))
from date_only_nexus import chart_for_date
SRC='research/events/documented_events.csv'; OUT='outputs/event_movement_analysis'; os.makedirs(OUT,exist_ok=True)
POS={'career_peak','career_breakthrough','business_milestone','comeback','military_victory','recognition','award','marriage','child_birth','wealth_gain','promotion','job_start','success'}
NEG={'electoral_defeat','political_crisis','death','divorce','bankruptcy','illness','accident','job_loss','financial_loss','failure'}
def classify(t):
 t=t.lower()
 if t in POS:return 'positive_or_gain'
 if t in NEG:return 'negative_or_loss'
 return 'unclassified'
rows=[]
for r in csv.DictReader(open(SRC,encoding='utf8')):
 c=chart_for_date(r['event_date']); m=c['midpoint_planets']; sat=m['Saturn']; phase=c['lunar']
 out={**r,'dataset_role':'reference_only_not_Q','event_class':classify(r['event_type']),'saturn_sign':sat['sign'],'saturn_degree':sat['degree'],'saturn_retrograde':sat['retrograde'],'saturn_speed_deg_day':sat['speed_deg_day'],'jupiter_sign':m['Jupiter']['sign'],'jupiter_retrograde':m['Jupiter']['retrograde'],'venus_sign':m['Venus']['sign'],'venus_retrograde':m['Venus']['retrograde'],'mars_sign':m['Mars']['sign'],'mars_retrograde':m['Mars']['retrograde'],'mercury_retrograde':m['Mercury']['retrograde'],'eclipse_proxy':phase['eclipse_proximity_proxy'],'lunar_phase':phase['phase']}
 rows.append(out)
with open(os.path.join(OUT,'available_events_with_movements.csv'),'w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
# Compact counts, deliberately not inferential because N is tiny and non-independent.
summary={'source':SRC,'events':len(rows),'people':len(set(r['name'] for r in rows)),'q_linked_events':0,'event_class_counts':dict(Counter(r['event_class'] for r in rows)),'saturn_retrograde_counts':{f"{k[0]}|retrograde={k[1]}":v for k,v in Counter((r['event_class'],str(r['saturn_retrograde'])) for r in rows).items()},'limitations':['Only 10 events for 2 reference people are present','No Q-series events are present','No causal inference','Date-only midpoint features are not exact event-time observations']}
json.dump(summary,open(os.path.join(OUT,'summary.json'),'w'),indent=2)
print(json.dumps(summary,indent=2))
