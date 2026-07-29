#!/usr/bin/env python3
"""Date-only birth-degree/sign feature discovery for Q series.
House-free: only sign, longitude, degree, conjunction and planet dignity.
"""
import csv,json,os,re,math
from collections import Counter
from scipy.stats import chi2_contingency
IN='outputs/all_planets_q_series/q_all_planet_positions.csv'; META='outputs/saturn_returns_q_series/q_saturn_returns.csv'; OUT='outputs/birth_degree_pattern_pipeline'; os.makedirs(OUT,exist_ok=True)
EXALT={'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
SIGN_LORD={'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
CLASS=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']
def group(s):
 s=(s or '').lower(); rules=[('Athlete',r'player|athlete|golfer|boxer|wrestl|cyclist|runner|swimmer|skater|cricketer|football|baseball|basketball|rugby|hockey'),('Actor_Media',r'actor|actress|singer|film|television|tv|director|producer|comedian|musician|entertain'),('Politics_Government',r'politician|president|prime minister|emperor|king|queen|minister|governor|senator|military|general'),('Academic_Science',r'scientist|physic|chemist|mathematic|professor|scholar|astronom|research|academic'),('Writer_Journalism',r'author|writer|journal|poet|novelist|historian|illustrator'),('Law',r'lawyer|judge|attorney|jurist'),('Medicine',r'doctor|physician|surgeon|medical|psychiat'),('Business',r'business|entrepreneur|industrial|merchant|banker|investor|ceo|manager'),('Religion',r'pope|priest|monk|imam|rabbi|bishop|religious|theolog'),('Engineering_Tech',r'engineer|inventor|programmer|computer|technolog|architect')]
 for n,p in rules:
  if re.search(p,s): return n
 return 'Other' if s else 'Unknown'
def ang(a,b):return abs((a-b+180)%360-180)
rows=list(csv.DictReader(open(IN))); meta={r['q_id']:r for r in csv.DictReader(open(META))}
features=[]
for r in rows:
 active=[p for p in CLASS if r[f'{p}_sign']==EXALT.get(p)]
 pairs=[]
 for i,a in enumerate(CLASS):
  for b in CLASS[i+1:]:
   d=ang(float(r[f'{a}_longitude']),float(r[f'{b}_longitude']))
   if d<=8:pairs.append(f'{a}-{b}')
 sign_counts=Counter(r[f'{p}_sign'] for p in CLASS)
 # Sign-based exchange candidate: planet A is in B's sign and B in A's sign.
 exch=[]
 for a in CLASS:
  for b in CLASS:
   if a<b and SIGN_LORD.get(r[f'{a}_sign'])==b and SIGN_LORD.get(r[f'{b}_sign'])==a:exch.append(f'{a}-{b}')
 x={'q_id':r['q_id'],'name':r['name'],'birth_date':r['birth_date'],'occupation':meta.get(r['q_id'],{}).get('occupation',''),'job_group':group(meta.get(r['q_id'],{}).get('occupation','')),'exalted_planets':'|'.join(active) or 'None','exalted_count':len(active),'sign_conjunctions':'|'.join(pairs) or 'None','conjunction_count':len(pairs),'sign_exchange_candidates':'|'.join(exch) or 'None','exchange_count':len(exch)}
 for p in CLASS:x[f'{p}_exalted']=r[f'{p}_sign']==EXALT.get(p)
 features.append(x)
with open(os.path.join(OUT,'q_birth_features.csv'),'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=features[0].keys());w.writeheader();w.writerows(features)
# Feature x job group omnibus tests; exploratory only.
tests=[]; groups=sorted(set(x['job_group'] for x in features))
for p in CLASS:
 tab=Counter((x['job_group'],x[f'{p}_exalted']) for x in features); mat=[[tab[g,False],tab[g,True]] for g in groups]
 chi,pv,df,_=chi2_contingency(mat); n=sum(map(sum,mat)); v=math.sqrt(chi/(n*min(len(groups)-1,1)))
 tests.append({'feature':f'{p}_exalted','n':n,'chi_square':chi,'df':df,'p_value':pv,'cramers_v':v})
for feat in ['exalted_count','conjunction_count','exchange_count']:
 # discretize count to a small categorical set
 vals=sorted(set(x[feat] for x in features)); tab=Counter((x['job_group'],x[feat]) for x in features);mat=[[tab[g,v] for v in vals] for g in groups];chi,pv,df,_=chi2_contingency(mat);n=sum(map(sum,mat));v=math.sqrt(chi/(n*min(len(groups)-1,len(vals)-1))) if len(vals)>1 else 0
 tests.append({'feature':feat,'n':n,'chi_square':chi,'df':df,'p_value':pv,'cramers_v':v})
with open(os.path.join(OUT,'feature_job_tests.csv'),'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=tests[0].keys());w.writeheader();w.writerows(tests)
summary={'people':len(features),'classical_exaltation_definitions':EXALT,'feature_counts':{'any_exalted':sum(x['exalted_count']>0 for x in features),'sign_conjunction_candidate':sum(x['conjunction_count']>0 for x in features),'sign_exchange_candidate':sum(x['exchange_count']>0 for x in features)},'q_event_rows_available':0,'limitations':['No houses or Ascendant, so classical house-based yogas cannot be evaluated','A sign conjunction is not automatically a classical yoga','Occupation is source-coded and cohort-confounded','No Q-linked big-day events are available; event pattern testing is pending']}
json.dump(summary,open(os.path.join(OUT,'summary.json'),'w'),indent=2)
print(json.dumps(summary,indent=2))
