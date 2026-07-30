#!/usr/bin/env python3
"""Cross-tab Q candidate events by natal Saturn sign and first later same-sign cycle.
No wealth/king/downfall labels are inferred.
"""
import csv,json,os
from collections import Counter,defaultdict
OUT='outputs/q_saturn_sign_cycle_test';os.makedirs(OUT,exist_ok=True)
q={r['q_id']:r for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv'))}
events=list(csv.DictReader(open('outputs/q_better_sequence_test/events.csv')))
rows=[]
for e in events:
 r=q.get(e['q_id'],{});rows.append({**e,'natal_saturn_sign':r.get('natal_saturn_sign',''),'natal_saturn_degree':r.get('natal_saturn_degree','')})
# Aggregate phase and event type by natal sign.
summary=defaultdict(lambda:Counter())
for r in rows:
 s=r['natal_saturn_sign'];summary[s][('events',r['phase'])]+=1;summary[s][('type',r['event_type'])]+=1
out={}
for s,c in sorted(summary.items()):out[s]={'events_total':sum(v for (k,_),v in c.items() if k=='events'),'phases':{x:c[('events',x)] for x in ['pre_ingress_180d','natal_sign_phase','exact_return_3deg','post_sign_180d','outside_window']},'event_types':{x:c[('type',x)] for x in sorted({x for k,x in c if k=='type'})}}
json.dump({'candidate_event_rows':len(rows),'by_natal_saturn_sign':out,'outcome_labels':{'wealth':0,'king_or_political_peak':0,'downfall_or_financial_loss':0,'verified_rags_to_riches':0},'interpretation':'Sign-cycle timing rows are available; real-world outcome labels are not available for Q.'},open(OUT+'/summary.json','w'),indent=2)
with open(OUT+'/events_by_natal_saturn_sign.csv','w',newline='') as f:
 fields=['q_id','name','event_type','event_date','phase','natal_saturn_sign','natal_saturn_degree'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k,'') for k in fields} for r in rows)
print(json.dumps({'candidate_event_rows':len(rows),'natal_signs':len(out),'outcome_labels_available':0},indent=2))
