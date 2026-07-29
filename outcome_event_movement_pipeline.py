#!/usr/bin/env python3
"""Build conservative outcome/event fields and date-only movement features.
Unknown is a required valid value; wealth/success is never guessed from occupation.
"""
import csv,json,os,re,sys
from datetime import datetime
sys.path.insert(0,os.path.dirname(__file__))
from date_only_nexus import chart_for_date
OUT='outputs/outcome_event_movement';os.makedirs(OUT,exist_ok=True)
bio=list(csv.DictReader(open('outputs/q_biographical_wikipedia/q_biographical_details.csv')))
enr={r['q_id']:r for r in csv.DictReader(open('outputs/q_people_enriched/q_people_enriched.csv'))}
# Date patterns supported: exact day/month/year, month/year, year. A year alone is not an exact event date.
months='January|February|March|April|May|June|July|August|September|October|November|December'
pat=re.compile(rf'(?P<full>(?:{months})\s+\d{{1,2}},?\s+\d{{3,4}}|\d{{1,2}}\s+(?:{months})\s+\d{{3,4}})|(?P<month>(?:{months})\s+\d{{3,4}})|(?P<year>(?<!\d)(1\d{{3}}|2\d{{3}})(?!\d))',re.I)
def dates(text):
 found=[]
 for m in pat.finditer(text or ''):
  raw=m.group(0); dt=None;prec='year'
  for f in ['%B %d, %Y','%B %d %Y','%d %B %Y','%B %Y']:
   try:dt=datetime.strptime(raw.replace(',',''),f.replace(',','')).date();prec='day' if '%d' in f else 'month';break
   except:pass
  if not dt and m.group('year'):
   try:dt=datetime(int(m.group('year')),7,1).date();prec='year'
   except:continue
  if dt and 1 <= dt.year <= 2026:found.append((raw,dt.isoformat(),prec))
 return list(dict.fromkeys(found))
def add_event(events,r,field,etype):
 for raw,dt,prec in dates(r.get(field,'')):
  events.append({'q_id':r['q_id'],'name':r['name'],'event_type':etype,'event_date':dt,'date_precision':prec,'date_raw':raw,'source_url':r['source_url'],'source_field':field,'verification_status':'candidate_extraction_only'})
# Required outcome fields; unknown is explicit and not a claim.
outcomes=[];events=[]
for r in bio:
 e=enr.get(r['q_id'],{})
 ach=e.get('achievement_score','')
 outcomes.append({'q_id':r['q_id'],'name':r['name'],'birth_date':r['birth_date'],'career':e.get('career',''),'achievement_score_source_value':ach,'wealth_category':'unknown_not_documented','poor_category':'unknown_not_documented','success_category':'unknown_not_documented','failure_category':'unknown_not_documented','marriage_status':'unknown_not_documented','children_status':'unknown_not_documented','outcome_data_required':True,'source_url':r['source_url']})
 add_event(events,r,'death_date','death');add_event(events,r,'debut','debut_or_career_start');add_event(events,r,'spouse','marriage_or_spouse_date_candidate');add_event(events,r,'incarceration','incarceration_or_conviction_candidate');add_event(events,r,'career_active','career_period_candidate')
# only exact day/month events are appropriate for exact-day transit tests; year/month retained separately.
cache={}; enriched=[]
for ev in events:
 if ev['date_precision']=='year':ev.update({'saturn_sign':'','saturn_degree':'','saturn_retrograde':'','jupiter_sign':'','planetary_data_status':'not_exact_day'})
 else:
  c=cache.setdefault(ev['event_date'],chart_for_date(ev['event_date']));m=c['midpoint_planets'];s=m['Saturn'];j=m['Jupiter'];ev.update({'saturn_sign':s['sign'],'saturn_degree':s['degree'],'saturn_retrograde':s['retrograde'],'jupiter_sign':j['sign'],'jupiter_retrograde':j['retrograde'],'venus_sign':m['Venus']['sign'],'mars_sign':m['Mars']['sign'],'planetary_data_status':'date_only_midpoint'})
 enriched.append(ev)
with open(OUT+'/q_outcome_status.csv','w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=outcomes[0]);w.writeheader();w.writerows(outcomes)
with open(OUT+'/q_candidate_events_with_movements.csv','w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=enriched[0] if enriched else ['q_id']);w.writeheader();w.writerows(enriched)
json.dump({'q_people':len(outcomes),'candidate_event_rows':len(enriched),'exact_day_or_month_rows':sum(x['date_precision']!='year' for x in enriched),'outcome_status_counts':{'wealth_unknown':len(outcomes),'poor_unknown':len(outcomes),'success_unknown':len(outcomes)},'warning':'Candidates extracted from infobox fields are not verified event records; no wealth/poverty/success/failure values were inferred.'},open(OUT+'/summary.json','w'),indent=2)
print(json.dumps({'q_people':len(outcomes),'candidate_events':len(enriched),'date_only_movement_rows':sum(x['planetary_data_status']=='date_only_midpoint' for x in enriched)},indent=2))
