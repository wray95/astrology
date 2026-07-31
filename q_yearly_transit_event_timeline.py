#!/usr/bin/env python3
"""Annual Q-series transit/retrograde timeline with available event counts.
Uses annual sign/retrograde summaries, not invented life outcomes.
"""
import csv,json,os,gzip
from datetime import date,timedelta
from collections import Counter,defaultdict
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
OUT='outputs/q_yearly_transit_timeline';os.makedirs(OUT,exist_ok=True)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PL=[('Saturn',swe.SATURN),('Mars',swe.MARS),('Venus',swe.VENUS),('Jupiter',swe.JUPITER),('Rahu',swe.MEAN_NODE)]
def calc(d):
 j=swe.julday(d.year,d.month,d.day,12);o={}
 for p,pid in PL:
  x,_=swe.calc_ut(j,pid,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED);lon=x[0]%360;o[p]={'sign':SIGNS[int(lon//30)],'degree':lon%30,'retro':x[3]<0,'speed':x[3]}
 o['Ketu']={'sign':SIGNS[int(((o['Rahu']['degree']+30*SIGNS.index(o['Rahu']['sign'])+180)%360)//30)],'degree':(o['Rahu']['degree']+180)%30,'retro':True,'speed':-o['Rahu']['speed']}
 return o
q=[]
for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv')):q.append(r)
events=defaultdict(Counter)
for r in csv.DictReader(open('outputs/outcome_event_movement/q_candidate_events_with_movements.csv')):
 try:y=int(r['event_date'][:4]);events[(r['q_id'],y)][r['event_type']]+=1
 except:pass
start_year=1800;end_year=2028
# Global annual astronomical summaries.
yearly={};prev=None
for y in range(start_year,end_year+1):
 d=date(y,1,1);end=date(y+1,1,1) if y<end_year else date(y,12,31)+timedelta(days=1);days=[];cur=d
 while cur<end:
  days.append(calc(cur));cur+=timedelta(days=1)
 summary={'year':y,'days':len(days),'planets':{}}
 for p in ['Saturn','Mars','Venus','Jupiter','Rahu','Ketu']:
  signs=[x[p]['sign'] for x in days];retro=sum(x[p]['retro'] for x in days);ing=sum(1 for i in range(1,len(signs)) if signs[i]!=signs[i-1]);
  summary['planets'][p]={'sign_at_year_start':signs[0],'sign_at_year_end':signs[-1],'sign_ingresses':ing,'retrograde_days':retro,'retrograde_present':retro>0,'stationary_proxy_days':sum(abs(x[p]['speed'])<0.01 for x in days)}
 yearly[y]=summary
# Stream one record per Q-person-year; ancient births use 1800 horizon.
count=0
with gzip.open(OUT+'/q_yearly_timeline.jsonl.gz','wt',encoding='utf8') as f:
 for r in q:
  by=int(r['birth_date'][:4]);first=max(1800,by)
  for y in range(first,end_year+1):
   a=yearly[y];ev=dict(events.get((r['q_id'],y),{}));sat=a['planets']['Saturn'];
   rec={'q_id':r['q_id'],'name':r['name'],'birth_year':by,'year':y,'natal_saturn_sign':r['natal_saturn_sign'],'saturn_same_natal_sign_at_year_start':sat['sign_at_year_start']==r['natal_saturn_sign'],'event_count':sum(ev.values()),'event_types':ev,'planetary_year':a['planets']}
   f.write(json.dumps(rec,separators=(',',':'))+'\n');count+=1
json.dump({'q_people':len(q),'timeline_rows':count,'year_range':'1800-2028 (birth years before 1800 truncated to 1800)','planetary_features':['year-start/end signs','sign ingresses','retrograde days','stationary proxy days'],'event_rows_source':'candidate biography extractions; not verified outcomes','outcome_labels':{'wealth':0,'success':0,'failure':0,'rags_to_riches':0},'limitations':['Annual aggregation cannot establish exact event timing','No invented outcomes','No causality']},open(OUT+'/summary.json','w'),indent=2)
print(json.dumps({'q_people':len(q),'timeline_rows':count,'output':OUT},indent=2))
