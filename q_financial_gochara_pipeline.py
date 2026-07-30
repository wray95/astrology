#!/usr/bin/env python3
"""Apply all date-only financial Gochara features to Q.
House/dasha/D10 features are intentionally excluded without verified birth time.
"""
import csv,json,os
OUT='outputs/q_financial_gochara';os.makedirs(OUT,exist_ok=True)
q=list(csv.DictReader(open('outputs/all_planets_q_series/q_all_planet_positions.csv')))
ret={r['q_id']:r for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv'))}
event_counts={}
for r in csv.DictReader(open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv')):
 event_counts.setdefault(r['q_id'],0);event_counts[r['q_id']]+=1
PLANETS=['Saturn','Jupiter','Venus','Rahu_mean','Ketu']
rows=[]
for r in q:
 x={'q_id':r['q_id'],'name':r['name'],'birth_date':r['birth_date'],'birth_time_used':False,'wealth_category':'unknown_not_documented','poverty_category':'unknown_not_documented','financial_outcome_date':None,'event_rows_candidate_count':event_counts.get(r['q_id'],0),'houses_available':False,'dasha_available':False,'d10_available':False,'saturn_first_return_date':ret.get(r['q_id'],{}).get('first_return_date'),'saturn_second_return_date':ret.get(r['q_id'],{}).get('second_return_date')}
 for p in PLANETS:x.update({f'{p}_birth_sign':r[f'{p}_sign'],f'{p}_birth_degree':r[f'{p}_degree'],f'{p}_birth_retrograde':r[f'{p}_retrograde']})
 rows.append(x)
with open(OUT+'/q_financial_features.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
json.dump({'q_people':len(rows),'financial_outcomes_verified':0,'features_applied':['Jupiter return/sign/degree baseline','Saturn pre-ingress/sign/exact-return windows','Venus degree/return baseline','Rahu/Ketu sign/degree and node-return baseline','candidate event-date movement fields from prior pipeline'],'features_not_applied':['2nd/6th/10th/11th houses','house lords','Dasha/Antardasha','D9','D10','house-based yogas'],'reason':'Birth times are unavailable and Q financial outcome dates are not yet verified.'},open(OUT+'/summary.json','w'),indent=2)
print(json.dumps({'q_people':len(rows),'financial_outcomes_verified':0},indent=2))
