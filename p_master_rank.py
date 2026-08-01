#!/usr/bin/env python3
"""P1-P9 MASTER RANKING — All 6 Dimensions"""
import swisseph as swe
from datetime import datetime, timezone, timedelta
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

P_CHARTS = [
    ("P1","Polgahawela Bappa","1962-05-27","03:38:54",7.3381,80.3003),
    ("P2","Upulakshi","1997-03-14","09:38:00",6.9355,79.8487),
    ("P3","Senith","1995-08-07","21:18:00",6.9355,79.8487),
    ("P4","Niromi","1967-04-25","08:17:37",6.9355,79.8487),
    ("P5","Senath","2001-05-14","16:08:40",6.9355,79.8487),
    ("P6","Dewli","2005-10-08","08:22:00",6.9097,79.8900),
    ("P7","Sineth","2005-04-05","16:05:48",6.9271,79.8612),
    ("P8","Lakshi Amma","1963-11-16","09:04:15",7.486,80.362),
    ("P9","Lalith Uncle","1970-08-31","21:55:30",7.2931,80.635),
]

def compute(pid,name,bd,bt,lat,lon):
    dt=datetime.strptime(bd+'T'+bt,'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=5.5)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    p={}
    for pn,pid2 in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt,_=swe.calc_ut(jd,pid2); lt=lt[0]
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30)
        house=(si-asc_idx)%12+1
        dgn=100 if (pn in EXALT and EXALT[pn]==sgn) else (75 if (pn in OWN and sgn in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==sgn) else 0))
        p[pn]={'sign':sgn,'house':house,'dignity':dgn,'sid':sid,'deg':round(sid%30,4)}
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    p['Rahu']={'sign':SIGNS[int(rh//30)],'house':(int(rh//30)-asc_idx)%12+1,'dignity':0}
    p['Ketu']={'sign':SIGNS[int(kh//30)],'house':(int(kh//30)-asc_idx)%12+1,'dignity':0}
    
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
    d10_10l_house=d10[SL[SIGNS[(v10li+9)%12]]]['house'] if SL[SIGNS[(v10li+9)%12]] in d10 else 0
    
    ms=p['Moon']['sid']; ml='?'; bal=0; mn='?'
    for n,s,l in NAKS:
        if s<=ms<s+13.334: bal=VIM_YRS[l]*(1-(ms-s)/13.334); ml=l; mn=n; break
    rd=datetime(2026,7,31,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-dt).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    for _ in range(9):
        if elapsed+rem>yfb: md2=VIM[mli]; break
        elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    
    return {'id':pid,'name':name,'asc':asc_sign,'asc_idx':asc_idx,'planets':p,'d9':d9,'d9_lagna_idx':v9li,'d10':d10,'d10_10l_house':d10_10l_house,'moon_nak':mn,'dasha':md2,'age':round(yfb,1)}

def fscore(p,ch):
    sc=0
    for ml in ['Mars','Mercury','Jupiter','Venus','Saturn']:
        if p[ml]['dignity']>=75 and p[ml]['house'] in [1,4,7,10]: sc+=4
    g={}
    for pn in P7: 
        lord=SL[p[pn]['sign']]
        if lord!=pn: g[pn]=lord
    loops=[]; visited=set()
    for start in P7:
        path=[]; curr=start
        while curr in g and curr not in path: path.append(curr); curr=g[curr]
        if curr in path:
            cycle=path[path.index(curr):]; t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in visited: visited.add(t); loops.append(cycle)
    if loops: sc+=2
    hinv={}
    for pn in P7: hinv.setdefault(p[pn]['house'],[]).append(pn)
    raja=set()
    for kh in [1,4,7,10]:
        for tr in [1,5,9]:
            for kl in hinv.get(kh,[]):
                for ccl in hinv.get(tr,[]):
                    if kl!=ccl and p[kl]['house']==p[ccl]['house']: raja.add(tuple(sorted([kl,ccl])))
    sc+=len(raja)
    if ch['d10_10l_house'] in [1,4,7,10]: sc+=2.5
    elif ch['d10_10l_house'] in [6,8,12]: sc-=2.5
    d9v=ch['d9']['Venus']
    if d9v['sign'] in ['Taurus','Libra','Pisces']: sc+=2
    elif d9v['sign']=='Virgo': sc-=2
    if ch['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada','Mula']: sc+=1
    if p['Sun']['house']==p['Mercury']['house']: sc+=1
    if p['Mercury']['house']==p['Venus']['house']: sc+=1
    ex=sum(1 for pn in P7 if p[pn]['dignity']==100)
    de=sum(1 for pn in P7 if p[pn]['dignity']==-100)
    sc+=(ex-de)*0.5
    return round(sc,1)

def cscore(p,ch):
    sc=0
    if ch['d10_10l_house'] in [1,4,7,10]: sc+=4
    elif ch['d10_10l_house'] in [6,8,12]: sc-=3
    else: sc+=1
    if p['Saturn']['house']==10: sc+=2
    elif p['Saturn']['house'] in [1,4,7]: sc+=1
    if p['Sun']['house']==p['Mercury']['house']: sc+=1
    if p['Jupiter']['house'] in [9,10]: sc+=1.5
    mh=p['Moon']['house']; sh=p['Saturn']['house']
    if mh in [1,4,7,10] and sh in [1,4,7,10]: sc+=1
    return round(sc,1)

def escore(p,ch):
    sc=0; jup=p['Jupiter']
    if jup['dignity']>=75: sc+=3
    elif jup['dignity']==-100: sc-=2
    if jup['house'] in [2,5,9,10]: sc+=2
    elif jup['house'] in [6,8,12]: sc-=1
    mer=p['Mercury']
    if mer['dignity']>=75: sc+=2
    if mer['house'] in [1,2,4,5,9,10]: sc+=1
    h5l=SL[SIGNS[(ch['asc_idx']+4)%12]]
    if h5l in p and p[h5l]['dignity']>=75: sc+=2
    if h5l in p and p[h5l]['house'] in [6,8,12]: sc-=1
    if p['Sun']['house']==p['Mercury']['house']: sc+=1
    return round(sc,1)

def mscore(p,ch):
    sc=0; d9=ch['d9']
    ven=p['Venus']
    if ven['dignity']>=75: sc+=3
    elif ven['dignity']==-100: sc-=3
    d9v=d9['Venus']
    if d9v['dignity']>=75: sc+=5
    elif d9v['dignity']==-100: sc-=4
    if d9v['house'] in [1,4,7,10]: sc+=2
    h7l=SL[SIGNS[(ch['asc_idx']+6)%12]]
    if h7l in p and p[h7l]['dignity']>=75: sc+=2
    if h7l in p and p[h7l]['house'] in [6,8,12]: sc-=1
    pl7=[pn for pn in P7 if p[pn]['house']==7]
    if 'Jupiter' in pl7: sc+=2
    if 'Venus' in pl7: sc+=2
    if 'Saturn' in pl7: sc-=1
    if 'Mars' in pl7: sc-=1
    if p.get('Rahu',{}).get('house')==7: sc-=1
    mh=p['Moon']['house']; jh=p['Jupiter']['house']
    if (mh+3)%12+1==jh or (mh+6)%12+1==jh or (mh+9)%12+1==jh or mh==jh: sc+=1
    return round(sc,1)

def chscore(p,ch):
    sc=0; d9=ch['d9']
    if d9['Moon']['house']==5: sc+=6
    d9_5l=SL[SIGNS[(ch['d9_lagna_idx']+4)%12]]
    if d9_5l in d9 and d9[d9_5l]['dignity']>=75: sc+=4
    if d9_5l in d9 and d9[d9_5l]['dignity']==-100: sc-=3
    if d9_5l in d9 and d9[d9_5l]['house']==5: sc+=3
    if d9_5l in d9 and d9[d9_5l]['house'] in [6,8,12]: sc-=2
    if d9['Jupiter']['dignity']>=75: sc+=2
    if d9['Jupiter']['dignity']==-100: sc-=1
    if d9['Jupiter']['house'] in [1,5,9]: sc+=2
    if d9['Jupiter']['house'] in [6,8,12]: sc-=1
    return round(sc,1)

def pscore(p,ch):
    sc=0; d9=ch['d9']
    if d9['Venus']['dignity']>=75: sc+=2
    if d9['Venus']['house'] in [1,4,7,10]: sc+=1
    if p['Venus']['house']==p['Sun']['house']: sc+=1
    if d9['Moon']['house']==5: sc+=3
    d9_5l=SL[SIGNS[(ch['d9_lagna_idx']+4)%12]]
    if d9_5l in d9 and d9[d9_5l]['dignity']>=75: sc+=2
    if d9['Jupiter']['house'] in [1,5,9]: sc+=2
    if d9['Jupiter']['dignity']>=75: sc+=2
    if d9['Jupiter']['dignity']==-100: sc-=1
    if p['Saturn']['house'] in [2,7,11]: sc+=1
    if p['Saturn']['dignity']>=75: sc+=1
    return round(sc,1)

charts=[]
for pid,name,bd,bt,lat,lon in P_CHARTS:
    ch=compute(pid,name,bd,bt,lat,lon)
    p=ch['planets']
    ch['fin']=fscore(p,ch); ch['car']=cscore(p,ch); ch['edu']=escore(p,ch)
    ch['mar']=mscore(p,ch); ch['child']=chscore(p,ch); ch['post']=pscore(p,ch)
    ch['comp']=round((ch['fin']+ch['car']+ch['edu']+ch['mar']+ch['child']+ch['post'])/6,1)
    charts.append(ch)

B='='*100

print(f'{B}')
print('  P1-P9 — MASTER RANKING (6 Dimensions + Composite)')
print('  Lahiri Ayanamsa + Whole Sign + Swiss Ephemeris · 18 Classical Sources')
print(f'{B}')
print()
print(f'  {"ID":<4} {"Name":<22} {"Fin":>5} {"Car":>5} {"Edu":>5} {"Mar":>5} {"Chd":>5} {"Post":>5} {"Comp":>6} {"Dasha":<12} {"Key Signals":<30}')
print(f'  {"-"*4} {"-"*22} {"-"*5} {"-"*5} {"-"*5} {"-"*5} {"-"*5} {"-"*5} {"-"*6} {"-"*12} {"-"*30}')

for ch in sorted(charts,key=lambda c:-c['comp']):
    sig=[]
    if ch['fin']>=6: sig.append('TOP-WEALTH')
    if ch['mar']>=4: sig.append('GOOD-MARR')
    if ch['child']>=2: sig.append('KIDS')
    if ch['post']>=5: sig.append('POST-PEAK')
    if ch['d9']['Moon']['house']==5: sig.append('Moon5H!')
    p=ch['planets']
    mp=sum(1 for ml in ['Mars','Mercury','Jupiter','Venus','Saturn'] if p[ml]['dignity']>=75 and p[ml]['house'] in [1,4,7,10])
    if mp>=1: sig.append(f'MPx{mp}')
    w=' ⚠️' if ch['id'] in ['P2','P7'] else ''
    print(f'  {ch["id"]:<4} {ch["name"]:<22} {ch["fin"]:>5.1f} {ch["car"]:>5.1f} {ch["edu"]:>5.1f} {ch["mar"]:>5.1f} {ch["child"]:>5.1f} {ch["post"]:>5.1f} {ch["comp"]:>6.1f} {ch["dasha"]:<12} {", ".join(sig) if sig else "—":<30}{w}')

# Dimension rankings
for dim,label in [('fin','FINANCE'),('car','CAREER'),('edu','EDUCATION'),('mar','MARRIAGE'),('child','CHILDREN'),('post','POST-MARRIAGE')]:
    print(f'\n{B}')
    print(f'  {label} RANKING')
    print(f'{B}')
    ranked=sorted(charts,key=lambda c:-c[dim])
    for i,c in enumerate(ranked):
        val=c[dim]
        bar='█'*max(1,min(25,int(val+6 if val>=0 else 1)))
        d9v=c['d9']['Venus']; vlab='OWN' if d9v['dignity']>=75 else ('DEB' if d9v['dignity']==-100 else 'neut')
        detail=''
        if dim=='fin':
            mp=sum(1 for ml in ['Mars','Mercury','Jupiter','Venus','Saturn'] if c['planets'][ml]['dignity']>=75 and c['planets'][ml]['house'] in [1,4,7,10])
            detail='MP:%d Moon:%s D9Ven:%s(%s)'%(mp,c['moon_nak'],d9v['sign'],vlab)
        elif dim=='mar':
            detail='D9Ven:%s(%s)H%d'%(d9v['sign'],vlab,d9v['house'])
        elif dim=='child':
            sig2=[]
            if c['d9']['Moon']['house']==5: sig2.append('Moon5H')
            d9_5l=SL[SIGNS[(c['d9_lagna_idx']+4)%12]]
            if d9_5l in c['d9']:
                if c['d9'][d9_5l]['dignity']>=75: sig2.append('5L'+d9_5l+'OWN')
                if c['d9'][d9_5l]['house']==5: sig2.append('5Lin5H')
            detail=','.join(sig2) if sig2 else ''
        print('  %d. %s %-22s %5.1f %s  %s'%(i+1,c['id'],c['name'],val,bar,detail))

# Composite
print(f'\n{B}')
print('  COMPOSITE MASTER RANKING')
print(f'{B}')
ranked=sorted(charts,key=lambda c:-c['comp'])
medals=['🥇','🥈','🥉','4','5','6','7','8','9']
for i,c in enumerate(ranked):
    bar='█'*max(1,min(30,int(c['comp']+5)))
    print('  %s %s %-22s %5.1f %s  F:%.0f C:%.0f E:%.0f M:%.0f K:%.0f P:%.0f'%(medals[i],c['id'],c['name'],c['comp'],bar,c['fin'],c['car'],c['edu'],c['mar'],c['child'],c['post']))

print()
print(f'{B}')
print('  DIMENSION SPECIALISTS')
print(f'{B}')
for dim,label in [('fin','Finance'),('car','Career'),('edu','Education'),('mar','Marriage'),('child','Children'),('post','Post-Marr')]:
    top=sorted(charts,key=lambda c:-c[dim])[0]
    print('  %-15s: %s %s (%s)'%(label,top['id'],top['name'],top[dim]))
