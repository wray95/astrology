#!/usr/bin/env python3
"""P1-P9 Career + Degree Matrix — Lahiri · Swiss Ephemeris v2.10.3.2 · Whole Sign"""
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

P=[('P1','Polgahawela Bappa','1962-05-27','03:38:54',7.3381,80.3003),
('P2','Upulakshi','1997-03-14','09:38:00',6.9355,79.8487),
('P3','Senith','1995-08-07','21:18:00',6.9355,79.8487),
('P4','Niromi','1967-04-25','08:17:37',6.9355,79.8487),
('P5','Senath','2001-05-14','16:08:40',6.9355,79.8487),
('P6','Dewli','2005-10-08','08:22:00',6.9097,79.8900),
('P7','Sineth','2005-04-05','16:05:48',6.9271,79.8612),
('P8','Lakshi Amma','1963-11-16','09:04:15',7.486,80.362),
('P9','Lalith Uncle','1970-08-31','21:55:30',7.2931,80.635)]

career_detail={
    'P1':{'title':'Industrial CEO / Manufacturing','degree':'Engineering / Business / Construction Mgmt','fit':'DUAL MP (Ruchaka+Sasa). D10 H8 = volatile. Budha-Aditya = sharp mind.','edu':'Saturn H10 + Mars H1 = hands-on leadership. D24 Jupiter 5L.','risk':'D10 H8 — career breaks. Wealth despite instability.'},
    'P2':{'title':'Media / MNC Manager','degree':'Communications / Journalism / Media','fit':'D10 H7 KENDRA. D9 Venus OWN H7. Krittika Moon = sharp communication.','edu':'Mercury+Krittika = communicator. Venus D9 = media/creative.','risk':'TOB corrected 09:38. Jupiter+Mercury both DEB.'},
    'P3':{'title':'Academic Researcher / System-Builder','degree':'Mathematics / Theoretical CS / Philosophy','fit':'D10 H12 = solitary work. 5-Loop Shrinkhala. ALL 7 neutral. Mula Moon.','edu':'Saturn H1. Jupiter Scorpio H9. D24 Saturn 4L H6 = autodidact.','risk':'D10 H12 — slow recognition. Peak after 2046 (Rahu MD).'},
    'P4':{'title':'Government / Corporate Leadership','degree':'Public Admin / Law / Business','fit':'Malavya MP (Venus H1). Swati Moon. D10 H9.','edu':'Mars H6 = service. D24 Moon 4L+Sun 5L.','risk':'D10 H9 — career can drift. Ketu/Mercury dasha ending.'},
    'P5':{'title':'Luxury / Beauty / Tech Entrepreneur','degree':'Business / Finance / Design / Tech','fit':'#1 FINANCE. Malavya MP + Shravana Moon. D10 H7 KENDRA.','edu':'Rahu/Sun dasha. Venus OWN H7. Shravana = master listener.','risk':'Saturn Taurus H9 = slow build. Patience required.'},
    'P6':{'title':'Strategy Consultant / AI-ML','degree':'Computer Science / AI / Data Science','fit':'Ruchaka MP (Mars H7). D10 H6. Jyeshtha Moon. Saturn Cancer = AI/ML.','edu':'Saturn Cancer H10. Mars H7 = strategy. D24 Jupiter 4L+Saturn 9L.','risk':'D10 H6 = daily grind. Low finance (2.0). Needs right niche.'},
    'P7':{'title':'Logistics / Industrial CEO','degree':'Supply Chain / Engineering / IT','fit':'Shatabhisha Moon + Budha-Aditya + Mer-Ven. D10 H2. Saturn Gemini.','edu':'Saturn Gemini = logistics. D24 Mars 4L = hands-on.','risk':'Lagna TBD — house placements unverified.'},
    'P8':{'title':'Psychology / Consulting / Academia','degree':'Psychology / Education / Counselling','fit':'Hamsa MP (Jupiter H4). Mer+Ven. Vishakha Moon. D10 H9.','edu':'Jupiter H4 OWN = teacher. D24 Jupiter 5L+Venus 7L.','risk':'D9 Venus Sagittarius H6 = marriage challenges.'},
    'P9':{'title':'Software / Tech / Audit Director','degree':'Computer Science / Accounting / Law','fit':'4 RAJA YOGAS. Malavya MP. D9 Venus+D9 Jupiter OWN. Magha Moon.','edu':'4 Raja Yogas = authority. D24 Saturn 9L+Mercury 5L.','risk':'Jupiter H7 = career via partnership. Slow starter.'},
}

