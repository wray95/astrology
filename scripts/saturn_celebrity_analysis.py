#!/usr/bin/env python3
"""Elon Musk · Jeff Bezos · Terry Crews — Saturn Analysis"""
import swisseph as swe
from datetime import datetime, timezone, timedelta
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL={'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
P7=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
NAKS=[('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]

def gn(lon):
    lon%=360
    for n,s,l in NAKS:
        if s<=lon<s+13.334: return n,l,(lon-s)/13.334
    return 'Revati','Mercury',0

celebs = [
    ("Elon Musk", "1971-06-28", "07:30:00", -25.7461, 28.1881, 2),
    ("Jeff Bezos", "1964-01-12", "14:00:00", 35.0853, -106.6056, -7),
    ("Terry Crews", "1968-07-30", "08:00:00", 43.0125, -83.6875, -5),
]

events_map = {
    "Elon Musk": [
        (1995,"Zip2 founded","Saturn Aquarius→Pisces"),
        (1999,"Zip2 sold $307M","Saturn Aries 5° — 16mo pre-Taurus ingress 🔥"),
        (2002,"PayPal sold $1.5B","Saturn Taurus→Gemini"),
        (2008,"Tesla CEO / SpaceX orbit","Saturn Leo → 1st return near"),
        (2012,"Model S launch","Saturn Libra 27° — pre-ingress Scorpio 🔥"),
        (2020,"Tesla $1T valuation","Saturn Capricorn→Aquarius (own sign!)"),
    ],
    "Jeff Bezos": [
        (1994,"Amazon founded","Saturn Aquarius→Pisces"),
        (1997,"Amazon IPO","Saturn Pisces→Aries"),
        (2007,"Kindle launched","Saturn Leo→Virgo"),
        (2013,"Buy Washington Post","Saturn Libra→Scorpio"),
        (2018,"$150B net worth peak","Saturn Sagittarius→Capricorn (own sign!)"),
        (2021,"Steps down as CEO","Saturn Capricorn→Aquarius"),
    ],
    "Terry Crews": [
        (1999,"NFL career begins","Saturn Taurus→Gemini"),
        (2005,"Everybody Hates Chris","Saturn Cancer→Leo"),
        (2010,"The Expendables","Saturn Virgo→Libra"),
        (2013,"Brooklyn 99 series lead","Saturn Libra→Scorpio"),
        (2017,"AGT host","Saturn Sagittarius→Capricorn"),
        (2022,"Career peak","Saturn Aquarius→Pisces"),
    ],
}

hthemes={1:'Self/identity',2:'Wealth/speech',3:'Communication/courage',4:'Home/peace',
         5:'Intelligence/children',6:'Daily work/health',7:'Partnerships/marriage',
         8:'Hidden/research/transformation',9:'Dharma/higher ed/luck',
         10:'Career/public image',11:'Gains/income/fulfillment',12:'Solitude/loss/foreign'}

for name,bd,bt,lat,lon,tz in celebs:
    dt=datetime.strptime(bd+'T'+bt,'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=tz)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_sign=SIGNS[int(asc_sid//30)]; asc_idx=int(asc_sid//30)
    
    # Natal Saturn
    lt_sat,_=swe.calc_ut(jd,6); nat_sat_sid=(lt_sat[0]-ayan)%360
    nat_sat_sign=SIGNS[int(nat_sat_sid//30)]; nat_sat_deg=round(nat_sat_sid%30,2)
    nat_sat_house=(int(nat_sat_sid//30)-asc_idx)%12+1
    nat_sat_nak,nat_sat_lord,_=gn(nat_sat_sid)
    natal_sat_start=SIGNS.index(nat_sat_sign)*30
    
    sat_dig='EXALTED' if nat_sat_sign=='Libra' else ('OWN' if nat_sat_sign in ['Capricorn','Aquarius'] else ('DEBILITATED' if nat_sat_sign=='Aries' else 'neutral'))
    
    # Saturn returns
    sat_returns=[]
    for yr in range(1900,2080):
        jd_t=swe.julday(yr,6,1,12)
        lt,_=swe.calc_ut(jd_t,6)
        st=(lt[0]-swe.get_ayanamsa(jd_t))%360
        if abs(st-nat_sat_sid)<5 or abs(st-nat_sat_sid-360)<5 or abs(st-nat_sat_sid+360)<5:
            sat_returns.append(yr)
    deduped=[]; prev=None
    for yr in sat_returns:
        if prev is None or yr-prev>1: deduped.append(yr)
        prev=yr
    
    # Pre-ingress windows
    pre_ingress=[]
    for yr in range(1920,2080):
        for month in [1,4,7,10]:
            jd_t=swe.julday(yr,month,1,12)
            lt,_=swe.calc_ut(jd_t,6)
            st=(lt[0]-swe.get_ayanamsa(jd_t))%360
            dist=(natal_sat_start-st+360)%360
            if 3<=dist<=18:
                pre_ingress.append((yr,month,round(dist,0)))
    wid=[]
    for w in pre_ingress:
        if not wid or abs(w[0]-wid[-1][0])>1: wid.append(w)
    
    # Current
    jd_now=swe.julday(2026,7,31,12)
    lt_now,_=swe.calc_ut(jd_now,6)
    sat_now=(lt_now[0]-swe.get_ayanamsa(jd_now))%360
    sat_now_sign=SIGNS[int(sat_now//30)]
    dist_now=min(abs(sat_now-nat_sat_sid),360-abs(sat_now-nat_sat_sid))
    
    # Saturn aspects
    sa=nat_sat_house
    asp=[sa,(sa+2)%12+1,(sa+6)%12+1,(sa+9)%12+1]
    
    # Other key planets
    moon_sat_dist=0
    for pn,pid in {'Moon':1,'Mars':4,'Jupiter':5,'Venus':3}.items():
        lt2,_=swe.calc_ut(jd,pid)
        ps=(lt2[0]-ayan)%360
        if pn=='Moon':
            moon_sat_dist=min(abs(ps-nat_sat_sid),360-abs(ps-nat_sat_sid))
    
    B='='*75
    print(f'{B}')
    print(f'  {name.upper()} — SATURN ANALYSIS')
    print(f'{B}')
    print(f'  DOB: {bd} | TOB: {bt} | Lagna: {asc_sign} {asc_sid%30:.02f}°')
    print(f'  NATAL SATURN: {nat_sat_sign} {nat_sat_deg}° | H{nat_sat_house}({hthemes[nat_sat_house]}) | {sat_dig}')
    print(f'  Saturn Nakshatra: {nat_sat_nak} ({nat_sat_lord})')
    print(f'  Saturn Returns (age): {[(deduped[i],\"~\"+str(deduped[i]-int(bd[:4]))) for i in range(min(4,len(deduped)))]}')
    print()
    
    # Saturn aspects
    aspect_houses=[(asp[i],hthemes[asp[i]]) for i in range(4)]
    print(f'  SATURN 3-7-10 ASPECTS:')
    for h,theme in aspect_houses:
        mark=' ← natal' if h==nat_sat_house else ''
        print(f'    H{h} ({theme}){mark}')
    
    print()
    print(f'  CAREER EVENTS vs SATURN TRANSIT:')
    print(f'  {"Year":<6} {"Event":<35} {"Saturn Context":<45}')
    print(f'  {"-"*6} {"-"*35} {"-"*45}')
    
    for yr,evt,ctx in events_map[name]:
        jd_ev=swe.julday(yr,6,15,12)
        lt_ev,_=swe.calc_ut(jd_ev,6)
        sat_ev=(lt_ev[0]-swe.get_ayanamsa(jd_ev))%360
        sat_ev_sign=SIGNS[int(sat_ev//30)]
        dist_nat=min(abs(sat_ev-nat_sat_sid),360-abs(sat_ev-nat_sat_sid))
        near=' ← RETURN' if dist_nat<8 else ''
        sat_pos=f'Sat {sat_ev_sign} {sat_ev%30:.0f}° Δ{round(dist_nat)}°{near}'
        print(f'  {yr:<6} {evt:<35} {sat_pos:<45}')
    
    print()
    print(f'  CURRENT (Jul 2026): Saturn {sat_now_sign} {sat_now%30:.1f}° — Δ{round(dist_now)}° from natal Saturn')
    
    # Next return
    for yr in deduped:
        if yr>=2026: print(f'  NEXT SATURN RETURN: ~{yr} (age {yr-int(bd[:4])})'); break
    
    print()
    print(f'  PRE-INGRESS HYPOTHESIS CHECK (3-18° before Saturn enters natal {nat_sat_sign}):')
    found_events=0
    for yr,month,dist in wid:
        # Check if any event happened in ±1 year window
        near_evt=[(y,e) for y,e,c in events_map[name] if abs(y-yr)<=1]
        for ey,ee in near_evt:
            print(f'    ✓ {yr}-{month:02d}: {ee} ({dist:.0f}° before ingress)')
            found_events+=1
    if found_events==0:
        print(f'    No clear pre-ingress events found in career timeline')
    
    print()
    print(f'  SATURN INDUSTRY FIT: {nat_sat_sign} → ', end='')
    ind_map={
        'Taurus':'CS/Engineering/Manufacturing (Turing match)',
        'Gemini':'Logistics/Communication/Transport',
        'Cancer':'AI/ML/Research (Hinton, Hassabis match)',
        'Leo':'Leadership/Entertainment/Self-made',
        'Virgo':'Analysis/Service/Health',
        'Pisces':'Marketing/Brand/Media (10.8% of marketers)',
    }
    print(ind_map.get(nat_sat_sign,'General'))
    print()

print('='*75)
print('  COMPARISON TABLE')
print('='*75)
print(f'  {"":<20} {"Musk":<25} {"Bezos":<25} {"Crews":<25}')
print(f'  {"-"*20} {"-"*25} {"-"*25} {"-"*25}')

for celeb_data in celebs:
    name,bd,bt,lat,lon,tz=celeb_data
    dt=datetime.strptime(bd+'T'+bt,'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=tz)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_idx=int(asc_sid//30)
    lt_sat,_=swe.calc_ut(jd,6); nat_sat_sid=(lt_sat[0]-ayan)%360
    nat_sat_sign=SIGNS[int(nat_sat_sid//30)]; nat_sat_deg=round(nat_sat_sid%30,2)
    nat_sat_house=(int(nat_sat_sid//30)-asc_idx)%12+1
    nat_sat_nak,nat_sat_lord,_=gn(nat_sat_sid)
    sat_dig='EX' if nat_sat_sign=='Libra' else ('OWN' if nat_sat_sign in ['Capricorn','Aquarius'] else ('DEB' if nat_sat_sign=='Aries' else 'neut'))
    
    info=[
        ('Saturn Sign',f'{nat_sat_sign} ({sat_dig})'),
        ('Saturn House',f'H{nat_sat_house}'),
        ('Saturn Nakshatra',nat_sat_nak),
        ('Saturn Degree',f'{nat_sat_deg}°'),
    ]
    if name==celebs[0][0]:
        for lbl,val in info:
            print(f'  {lbl:<20} {val:<25}',end='')
    # We'll print line by line
