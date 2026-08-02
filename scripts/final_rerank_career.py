#!/usr/bin/env python3
"""P1-P9 FINAL RERANK — Career Path + Wealth Level"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
VIM = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN=360/27; P7=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

def gn(lon):
    lon%=360
    for n,s,l in NAKS:
        if s<=lon<s+NAK_SPAN: return n,l,(lon-s)/NAK_SPAN
    return 'Revati','Mercury',0

def dg(p,s):
    if p in EXALT and EXALT[p]==s: return 100
    if p in OWN and s in OWN[p]: return 75
    if p in DEBIL and DEBIL[p]==s: return -100
    return 0

P_CHARTS = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"note":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"note":"Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5},
]

def compute(c):
    dt=datetime.strptime(c['birthday']+'T'+c['birth_time'],'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    asc_trop,_=swe.houses_ex(jd,c['lat'],c['lon'],b'A')
    ayan=swe.get_ayanamsa(jd)
    asc_sid=(asc_trop[0]-ayan)%360; asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    p={}
    for pn,pid in PLANETS_MAP.items():
        lt,_=swe.calc_ut(jd,pid); lt=lt[0]
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30)
        nk,nl,_=gn(sid)
        p[pn]={'sidereal':round(sid,4),'sign':sgn,'sign_idx':si,'deg_in_sign':round(sid%30,4),'dignity':dg(pn,sgn),'nakshatra':nk,'nakshatra_lord':nl,'house':(si-asc_idx)%12+1}
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    for pn,rl in [('Rahu',rh),('Ketu',kh)]:
        sgn=SIGNS[int(rl//30)]; si=int(rl//30); nk,nl,_=gn(rl)
        p[pn]={'sidereal':round(rl,4),'sign':sgn,'sign_idx':si,'deg_in_sign':round(rl%30,4),'dignity':0,'nakshatra':nk,'nakshatra_lord':nl,'house':(si-asc_idx)%12+1}
    ms=p['Moon']['sidereal']; ml=mn='?'; bal=0
    for n,s,l in NAKS:
        if s<=ms<s+NAK_SPAN: bal=VIM_YRS[l]*(1-(ms-s)/NAK_SPAN); ml=l; mn=n; break
    return {'ascendant':{'sign':asc_sign,'deg':round(asc_sid%30,4)},'planets':p,'moon_nakshatra':{'name':mn,'lord':ml,'balance_yrs':round(bal,2)}}

def varga(d1,div):
    p=d1['planets']; asc_sid=d1['ascendant']['deg']+SIGNS.index(d1['ascendant']['sign'])*30
    vp={}
    for pn in p: vlon=(p[pn]['sidereal']*div)%360; vp[pn]={'sign':SIGNS[int(vlon//30)]}
    vl=SIGNS[int((asc_sid*div)%360//30)]; vli=SIGNS.index(vl)
    for pn in vp: vp[pn]['house']=(SIGNS.index(vp[pn]['sign'])-vli)%12+1
    return {'lagna':vl,'planets':vp}

def shrinkhala(p):
    signs_of={pn:p[pn]['sign'] for pn in P7 if pn in p and p[pn].get('sign')}
    in_sign_of={}
    for pn,sign in signs_of.items():
        lord=SL.get(sign)
        if lord and lord!=pn: in_sign_of[pn]=lord
    loops=[]
    def dfs(start,current,path):
        if len(path)>7: return
        if current==start and len(path)>=2: loops.append(path[:]); return
        if current in path[:-1]: return
        nxt=in_sign_of.get(current)
        if nxt and nxt not in path[1:-1]: dfs(start,nxt,path+[nxt])
    for start in P7:
        if start in in_sign_of: dfs(start,in_sign_of[start],[start,in_sign_of[start]])
    unique=[]; seen=set()
    for loop in loops:
        mi=min(range(len(loop)),key=lambda i:loop[i])
        rot=tuple(loop[mi:]+loop[:mi])
        if rot not in seen: seen.add(rot); unique.append(list(rot))
    return unique

results=[]
for c in P_CHARTS:
    d1=compute(c); d1['id']=c['id']; d1['name']=c['name']; d1['note']=c.get('note','')
    p=d1['planets']; asc=d1['ascendant']['sign']; ai=SIGNS.index(asc)
    houses={h:SL[SIGNS[(ai+h-1)%12]] for h in range(1,13)}
    
    d9=varga(d1,9); d10=varga(d1,10); d10i=SIGNS.index(d10['lagna'])
    d10_10l_sign=SIGNS[(d10i+9)%12]; d10_10l=SL[d10_10l_sign]
    d10_10l_house=d10['planets'][d10_10l]['house'] if d10_10l in d10['planets'] else 0
    
    loops=shrinkhala(p)
    
    score=0
    mp=0; mp_names=[]
    for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if pl in p and p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10]:
            mp+=1; mp_names.append(yn+':'+pl+' H'+str(p[pl]['house']))
    score+=mp*4.0
    
    has_shrink=len(loops)>0
    score+=2.0 if has_shrink else 0
    if len(loops)>=2: score+=1.0
    
    raja=0; seen=set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            kl=houses[kh]; cl=houses[ch]
            if kl==cl: continue
            key=tuple(sorted([kl,cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house']==p[cl]['house']:
                seen.add(key); raja+=1
    score+=raja*1.0
    
    if d10_10l_house in [1,4,7,10]: score+=2.5
    elif d10_10l_house in [6,8,12]: score-=2.5
    
    d9_venus=d9['planets'].get('Venus',{}).get('sign','?')
    if d9_venus in ['Taurus','Libra','Pisces']: score+=2.0
    elif d9_venus=='Virgo': score-=2.0
    
    nbr_max=0
    for pl in P7:
        if pl not in p or p[pl]['dignity']!=-100: continue
        conds=0
        dl=SL[DEBIL[pl]]
        if dl in p and p[dl]['house'] in [1,4,7,10]: conds+=1
        el=SL[EXALT[pl]]
        if el in p:
            eh,dh=p[el]['house'],p[pl]['house']
            if (eh+6)%12+1==dh or ((eh+4)%12+1==dh): conds+=1
        if p[pl]['house'] in [1,4,7,10]: conds+=1
        nbr_max=max(nbr_max,conds)
    if nbr_max>=4: score+=3.0
    elif nbr_max>=2: score+=1.0
    
    varg=sum(1 for pl in P7 if pl in d9['planets'] and pl in p and d9['planets'][pl]['sign']==p[pl]['sign'])
    score+=varg*0.5
    
    d60=varga(d1,60); d60i=SIGNS.index(d60['lagna']); d60_ll=SL[d60['lagna']]
    d60_ll_house=d60['planets'][d60_ll]['house'] if d60_ll in d60['planets'] else 0
    if d60_ll_house in [1,4,7,10]: score+=1.0
    elif d60_ll_house in [6,8,12]: score-=1.0
    
    moon_nak=p['Moon']['nakshatra']
    if moon_nak in ['Shravana','Swati','Purva Bhadrapada','Mula']: score+=1.0
    
    if 'Sun' in p and 'Mercury' in p and p['Sun']['house']==p['Mercury']['house']: score+=1.0
    if 'Mercury' in p and 'Venus' in p and p['Mercury']['house']==p['Venus']['house']: score+=1.0
    
    ex_cnt=sum(1 for pl in P7 if pl in p and p[pl]['dignity']==100)
    deb_cnt=sum(1 for pl in P7 if pl in p and p[pl]['dignity']==-100)
    score+=(ex_cnt-deb_cnt)*0.5
    
    # Dasha
    ml=d1['moon_nakshatra']['lord']; bal=d1['moon_nakshatra']['balance_yrs']
    bd=datetime.strptime(c['birthday']+'T'+c['birth_time'],'%Y-%m-%dT%H:%M:%S')
    bd=bd.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    rd=datetime(2026,7,15,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-bd).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    while elapsed+rem<=yfb: elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    cmd=VIM[mli]; nmd=VIM[(mli+1)%9]; pct=round((yfb-elapsed)/rem*100,1)
    adi=VIM.index(cmd); ad_elapsed=0
    for ai in range(9):
        al=VIM[(adi+ai)%9]; ad=VIM_YRS[al]/120*VIM_YRS[cmd]
        if ad_elapsed+ad>yfb-elapsed: cad=al; break
        ad_elapsed+=ad
    
    top_planets=sorted([(pn,p[pn]['dignity'],p[pn]['house']) for pn in P7 if pn in p],key=lambda x:(-(x[1]==100),-(x[1]==75),-(x[2] in [1,4,7,10])))
    archetype_map={'Sun':'Executive/Leadership','Mars':'Executive/Operations','Mercury':'Logic/Systems','Saturn':'Governance/Structure','Venus':'Creative/Commerce','Jupiter':'Advisory/Wisdom','Moon':'Public/Influence'}
    primary=top_planets[0][0]
    archetype=archetype_map.get(primary,'General')
    
    career_paths={
        'Executive/Leadership':['Government','Corporate Leadership','Military/Defense','Politics'],
        'Executive/Operations':['Industrial CEO','Manufacturing','Supply Chain','Construction'],
        'Logic/Systems':['Software/Tech','Quant Finance','Data Science','Engineering'],
        'Governance/Structure':['Audit/Compliance','Government Director','Law','Infrastructure'],
        'Creative/Commerce':['Luxury/Beauty','Media/Entertainment','Design','Fashion'],
        'Advisory/Wisdom':['Psychology','Consulting','Academia','Law'],
        'Public/Influence':['Media','Politics','PR/Communications','Education'],
    }
    paths=career_paths.get(archetype,['General'])
    
    if d10_10l_house in [1,4,7,10]: stability='Stable Kendra path'
    elif d10_10l_house in [6,8,12]: stability='Volatile transformation path'
    else: stability='Adaptable path'
    
    wealth='Moderate'; wi=[]
    if mp>=2: wealth='High'; wi.append(str(mp)+' Mahapurushas')
    elif mp==1 and has_shrink: wealth='High'; wi.append('MP+Shrinkhala')
    elif has_shrink: wealth='Above Average'; wi.append('Shrinkhala')
    if d10_10l_house in [1,4,7,10]: wealth='Above Average' if wealth=='Moderate' else wealth
    if d10_10l_house in [6,8,12] and wealth=='High': wealth='Above Average'
    if raja>=3: wealth='Above Average' if wealth=='Moderate' else wealth
    wmap={'High':3,'Above Average':2,'Moderate':1}
    if d10_10l_house in [1,4,7,10] and wmap.get(wealth,0)<2: wealth='Above Average'
    
    results.append({
        'id':c['id'],'name':c['name'],'note':c.get('note',''),
        'score':round(score,1),'asc':asc,'mp':mp,'mp_names':mp_names,
        'has_shrinkhala':has_shrink,'shrinkhala_count':len(loops),
        'raja':raja,'d10_10l_house':d10_10l_house,'d9_venus':d9_venus,
        'nbr_max':nbr_max,'vargottama':varg,'moon_nak':moon_nak,
        'dasha':cmd+'/'+cad,'dasha_pct':pct,
        'archetype':archetype,'career_paths':paths[:2],'stability':stability,
        'wealth':wealth,'wealth_indicators':wi,
    })

results.sort(key=lambda x:-x['score'])

print('='*115)
print('P1-P9 FINAL CALIBRATED RERANK — Career Path + Wealth Level')
print('='*115)
print(f"{'Rk':<4} {'ID':<4} {'Name':<20} {'Score':>6} {'Lagna':<8} {'Moon':<16} {'MP':>3} {'Shrink':>6} {'D10':>4} {'D9_':<10} {'Career Path':<28} {'Wealth':<14} {'Dasha':<14}")
print('-'*130)

for i,r in enumerate(results,1):
    tier=' B' if r['note'] else 'A'
    print(f"{i:<4} {r['id']:<4} {r['name']:<20} {r['score']:>6.1f} {r['asc']:<8} {r['moon_nak']:<16} {r['mp']:>3} {'Y' if r['has_shrinkhala'] else 'N':>6} {r['d10_10l_house']:>4} {r['d9_venus']:<10} {r['career_paths'][0][:26]:<28} {r['wealth']:<14} {r['dasha']:<14}")

print(f"\n{'='*115}")
print("DETAIL CARDS")
print('='*115)
for i,r in enumerate(results,1):
    tier=' [REF ONLY]' if r['note'] else ''
    print(f"\n#{i} {r['id']} {r['name']} — Score={r['score']}{tier}")
    print(f"  Lagna: {r['asc']} | Moon: {r['moon_nak']} | Dasha: {r['dasha']} ({r['dasha_pct']}% thru)")
    print(f"  Career: {r['archetype']} -> {' | '.join(r['career_paths'])}")
    print(f"  Path: {r['stability']} (D10 10L H{r['d10_10l_house']})")
    print(f"  Wealth: {r['wealth']} — {', '.join(r['wealth_indicators']) if r['wealth_indicators'] else 'standard channels'}")
    if r['mp']: print(f"  MP: {r['mp']} ({', '.join(r['mp_names'])})")
    if r['has_shrinkhala']: print(f"  Shrinkhala: {r['shrinkhala_count']} loop(s)")
    if r['raja']: print(f"  Raja Yogas: {r['raja']}")
    if r['nbr_max']>=4: print(f"  NBRY: {r['nbr_max']} conditions — STRONG")
    elif r['nbr_max']>=2: print(f"  NBRY: {r['nbr_max']} conditions — moderate")
    if r['d9_venus'] in ['Taurus','Libra','Pisces']: print(f"  D9 Venus: {r['d9_venus']} — ethical wealth channel")
    elif r['d9_venus']=='Virgo': print(f"  D9 Venus: DEBIL — compromised ethics risk")
    if r['vargottama']: print(f"  Vargottama: {r['vargottama']}")
    if r['note']: print(f"  WARNING: {r['note']} — ALL FEATURES UNRELIABLE")

with open('dataset/p1p9_final_career_wealth.json','w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to dataset/p1p9_final_career_wealth.json")
