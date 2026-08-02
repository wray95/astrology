#!/usr/bin/env python3
import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from date_only_nexus import chart_for_date
CASES=[
 {'name':'Mahinda Rajapaksa','birth_date':'1945-11-18','election_date':'2005-11-17','inauguration_date':'2005-11-19','milestone':'Elected president; inaugurated two days later','source_urls':['https://en.wikipedia.org/wiki/2005_Sri_Lankan_presidential_election']},
 {'name':'Gotabaya Rajapaksa','birth_date':'1949-06-20','election_date':'2019-11-16','inauguration_date':'2019-11-18','milestone':'Elected president; sworn in two days later','source_urls':['https://www.un.int/srilanka/news/new-president-sworn']},
 {'name':'Anura Kumara Dissanayake','birth_date':'1968-11-24','election_date':'2024-09-21','inauguration_date':'2024-09-23','milestone':'Elected president; sworn in two days later; first post-independence president outside the two traditional party families','source_urls':['https://www.thehindu.com/news/international/anura-kumara-dissanayake-elected-sri-lanka-president/article68671042.ece','https://eastasiaforum.org/2024/09/28/a-political-and-policy-tightrope-awaits-sri-lanka-s-new-president/']}
]
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def from_moon(moon,planet):return (SIGNS.index(planet)-SIGNS.index(moon))%12+1
out=[]
for x in CASES:
 b=chart_for_date(x['birth_date']);e=chart_for_date(x['election_date']);bm=b['midpoint_planets'];em=e['midpoint_planets']; moon=bm['Moon']; sat=em['Saturn']
 x.update({'method':'Date-only UTC-noon midpoint; Lahiri sidereal; no birth time used','birth_moon':{'sign':moon['sign'],'degree':moon['degree'],'longitude':moon['longitude'],'nakshatra_midpoint':moon['nakshatra'],'sign_stable_over_UTC_day':b['daily_interval']['Moon']['sign_stable'],'nakshatra_time_sensitive':True},'election_year_saturn':{'sign':sat['sign'],'degree':sat['degree'],'longitude':sat['longitude'],'retrograde':sat['retrograde'],'speed_deg_day':sat['speed_deg_day'],'near_station_abs_speed_lt_0.01':abs(sat['speed_deg_day'])<0.01,'whole_sign_from_natal_moon':from_moon(moon['sign'],sat['sign'])},'election_year_planets':{p:{'sign':em[p]['sign'],'degree':em[p]['degree'],'retrograde':em[p]['retrograde']} for p in ['Saturn','Mars','Venus','Jupiter','Rahu_mean','Ketu']},'interpretation_status':'Descriptive alignment only; no causal inference'})
 out.append(x)
os.makedirs('outputs/sri_lanka_gochara',exist_ok=True)
json.dump(out,open('outputs/sri_lanka_gochara/sri_lanka_gochara_benchmark.json','w'),indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
