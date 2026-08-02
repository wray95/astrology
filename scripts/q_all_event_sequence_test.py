#!/usr/bin/env python3
"""Run the date-only sequence screen across all available Q event candidates.
Rags-to-riches and outcome categories remain unknown unless sourced.
"""
import csv,json,os,random
from datetime import date,timedelta
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];PL=['Saturn','Mars','Venus','Jupiter','Rahu_mean','Ketu']
OUT='outputs/q_all_event_sequence_test';os.makedirs(OUT,exist_ok=True)
def astro(d):
 j=swe.julday(d.year,d.month,d.day,12);out={}
 for p,pid in [('Saturn',swe.SATURN),('Mars',swe.MARS),('Venus',swe.VENUS),('Jupiter',swe.JUPITER),('Rahu_mean',swe.MEAN_NODE)]:
  x,_=swe.calc_ut(j,pid,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED);lon=x[0]%360;out[p]={'lon':lon,'sign':SIGNS[int(lon//30)],'retro':x[3]<0,'speed':x[3]}
 r=out['Rahu_mean']['lon'];out['Ketu']={'lon':(r+180)%360,'sign':SIGNS[int(((r+180)%360)//30)],'retro':True,'speed':-out['Rahu_mean']['speed']}
 return out
def ang(a,b):return abs((a-b+180)%360-180)
q={r['q_id']:{'birth':date.fromisoformat(r['birth_date']),'natal':{p:float(r[f'{p if p != "Rahu_mean" else "Rahu_mean"}_longitude']) if f'{p}_longitude' in r else None for p in []}} for r in []}
# natal positions from the all-planet Q file
for r in csv.DictReader(open('outputs/all_planets_q_series/q_all_planet_positions.csv')):
 q[r['q_id']]={'birth':date.fromisoformat(r['birth_date']),'natal':{p:float(r[f'{p}_longitude']) for p in PL},'natal_sign':{p:r[f'{p}_sign'] for p in PL}}
events=list(csv.DictReader(open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv')))
all_counts={}
for r in events:all_counts[r['event_type']]=all_counts.get(r['event_type'],0)+1
usable=[r for r in events if r['date_precision']!='year' and r['q_id'] in q]
cache={}; rows=[]
for r in usable:
 d=date.fromisoformat(r['event_date']);z=q[r['q_id']];a=cache.setdefault(d,astro(d));o={**r,'data_role':'candidate_event_not_verified'}
 for p in PL:o.update({f'{p}_same_natal_sign':a[p]['sign']==z['natal_sign'][p],f'{p}_within_3deg':ang(a[p]['lon'],z['natal'][p])<=3,f'{p}_retrograde':a[p]['retro']})
 rows.append(o)
rng=random.Random(20260730);controls=[]
for r in rows:
 z=q[r['q_id']];end=date.fromisoformat(r['event_date']);start=z['birth']+timedelta(days=18*365)
 if end<=start:continue
 for _ in range(3):
  d=start+timedelta(days=rng.randrange((end-start).days+1));a=cache.setdefault(d,astro(d));o={'q_id':r['q_id'],'event_type':r['event_type']}
  for p in PL:o.update({f'{p}_same_natal_sign':a[p]['sign']==z['natal_sign'][p],f'{p}_within_3deg':ang(a[p]['lon'],z['natal'][p])<=3,f'{p}_retrograde':a[p]['retro']})
  controls.append(o)
def stats(a):return {'n':len(a),**{f'{p}_same_sign':sum(x[f'{p}_same_natal_sign'] for x in a) for p in PL},**{f'{p}_within_3deg':sum(x[f'{p}_within_3deg'] for x in a) for p in PL},**{f'{p}_retrograde':sum(x[f'{p}_retrograde'] for x in a) for p in PL}}
summary={'q_people':len(q),'all_candidate_event_rows':len(events),'candidate_event_type_counts':all_counts,'usable_date_rows':len(rows),'control_rows':len(controls),'event_stats':stats(rows),'control_stats':stats(controls),'outcome_gaps':{'rags_to_riches':0,'wealth_gain':0,'poverty_or_loss':0,'major_success':0,'major_failure':0,'child_birth':0},'limitations':['No verified Q outcome labels','Rags-to-riches cannot be inferred from occupation or planetary data','Candidate events are source-field extractions and may be false or imprecise','No causal inference; controls are preliminary']}
json.dump(summary,open(OUT+'/summary.json','w'),indent=2)
with open(OUT+'/events.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
with open(OUT+'/controls.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=controls[0].keys());w.writeheader();w.writerows(controls)
print(json.dumps(summary,indent=2))