charts=[]
for pid,name,bd,bt,lat,lon in P:
    dt=datetime.strptime(bd+'T'+bt,'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=5.5)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    p={}
    for pn2,pi in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt,_=swe.calc_ut(jd,pi); lt=lt[0]
        sid=(lt-ayan)%360; sgn=SIGNS[int(sid//30)]; si=int(sid//30); h=(si-asc_idx)%12+1
        dgn=100 if (pn2 in EXALT and EXALT[pn2]==sgn) else (75 if (pn2 in OWN and sgn in OWN[pn2]) else (-100 if (pn2 in DEBIL and DEBIL[pn2]==sgn) else 0))
        p[pn2]={'sign':sgn,'house':h,'dignity':dgn,'sid':sid}
    rh2,_=swe.calc_ut(jd,swe.MEAN_NODE); rh2=(rh2[0]-ayan)%360; kh2=(rh2+180)%360
    p['Rahu']={'sign':SIGNS[int(rh2//30)],'house':(int(rh2//30)-asc_idx)%12+1}
    v10l=(asc_sid*10)%360; v10li=SIGNS.index(SIGNS[int(v10l//30)])
    d10={}
    for pn2 in P7:
        vl=(p[pn2]['sid']*10)%360; vs=SIGNS[int(vl//30)]; vh=(SIGNS.index(vs)-v10li)%12+1
        d10[pn2]={'sign':vs,'house':vh}
    d10_10l=SL[SIGNS[(v10li+9)%12]]; d10_10l_h=d10[d10_10l]['house'] if d10_10l in d10 else 0
    ms=p['Moon']['sid']; ml='?'; bal=0; mn='?'
    for n,s,l in NAKS:
        if s<=ms<s+13.334: bal=VIM_YRS[l]*(1-(ms-s)/13.334); ml=l; mn=n; break
    rd=datetime(2026,7,31,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-dt).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    for _ in range(9):
        if elapsed+rem>yfb: md=VIM[mli]; break
        elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    car=round((4 if d10_10l_h in [1,4,7,10] else (-3 if d10_10l_h in [6,8,12] else 1))+(2 if p['Saturn']['house']==10 else (1 if p['Saturn']['house'] in [1,4,7] else 0))+(1 if p['Sun']['house']==p['Mercury']['house'] else 0)+(1.5 if p['Jupiter']['house'] in [9,10] else 0)+(1 if p['Moon']['house'] in [1,4,7,10] and p['Saturn']['house'] in [1,4,7,10] else 0),1)
    path='KENDRA' if d10_10l_h in [1,4,7,10] else ('DUSTHANA' if d10_10l_h in [6,8,12] else 'ADAPTABLE')
    charts.append({'id':pid,'name':name,'asc':asc_sign,'d10_10l_h':d10_10l_h,'path':path,'car':car,'dasha':md,'age':round(yfb,1),'moon_nak':mn,'jup_h':p['Jupiter']['house'],'jup_dig':p['Jupiter']['dignity'],'mer_dig':p['Mercury']['dignity'],'sat_h':p['Saturn']['house']})

B='='*95
print(f'{B}')
print('  P1-P9 — CAREER + DEGREE RANKING (Lahiri · Swiss Ephemeris · Whole Sign)')
print(f'{B}')
print()
print(f'  {"Rk":<4} {"ID":<4} {"Name":<22} {"Car":>5} {"D10 Path":<12} {"Tier":<10} {"Degree":<45} {"Career Path":<35}')
print(f'  {"-"*4} {"-"*4} {"-"*22} {"-"*5} {"-"*12} {"-"*10} {"-"*45} {"-"*35}')
for i,c in enumerate(sorted(charts,key=lambda x:-x['car'])):
    d=career_detail.get(c['id'],{})
    tier='STRONG' if c['car']>=4 else ('GOOD' if c['car']>=2 else ('ADEQUATE' if c['car']>=0 else 'CHALLENGED'))
    print(f'  {i+1:<4} {c["id"]:<4} {c["name"]:<22} {c["car"]:>5.1f} {c["path"]:<12} {tier:<10} {d.get("degree","")[:44]:<45} {d.get("title","")[:34]:<35}')

print(f'\n{B}')
print('  CAREER DETAILS')
print(f'{B}')
for c in sorted(charts,key=lambda x:-x['car']):
    d=career_detail.get(c['id'],{})
    print(f'\n  {c["id"]} {c["name"]} | Car:{c["car"]} | {c["asc"]} Lagna | {c["moon_nak"]} Moon | {c["dasha"]} | Age:{c["age"]}')
    print(f'  CAREER:  {d.get("title","")}')
    print(f'  DEGREE:  {d.get("degree","")}')
    print(f'  FIT:     {d.get("fit","")}')
    print(f'  EDU:     {d.get("edu","")}')
    print(f'  CAUTION: {d.get("risk","")}')
