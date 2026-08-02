#!/usr/bin/env python3
"""Find 10 real people matching each P-series chart (90 total)"""
import swisseph as swe, csv, gzip
from datetime import datetime, timezone, timedelta
swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
P7=['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

P_CHARTS=[
    ('P1','Polgahawela Bappa','1962-05-27','03:38:54',7.3381,80.3003),
    ('P2','Upulakshi','1997-03-14','09:38:00',6.9355,79.8487),
    ('P3','Senith','1995-08-07','21:18:00',6.9355,79.8487),
    ('P4','Niromi','1967-04-25','08:17:37',6.9355,79.8487),
    ('P5','Senath','2001-05-14','16:08:40',6.9355,79.8487),
    ('P6','Dewli','2005-10-08','08:22:00',6.9097,79.8900),
    ('P7','Sineth','2005-04-05','16:05:48',6.9271,79.8612),
    ('P8','Lakshi Amma','1963-11-16','09:04:15',7.486,80.362),
    ('P9','Lalith Uncle','1970-08-31','21:55:30',7.2931,80.635),
]

p_signs={}
for pid,name,bd,bt,lat,lon in P_CHARTS:
    dt=datetime.strptime(bd+'T'+bt,'%Y-%m-%dT%H:%M:%S')
    dt=dt.replace(tzinfo=timezone(timedelta(hours=5.5)))
    dt_utc=dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd=swe.julday(dt_utc.year,dt_utc.month,dt_utc.day,dt_utc.hour+dt_utc.minute/60+dt_utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    signs={}
    for pn,pid2 in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt,_=swe.calc_ut(jd,pid2); lt=lt[0]; sid=(lt-ayan)%360
        signs[pn]=SIGNS[int(sid//30)]
    rh,_=swe.calc_ut(jd,swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    signs['Rahu']=SIGNS[int(rh//30)]; signs['Ketu']=SIGNS[int(kh//30)]
    p_signs[pid]=signs

print('P-Series Signs:')
for pid in sorted(p_signs):
    s=p_signs[pid]
    print(f'  {pid}: Sun={s["Sun"]} Moon={s["Moon"]} Mars={s["Mars"]} Merc={s["Mercury"]} Jup={s["Jupiter"]} Ven={s["Venus"]} Sat={s["Saturn"]}')
print()

# Load Q-series
q_people=[]
with gzip.open('outputs/all_planets_q_series/q_all_planet_positions.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        signs={}
        for pn in P7+['Rahu','Ketu']:
            sn=row.get(f'{pn}_sign','')
            if sn: signs[pn]=sn
        if len(signs)>=7:
            q_people.append({'qid':row['q_id'],'name':row.get('name','?'),'bd':row.get('birth_date',''),'signs':signs})

# Load bio
bio_map={}
with gzip.open('outputs/q_biographical_wikipedia/q_biographical_details.csv.gz','rt') as f:
    for row in csv.DictReader(f):
        bio_map[row['q_id']]={'occ':row.get('occupation',''),'kids':row.get('children','')[:60]}

B='='*85

for pid in [f'P{i}' for i in range(1,10)]:
    p_v=p_signs[pid]
    p_name=P_CHARTS[int(pid[1])-1][1]
    scored=[]
    for q in q_people:
        score=0; match_planets=[]
        for pn in P7:
            if pn in p_v and pn in q['signs']:
                if p_v[pn]==q['signs'][pn]:
                    score+=1
                    match_planets.append(pn)
        if score>=5:
            scored.append((score,','.join(match_planets),q))
    scored.sort(key=lambda x:-x[0])
    
    print(f'{B}')
    print(f'  {pid} {p_name} — Top 10 Matches')
    print(f'{B}')
    hdr=f'  {"Name":<32} {"Birth":<12} {"S":>2} {"Matched Planets":<45} {"Occupation":<40}'
    print(hdr)
    print('  '+'-'*(len(hdr)-4))
    for s,mps,q in scored[:10]:
        bio=bio_map.get(q['qid'],{})
        occ=bio.get('occ','?')[:39]
        print(f'  {q["name"]:<32} {q["bd"]:<12} {s:>2}  {mps:<45} {occ:<40}')
    if not scored: print('  No 5+/7 matches found.')
    print()

print(f'{B}')
print('  SUMMARY')
print(f'{B}')
for pid in [f'P{i}' for i in range(1,10)]:
    p_v=p_signs[pid]
    p_name=P_CHARTS[int(pid[1])-1][1]
    count=sum(1 for q in q_people if sum(1 for pn in P7 if pn in p_v and pn in q['signs'] and p_v[pn]==q['signs'][pn])>=5)
    best_match=max((sum(1 for pn in P7 if pn in p_v and pn in q['signs'] and p_v[pn]==q['signs'][pn]),q['name']) for q in q_people) if q_people else (0,'?')
    print(f'  {pid} {p_name:<22s}: {count:>4d} matches (5+/7), best: {best_match[1]} ({best_match[0]}/7)')
