#!/usr/bin/env python3
"""P1-P9 Finance · Education · Career — Detailed Breakdown"""
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

P_CHARTS=[('P1','Polgahawela Bappa','1962-05-27','03:38:54',7.3381,80.3003),
('P2','Upulakshi','1997-03-14','09:38:00',6.9355,79.8487),
('P3','Senith','1995-08-07','21:18:00',6.9355,79.8487),
('P4','Niromi','1967-04-25','08:17:37',6.9355,79.8487),
('P5','Senath','2001-05-14','16:08:40',6.9355,79.8487),
('P6','Dewli','2005-10-08','08:22:00',6.9097,79.8900),
('P7','Sineth','2005-04-05','16:05:48',6.9271,79.8612),
('P8','Lakshi Amma','1963-11-16','09:04:15',7.486,80.362),
('P9','Lalith Uncle','1970-08-31','21:55:30',7.2931,80.635)]

career_map={
    'P1':'Industrial CEO / Manufacturing',
    'P2':'Media / MNC Manager',
    'P3':'Academic Researcher / System-Builder',
    'P4':'Government / Corporate Leadership',
    'P5':'Luxury / Beauty / Tech Entrepreneur',
    'P6':'Strategy Consultant / AI-ML',
    'P7':'Logistics / Industrial CEO',
    'P8':'Psychology / Consulting / Academia',
    'P9':'Software / Tech / Audit Director',
}

