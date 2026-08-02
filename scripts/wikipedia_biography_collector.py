#!/usr/bin/env python3
"""Resumable Wikipedia source collector for Q biographies.

Collects raw, source-attributed infobox fields; it does not infer missing dates.
"""
import csv,json,os,re,time,requests
from urllib.parse import unquote,urlparse
IN='data/births_people.json'; OUT='outputs/q_biographical_wikipedia'; os.makedirs(OUT,exist_ok=True)
CACHE=OUT+'/wikipedia_raw_cache.json'; RESULT=OUT+'/q_biographical_details.csv'
UA='ArenaAstrologyResearch/1.0 (research dataset; contact: research@example.com)'
S=requests.Session();S.headers.update({'User-Agent':UA})
fields_map={'birth_date':['birth_date','date of birth'],'death_date':['death_date','date of death'],'spouse':['spouse','spouse(s)'],'marriage_date':['marriage_date','married'],'children':['children'],'occupation':['occupation'],'career_active':['years_active','years active','career_start','career_end'],'debut':['debut','debut_date','professional_debut'],'incarceration':['imprisoned','incarceration','criminal_penalty','conviction','detained'],'education':['alma_mater','education'],'employer':['employer'],'wealth':['net_worth']}
def title(url,name):
 if '/wiki/' in (url or ''): return unquote(url.split('/wiki/',1)[1]).replace('_',' ')
 return name
def clean(v):
 v=re.sub(r'<[^>]+>',' ',v);v=re.sub(r'\{\{[^{}]*\}\}',' ',v);v=re.sub(r'\[\[([^]|]+)(?:\|[^]]+)?\]\]',r'\1',v);v=re.sub(r'<ref[^>]*>.*?</ref>',' ',v,flags=re.S);v=re.sub(r'\s+',' ',v);return v.strip(' |')
def infobox(text):
 out={}; inside=False
 for line in text.splitlines():
  if line.startswith('{{Infobox'):inside=True;continue
  if inside and line.strip().startswith('}}'):break
  if inside:
   m=re.match(r'\s*\|\s*([^=]+?)\s*=\s*(.*)',line)
   if m:out[m.group(1).strip().lower()]=clean(m.group(2))
 return out
def api_batch(titles):
 params={'action':'query','prop':'revisions|extracts','rvprop':'content','rvslots':'main','explaintext':1,'exchars':5000,'titles':'|'.join(titles),'format':'json','formatversion':2}
 for attempt in range(6):
  r=S.get('https://en.wikipedia.org/w/api.php',params=params,timeout=60)
  if r.status_code == 200:return r.json().get('query',{}).get('pages',[])
  if r.status_code == 429:
   time.sleep(10*(attempt+1)); continue
  r.raise_for_status()
 raise RuntimeError('rate limited after retries')
people=json.load(open(IN))
try:
 cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
except json.JSONDecodeError:
 cache={}; print('corrupt cache discarded; restarting safely',flush=True)
items=[]
for p in people:
 t=title(p.get('source_url',''),p.get('name',''));items.append((p,t))
need=[t for _,t in items if t not in cache]
for start in range(0,len(need),25):
 batch=need[start:start+25]
 try:
  for page in api_batch(batch):
   t=page.get('title'); raw=((page.get('revisions') or [{}])[0].get('slots',{}).get('main',{}).get('content',''))
   cache[t]={'pageid':page.get('pageid'),'title':t,'wikitext':raw,'extract':page.get('extract',''),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
  tmp=CACHE+'.tmp'; json.dump(cache,open(tmp,'w'),ensure_ascii=False); os.replace(tmp,CACHE)
  print(start+len(batch),'/',len(need),flush=True)
 except Exception as e: print('batch failed',start,e,flush=True)
 time.sleep(1.0)
rows=[]
for p,t in items:
 c=cache.get(t,{}) ; ib=infobox(c.get('wikitext','')); row={'q_id':f"Q{people.index(p)+1}",'name':p.get('name',''),'birth_date':p.get('birth_date',''),'source_url':p.get('source_url',''),'wikipedia_title':t,'source_status':'retrieved' if c else 'not_retrieved','retrieved_utc':c.get('retrieved_utc','')}
 for dest,aliases in fields_map.items():row[dest]=' | '.join(ib[a] for a in aliases if a in ib)
 text=c.get('extract','');row['incarceration_text_flag']='yes' if re.search(r'\b(imprison|incarcerat|jailed|detain|sentenced|convicted)\b',text,re.I) else 'no';row['source_note']='Raw infobox extraction; verify each date against cited source before statistical use'
 rows.append(row)
with open(RESULT,'w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
json.dump({'people':len(rows),'retrieved_pages':sum(r['source_status']=='retrieved' for r in rows),'fields':list(fields_map),'method':'Wikipedia API raw infobox/extract collection','warning':'Fields may be blank, ambiguous or template-formatted; no dates were inferred. Manual/source verification required.'},open(OUT+'/summary.json','w'),indent=2)
print('done',len(rows))
