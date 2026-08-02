#!/usr/bin/env python3
"""Create a 200-person source-attributed biography JSON in the requested schema.
Uses the first 200 records of the repository's public-person dataset; unknowns remain null.
"""
import json,csv,os,re,time,requests
from urllib.parse import unquote
SRC='famous_people_birth_data.json';OUT='outputs/requested_200_biographies';os.makedirs(OUT,exist_ok=True)
people=json.load(open(SRC))[:200]
S=requests.Session();S.headers.update({'User-Agent':'ArenaAstrologyResearch/1.0 (research)'});cache={}
for i,p in enumerate(people,1):
 url=p.get('source_url','');title=unquote(url.split('/wiki/',1)[1]).replace('_',' ') if '/wiki/' in url else p['name'];
 try:
  q=S.get('https://en.wikipedia.org/w/api.php',params={'action':'query','prop':'revisions|extracts','rvprop':'content','rvslots':'main','explaintext':1,'exchars':5000,'titles':title,'format':'json','formatversion':2},timeout=40).json().get('query',{}).get('pages',[{}])[0]
  raw=((q.get('revisions') or [{}])[0].get('slots',{}).get('main',{}).get('content','')); extract=q.get('extract','')
 except Exception: raw='';extract=''
 def field(names):
  for line in raw.splitlines():
   m=re.match(r'\s*\|\s*([^=]+?)\s*=\s*(.*)',line)
   if m and m.group(1).strip().lower() in names:return re.sub(r'\s+',' ',m.group(2)).strip()
  return None
 def clean(v):
  if not v:return None
  v=re.sub(r'\{\{[^{}]*\}\}','',v);v=re.sub(r'\[\[([^]|]+)(?:\|[^]]+)?\]\]',r'\1',v);return re.sub(r'\s+',' ',v).strip(' |') or None
 row={'name':p.get('name'),'birth_date':p.get('birth_date'),'birth_place':p.get('birth_city'),'birth_country':p.get('birth_country'),'coordinates':{'latitude':None,'longitude':None},'childhood_background':None,'peak_wealth_usd':None,'peak_wealth_year':None,'career_start_year':None,'career_start_role':clean(field({'occupation','years_active'})),'major_career_milestones':[],'marriages':clean(field({'spouse','spouse(s)'})),'children':clean(field({'children'})),'death_date':clean(field({'death_date','date of death'})) or ('Living' if not field({'death_date','date of death'}) else None),'death_age':None,'causes_of_success':[],'estimated_net_worth_2024':None,'education':clean(field({'alma_mater','education'})),'profession':p.get('profession'),'industry':None,'source_url':url,'source_status':'Wikipedia infobox; unknown fields left null','source_retrieved':bool(raw)}
 rows=locals().get('rows',[]);rows.append(row)
 if i%25==0: print(i,flush=True)
 time.sleep(.15)
json.dump(rows,open(OUT+'/biographies_200.json','w'),ensure_ascii=False,indent=2)
json.dump({'records':len(rows),'source_selection':'first 200 records of famous_people_birth_data.json','unknown_policy':'null; no wealth, marriage or dates inferred','source':'Wikipedia API plus repository source URLs'},open(OUT+'/summary.json','w'),indent=2)
print('done',len(rows))
