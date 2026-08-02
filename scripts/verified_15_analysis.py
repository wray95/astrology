#!/usr/bin/env python3
"""
VERIFIED 15 TIER A CHARTS — Compute, verify Moon nakshatras, run 3-layer analysis, cross-ref P1-P9
"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
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

VERIFIED = [
    # name, bday, btime, lat, lon, tz, expected_moon_nak, wealth, social
    ("Jeff Bezos","1964-01-12","11:28:00",35.084,-106.65,-7,"Uttara Ashadha","Rich","Neutral"),
    ("Elon Musk","1971-06-28","19:30:00",-25.747,28.229,2,"Revati","Rich","Neutral"),
    ("Warren Buffett","1930-08-30","15:00:00",41.256,-95.934,-6,"Chitra","Rich","Good"),
    ("Bill Gates","1955-10-28","22:00:00",47.606,-122.332,-8,"Rohini","Rich","Good"),
    ("Neil Armstrong","1930-08-05","00:31:00",40.565,-84.195,-5,"Mula","Neutral","Good"),
    ("Yuri Gagarin","1934-03-09","06:00:00",55.55,35.016,3,"Mula","Neutral","Good"),
    ("Mahatma Gandhi","1869-10-02","07:11:00",21.642,69.609,5.17,"Uttara Ashadha","Neutral","Good"),
    ("Martin Luther King Jr.","1929-01-15","12:00:00",33.749,-84.388,-5,"Krittika","Neutral","Good"),
    ("Adolf Hitler","1889-04-20","18:30:00",48.259,13.035,1.08,"Pushya","Neutral","Bad"),
    ("Bernie Madoff","1938-04-29","19:35:00",40.728,-73.794,-5,"Anuradha","Poor","Bad"),
    ("J. Robert Oppenheimer","1904-04-22","23:00:00",40.712,-74.006,-5,"Purva Bhadrapada","Neutral","Mixed"),
    ("Steve Jobs","1955-02-24","19:15:00",37.774,-122.419,-8,"Mrigashira","Rich","Neutral"),
    ("Taylor Swift","1989-12-13","05:17:00",40.335,-75.926,-5,"Krittika","Rich","Good"),
    ("Usain Bolt","1986-08-21","09:30:00",18.329,-77.568,-5,"Ashwini","Rich","Good"),
    ("Marie Curie","1867-11-07","12:00:00",52.229,21.012,1,"Rohini","Neutral","Good"),
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
    ms=p['Moon']['sidereal']; ml=mn='?'
    for n,s,l in NAKS:
        if s<=ms<s+NAK_SPAN: ml=l; mn=n; break
    return {'ascendant':{'sign':asc_sign,'deg':round(asc_sid%30,4),'sidereal':round(asc_sid,4)},'planets':p,'moon_nakshatra':mn}

def varga(d1,div):
    p=d1['planets']; asc_sid=d1['ascendant']['sidereal']
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
for name,bday,btime,lat,lon,tz,exp_nak,wealth,social in VERIFIED:
    c={'birthday':bday,'birth_time':btime,'lat':lat,'lon':lon,'tz':tz}
    d1=compute(c); p=d1['planets']; asc=d1['ascendant']['sign']; ai=SIGNS.index(asc)
    houses={h:SL[SIGNS[(ai+h-1)%12]] for h in range(1,13)}
    
    moon_nak=d1['moon_nakshatra']
    nak_match='✓' if moon_nak==exp_nak else f'✗ (expected {exp_nak})'
    
    # Mahapurusha
    mp=0; mp_names=[]
    for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if pl in p and p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10]:
            mp+=1; mp_names.append(yn+':'+pl)
    
    # Shrinkhala
    loops=shrinkhala(p); has_shrink=len(loops)>0
    
    # D10
    d10=varga(d1,10); d10i=SIGNS.index(d10['lagna'])
    d10_10l=SL[SIGNS[(d10i+9)%12]]
    d10_10l_house=d10['planets'][d10_10l]['house'] if d10_10l in d10['planets'] else 0
    
    # D9 Venus
    d9=varga(d1,9); d9_venus=d9['planets'].get('Venus',{}).get('sign','?')
    
    # NBRY
    nbr_max=0
    for pl in P7:
        if pl not in p or p[pl]['dignity']!=-100: continue
        conds=0; dl=SL[DEBIL[pl]]
        if dl in p and p[dl]['house'] in [1,4,7,10]: conds+=1
        el=SL[EXALT[pl]]
        if el in p:
            eh,dh=p[el]['house'],p[pl]['house']
            if (eh+6)%12+1==dh or ((eh+4)%12+1==dh): conds+=1
        if p[pl]['house'] in [1,4,7,10]: conds+=1
        nbr_max=max(nbr_max,conds)
    
    # Raja
    raja=0; seen=set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            kl=houses[kh]; cl=houses[ch]
            if kl==cl: continue
            key=tuple(sorted([kl,cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house']==p[cl]['house']:
                seen.add(key); raja+=1
    
    # Score
    score=mp*4.0 + (2.0 if has_shrink else 0) + (1.0 if len(loops)>=2 else 0) + raja*1.0
    if d10_10l_house in [1,4,7,10]: score+=2.5
    elif d10_10l_house in [6,8,12]: score-=2.5
    if d9_venus in ['Taurus','Libra','Pisces']: score+=2.0
    elif d9_venus=='Virgo': score-=2.0
    if nbr_max>=4: score+=3.0
    elif nbr_max>=2: score+=1.0
    
    results.append({
        'name':name,'asc':asc,'moon_nak':moon_nak,'nak_check':nak_match,
        'mp':mp,'mp_names':mp_names,'has_shrinkhala':has_shrink,'shrinkhala_count':len(loops),
        'raja':raja,'d10_10l_house':d10_10l_house,'d9_venus':d9_venus,
        'nbr_max':nbr_max,'score':round(score,1),
        'wealth':wealth,'social':social,
    })

results.sort(key=lambda x:-x['score'])

print('='*120)
print('VERIFIED 15 TIER A CHARTS — Moon Nakshatra, Mahapurusha, Shrinkhala, NEXUS Score')
print('='*120)
print(f"{'Name':<22} {'Lagna':<8} {'Moon Nak':<18} {'Verify':<6} {'MP':>3} {'Shrink':>6} {'Raja':>4} {'D10':>4} {'D9♀':<10} {'NBRY':>4} {'Score':>6} {'Wealth':<10} {'Social'}")
print('-'*130)

for r in results:
    print(f"{r['name']:<22} {r['asc']:<8} {r['moon_nak']:<18} {r['nak_check']:<6} {r['mp']:>3} {'✓' if r['has_shrinkhala'] else '✗':>6} {r['raja']:>4} {r['d10_10l_house']:>4} {r['d9_venus']:<10} {r['nbr_max']:>4} {r['score']:>6.1f} {r['wealth']:<10} {r['social']}")

# Validations
print(f"\n{'='*120}")
print("VALIDATION RESULTS")
print('='*120)

# Mula Moon test
mula = [r for r in results if r['moon_nak']=='Mula']
print(f"\n1. MULA MOON = FRONTIER: {len(mula)}/2 confirmed ({', '.join(r['name'] for r in mula)})")

# Uttara Ashadha
ua = [r for r in results if r['moon_nak']=='Uttara Ashadha']
print(f"2. UTTARA ASHADHA = INSTITUTION: {len(ua)}/2 confirmed ({', '.join(r['name'] for r in ua)})")

# Rich vs Poor scores
rich = [r for r in results if r['wealth']=='Rich']
poor = [r for r in results if r['wealth']=='Poor']
neutral = [r for r in results if r['wealth']=='Neutral']
print(f"\n3. RICH (n={len(rich)}): avg Score = {sum(r['score'] for r in rich)/len(rich):.1f}")
print(f"   POOR (n={len(poor)}): avg Score = {sum(r['score'] for r in poor)/len(poor):.1f}" if poor else "   POOR: none")
print(f"   NEUTRAL (n={len(neutral)}): avg Score = {sum(r['score'] for r in neutral)/len(neutral):.1f}")

# MP + Shrinkhala billionaires
mp_shrink = [r for r in results if r['mp']>=1 and r['has_shrinkhala']]
print(f"\n4. MAHAPURUSHA + SHRINKHALA (n={len(mp_shrink)}): {', '.join(r['name'] for r in mp_shrink)}")
print(f"   Avg Score: {sum(r['score'] for r in mp_shrink)/len(mp_shrink):.1f}" if mp_shrink else "   None")

# Cross-ref with P1-P9 scores
print(f"\n5. CROSS-REFERENCE: P1-P9 Tier A scores")
p_scores = {'P5':14.5,'P1':12.0,'P9':12.0,'P4':7.5,'P8':5.5,'P6':2.5,'P3':1.5}
for pid,ps in sorted(p_scores.items(), key=lambda x:-x[1]):
    above = [r['name'] for r in results if r['score']>=ps]
    below = [r['name'] for r in results if r['score']<ps]
    print(f"  {pid} ({ps}): {len(above)} above, {len(below)} below")

# Save
with open('dataset/verified_15_tier_a.json','w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → dataset/verified_15_tier_a.json")
