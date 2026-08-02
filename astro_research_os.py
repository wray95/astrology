#!/usr/bin/env python3
"""ASTROLOGY RESEARCH OS v2.0 — F00001-F05000+ Registry + Hypothesis Engine"""
import swisseph as swe, csv, gzip, json, os, numpy as np
from datetime import datetime, timezone, timedelta
from collections import Counter
import warnings; warnings.filterwarnings('ignore')
from scipy import stats
from sklearn.ensemble import RandomForestClassifier

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL={'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EXALT={'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL={'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN={'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
P7=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
VIM=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS={'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
NAKS=[('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]

B='='*65

# Register features F00001+
FEATURES={}; fid=0
def reg(desc,cat):
    global fid; fid+=1; FEATURES[f'{fid:05d}']={'desc':desc,'cat':cat}; return f'{fid:05d}'

for p in P7:
    reg(f'{p} exalted in D1','d1_dig'); reg(f'{p} debilitated in D1','d1_dig')
    reg(f'{p} own sign in D1','d1_dig'); reg(f'{p} in Kendra D1','d1_house')
    reg(f'{p} in Trikona D1','d1_house'); reg(f'{p} in Dusthana D1','d1_house')
    for h in range(1,13): reg(f'{p} in D1 H{h}','d1_house')
for p in P7:
    reg(f'{p} exalted in D9','d9_dig'); reg(f'{p} debilitated in D9','d9_dig')
    reg(f'{p} own sign in D9','d9_dig'); reg(f'{p} vargottama','vargottama')
    for h in range(1,13): reg(f'{p} in D9 H{h}','d9_house')
for p in P7:
    for h in range(1,13): reg(f'{p} in D10 H{h}','d10_house')
reg('D10 10L Kendra','d10_c'); reg('D10 10L Dusthana','d10_c')
reg('D10 10L in 6H','d10_c'); reg('D10 10L in 8H','d10_c'); reg('D10 10L in 12H','d10_c')
for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
    reg(f'{yn} MP','yoga')
reg('Raja Yoga count','yoga'); reg('Gaj-Kesari Yoga','yoga'); reg('Budha-Aditya Yoga','yoga')
reg('Chandra-Mangala Yoga','yoga'); reg('Lakshmi Yoga','yoga')
reg('Shrinkhala present','yoga'); reg('Shrinkhala max loop','yoga')
reg('Parivartana count','yoga'); reg('NBRY>=2','yoga'); reg('Guru-Chandal','yoga')
for md in VIM: reg(f'{md} MD','dasha')
for t in ['Saturn Return','Saturn Pre-Ingress','Saturn asp 5H','Saturn asp 10H','Saturn asp Lagna']:
    reg(t,'saturn')
for t in ['Jupiter 5H transit','Jupiter 9H transit','Jupiter 11H transit']: reg(t,'jupiter')
combos=[('Sat ex D1+D9','combo'),('Ven own D1+D9','combo'),('Moon ex + D9 Moon5H','combo'),('MP+Shrinkhala','combo'),('MP+Raja','combo')]
for desc,cat in combos: reg(desc,cat)
for o in ['WEALTH','CHILDREN','CAREER','MARRIAGE','FAME']: reg(f'[Y] {o}','outcome')

print(f'{B}')
print(f'  ASTROLOGY RESEARCH OS v2.0')
print(f'  Features registered: {len(FEATURES)} (F00001-F{fid:05d})')
print(f'  Categories: {dict(Counter(v["cat"] for v in FEATURES.values()).most_common(10))}')
print(f'{B}')

# Compute charts
def compute_chart(bd,lat=20,lon=77):
    dt=datetime.strptime(bd+'T12:00:00','%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone(timedelta(hours=0)))
    jd=swe.julday(dt.year,dt.month,dt.day,12); ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A'); asc_sid=(asc_trop[0]-ayan)%360; asc_idx=int(asc_sid//30)
    p={}
    for pn,pid in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt,_=swe.calc_ut(jd,pid); sid=(lt[0]-ayan)%360
        sgn=SIGNS[int(sid//30)]; h=(SIGNS.index(sgn)-asc_idx)%12+1
        dgn=100 if (pn in EXALT and EXALT[pn]==sgn) else (75 if (pn in OWN and sgn in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==sgn) else 0))
        nk=None
        for n,s,l in NAKS:
            if s<=sid<s+13.334: nk=n; break
        p[pn]={'sign':sgn,'house':h,'dignity':dgn,'nakshatra':nk,'sid':sid}
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360
    p['Rahu']={'sign':SIGNS[int(rh//30)],'house':(int(rh//30)-asc_idx)%12+1}
    v9l=(asc_sid*9)%360; v9li=SIGNS.index(SIGNS[int(v9l//30)])
    d9={}
    for pn in P7:
        vl=(p[pn]['sid']*9)%360; vs=SIGNS[int(vl//30)]; vh=(SIGNS.index(vs)-v9li)%12+1
        dgn9=100 if (pn in EXALT and EXALT[pn]==vs) else (75 if (pn in OWN and vs in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==vs) else 0))
        d9[pn]={'sign':vs,'house':vh,'dignity':dgn9}
    v10l=(asc_sid*10)%360; v10li=SIGNS.index(SIGNS[int(v10l//30)])
    d10={}
    for pn in P7:
        vl=(p[pn]['sid']*10)%360; vs=SIGNS[int(vl//30)]; vh=(SIGNS.index(vs)-v10li)%12+1
        d10[pn]={'sign':vs,'house':vh}
    d10_10l=SL[SIGNS[(v10li+9)%12]]; d10_10l_h=d10[d10_10l]['house'] if d10_10l in d10 else 0
    ms=p['Moon']['sid']; ml='?'; bal=0
    for n,s,l in NAKS:
        if s<=ms<s+13.334: bal=VIM_YRS[l]*(1-(ms-s)/13.334); ml=l; break
    rd=datetime(2026,7,31,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-dt).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    for _ in range(9):
        if elapsed+rem>yfb: md2=VIM[mli]; break
        elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    jd_now=swe.julday(2026,7,31,12); ayan_t=swe.get_ayanamsa(jd_now)
    lt_sat,_=swe.calc_ut(jd_now,6); sat_now=(lt_sat[0]-ayan_t)%360
    natal_sat_deg=SIGNS.index(p['Saturn']['sign'])*30+(p['Saturn']['sid']%30)
    sat_dist=min(abs(sat_now-natal_sat_deg),360-abs(sat_now-natal_sat_deg))
    natal_sat_start=SIGNS.index(p['Saturn']['sign'])*30
    pre_ingress=(natal_sat_start-sat_now+360)%360
    lt_jup,_=swe.calc_ut(jd_now,5); jup_now=(lt_jup[0]-ayan_t)%360
    jup_house=(SIGNS.index(SIGNS[int(jup_now//30)])-asc_idx)%12+1
    return {'planets':p,'d9':d9,'d10':d10,'d10_10l_h':d10_10l_h,'d10_10l':d10_10l,'asc':SIGNS[asc_idx],'asc_idx':asc_idx,'dasha_md':md2,'sat_dist':sat_dist,'pre_ingress':pre_ingress,'sat_house':p['Saturn']['house'],'jup_house':jup_house}

def make_features(ch):
    p=ch['planets']; d9=ch['d9']; d10=ch['d10']; v={}
    for pn in P7:
        v[f'{pn} exalted in D1']=1 if p[pn]['dignity']==100 else 0
        v[f'{pn} debilitated in D1']=1 if p[pn]['dignity']==-100 else 0
        v[f'{pn} own sign in D1']=1 if p[pn]['dignity']==75 else 0
        v[f'{pn} in Kendra D1']=1 if p[pn]['house'] in [1,4,7,10] else 0
        v[f'{pn} in Trikona D1']=1 if p[pn]['house'] in [5,9] else 0
        v[f'{pn} in Dusthana D1']=1 if p[pn]['house'] in [6,8,12] else 0
        for h in range(1,13): v[f'{pn} in D1 H{h}']=1 if p[pn]['house']==h else 0
    for pn in P7:
        if pn in d9:
            v[f'{pn} exalted in D9']=1 if d9[pn]['dignity']==100 else 0
            v[f'{pn} debilitated in D9']=1 if d9[pn]['dignity']==-100 else 0
            v[f'{pn} own sign in D9']=1 if d9[pn]['dignity']==75 else 0
            v[f'{pn} vargottama']=1 if p[pn]['sign']==d9[pn]['sign'] else 0
            for h in range(1,13): v[f'{pn} in D9 H{h}']=1 if d9[pn]['house']==h else 0
    for pn in P7:
        if pn in d10:
            for h in range(1,13): v[f'{pn} in D10 H{h}']=1 if d10[pn]['house']==h else 0
    v['D10 10L Kendra']=1 if ch['d10_10l_h'] in [1,4,7,10] else 0
    v['D10 10L Dusthana']=1 if ch['d10_10l_h'] in [6,8,12] else 0
    v['D10 10L in 6H']=1 if ch['d10_10l_h']==6 else 0
    v['D10 10L in 8H']=1 if ch['d10_10l_h']==8 else 0
    v['D10 10L in 12H']=1 if ch['d10_10l_h']==12 else 0
    for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        v[f'{yn} MP']=1 if p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10] else 0
    hinv={}
    for pn in P7: hinv.setdefault(p[pn]['house'],[]).append(pn)
    raja=0
    for kh in [1,4,7,10]:
        for tr in [1,5,9]:
            for kl in hinv.get(kh,[]):
                for ccl in hinv.get(tr,[]):
                    if kl!=ccl and p[kl]['house']==p[ccl]['house']: raja+=1
    v['Raja Yoga count']=min(raja,10)
    mh=p['Moon']['house']; jh=p['Jupiter']['house']
    v['Gaj-Kesari Yoga']=1 if (mh+3)%12+1==jh or (mh+6)%12+1==jh or (mh+9)%12+1==jh or mh==jh else 0
    v['Budha-Aditya Yoga']=1 if p['Sun']['house']==p['Mercury']['house'] else 0
    v['Chandra-Mangala Yoga']=1 if p['Moon']['house']==p['Mars']['house'] else 0
    d1_9l=SL[SIGNS[(ch['asc_idx']+8)%12]]
    v['Lakshmi Yoga']=1 if (d1_9l in p and (p['Venus']['house']==p[d1_9l]['house'] or (p['Venus']['house'] in [1,5,9] and p[d1_9l]['house'] in [1,5,9]))) else 0
    g={}
    for pn in P7:
        lord=SL[p[pn]['sign']]
        if lord!=pn: g[pn]=lord
    loops5=[]; visited=set()
    for start in P7:
        path=[]; curr=start
        while curr in g and curr not in path: path.append(curr); curr=g[curr]
        if curr in path:
            cycle=path[path.index(curr):]; t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in visited: visited.add(t); loops5.append(cycle)
    v['Shrinkhala present']=1 if loops5 else 0
    v['Shrinkhala max loop']=max([len(l) for l in loops5]) if loops5 else 0
    pariv=len([pz for pz in g if g.get(g.get(pz))==pz and pz<g[pz]])
    v['Parivartana count']=min(pariv,5)
    nbr=0
    for pl in P7:
        if p[pl]['dignity']==-100:
            c=0; dl2=SL[DEBIL[pl]]
            if dl2 in p and p[dl2]['house'] in [1,4,7,10]: c+=1
            el2=SL[EXALT[pl]]
            if el2 in p:
                eh2=p[el2]['house']; dh2=p[pl]['house']
                if (eh2+6)%12+1==dh2 or (eh2+4)%12+1==dh2: c+=1
            if p[pl]['house'] in [1,4,7,10]: c+=1; nbr=max(nbr,c)
    v['NBRY>=2']=1 if nbr>=2 else 0
    v['Guru-Chandal']=1 if 'Rahu' in p and p['Jupiter']['house']==p['Rahu']['house'] else 0
    v[f'{ch["dasha_md"]} MD']=1
    v['Saturn Return']=1 if ch['sat_dist']<3 else 0
    v['Saturn Pre-Ingress']=1 if 3<=ch['pre_ingress']<=18 else 0
    sat_h=ch['sat_house']
    v['Saturn asp 5H']=1 if (sat_h+4)%12+1==5 or (sat_h+6)%12+1==5 or (sat_h+9)%12+1==5 else 0
    v['Saturn asp 10H']=1 if (sat_h+4)%12+1==10 or (sat_h+6)%12+1==10 or (sat_h+9)%12+1==10 else 0
    v['Saturn asp Lagna']=1 if (sat_h+4)%12+1==1 or (sat_h+6)%12+1==1 or (sat_h+9)%12+1==1 else 0
    v['Jupiter 5H transit']=1 if ch['jup_house']==5 else 0
    v['Jupiter 9H transit']=1 if ch['jup_house']==9 else 0
    v['Jupiter 11H transit']=1 if ch['jup_house']==11 else 0
    v['Sat ex D1+D9']=1 if (p['Saturn']['dignity']==100 and d9.get('Saturn',{}).get('dignity',0)==100) else 0
    v['Ven own D1+D9']=1 if (p['Venus']['dignity']>=75 and d9.get('Venus',{}).get('dignity',0)>=75) else 0
    v['Moon ex + D9 Moon5H']=1 if (p['Moon']['dignity']==100 and d9.get('Moon',{}).get('house')==5) else 0
    has_mp=sum(1 for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10])>0
    v['MP+Shrinkhala']=1 if (has_mp and loops5) else 0
    v['MP+Raja']=1 if (has_mp and raja>0) else 0
    return v

# Build matrix
print('Building feature matrix from Q-series...')
bio_map={}
with gzip.open('outputs/q_biographical_wikipedia/q_biographical_details.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        kids=row.get('children','').strip()
        bio_map[row['q_id']]=1 if (kids and len(kids)>3 and kids not in ('N/A','None')) else 0
enrich_map={}
with gzip.open('outputs/q_people_enriched/q_people_enriched.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        enrich_map[row['q_id']]=row.get('wealth_details','')+' '+row.get('career','')
wk=['billion','million','fortune','wealth','rich','estate','ceo','founder','president','nobel','king','queen','general','admiral','governor','prime minister']

X_list=[]; y_w=[]; y_c=[]
with gzip.open('outputs/all_planets_q_series/q_all_planet_positions.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        bd=row.get('birth_date','')
        if not bd or bd.startswith('0'): continue
        try:
            ch=compute_chart(bd); vec=make_features(ch)
            X_list.append(vec)
            tx=enrich_map.get(row['q_id'],'').lower()
            y_w.append(1 if any(k in tx for k in wk) else 0)
            y_c.append(bio_map.get(row['q_id'],0))
        except: pass

print(f'  Charts: {len(X_list)}')
all_descs=sorted(set.union(*[set(v.keys()) for v in X_list]))
fmap={v['desc']:k for k,v in FEATURES.items()}
X=np.zeros((len(X_list),len(all_descs)),dtype=np.float32)
for i,vec in enumerate(X_list):
    for j,d in enumerate(all_descs): X[i,j]=vec.get(d,0)
y_w2=np.array(y_w); y_c2=np.array(y_c)
print(f'  Features: {len(all_descs)} | Wealth+: {int(y_w2.sum())} | Children+: {int(y_c2.sum())}')

# Hypothesis engine
print(f'\n{B}')
print(f'  HYPOTHESIS ENGINE — Classical Rule Validation')
print(f'{B}')

H_TESTS=[
    ('H001','Sat ex D1 → wealth','Saturn exalted in D1',y_w2),
    ('H002','Moon ex → children','Moon exalted in D1',y_c2),
    ('H003','Ven own D9 → children','Venus own sign in D9',y_c2),
    ('H004','Shrinkhala → wealth','Shrinkhala present',y_w2),
    ('H005','Gaj-Kesari → wealth','Gaj-Kesari Yoga',y_w2),
    ('H006','Parivartana → wealth','Parivartana count',y_w2),
    ('H007','D10 10L Kendra → wealth','D10 10L Kendra',y_w2),
    ('H008','Budha-Aditya → wealth','Budha-Aditya Yoga',y_w2),
    ('H009','Moon ex+D9Moon5H → children','Moon ex + D9 Moon5H',y_c2),
    ('H010','Sat asp 5H → children','Saturn asp 5H',y_c2),
    ('H011','NBRY → wealth','NBRY>=2',y_w2),
    ('H012','Raja count → wealth','Raja Yoga count',y_w2),
    ('H013','Shrinkhala len → wealth','Shrinkhala max loop',y_w2),
    ('H014','D10 Dusthana → wealth','D10 10L Dusthana',y_w2),
    ('H015','Jup 5H transit → children','Jupiter 5H transit',y_c2),
]

results=[]
for hid,desc,fname,yt in H_TESTS:
    if fname not in all_descs: continue
    ci=all_descs.index(fname); fc=X[:,ci]
    pos=(fc>=1) if 'count' in fname or 'loop' in fname else (fc==1)
    neg=~pos
    if pos.sum()<10: continue
    pr=yt[pos].mean(); nr=yt[neg].mean()
    np_=int(pos.sum()); nn_=int(neg.sum())
    try:
        ct=np.array([[pr*np_,(1-pr)*np_],[nr*nn_,(1-nr)*nn_]])
        chi2,pv,_,_=stats.chi2_contingency(ct.clip(1))
    except: chi2,pv=0,1.0
    effect=pr-nr
    or_=(pr/(1-pr))/(nr/(1-nr)) if nr>0 and nr<1 and pr>0 and pr<1 else 1.0
    rf=RandomForestClassifier(n_estimators=100,max_depth=6,random_state=42,n_jobs=1)
    rf.fit(X,yt); imp=rf.feature_importances_[ci]
    ev='STRONG⭐' if pv<0.01 and abs(effect)>0.03 else ('MODERATE' if pv<0.05 or abs(effect)>0.02 else 'WEAK')
    results.append({'id':hid,'desc':desc,'+Rate':round(pr,3),'-Rate':round(nr,3),
        'effect':round(effect,3),'OR':round(or_,2),'p':round(pv,4),'RF':round(imp,4),
        'n_pos':np_,'n_neg':nn_,'evidence':ev})
results.sort(key=lambda r:(-abs(r['effect']),r['p']))

print(f'  {"H":<6} {"Hypothesis":<48} {"PosRt":>7} {"NegRt":>7} {"Effect":>7} {"p-val":>7} {"RF":>6} {"Evid":<10}')
print(f'  {"-"*6} {"-"*48} {"-"*7} {"-"*7} {"-"*7} {"-"*7} {"-"*6} {"-"*10}')
for r in results:
    eff_str = f'{r["effect"]:+.3f}' if r["effect"] != 0 else ' 0.000'
    print(f'  {r["id"]:<6} {r["desc"][:47]:<48} {r["+Rate"]:>7.3f} {r["-Rate"]:>7.3f} {eff_str:>7} {r["p"]:>7.4f} {r["RF"]:>6.4f} {r["evidence"]:<10}')

# Save
np.savez_compressed('dataset/astro_research_os_matrix.npz',X=X,y_wealth=y_w2,y_children=y_c2,
    feature_ids=np.array([fmap.get(d,'F00000') for d in all_descs]),feature_descs=np.array(all_descs))
with open('dataset/astro_research_os_features.json','w') as f: json.dump(FEATURES,f,indent=2)
with open('dataset/astro_research_os_hypotheses.json','w') as f: json.dump(results,f,indent=2)

strong=sum(1 for r in results if 'STRONG' in r['evidence'])
mod=sum(1 for r in results if 'MODERATE' in r['evidence'])
print(f'\n{B}')
print(f'  SAVED: {len(results)} hypotheses | STRONG: {strong} | MODERATE: {mod} | WEAK: {len(results)-strong-mod}')
print(f'  Files: astro_research_os_matrix.npz, astro_research_os_features.json, astro_research_os_hypotheses.json')
print(f'{B}')
