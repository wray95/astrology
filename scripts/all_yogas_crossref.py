#!/usr/bin/env python3
"""ALL YOGAS D1+D9 detection + cross-reference against 297 Q-series parents"""
import swisseph as swe, csv, gzip, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL={'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EXALT={'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL={'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN={'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
P7=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
VIM=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS={'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

def compute_chart(birth_date, lat=20, lon=77, tz=5.5):
    dt=datetime.strptime(birth_date+'T12:00:00','%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=tz)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360
    asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    p={}
    for pn,pid in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt,_=swe.calc_ut(jd,pid); lt=lt[0]
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30)
        p[pn]={'sign':sgn,'house':(si-asc_idx)%12+1,'dignity':100 if (pn in EXALT and EXALT[pn]==sgn) else (75 if (pn in OWN and sgn in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==sgn) else 0)),'sid':sid,'sign_idx':si}
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    for pn,rl in [('Rahu',rh),('Ketu',kh)]:
        sgn=SIGNS[int(rl//30)]; si=int(rl//30)
        p[pn]={'sign':sgn,'house':(si-asc_idx)%12+1,'dignity':0,'sid':rl,'sign_idx':si}
    asc_v9=(asc_sid*9)%360; v9_lagna=SIGNS[int(asc_v9//30)]; v9_li=SIGNS.index(v9_lagna)
    d9={'lagna':v9_lagna,'lagna_idx':v9_li,'planets':{}}
    for pn in P7:
        vl=(p[pn]['sid']*9)%360; vs=SIGNS[int(vl//30)]; vh=(SIGNS.index(vs)-v9_li)%12+1
        d9['planets'][pn]={'sign':vs,'house':vh,'dignity':100 if (pn in EXALT and EXALT[pn]==vs) else (75 if (pn in OWN and vs in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==vs) else 0))}
    return {'asc':asc_sign,'asc_idx':asc_idx,'planets':p,'d9':d9,'jd':jd,'ayan':ayan}

def get_chart(planets_dict, is_d9=False):
    """helper: return planets dict depending on D1 or D9"""
    if is_d9: return plan_dict.get('_d9_planets',planets_dict)
    return planets_dict

def detect_all_yogas(chart):
    p=chart['planets']; d9p=chart['d9']['planets']
    d9li=chart['d9']['lagna_idx']; li=chart['asc_idx']
    p['Rahu']=chart['planets']['Rahu']; p['Ketu']=chart['planets']['Ketu']
    y={}

    # Raja Yoga
    hinv={}; 
    for pn in P7: hinv.setdefault(p[pn]['house'],[]).append(pn)
    raja=set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            for kl in hinv.get(kh,[]):
                for ccl in hinv.get(ch,[]):
                    if kl!=ccl and p[kl]['house']==p[ccl]['house']: raja.add(tuple(sorted([kl,ccl])))
    y['d1_raja']=len(raja)

    # Parivartana
    g={}
    for pn in P7: 
        lord=SL[p[pn]['sign']]
        if lord!=pn: g[pn]=lord
    y['d1_pariv']=len([pn for pn in g if g.get(g.get(pn))==pn and pn<g[pn]])

    # Shrinkhala
    visited=set(); loops=[]
    for start in P7:
        path=[]; curr=start
        while curr in g and curr not in path: path.append(curr); curr=g[curr]
        if curr in path:
            cycle=path[path.index(curr):]; t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in visited: visited.add(t); loops.append(cycle)
    y['d1_shrink']=len(loops); y['d1_shrink_max']=max([len(l) for l in loops]) if loops else 0

    # MP
    y['d1_mp']=sum(1 for pl in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if p[pl[0]]['dignity']>=75 and p[pl[0]]['house'] in [1,4,7,10])

    # Dhana
    dhana=set()
    for dh in [2,11]:
        for th in [1,5,9,10]:
            for dl in hinv.get(dh,[]):
                for tl in hinv.get(th,[]):
                    if dl!=tl and p[dl]['house']==p[tl]['house']: dhana.add(tuple(sorted([dl,tl])))
    y['d1_dhana']=len(dhana)

    # Budha-Aditya
    y['d1_budha_aditya']=1 if ('Sun' in p and 'Mercury' in p and p['Sun']['house']==p['Mercury']['house']) else 0

    # Mer-Ven
    y['d1_mer_ven']=1 if ('Mercury' in p and 'Venus' in p and p['Mercury']['house']==p['Venus']['house']) else 0

    # Gaj-Kesari
    mh=p['Moon']['house']; jh=p['Jupiter']['house']
    y['d1_gaj_kesari']=1 if (mh in [(jh+2)%12+1,(jh+3)%12+1,(jh+4)%12+1,(jh+5)%12+1,(jh+6)%12+1,(jh+7)%12+1,(jh+8)%12+1,(jh+9)%12+1,(jh+10)%12+1] or mh==jh or jh in [(mh+3)%12+1,(mh+6)%12+1,(mh+9)%12+1]) else 0
    # Simplify: Moon in kendra from Jupiter or Jupiter in kendra from Moon
    y['d1_gaj_kesari']=1 if ((mh+3)%12+1==jh or (mh+6)%12+1==jh or (mh+9)%12+1==jh or mh==jh) else 0

    # VRY (6/8/12 lord in 6/8/12)
    vry=0
    for dh in [6,8,12]:
        dl_s=SIGNS[(li+dh-1)%12]; dl=SL[dl_s]
        if dl in p and p[dl]['house'] in [6,8,12]: vry+=1
    y['d1_vry']=vry

    # Chandra-Mangala
    y['d1_chandra_mangala']=1 if ('Moon' in p and 'Mars' in p and p['Moon']['house']==p['Mars']['house']) else 0

    # Lakshmi (Venus+9L connection)
    d1_9l_s=SIGNS[(li+8)%12]; d1_9l=SL[d1_9l_s]
    y['d1_lakshmi']=1 if (d1_9l in p and 'Venus' in p and (p['Venus']['house']==p[d1_9l]['house'] or (p['Venus']['house'] in [1,5,9] and p[d1_9l]['house'] in [1,5,9]))) else 0

    # NBRY
    nbr=0
    for pl in P7:
        if pl in p and p[pl]['dignity']==-100:
            c=0; dl2=SL[DEBIL[pl]]
            if dl2 in p and p[dl2]['house'] in [1,4,7,10]: c+=1
            el=SL[EXALT[pl]]
            if el in p: eh2=p[el]['house']; dh2=p[pl]['house']
            if (eh2+6)%12+1==dh2 or (eh2+4)%12+1==dh2: c+=1
            if p[pl]['house'] in [1,4,7,10]: c+=1; nbr=max(nbr,c)
    y['d1_nbry']=nbr

    # Sun+Jupiter conj
    y['d1_sun_jup']=1 if ('Sun' in p and 'Jupiter' in p and p['Sun']['house']==p['Jupiter']['house']) else 0

    # --- D9 YOGAS ---
    d9inv={}; [d9inv.setdefault(d9p[pn]['house'],[]).append(pn) for pn in P7]
    d9raja=set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            for kl in d9inv.get(kh,[]):
                for ccl in d9inv.get(ch,[]):
                    if kl!=ccl and d9p[kl]['house']==d9p[ccl]['house']: d9raja.add(tuple(sorted([kl,ccl])))
    y['d9_raja']=len(d9raja)

    g9={}
    for pn in P7: 
        lord9=SL[d9p[pn]['sign']]
        if lord9!=pn: g9[pn]=lord9
    y['d9_pariv']=len([pn for pn in g9 if g9.get(g9.get(pn))==pn and pn<g9[pn]])

    visited9=set(); loops9=[]
    for start in P7:
        path=[]; curr=start
        while curr in g9 and curr not in path: path.append(curr); curr=g9[curr]
        if curr in path:
            cycle=path[path.index(curr):]; t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in visited9: visited9.add(t); loops9.append(cycle)
    y['d9_shrink']=len(loops9); y['d9_shrink_max']=max([len(l) for l in loops9]) if loops9 else 0

    y['d9_mp']=sum(1 for pl in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if d9p[pl[0]]['dignity']>=75 and d9p[pl[0]]['house'] in [1,4,7,10])

    d9dhana=set()
    for dh in [2,11]:
        for th in [1,5,9,10]:
            for dl in d9inv.get(dh,[]):
                for tl in d9inv.get(th,[]):
                    if dl!=tl and d9p[dl]['house']==d9p[tl]['house']: d9dhana.add(tuple(sorted([dl,tl])))
    y['d9_dhana']=len(d9dhana)

    y['d9_budha_aditya']=1 if (d9p['Sun']['house']==d9p['Mercury']['house']) else 0
    y['d9_mer_ven']=1 if (d9p['Mercury']['house']==d9p['Venus']['house']) else 0
    mh9=d9p['Moon']['house']; jh9=d9p['Jupiter']['house']
    y['d9_gaj_kesari']=1 if ((mh9+3)%12+1==jh9 or (mh9+6)%12+1==jh9 or (mh9+9)%12+1==jh9 or mh9==jh9) else 0
    y['d9_chandra_mangala']=1 if (d9p['Moon']['house']==d9p['Mars']['house']) else 0
    d9_9l_s=SIGNS[(d9li+8)%12]; d9_9l=SL[d9_9l_s]
    y['d9_lakshmi']=1 if (d9_9l in d9p and (d9p['Venus']['house']==d9p[d9_9l]['house'] or (d9p['Venus']['house'] in [1,5,9] and d9p[d9_9l]['house'] in [1,5,9]))) else 0
    y['d9_sun_jup']=1 if (d9p['Sun']['house']==d9p['Jupiter']['house']) else 0
    y['d9_moon_5h']=1 if (d9p['Moon']['house']==5) else 0
    y['d9_5l_house']=d9p[SL[SIGNS[(d9li+4)%12]]]['house'] if SL[SIGNS[(d9li+4)%12]] in d9p else 0
    y['d9_5l_dignity']=d9p[SL[SIGNS[(d9li+4)%12]]]['dignity'] if SL[SIGNS[(d9li+4)%12]] in d9p else 0
    nbr9=0
    for pl in P7:
        if pl in d9p and d9p[pl]['dignity']==-100:
            c9=0; dl9=SL[DEBIL[pl]]
            if dl9 in d9p and d9p[dl9]['house'] in [1,4,7,10]: c9+=1
            el9=SL[EXALT[pl]]
            if el9 in d9p: eh9=d9p[el9]['house']; dh9=d9p[pl]['house']
            if (eh9+6)%12+1==dh9 or (eh9+4)%12+1==dh9: c9+=1
            if d9p[pl]['house'] in [1,4,7,10]: c9+=1; nbr9=max(nbr9,c9)
    y['d9_nbry']=nbr9

    # Moon nakshatra
    rl=p['Moon']['sid']
    NAKS=[('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]
    for n,s,l in NAKS:
        if s<=rl<s+13.334: y['moon_nak']=n; y['moon_nak_lord']=l; break

    return y

# ===== MAIN =====
children_map = {}
with gzip.open('outputs/q_biographical_wikipedia/q_biographical_details.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        kids=row.get('children','').strip()
        if kids and len(kids)>3 and kids not in ('N/A','None'):
            children_map[row['q_id']]={'name':row['name'],'kids':kids[:100]}

wealth_data = {}
with gzip.open('outputs/q_people_enriched/q_people_enriched.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        wealth_data[row['q_id']]={'career':row.get('career',''),'industry':row.get('industry_group',''),'wealth':row.get('wealth_details','')}

print(f'Computing ALL yogas for {len(children_map)} parents...')
results=[]
processed=0
with gzip.open('outputs/all_planets_q_series/q_all_planet_positions.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        qid=row['q_id']
        if qid not in children_map: continue
        bd=row.get('birth_date','')
        if bd.startswith('0') or not '-' in bd: continue
        try: chart=compute_chart(bd)
        except: continue
        yogas=detect_all_yogas(chart)
        yogas['qid']=qid; yogas['name']=children_map[qid]['name']
        yogas['kids']=children_map[qid]['kids']
        if qid in wealth_data:
            yogas['career']=wealth_data[qid]['career']
            yogas['industry']=wealth_data[qid]['industry']
            yogas['wealth']=wealth_data[qid]['wealth']
        results.append(yogas)
        processed+=1
        if processed%50==0: print(f'  {processed}...')

print(f'Done: {len(results)} charts with {len(yogas)-7} yoga types each.')

# SAVE
with open('/tmp/all_yogas_297.json','w') as f: json.dump(results,f,indent=2)

# SUMMARY TABLE
print()
print('='*80)
print('  ALL YOGA FREQUENCIES IN 297 PARENTS — CHILD & WEALTH EFFECTS')
print('='*80)
print()
print(f'  {"Yoga":<30s} {"D1%":>6s} {"D9%":>6s} {"Both%":>6s} {"KidsΔ":>6s} {"WlthΔ":>6s}  Signal')
print(f'  {"─"*30} {"─"*6} {"─"*6} {"─"*6} {"─"*6} {"─"*6}  {"─"*25}')

yoga_keys=['raja','pariv','shrink','mp','dhana','budha_aditya','mer_ven','gaj_kesari','sun_jup','chandra_mangala','lakshmi','nbry','vry']
yoga_labels={'raja':'Raja Yoga','pariv':'Parivartana','shrink':'Shrinkhala','mp':'Mahapurusha','dhana':'Dhana Yoga','budha_aditya':'Budha-Aditya','mer_ven':'Mercury-Venus','gaj_kesari':'Gaj-Kesari','sun_jup':'Sun-Jupiter conj','chandra_mangala':'Chandra-Mangala','lakshmi':'Lakshmi Yoga','nbry':'NBRY (max conds)','vry':'VRY (Viparita Raja)'}

N=len(results)
ww=['billion','million','fortune','wealth','rich','estate','ceo','founder','president','nobel','king','queen']

# Moon in 5H
d9_moon_5h=[r for r in results if r.get('d9_moon_5h')]
m5_multi=sum(1 for r in d9_moon_5h if ',' in r.get('kids','') or ' and ' in r.get('kids','').lower())
m5_wealth=sum(1 for r in d9_moon_5h if any(w in (r.get('wealth','')+r.get('career','')+r.get('industry','')).lower() for w in ww))
print(f'  {"★ D9 Moon in 5H":<30s} {"─":>6s} {len(d9_moon_5h)/N*100:>5.1f}% {"─":>6s} {m5_multi/len(d9_moon_5h)*100 if d9_moon_5h else 0:>5.0f}% {m5_wealth/len(d9_moon_5h)*100 if d9_moon_5h else 0:>5.0f}%  PUTRASTHANA — strongest child signal')

# D9 9L in 5H
d9_9l_5h=[r for r in results if r.get('d9_5l_house')==5]
m95_multi=sum(1 for r in d9_9l_5h if ',' in r.get('kids','') or ' and ' in r.get('kids','').lower())
print(f'  {"★ D9 5L in 5H":<30s} {"─":>6s} {len(d9_9l_5h)/N*100:>5.1f}% {"─":>6s} {m95_multi/len(d9_9l_5h)*100 if d9_9l_5h else 0:>5.0f}% {"─":>6}  5th lord in own house — dharma of children')

for yk in yoga_keys:
    d1_key=f'd1_{yk}'; d9_key=f'd9_{yk}'
    if d1_key not in results[0] and d9_key not in results[0]: continue
    
    # D1 count
    if yk=='nbry':
        d1_n=sum(1 for r in results if r.get(d1_key,0)>=2)
        d9_n=sum(1 for r in results if r.get(d9_key,0)>=2)
    elif yk in ('shrink','vry'):
        d1_n=sum(1 for r in results if r.get(d1_key,0)>0)
        d9_n=sum(1 for r in results if r.get(d9_key,0)>0)
    else:
        d1_n=sum(1 for r in results if r.get(d1_key,0)>0)
        d9_n=sum(1 for r in results if r.get(d9_key,0)>0)
    
    both_n=sum(1 for r in results if (r.get(d1_key,0)>0 or (yk=='nbry' and r.get(d1_key,0)>=2)) and (r.get(d9_key,0)>0 or (yk=='nbry' and r.get(d9_key,0)>=2)))
    
    # Kids multi-check for D1+D9 group
    both_group=[r for r in results if (r.get(d1_key,0)>0 or (yk=='nbry' and r.get(d1_key,0)>=2)) and (r.get(d9_key,0)>0 or (yk=='nbry' and r.get(d9_key,0)>=2))]
    all_group=[r for r in results]
    if both_group:
        b_multi=sum(1 for r in both_group if ',' in r.get('kids','') or ' and ' in r.get('kids','').lower())
        b_wealth=sum(1 for r in both_group if any(w in (r.get('wealth','')+r.get('career','')+r.get('industry','')).lower() for w in ww))
        a_multi=sum(1 for r in all_group if ',' in r.get('kids','') or ' and ' in r.get('kids','').lower())
        a_wealth=sum(1 for r in all_group if any(w in (r.get('wealth','')+r.get('career','')+r.get('industry','')).lower() for w in ww))
        kd=(b_multi/len(both_group)-a_multi/len(all_group))*100
        wd=(b_wealth/len(both_group)-a_wealth/len(all_group))*100
    else:
        kd=wd=0
    
    signal=''
    if kd>5: signal='STRONG KIDS ↑'
    elif kd>0: signal='slight kids ↑'
    elif kd<-5: signal='↓ kids'
    if wd>5: signal+=(' + ' if signal else '')+'WEALTH ↑'
    elif wd>0: signal+=(' + ' if signal else '')+'wealth ↑'
    
    label=yoga_labels.get(yk,yk)
    sign = '+' if kd > 0 else ''
    sign_w = '+' if wd > 0 else ''
    print(f'  {label:<30s} {d1_n/N*100:>5.1f}% {d9_n/N*100:>5.1f}% {both_n/N*100:>5.1f}% {sign}{kd:>5.0f}pp {sign_w}{wd:>5.0f}pp  {signal}')

print()
print('='*80)
print('  TOP YOGAS FOR CHILDREN')
print('='*80)
child_rank=[]
for yk in yoga_keys:
    both_g=[r for r in results if (r.get(f'd1_{yk}',0)>0) and (r.get(f'd9_{yk}',0)>0)]
    if len(both_g)>=3:
        rate=sum(1 for r in both_g if ',' in r.get('kids','') or ' and ' in r.get('kids','').lower())/len(both_g)*100
        child_rank.append((yoga_labels[yk],rate,len(both_g)))
child_rank.sort(key=lambda x:-x[1])
for i,(name,rate,n) in enumerate(child_rank[:15]):
    bar='█'*int(rate/5)
    print(f'  {i+1:>2}. {name:<28s} {rate:>5.1f}% ({n}) {bar}')

print()
print('='*80)
print('  TOP YOGAS FOR WEALTH/CAREER')
print('='*80)
wealth_rank=[]
for yk in yoga_keys:
    both_g=[r for r in results if (r.get(f'd1_{yk}',0)>0) and (r.get(f'd9_{yk}',0)>0)]
    if len(both_g)>=3:
        rate=sum(1 for r in both_g if any(w in (r.get('wealth','')+r.get('career','')+r.get('industry','')).lower() for w in ww))/len(both_g)*100
        wealth_rank.append((yoga_labels[yk],rate,len(both_g)))
wealth_rank.sort(key=lambda x:-x[1])
for i,(name,rate,n) in enumerate(wealth_rank[:15]):
    bar='█'*int(rate/2)
    print(f'  {i+1:>2}. {name:<28s} {rate:>5.1f}% ({n}) {bar}')
