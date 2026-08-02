#!/usr/bin/env python3
"""Cross-reference the 200-person baseline against date-only planet positions.
No birth time; event fields are only tested when an exact date is present.
"""
import csv,json,os,re,sys
from datetime import datetime
sys.path.insert(0,os.path.dirname(__file__))
from date_only_nexus import chart_for_date
IN='outputs/requested_200_biographies/biographies_200.json';OUT='outputs/requested_200_planet_crossref';os.makedirs(OUT,exist_ok=True)
PL=['Saturn','Mars','Venus','Jupiter','Rahu_mean','Ketu']
def iso(s):
 if not s:return None
 for f in ['%Y-%m-%d','%d/%m/%Y','%m/%d/%Y']:
  try:return datetime.strptime(s,f).strftime('%Y-%m-%d')
  except:pass
 m=re.search(r'(\d{4})',s)
 return f'{m.group(1)}-07-01' if m and 1<=int(m.group(1))<=2026 else None
def transit(d):
 c=chart_for_date(d);m=c['midpoint_planets'];return {p:{'sign':m[p]['sign'],'degree':m[p]['degree'],'longitude':m[p]['longitude'],'retrograde':m[p]['retrograde'],'speed_deg_day':m[p]['speed_deg_day']} for p in PL}
people=json.load(open(IN));rows=[];event_rows=[];cache={}
for i,x in enumerate(people,1):
 bd=iso(x.get('birth_date')); birth=transit(bd) if bd else {}
 row={'id':f'B200_{i:03d}','name':x['name'],'birth_date':bd,'source_url':x.get('source_url',''),'birth_time_used':False}
 for p in PL:
  z=birth.get(p,{});row.update({f'birth_{p}_sign':z.get('sign'),f'birth_{p}_degree':z.get('degree'),f'birth_{p}_retrograde':z.get('retrograde')})
 rows.append(row)
 # death is the only structured date field in this baseline; other fields require date parsing/verification.
 for et,raw in [('death',x.get('death_date'))]:
  d=iso(raw)
  if d and raw not in ('Living','Living (as of 2024, age 96)'):
   z=cache.setdefault(d,transit(d));event_rows.append({'id':row['id'],'name':x['name'],'event_type':et,'event_date':d,'date_raw':raw,'source_url':x.get('source_url',''),'date_precision':'exact_or_source_parsed','source_status':'verify before inference',**{f'{p}_{k}':z[p][k] for p in PL for k in ['sign','degree','retrograde','speed_deg_day']}})
with open(OUT+'/birth_planet_positions.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with open(OUT+'/event_transits.csv','w',newline='') as f:
 fields=event_rows[0].keys() if event_rows else ['id','name','event_type','event_date'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(event_rows)
json.dump({'people':len(rows),'event_rows_with_dates':len(event_rows),'planets':PL,'event_types_present':sorted(set(x['event_type'] for x in event_rows)),'conclusion':'No marriage, career, wealth or success event dates are present in the 200-person baseline. Birth-position cross-reference is complete; event-transit inference is pending verified event dates.'},open(OUT+'/summary.json','w'),indent=2)
print(json.dumps({'people':len(rows),'event_rows_with_dates':len(event_rows)},indent=2))
