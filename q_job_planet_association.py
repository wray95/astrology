#!/usr/bin/env python3
import csv, re, json, os
from collections import Counter
from scipy.stats import chi2_contingency

def bh_adjust(pvals):
    order=sorted(range(len(pvals)), key=lambda i:pvals[i]); q=[1.0]*len(pvals); prev=1.0; n=len(pvals)
    for rank,i in reversed(list(enumerate(order,1))):
        prev=min(prev,pvals[i]*n/rank); q[i]=prev
    return q, [q[i] < 0.05 for i in range(n)]
IN='outputs/all_planets_q_series/q_all_planet_positions.csv'; OUT='outputs/q_job_planet_association'; os.makedirs(OUT,exist_ok=True)

def group(s):
 s=(s or '').lower()
 if not s:return 'Unknown'
 rules=[('Athlete',r'player|athlete|golfer|boxer|wrestl|cyclist|runner|swimmer|skater|cricketer|football|baseball|basketball|rugby|hockey'),('Actor_Media',r'actor|actress|singer|film|television|tv|director|producer|comedian|musician|entertain'),('Politics_Government',r'politician|president|prime minister|emperor|king|queen|minister|governor|senator|military|general'),('Academic_Science',r'scientist|physic|chemist|mathematic|professor|scholar|astronom|research|academic'),('Writer_Journalism',r'author|writer|journal|poet|novelist|historian|illustrator'),('Law',r'lawyer|judge|attorney|jurist'),('Medicine',r'doctor|physician|surgeon|medical|psychiat'),('Business',r'business|entrepreneur|industrial|merchant|banker|investor|ceo|manager'),('Religion',r'pope|priest|monk|imam|rabbi|bishop|religious|theolog'),('Engineering_Tech',r'engineer|inventor|programmer|computer|technolog|architect')]
 for n,pat in rules:
  if re.search(pat,s):return n
 return 'Other'
rows=list(csv.DictReader(open(IN)))
meta={r['q_id']:r for r in csv.DictReader(open('outputs/saturn_returns_q_series/q_saturn_returns.csv'))}
for r in rows:
 r['occupation']=meta.get(r['q_id'],{}).get('occupation','')
 r['job_group']=group(r['occupation'])
planets=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Rahu_mean','Ketu']
res=[]; pvals=[]
for pl in planets:
 tab={}
 for r in rows: tab.setdefault(r['job_group'],Counter())[r[f'{pl}_sign']]+=1
 groups=sorted(tab); signs=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
 mat=[[tab[g][s] for s in signs] for g in groups]
 chi,p,dof,exp=chi2_contingency(mat); n=sum(map(sum,mat)); v=(chi/(n*min(len(groups)-1,len(signs)-1)))**.5
 res.append({'planet':pl,'n':n,'job_groups':len(groups),'chi_square':chi,'df':dof,'p_value':p,'cramers_v':v});pvals.append(p)
q,rej=bh_adjust(pvals)
for r,a,b in zip(res,rej,q):r['fdr_significant']=bool(a);r['fdr_q_value']=b
with open(os.path.join(OUT,'planet_job_tests.csv'),'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=res[0].keys());w.writeheader();w.writerows(res)
with open(os.path.join(OUT,'job_group_counts.csv'),'w',newline='') as f:
 w=csv.writer(f);w.writerow(['job_group','count']);w.writerows(Counter(r['job_group'] for r in rows).most_common())
json.dump({'method':'Exploratory association of occupation keyword groups with birth-date midpoint planetary sign','caution':'This is not a transit/event test; occupation is source-coded and may be biased. No causal inference. Multiple testing controlled by Benjamini-Hochberg FDR.','people':len(rows),'occupied_records':sum(r['job_group']!='Unknown' for r in rows)},open(os.path.join(OUT,'report.json'),'w'),indent=2)
print(json.dumps(res,indent=2))
