#!/usr/bin/env python3
"""Q Saturn sign-window test with a 3-year lead/lag around every same-sign passage."""
import csv,json,os
from datetime import date,timedelta
from collections import Counter
OUT='outputs/q_saturn_wide_window_test';os.makedirs(OUT,exist_ok=True)
passages={}
for r in csv.DictReader(open('outputs/saturn_same_sign_passages/all_passages.csv')):
 if r['series']=='Q':passages.setdefault(r['person_id'],[]).append(r)
events=[r for r in csv.DictReader(open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv')) if r['date_precision']!='year']
rows=[]
for e in events:
 if e['q_id'] not in passages:continue
 d=date.fromisoformat(e['event_date']); best=None
 for p in passages[e['q_id']]:
  ing=date.fromisoformat(p['saturn_ingress']); ex=date.fromisoformat(p['saturn_exit']);
  if ing-timedelta(days=3*365)<=d<=ex+timedelta(days=3*365):
   dist=0 if ing<=d<=ex else min(abs((d-ing).days),abs((d-ex).days));cand=(dist,p)
   if best is None or cand[0]<best[0]:best=cand
 if best:
  p=best[1];ing=date.fromisoformat(p['saturn_ingress']);ex=date.fromisoformat(p['saturn_exit']);
  phase='core_natal_sign' if ing<=d<=ex else ('lead_3y_before_ingress' if d<ing else 'lag_3y_after_exit')
  rows.append({**e,'natal_saturn_sign':p['natal_saturn_sign'],'natal_saturn_degree':p['natal_saturn_degree'],'saturn_ingress':p['saturn_ingress'],'saturn_exit':p['saturn_exit'],'wide_3y_phase':phase,'wide_window_start':(ing-timedelta(days=3*365)).isoformat(),'wide_window_end':(ex+timedelta(days=3*365)).isoformat()})
c=Counter(r['wide_3y_phase'] for r in rows);by_sign={}
for s in sorted(set(r['natal_saturn_sign'] for r in rows)):
 z=[r for r in rows if r['natal_saturn_sign']==s];by_sign[s]=dict(Counter(r['wide_3y_phase'] for r in z))
summary={'usable_candidate_events':len(events),'events_in_3y_lead_core_lag_windows':len(rows),'phase_counts':dict(c),'event_type_counts':dict(Counter(r['event_type'] for r in rows)),'by_natal_saturn_sign':by_sign,'outcome_labels_available':{'q_wealth':0,'q_rags_to_riches':0,'q_downfall':0},'interpretation':'Widened timing screen; not an outcome test and not causal.'}
json.dump(summary,open(OUT+'/summary.json','w'),indent=2)
with open(OUT+'/events.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys() if rows else ['q_id']);w.writeheader();w.writerows(rows)
print(json.dumps(summary,indent=2))
