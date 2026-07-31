#!/usr/bin/env python3
"""Test Saturn natal-sign ingress/return sequence on available Q candidate events.
Candidate events are not yet manually verified; outputs are exploratory.
"""
import csv,json,os,random,math
from datetime import date,timedelta
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
EV='outputs/outcome_event_movement/q_candidate_events_with_movements.csv'; Q='outputs/saturn_returns_q_series/q_saturn_returns.csv'; OUT='outputs/q_saturn_sequence_test';os.makedirs(OUT,exist_ok=True)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def sat(d):
 j=swe.julday(d.year,d.month,d.day,12);x,_=swe.calc_ut(j,swe.SATURN,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED);lon=x[0]%360;return lon,SIGNS[int(lon//30)],x[3]
def ang(a,b):return abs((a-b+180)%360-180)
def asdate(x):return date.fromisoformat(x)
q={r['q_id']:{'birth':asdate(r['birth_date']),'natal_lon':float(r['natal_saturn_longitude_utc_noon']),'natal_sign':r['natal_saturn_sign']} for r in csv.DictReader(open(Q))}
events=[r for r in csv.DictReader(open(EV)) if r['q_id'] in q and r['date_precision']!='year']
rows=[]
for r in events:
 d=asdate(r['event_date']); z=q[r['q_id']];lon,sg,sp=sat(d); same=sg==z['natal_sign']; exact=ang(lon,z['natal_lon'])<=3
 rows.append({**r,'natal_saturn_sign':z['natal_sign'],'event_saturn_sign':sg,'event_saturn_longitude':lon,'event_saturn_speed':sp,'saturn_retrograde':sp<0,'saturn_in_natal_sign':same,'saturn_exact_return_3deg':exact,'sequence_phase':'sign_return_window' if same else ('exact_return_3deg' if exact else 'outside_return_sign')})
# matched controls: three random dates in each person's lifespan through the candidate event date.
rng=random.Random(19681124);controls=[]
for r in rows:
 z=q[r['q_id']]; end=asdate(r['event_date']); start=z['birth']+timedelta(days=365*18)
 if end<=start: continue
 for k in range(3):
  d=start+timedelta(days=rng.randrange((end-start).days+1));lon,sg,sp=sat(d);controls.append({'q_id':r['q_id'],'event_type':r['event_type'],'saturn_in_natal_sign':sg==z['natal_sign'],'saturn_exact_return_3deg':ang(lon,z['natal_lon'])<=3,'saturn_retrograde':sp<0})
with open(OUT+'/q_events_saturn_sequence.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with open(OUT+'/q_controls_saturn_sequence.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=controls[0].keys());w.writeheader();w.writerows(controls)
def counts(a):return {'n':len(a),'same_sign':sum(x['saturn_in_natal_sign'] for x in a),'exact_3deg':sum(x['saturn_exact_return_3deg'] for x in a),'retrograde':sum(x.get('saturn_retrograde',False) for x in a)}
summary={'candidate_events':counts(rows),'matched_controls':counts(controls),'by_event_type':{}}
for t in sorted(set(x['event_type'] for x in rows)):
 a=[x for x in rows if x['event_type']==t];c=[x for x in controls if x['event_type']==t];summary['by_event_type'][t]={'events':counts(a),'controls':counts(c)}
summary['limitations']=['Candidate extraction only; not manually verified','Controls are preliminary age-window random dates, not final matched design','No Q wealth/success/failure labels are available','Association is not causation']
json.dump(summary,open(OUT+'/summary.json','w'),indent=2)
print(json.dumps(summary,indent=2))
