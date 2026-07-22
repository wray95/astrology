#!/usr/bin/env python3
"""Validate the prediction framework against real celebrity charts.
Computes sidereal (Lahiri) positions via Swiss Ephemeris and tallies the
'high-potential' markers used in the repo's yoga references:
exaltation, own-sign, debilitation, Gajakesari, Mahapurisa.
"""
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
SIGNS = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']

# BPHS exaltation / debilitation (sign indices: Aries=0..Pisces=11)
EX = {'Su':0,'Mo':1,'Ma':9,'Me':5,'Ju':3,'Ve':11,'Sa':6}  # Sun exalts in ARIES (0), not Leo
DB = {'Su':7,'Mo':8,'Ma':3,'Me':11,'Ju':9,'Ve':5,'Sa':0}
# own signs
OW = {'Su':[4],'Mo':[3],'Ma':[0,8],'Me':[2,5],'Ju':[8,11],'Ve':[1,6],'Sa':[9,10]}

def jd_ut(y,m,d,h,mi,tz):
    # robust: add fractional day to midnight JD (handles prev/next-day rollover)
    return swe.julday(y,m,d,0) + (h - tz + mi/60.0)/24.0

def pos(jd, ipl):
    res = swe.calc_ut(jd, ipl, swe.FLG_SIDEREAL)
    return res[0][0] % 360.0

def status(pl, sign):
    if sign == EX[pl]: return 'Ex'
    if sign == DB[pl]: return 'Db'
    if sign in OW[pl]: return 'Own'
    return '-'

def chart(y,m,d,h,mi,tz,lat,lon):
    jd = jd_ut(y,m,d,h,mi,tz)
    asc = swe.houses(jd, lat, lon, b'W')[1][0] % 360.0
    lag = int(asc/30)
    pls = {'Su':0,'Mo':1,'Ma':4,'Me':2,'Ju':5,'Ve':3,'Sa':6}
    out = {}
    for pl,ipl in pls.items():
        lon = pos(jd,ipl); s=int(lon/30); dgr=lon-s*30
        house = ((s - lag) % 12) + 1
        out[pl] = {'sign':s,'deg':round(dgr,1),'status':status(pl,s),'house':house}
    # nodes
    rahu = pos(jd, swe.MEAN_NODE); rs=int(rahu/30)
    ketu = (rahu+180)%360; ks=int(ketu/30)
    out['Ra']={'sign':rs,'deg':round(rahu%30,1),'status':'-','house':((rs-lag)%12)+1}
    out['Ke']={'sign':ks,'deg':round(ketu%30,1),'status':'-','house':((ks-lag)%12)+1}
    # markers
    ex=sum(1 for p in pls if out[p]['status']=='Ex')
    own=sum(1 for p in pls if out[p]['status']=='Own')
    db=sum(1 for p in pls if out[p]['status']=='Db')
    # Gajakesari: Moon Kendra from Jupiter
    gaja = ((out['Mo']['house'] - out['Ju']['house']) % 12) in (0,3,6,9)
    # Mahapurisa: Mars/Mer/Jup/Ven/Sat in Kendra(1,4,7,10) AND Ex/Own
    maha=[]
    for p in ['Ma','Me','Ju','Ve','Sa']:
        if out[p]['house'] in (1,4,7,10) and out[p]['status'] in ('Ex','Own'):
            maha.append(p)
    strong = ex + own
    return {'jd':jd,'lag':lag,'lag_name':SIGNS[lag],'pl':out,
            'ex':ex,'own':own,'db':db,'gaja':gaja,'maha':maha,'strong':strong}

def line(name, c):
    pls = c['pl']
    parts=[f"{p}:{SIGNS[pls[p]['sign']]}/{pls[p]['status']}" for p in ['Su','Mo','Ma','Me','Ju','Ve','Sa']]
    return (f"{name:18} Lg={SIGNS[c['lag']]:3} | "+" ".join(parts)+
            f" | Ex{ c['ex']} Own{c['own']} Db{c['db']} Gaja{'Y' if c['gaja'] else 'N'} "
            f"Maha:{','.join(c['maha']) or '-'} strong={c['strong']}")

PEOPLE = [
  # celebrities (globally successful) — birth data from indastro.com
  ("Elon Musk",1971,6,28,7,30,2,-25.7479,28.2293),
  ("Beyonce",1981,9,4,21,47,-5,29.7604,-95.3698),
  ("A.R.Rahman",1966,1,6,16,33,5.5,13.0827,80.2707),
  ("Lionel Messi",1987,6,24,20,30,-3,-32.9442,-60.6505),
  ("Sachin Tendulkar",1973,4,24,16,28,5.5,19.0760,72.8777),
  ("Aamir Khan",1965,3,14,6,15,5.5,19.0760,72.8777),
  ("Billie Eilish",2001,12,18,11,30,-8,34.0522,-118.2437),
  ("Rihanna",1988,2,20,8,50,-4,13.1939,-59.5432),
  ("Tom Brady",1977,8,3,11,48,-7,37.5625,-122.2742),
  # our three persons
  ("Person2 (1997)",1997,3,14,9,38,5.5,6.9271,79.8612),
  ("Person3 (1995)",1995,8,7,21,18,5.5,6.9271,79.8612),
  ("Person1 (1962)",1962,5,27,3,38,5.5,6.47,79.98),
]

celeb, pers = [], []
for nm in PEOPLE:
    name,y,m,d,h,mi,tz,lat,lon = nm
    c = chart(y,m,d,h,mi,tz,lat,lon)
    print(line(name,c))
    (celeb if name.startswith(('Elon','Bey','A.R','Lio','Sac','Aam','Bil','Rih','Tom')) else pers).append((name,c))

print("\n=== META ===")
import statistics as st
cavg = st.mean(c['strong'] for _,c in celeb)
pavg = st.mean(c['strong'] for _,c in pers)
print(f"Avg 'strong' markers (Ex+Own): celebrities={cavg:.2f}  our-persons={pavg:.2f}")
for name,c in celeb+pers:
    print(f"  {name:18} strong={c['strong']}  Gaja={'Y' if c['gaja'] else 'N'}  Maha={','.join(c['maha']) or '-'}")
