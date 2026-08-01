#!/usr/bin/env python3
"""200-academic-field cross-ref against P1-P9 Saturn signs"""
import swisseph as swe
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
EXALT = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
PLANETS = {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}
NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]

def gn(lon):
    for n,s,l in NAKS:
        if s<=lon%360<s+13.334: return n,l
    return 'Revati','Mercury'

def get_tz(place, country):
    p = place + ' ' + country
    if any(w in p for w in ['India','Sri Lanka','Pakistan']): return 5.5
    if any(w in p for w in ['China','Taiwan','Hong Kong']): return 8
    if any(w in p for w in ['Japan']): return 9
    if any(w in p for w in ['UK','England','Scotland','Wales','Ireland']): return 0
    if any(w in p for w in ['Germany','France','Italy','Spain','Netherlands','Belgium','Austria','Switzerland','Poland','Hungary','Czech','Romania','Norway','Sweden','Denmark','Finland','Latvia','Lithuania']): return 1
    if any(w in p for w in ['Russia','Soviet','Ukraine','Belarus','Georgia']): return 3
    if any(w in p for w in ['Brazil']): return -3
    if any(w in p for w in ['Argentina']): return -3
    if any(w in p for w in ['Mexico']): return -6
    if any(w in p for w in ['Canada']): return -5
    if any(w in p for w in ['Australia','New Zealand']): return 10
    if any(w in p for w in ['Egypt','Kenya','South Africa','Zambia']): return 2
    if any(w in p for w in ['Israel','Palestine']): return 2
    if any(w in p for w in ['Algeria']): return 1
    return -5

SAMPLE = [
    ('Richard Feynman','1918-05-11','New York','United States','Physics'),
    ('Stephen Hawking','1942-01-08','Oxford','United Kingdom','Physics'),
    ('Alan Turing','1912-06-23','London','United Kingdom','Math/CS'),
    ('John von Neumann','1903-12-28','Budapest','Hungary','Math/CS'),
    ('Grace Hopper','1906-12-09','New York','United States','CS'),
    ('Linus Torvalds','1969-12-28','Helsinki','Finland','CS'),
    ('Tim Berners-Lee','1955-06-08','London','United Kingdom','CS'),
    ('Francis Crick','1916-06-08','Northampton','United Kingdom','Biology'),
    ('Rosalind Franklin','1920-07-25','London','United Kingdom','Biology'),
    ('James Watson','1928-04-06','Chicago','United States','Biology'),
    ('Richard Dawkins','1941-03-26','Nairobi','Kenya','Biology'),
    ('Linus Pauling','1901-02-28','Portland','United States','Chemistry'),
    ('Jonas Salk','1914-10-28','New York','United States','Medicine'),
    ('Milton Friedman','1912-07-31','New York','United States','Economics'),
    ('Amartya Sen','1933-11-03','Santiniketan','India','Economics'),
    ('B.F. Skinner','1904-03-20','Susquehanna','United States','Psychology'),
    ('Noam Chomsky','1928-12-07','Philadelphia','United States','Psychology/Ling'),
    ('Geoffrey Hinton','1947-12-06','London','United Kingdom','AI/ML'),
    ('Fei-Fei Li','1976-07-03','Beijing','China','AI/ML'),
    ('Demis Hassabis','1976-07-27','London','United Kingdom','AI/ML'),
    ('Jane Goodall','1934-04-03','London','United Kingdom','Anthropology'),
    ('Jennifer Doudna','1964-02-19','Washington','United States','Biotech'),
    ('Vera Rubin','1923-07-23','Philadelphia','United States','Astronomy'),
    ('Carl Sagan','1934-11-09','New York','United States','Astronomy/Physics'),
    ('Edwin Hubble','1889-11-20','Marshfield','United States','Astronomy'),
    ('Marie Curie','1867-11-07','Warsaw','Poland','Chemistry/Physics'),
    ('Albert Einstein','1879-03-14','Ulm','Germany','Physics'),
    ('Niels Bohr','1885-10-07','Copenhagen','Denmark','Physics'),
    ('J. Robert Oppenheimer','1904-04-22','New York','United States','Physics'),
    ('Enrico Fermi','1901-09-29','Rome','Italy','Physics'),
    ('Paul Dirac','1902-08-08','Bristol','United Kingdom','Physics'),
]

results = []
for name,bday,city,country,field in SAMPLE:
    try:
        y,m,d = map(int,bday.split('-'))
        dt = datetime(y,m,d,12,0,0)
        dt = dt.replace(tzinfo=timezone(timedelta(hours=get_tz(city,country))))
        dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,12)
        ayan = swe.get_ayanamsa(jd)
        planets = {}
        for pn,pid in PLANETS.items():
            lt,_ = swe.calc_ut(jd,pid); lt=lt[0]
            sid = (lt-ayan)%360; sgn = SIGNS[int(sid//30)]; nk,nl = gn(sid)
            dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
            planets[pn] = {'sign':sgn,'nakshatra':nk,'dignity':dig}
        rh,_ = swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360
        planets['Rahu'] = {'sign':SIGNS[int(rh//30)]}
        
        results.append({
            'name':name,'field':field,
            'sat_sign':planets['Saturn']['sign'],
            'moon_nak':planets['Moon']['nakshatra'],
            'sun_sign':planets['Sun']['sign'],
        })
    except Exception as e:
        pass

print(f'Computed: {len(results)} academics')

# Group by field category
fields = {}
for r in results:
    f = r['field']
    if '/' in f: f = f.split('/')[0]
    if f not in fields: fields[f] = []
    fields[f].append(r)

print()
print('='*60)
print('ACADEMIC FIELD x SATURN SIGN')
print('='*60)
for field, people in sorted(fields.items()):
    sats = Counter(p['sat_sign'] for p in people)
    top = sats.most_common(2)
    print(f'{field:<18} n={len(people):>2} | ' + ' | '.join(f'{s}({c})' for s,c in top))

print()
print('='*60)
print('P1-P9 SATURN vs ACADEMIC FIELDS')
print('='*60)
p_sat = {'P1':'Capricorn','P3':'Pisces','P4':'Pisces','P5':'Taurus','P6':'Cancer','P7':'Gemini','P8':'Capricorn','P9':'Aries'}
for pid,ps in p_sat.items():
    matches = []
    for r in results:
        if r['sat_sign'] == ps:
            matches.append(r['name'] + '(' + r['field'] + ')')
    print(f'{pid} Saturn {ps:<12}: {len(matches)} — {", ".join(matches[:3])}')

# AI/ML specific
print()
print('='*60)
print('AI/ML & COMPUTER SCIENCE SATURN SIGNS')
print('='*60)
cs_ai = [r for r in results if r['field'] in ['CS','AI','Math/CS','Physics']]
sats = Counter(r['sat_sign'] for r in cs_ai)
for s,c in sats.most_common():
    names = [r['name'] for r in cs_ai if r['sat_sign']==s]
    print(f'  Saturn {s:<12}: {c} — {", ".join(names[:4])}')
