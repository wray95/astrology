#!/usr/bin/env python3
"""List every Saturn passage into each person's natal Saturn sign, plus pre-ingress windows.
Date-only, Lahiri sidereal, no birth time/houses.
"""
import csv,json,os
from datetime import date,timedelta
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
OUT='outputs/saturn_same_sign_passages';os.makedirs(OUT,exist_ok=True)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def sat(d):
 j=swe.julday(d.year,d.month,d.day,12);x,_=swe.calc_ut(j,swe.SATURN,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED);return x[0]%360,SIGNS[int((x[0]%360)//30)],x[3]
def ang(a,b):return abs((a-b+180)%360-180)
# Person inputs
people=[]
for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv')):
 people.append({'series':'Q','id':r['q_id'],'name':r['name'],'birth_date':r['birth_date'],'natal_sign':r['natal_saturn_sign'],'natal_lon':float(r['natal_saturn_longitude_utc_noon'])})
for i,r in enumerate(csv.DictReader(open('outputs/p_date_only_reanalysis/p_date_only_positions.csv')),1):
 people.append({'series':'P','id':r['p_id'],'name':r['name'],'birth_date':r['birth_date'],'natal_sign':r['saturn_sign'],'natal_lon':float(r['saturn_degree'])+30*SIGNS.index(r['saturn_sign'])})
# Practical research horizon: 1800 onward. Ancient records are retained in Q, but
# a multi-century daily ephemeris is not a useful comparable modern-life window.
start=max(date(1800,1,1),min(date.fromisoformat(p['birth_date']) for p in people)); end=date(2028,12,31)
# Precompute once so 5,019 people do not repeat ephemeris calls.
sky={};intervals=[];d=start;last=None;beg=None
while d<=end:
 sky[d]=sat(d); sg=sky[d][1]
 if sg!=last:
  if last is not None:intervals.append((beg,d-timedelta(days=1),last))
  beg=d;last=sg
 d+=timedelta(days=1)
intervals.append((beg,end,last))
rows=[]
for p in people:
 b=date.fromisoformat(p['birth_date']); idx=0
 for ing,exit,sg in intervals:
  if sg!=p['natal_sign'] or exit<b:continue
  ing=max(ing,b);pre_start=ing-timedelta(days=180);pre_end=ing-timedelta(days=1)
  # nearest degree return within this passage, if any
  best=None;dd=ing
  while dd<=exit:
   lon,_,speed=sky[dd];e=ang(lon,p['natal_lon']);cand=(e,dd,lon,speed)
   if best is None or cand[0]<best[0]:best=cand
   dd+=timedelta(days=1)
  idx+=1
  rows.append({'series':p['series'],'person_id':p['id'],'name':p['name'],'birth_date':p['birth_date'],'natal_saturn_sign':p['natal_sign'],'natal_saturn_degree':round(p['natal_lon']%30,6),'passage_number':idx,'saturn_ingress':ing.isoformat(),'saturn_exit':exit.isoformat(),'pre_ingress_180d_start':pre_start.isoformat(),'pre_ingress_180d_end':pre_end.isoformat(),'nearest_degree_date':best[1].isoformat(),'nearest_degree_error':round(best[0],6),'passage_status':'past' if exit<date.today() else ('current_or_future' if ing<=end else 'future')})
with open(OUT+'/all_passages.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
json.dump({'people':len(people),'q_people':sum(p['series']=='Q' for p in people),'p_people':sum(p['series']=='P' for p in people),'passages':len(rows),'horizon_end':end.isoformat(),'definition':'Each contiguous Saturn sidereal passage through the person\'s natal Saturn sign; pre-window is 180 days before ingress','limitations':['UTC-noon date-only ephemeris','No birth time, houses, Lagna, D1 or D9','Sign passage is not exact-degree return','Future dates are astronomical windows, not predictions']},open(OUT+'/summary.json','w'),indent=2)
print(json.dumps({'people':len(people),'passages':len(rows),'output':OUT},indent=2))
