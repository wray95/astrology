#!/usr/bin/env python3
"""Improved Q-series Saturn sequence test.
Uses candidate event dates and within-person, same-calendar-month controls.
Pre-ingress = 180 days before Saturn enters natal Saturn sign; sign phase = Saturn in natal sign; exact return <=3 degrees.
"""
import csv,json,os,random
from datetime import date,timedelta
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];OUT='outputs/q_better_sequence_test';os.makedirs(OUT,exist_ok=True)
def astro(d):
 j=swe.julday(d.year,d.month,d.day,12);x,_=swe.calc_ut(j,swe.SATURN,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED);lon=x[0]%360;return lon,SIGNS[int(lon//30)],x[3]
def phase(d,natal_sign,natal_lon):
 lon,sg,sp=astro(d); exact=abs((lon-natal_lon+180)%360-180)<=3
 if sg==natal_sign:return 'natal_sign_phase' if not exact else 'exact_return_3deg'
 # identify nearest daily ingress/exit in a bounded window
 for k in range(1,181):
  future=d+timedelta(days=k)
  _,sf,_=astro(future)
  if sf==natal_sign:return 'pre_ingress_180d'
  past=d-timedelta(days=k)
  _,spast,_=astro(past)
  if spast==natal_sign:return 'post_sign_180d'
 return 'outside_window'
def parse(x):return date.fromisoformat(x)
q={r['q_id']:{'birth':parse(r['birth_date']),'natal_sign':r['natal_saturn_sign'],'natal_lon':float(r['natal_saturn_longitude_utc_noon'])} for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv'))}
events=[r for r in csv.DictReader(open('outputs/outcome_movement' if False else 'outputs/outcome_event_movement/q_candidate_events_with_movements.csv')) if r['date_precision']!='year' and r['q_id'] in q]
rng=random.Random(20260730);event_rows=[];control_rows=[]
for r in events:
 z=q[r['q_id']];d=parse(r['event_date']);ph=phase(d,z['natal_sign'],z['natal_lon']);event_rows.append({'q_id':r['q_id'],'event_type':r['event_type'],'event_date':r['event_date'],'phase':ph,'candidate':True})
 # same-month controls, before the event (or lifespan if event is early)
 start=z['birth']+timedelta(days=18*365); end=d-timedelta(days=30)
 pool=[]
 if end>start:
  cur=start
  while cur<=end:
   if cur.month==d.month:pool.append(cur)
   cur+=timedelta(days=1)
  if pool:
   for cd in rng.sample(pool,min(20,len(pool))):control_rows.append({'q_id':r['q_id'],'event_type':r['event_type'],'control_date':cd.isoformat(),'phase':phase(cd,z['natal_sign'],z['natal_lon']),'candidate':False})
def count(rs):
 from collections import Counter
 c=Counter(x['phase'] for x in rs);return {'n':len(rs),**{k:c[k] for k in ['pre_ingress_180d','natal_sign_phase','exact_return_3deg','post_sign_180d','outside_window']}}
summary={'events':count(event_rows),'controls':count(control_rows),'by_event_type':{},'design':'within-person same-calendar-month controls, up to 20 per candidate event','limitations':['Candidate dates are not fully verified','Year/month midpoint dates may be imprecise','No verified Q wealth/success/failure labels','Phase scanning is date-only and uses sign not houses','Observational association, not causation']}
for t in sorted(set(x['event_type'] for x in event_rows)):
 summary['by_event_type'][t]={'events':count([x for x in event_rows if x['event_type']==t]),'controls':count([x for x in control_rows if x['event_type']==t])}
json.dump(summary,open(OUT+'/summary.json','w'),indent=2)
for fn,data in [('events.csv',event_rows),('controls.csv',control_rows)]:
 with open(OUT+'/'+fn,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
print(json.dumps(summary,indent=2))