results=[]
for pid,name,bd,bt,lat,lon in P_CHARTS:
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
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30); house=(si-asc_idx)%12+1
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
    d10_10l=SL[SIGNS[(v10li+9)%12]]
    d10_10l_sign=d10[d10_10l]['sign'] if d10_10l in d10 else '?'
    v24l=(asc_sid*24)%360; v24li=SIGNS.index(SIGNS[int(v24l//30)])
    d24={}
    for pn in P7:
        vl=(p[pn]['sid']*24)%360; vs=SIGNS[int(vl//30)]; vh=(SIGNS.index(vs)-v24li)%12+1
        d24[pn]={'sign':vs,'house':vh}
    d24_4l=SL[SIGNS[(v24li+3)%12]]; d24_5l=SL[SIGNS[(v24li+4)%12]]; d24_9l=SL[SIGNS[(v24li+8)%12]]
    ms=p['Moon']['sid']; ml='?'; bal=0; mn='?'
    for n,s,l in NAKS:
        if s<=ms<s+13.334: bal=VIM_YRS[l]*(1-(ms-s)/13.334); ml=l; mn=n; break
    rd=datetime(2026,7,31,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-dt).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    for _ in range(9):
        if elapsed+rem>yfb: md2=VIM[mli]; break
        elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    mp=sum(1 for ml2 in ['Mars','Mercury','Jupiter','Venus','Saturn'] if p[ml2]['dignity']>=75 and p[ml2]['house'] in [1,4,7,10])
    g={}
    for pn2 in P7: lord=SL[p[pn2]['sign']];
    if lord!=pn2: g[pn2]=lord
    loops=[]; visited=set()
    for start in P7:
        path=[]; curr=start
        while curr in g and curr not in path: path.append(curr); curr=g[curr]
        if curr in path:
            cycle=path[path.index(curr):]; t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in visited: visited.add(t); loops.append(cycle)
    has_shrink=len(loops)>0
    hinv={}
    for pn2 in P7: hinv.setdefault(p[pn2]['house'],[]).append(pn2)
    raja=set()
    for kh in [1,4,7,10]:
        for tr in [1,5,9]:
            for kl in hinv.get(kh,[]):
                for ccl in hinv.get(tr,[]):
                    if kl!=ccl and p[kl]['house']==p[ccl]['house']: raja.add(tuple(sorted([kl,ccl])))
    raja_count=len(raja)
    ex=sum(1 for pn2 in P7 if p[pn2]['dignity']==100)
    de=sum(1 for pn2 in P7 if p[pn2]['dignity']==-100)
    own_cnt=sum(1 for pn2 in P7 if p[pn2]['dignity']==75)
    budha_adi=1 if p['Sun']['house']==p['Mercury']['house'] else 0
    mer_ven=1 if p['Mercury']['house']==p['Venus']['house'] else 0
    results.append({
        'id':pid,'name':name,'age':round(yfb,1),'asc':asc_sign,
        'moon_nak':mn,'moon_house':p['Moon']['house'],
        'saturn_sign':p['Saturn']['sign'],'saturn_house':p['Saturn']['house'],'saturn_dig':p['Saturn']['dignity'],
        'jupiter_sign':p['Jupiter']['sign'],'jupiter_house':p['Jupiter']['house'],'jupiter_dig':p['Jupiter']['dignity'],
        'mercury_sign':p['Mercury']['sign'],'mercury_house':p['Mercury']['house'],'mercury_dig':p['Mercury']['dignity'],
        'venus_sign':p['Venus']['sign'],'venus_house':p['Venus']['house'],'venus_dig':p['Venus']['dignity'],
        'sun_house':p['Sun']['house'],
        'd9_venus_sign':d9['Venus']['sign'],'d9_venus_house':d9['Venus']['house'],'d9_venus_dig':d9['Venus']['dignity'],
        'd9_jupiter_dig':d9['Jupiter']['dignity'],
        'd10_10l':d10_10l,'d10_10l_sign':d10_10l_sign,'d10_10l_house':d10_10l_house,
        'd10_lagna':SIGNS[v10li],'d10_saturn_sign':d10['Saturn']['sign'],'d10_saturn_house':d10['Saturn']['house'],
        'd24_lagna':SIGNS[v24li],'d24_4l':d24_4l,'d24_5l':d24_5l,'d24_9l':d24_9l,
        'd24_4l_house':d24[d24_4l]['house'],'d24_5l_house':d24[d24_5l]['house'],'d24_9l_house':d24[d24_9l]['house'],
        'dasha':md2,'mp':mp,'shrink':has_shrink,'raja':raja_count,
        'exalted':ex,'debilitated':de,'own':own_cnt,'budha_aditya':budha_adi,'mer_ven':mer_ven,
    })

B='='*98

# ═══ FINANCE ═══
print(f'{B}')
print('  P1-P9 FINANCE — DETAILED SCORING')
print(f'{B}')
print()
print('  Formula: MP×4 + Shrinkhala×2 + Raja×1 + D10_10L±2.5 + D9_Venus±2 + Nakshatra×1 + Budha-Aditya×1 + Mer-Ven×1 + (Ex-Deb)×0.5')
print()
print(f'  {"ID":<4} {"Name":<22} {"Fin":>5} {"Lg":<8} {"Moon":<15} {"MP":>4} {"Shr":>4} {"Raj":>4} {"D10H":>5} {"D9Venus":<16} {"B-A":>4} {"M-V":>4} {"Ex":>3} {"Nb":>4}')
print(f'  {"-"*4} {"-"*22} {"-"*5} {"-"*8} {"-"*15} {"-"*4} {"-"*4} {"-"*4} {"-"*5} {"-"*16} {"-"*4} {"-"*4} {"-"*3} {"-"*4}')
for r in sorted(results,key=lambda r:-r['mp']):
    fin=round(r['mp']*4+(2 if r['shrink'] else 0)+r['raja']+(2.5 if r['d10_10l_house'] in [1,4,7,10] else (-2.5 if r['d10_10l_house'] in [6,8,12] else 0))+(2 if r['d9_venus_sign'] in ['Taurus','Libra','Pisces'] else (-2 if r['d9_venus_sign']=='Virgo' else 0))+(1 if r['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada','Mula'] else 0)+r['budha_aditya']+r['mer_ven']+(r['exalted']-r['debilitated'])*0.5,1)
    d9v=f'{r["d9_venus_sign"]}(OWN)' if r['d9_venus_dig']>=75 else f'{r["d9_venus_sign"]}(DEB)' if r['d9_venus_dig']==-100 else f'{r["d9_venus_sign"]}(neut)'
    print(f'  {r["id"]:<4} {r["name"]:<22} {fin:>5.1f} {r["asc"]:<8} {r["moon_nak"]:<15} {r["mp"]:>4} {"✓" if r["shrink"] else "✗":>4} {r["raja"]:>4} {r["d10_10l_house"]:>5} {d9v:<16} {r["budha_aditya"]:>4} {r["mer_ven"]:>4} {r["exalted"]:>3} {r["debilitated"]:>4}')

print()
print(f'  WEALTH TIERS:')
for r in sorted(results,key=lambda r:-r['mp']):
    fin=round(r['mp']*4+(2 if r['shrink'] else 0)+r['raja']+(2.5 if r['d10_10l_house'] in [1,4,7,10] else (-2.5 if r['d10_10l_house'] in [6,8,12] else 0))+(2 if r['d9_venus_sign'] in ['Taurus','Libra','Pisces'] else (-2 if r['d9_venus_sign']=='Virgo' else 0))+(1 if r['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada','Mula'] else 0)+r['budha_aditya']+r['mer_ven']+(r['exalted']-r['debilitated'])*0.5,1)
    tier='HIGH NET WORTH' if fin>=7 else ('ABOVE AVG' if fin>=3 else ('MODERATE' if fin>=0 else 'CHALLENGED'))
    mps=[y for pl,y in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if results[0] and False]
    # Just show key
    sigs=[]
    if r['mp']: sigs.append(f'{r["mp"]}MP')
    if r['shrink']: sigs.append('Shrinkhala')
    if r['raja']: sigs.append(f'{r["raja"]}Raja')
    sig_str = " · ".join(sigs) if sigs else "no major yogas"
    print(f'    {r["id"]} {r["name"]:<22s} {fin:>4.0f} -> {tier:<12s}   {sig_str}')

# ═══ EDUCATION ═══
print(f'\n{B}')
print('  P1-P9 EDUCATION — DETAILED SCORING')
print(f'{B}')
print()
print(f'  Formula: Jupiter dignity(±3/±2) + Jupiter house(±2/±1) + Mercury dignity(±2) + Mercury house(±1) + 5L bonus(±2) + Budha-Aditya(±1)')
print()
print(f'  {"ID":<4} {"Name":<22} {"Edu":>5} {"Jupiter(D1)":<18} {"JupH":>4} {"Mercury(D1)":<18} {"MerH":>4} {"5L":<6} {"D9 Jup":<14} {"D24: Lg/4L/5L/9L"}')
print(f'  {"-"*4} {"-"*22} {"-"*5} {"-"*18} {"-"*4} {"-"*18} {"-"*4} {"-"*6} {"-"*14} {"-"*25}')
for r in sorted(results,key=lambda r:(-r['jupiter_dig'],-r['mercury_dig'])):
    edu=round((3 if r['jupiter_dig']>=75 else (-2 if r['jupiter_dig']==-100 else 0))+(2 if r['jupiter_house'] in [2,5,9,10] else (-1 if r['jupiter_house'] in [6,8,12] else 0))+(2 if r['mercury_dig']>=75 else 0)+(1 if r['mercury_house'] in [1,2,4,5,9,10] else 0)+(2 if r['jupiter_house'] in [2,5,9,10] else 0)+r['budha_aditya'],1)
    jdl='OWN' if r['jupiter_dig']>=75 else ('DEB' if r['jupiter_dig']==-100 else 'neut')
    mdl='OWN' if r['mercury_dig']>=75 else ('DEB' if r['mercury_dig']==-100 else 'neut')
    asc_i=SIGNS.index(r['asc'])
    h5l=SL[SIGNS[(asc_i+4)%12]]
    d9jl='OWN/EX' if r['d9_jupiter_dig']>=75 else ('DEB' if r['d9_jupiter_dig']==-100 else 'neut')
    d24s=f'{r["d24_lagna"]} | {r["d24_4l"]}H{r["d24_4l_house"]} | {r["d24_5l"]}H{r["d24_5l_house"]} | {r["d24_9l"]}H{r["d24_9l_house"]}'
    print(f'  {r["id"]:<4} {r["name"]:<22} {edu:>5.1f} {r["jupiter_sign"]}({jdl}){" ":<12} {r["jupiter_house"]:>4} {r["mercury_sign"]}({mdl}){" ":<12} {r["mercury_house"]:>4} {h5l:<6} {d9jl:<14} {d24s}')

# ═══ CAREER ═══
print(f'\n{B}')
print('  P1-P9 CAREER — DETAILED SCORING')
print(f'{B}')
print()
print(f'  Formula: D10_10L_H(±4/±3/±1) + Saturn_H(±2/±1) + Budha-Aditya(±1) + Jupiter_H9/H10(±1.5) + Moon+Sat_Kendra(±1)')
print()
print(f'  {"ID":<4} {"Name":<22} {"Car":>5} {"D10 Lg":<8} {"D10 10L":<12} {"10LH":>4} {"Path":<12} {"D1 Sat":<12} {"D10 Sat":<14} {"JupH":>4} {"B-A":>4} {"M+S K":>6}  {"Career Direction"}' )
print(f'  {"-"*4} {"-"*22} {"-"*5} {"-"*8} {"-"*12} {"-"*4} {"-"*12} {"-"*12} {"-"*14} {"-"*4} {"-"*4} {"-"*6}  {"-"*30}')
for r in results:
    car=round((4 if r['d10_10l_house'] in [1,4,7,10] else (-3 if r['d10_10l_house'] in [6,8,12] else 1))+(2 if r['saturn_house']==10 else (1 if r['saturn_house'] in [1,4,7] else 0))+r['budha_aditya']+(1.5 if r['jupiter_house'] in [9,10] else 0)+(1 if r['moon_house'] in [1,4,7,10] and r['saturn_house'] in [1,4,7,10] else 0),1)
    path='S-KENDRA' if r['d10_10l_house'] in [1,4,7,10] else ('V-DUSTHANA' if r['d10_10l_house'] in [6,8,12] else 'ADAPTABLE')
    sat_d1=f'{r["saturn_sign"]} H{r["saturn_house"]}'
    d10s=f'{r["d10_saturn_sign"]} H{r["d10_saturn_house"]}'
    d10_10l_d=f'{r["d10_10l"]} {r["d10_10l_sign"]}'
    msk='YES' if r['moon_house'] in [1,4,7,10] and r['saturn_house'] in [1,4,7,10] else 'no'
    print(f'  {r["id"]:<4} {r["name"]:<22} {car:>5.1f} {r["d10_lagna"]:<8} {d10_10l_d:<12} {r["d10_10l_house"]:>4} {path:<12} {sat_d1:<12} {d10s:<14} {r["jupiter_house"]:>4} {r["budha_aditya"]:>4} {msk:>6}  {career_map[r["id"]]}')

print()
print(f'{B}')
print('  P1-P9 — FINANCE · EDUCATION · CAREER — RANKED SUMMARY')
print(f'{B}')
print(f'  {"ID":<4} {"Name":<22} {"Fin":>5} {"Fin Tier":<12} {"Edu":>5} {"Edu Tier":<12} {"Car":>5} {"Car Tier":<12} {"OVERALL":>8}')
print(f'  {"-"*4} {"-"*22} {"-"*5} {"-"*12} {"-"*5} {"-"*12} {"-"*5} {"-"*12} {"-"*8}')
for r in sorted(results,key=lambda r:-r['mp']):
    fin=round(r['mp']*4+(2 if r['shrink'] else 0)+r['raja']+(2.5 if r['d10_10l_house'] in [1,4,7,10] else (-2.5 if r['d10_10l_house'] in [6,8,12] else 0))+(2 if r['d9_venus_sign'] in ['Taurus','Libra','Pisces'] else (-2 if r['d9_venus_sign']=='Virgo' else 0))+(1 if r['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada','Mula'] else 0)+r['budha_aditya']+r['mer_ven']+(r['exalted']-r['debilitated'])*0.5,1)
    edu=round((3 if r['jupiter_dig']>=75 else (-2 if r['jupiter_dig']==-100 else 0))+(2 if r['jupiter_house'] in [2,5,9,10] else (-1 if r['jupiter_house'] in [6,8,12] else 0))+(2 if r['mercury_dig']>=75 else 0)+(1 if r['mercury_house'] in [1,2,4,5,9,10] else 0)+(2 if r['jupiter_house'] in [2,5,9,10] else 0)+r['budha_aditya'],1)
    car=round((4 if r['d10_10l_house'] in [1,4,7,10] else (-3 if r['d10_10l_house'] in [6,8,12] else 1))+(2 if r['saturn_house']==10 else (1 if r['saturn_house'] in [1,4,7] else 0))+r['budha_aditya']+(1.5 if r['jupiter_house'] in [9,10] else 0)+(1 if r['moon_house'] in [1,4,7,10] and r['saturn_house'] in [1,4,7,10] else 0),1)
    ft='HIGH' if fin>=7 else ('ABOVE AVG' if fin>=3 else ('MODERATE' if fin>=0 else 'LOW'))
    et='STRONG' if edu>=5 else ('GOOD' if edu>=3 else ('BASIC' if edu>=1 else 'CHALLENGED'))
    ct='STRONG' if car>=4 else ('GOOD' if car>=2 else ('ADEQUATE' if car>=0 else 'CHALLENGED'))
    ov=round((fin+edu+car)/3,1)
    print(f'  {r["id"]:<4} {r["name"]:<22} {fin:>5.1f} {ft:<12} {edu:>5.1f} {et:<12} {car:>5.1f} {ct:<12} {ov:>8.1f}')
