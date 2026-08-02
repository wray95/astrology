#!/usr/bin/env python3
"""
═════════════════════════════════════════════════════════
NEXUS P-SERIES RANKING — NAME-BASED · PERCENTAGE SCORES
SL Degrees (Metro/ESOFT) + Career + Marriage + Children
═════════════════════════════════════════════════════════
"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
S = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EX = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DB = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OW = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

PD = {
    'Bappa':      ('Polgahawela Bappa',1962,5,27,3,38,54,7.3381,80.3003,5.5),
    'Upulakshi':  ('Upulakshi',1997,3,14,9,38,0,6.9355,79.8487,5.5),
    'Senith':     ('Senith',1995,8,7,21,18,0,6.9355,79.8487,5.5),
    'Niromi':     ('Niromi',1967,4,25,8,17,37,6.9355,79.8487,5.5),
    'Senath':     ('Senath',2001,5,14,16,8,40,6.9355,79.8487,5.5),
    'Dewli':      ('Dewli',2005,10,8,8,22,0,6.9097,79.8900,5.5),
    'Sineth':     ('Sineth',2005,4,5,16,5,48,6.9271,79.8612,5.5),
    'Lakshi Amma':('Lakshi Amma',1963,11,16,9,4,15,7.486,80.362,5.5),
    'Lalith Uncle':('Lalith Uncle',1970,8,31,21,55,30,7.2931,80.635,5.5),
}

SL_MARKET = {
    'IT/Tech':      {'jobs':['Software Engineer','Data Scientist','Network Eng','QA Engineer','DevOps'],'degree':'BSc SE/DS (Metro) / BSc IT (ESOFT)'},
    'Banking':      {'jobs':['Banker','Financial Analyst','Accountant','Auditor'],'degree':'BBA (Metro) / BSc Business (ESOFT)'},
    'Logistics':    {'jobs':['Logistics Mgr','SCM Analyst','Freight Forwarder','Shipping'],'degree':'BBA (Metro) / BSc QS (Metro)'},
    'Tourism':      {'jobs':['Hotel Manager','Chef','Travel Agent','Event Mgr'],'degree':'BSc Psychology (Metro) / BBA (Metro)'},
    'BPO':          {'jobs':['CSR','Call Center Mgr','BPO Lead','KPO Analyst'],'degree':'BSc IT (ESOFT) / HND Computing (ESOFT)'},
    'Construction': {'jobs':['Civil Engineer','QS','Architect','Project Mgr'],'degree':'BSc QS (Metro) / BSc Civil Eng'},
    'Education':    {'jobs':['Lecturer','Tuition Master','Academic Coord','Principal'],'degree':'BSc IT (Metro/ESOFT) / BA Education'},
    'Healthcare':   {'jobs':['Doctor','Nurse','Pharmacist','Radiographer'],'degree':'BSc Psychology (Metro) / MBBS'},
    'Government':   {'jobs':['Admin Officer','SLAS','SLPS','Foreign Service'],'degree':'BBA (Metro) / LLB (Metro)'},
}

def to_pct(raw, floor=-2.0, ceil=10.5):
    """Convert raw composite score to 0-100% scale."""
    return max(0, min(100, round((raw - floor) / (ceil - floor) * 100)))

def compute(name_key):
    name,y,m,d,h,mi,s,lat,lon,tz = PD[name_key]
    ist=timezone(timedelta(hours=tz)); dt=datetime(y,m,d,h,mi,s,tzinfo=ist)
    utc=dt.astimezone(timezone.utc)
    jd=swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60+utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_idx=int(asc_sid//30); lagna=S[asc_idx]
    planets={}
    for pn,pid2 in [('Sun',0),('Moon',1),('Mars',4),('Mercury',2),('Jupiter',5),('Venus',3),('Saturn',6)]:
        lt,_=swe.calc_ut(jd,pid2); sid=(lt[0]-ayan)%360; sgn=S[int(sid//30)]
        h=(int(sid//30)-asc_idx)%12+1
        dgn=100 if(pn in EX and EX[pn]==sgn) else (75 if(pn in OW and sgn in OW[pn]) else (-100 if(pn in DB and DB[pn]==sgn) else 0))
        planets[pn]={'sign':sgn,'house':h,'dignity':dgn,'sid':sid}
    v9l=(asc_sid*9)%360; v9li=int(v9l//30)
    d9={}
    for pn in P7:
        vl=(planets[pn]['sid']*9)%360; vs=S[int(vl//30)]; vh=(S.index(vs)-v9li)%12+1
        dgn9=100 if(pn in EX and EX[pn]==vs)else(75 if(pn in OW and vs in OW[pn])else(-100 if(pn in DB and DB[pn]==vs)else 0))
        d9[pn]={'sign':vs,'house':vh,'dignity':dgn9}
    v10l=(asc_sid*10)%360; v10li=int(v10l//30)
    d10_10l_sign=S[(v10li+9)%12]; d10l=SL[d10_10l_sign]
    d10={}
    for pn in P7:
        vl=(planets[pn]['sid']*10)%360; vs=S[int(vl//30)]; vh=(S.index(vs)-v10li)%12+1
        d10[pn]={'sign':vs,'house':vh}
    d10h=d10[d10l]['house']
    d1_10l=SL[S[(asc_idx+9)%12]]; d1h=planets[d1_10l]['house']
    # D7 (Saptamsha) — marriage
    v7l=(asc_sid*7)%360; v7li=int(v7l//30)
    d7={'asc':S[v7li]}
    for pn in P7:
        vl=(planets[pn]['sid']*7)%360; vs=S[int(vl//30)]
        vh=(S.index(vs)-v7li)%12+1
        dgn7=100 if(pn in EX and EX[pn]==vs)else(75 if(pn in OW and vs in OW[pn])else(-100 if(pn in DB and DB[pn]==vs)else 0))
        d7[pn]={'sign':vs,'house':vh,'dignity':dgn7}
    # D5 (Panchamsha) — children
    v5l=(asc_sid*5)%360; v5li=int(v5l//30)
    d5={'asc':S[v5li]}
    for pn in P7:
        vl=(planets[pn]['sid']*5)%360; vs=S[int(vl//30)]
        vh=(S.index(vs)-v5li)%12+1
        dgn5=100 if(pn in EX and EX[pn]==vs)else(75 if(pn in OW and vs in OW[pn])else(-100 if(pn in DB and DB[pn]==vs)else 0))
        d5[pn]={'sign':vs,'house':vh,'dignity':dgn5}
    return {
        'name':name,'lagna':lagna,'asc_deg':asc_sid%30,'planets':planets,'d9':d9,
        'd1_10l':d1_10l,'d1_10l_h':d1h,'d10_10l':d10l,'d10_10l_h':d10h,
        'age':2026-y,'d7':d7,'d5':d5
    }

def score_career(ch):
    p=ch['planets']; sc={k:0 for k in SL_MARKET}
    ss=p['Saturn']['sign']
    if ss=='Gemini':sc['Logistics']+=3
    if ss in('Capricorn','Aquarius'):sc['Construction']+=2;sc['Government']+=1
    if ss=='Pisces':sc['Education']+=2;sc['Tourism']+=1
    d1l=ch['d1_10l'];d1h=ch['d1_10l_h'];d10h=ch['d10_10l_h']
    if d1l=='Mercury':sc['IT/Tech']+=3;sc['BPO']+=2;sc['Education']+=2
    if d1l=='Venus':sc['Tourism']+=2
    if d1l=='Mars':sc['Construction']+=2;sc['Logistics']+=2
    if d1l=='Jupiter':sc['Education']+=3;sc['Government']+=2;sc['Banking']+=2
    if d1l=='Saturn':sc['Construction']+=3;sc['Government']+=2
    if d1l=='Sun':sc['Government']+=3
    if d1l=='Moon':sc['Healthcare']+=2;sc['Tourism']+=2
    if d1h in(1,4,7,10):sc['Government']+=1
    if d10h in(1,4,7,10):
        for k in sc:sc[k]+=1
    elif d10h in(6,8,12):sc['BPO']+=1;sc['Logistics']+=1
    if sum(1 for pn in P7 if p[pn]['house']==10)>=3:sc['Education']+=3
    return max(sc,key=sc.get)

def composite(ch):
    p=ch['planets'];comp=0
    for pl in[('Mars',''),('Mercury',''),('Jupiter',''),('Venus',''),('Saturn','')]:
        if p[pl[0]]['dignity']>=75 and p[pl[0]]['house']in(1,4,7,10):comp+=4.0
    g={}
    for pn in P7:
        lord=SL[p[pn]['sign']]
        if lord!=pn:g[pn]=lord
    loops=[];vis=set()
    for start in P7:
        path=[];curr=start
        while curr in g and curr not in path:path.append(curr);curr=g[curr]
        if curr in path:
            cycle=path[path.index(curr):];t=tuple(sorted(cycle))
            if 2<=len(cycle)<=5 and t not in vis:vis.add(t);loops.append(cycle)
    if loops:comp+=2.0
    if ch['d10_10l_h']in(1,4,7,10):comp+=2.5
    elif ch['d10_10l_h']in(6,8,12):comp-=2.5
    hinv={}
    for pn in P7:hinv.setdefault(p[pn]['house'],[]).append(pn)
    raja=0
    for kh in[1,4,7,10]:
        for tr in[1,5,9]:
            for kl in hinv.get(kh,[]):
                for cl in hinv.get(tr,[]):
                    if kl!=cl and p[kl]['house']==p[cl]['house']:raja+=1
    comp+=min(raja,5)*1.0
    if ch['d9'].get('Venus',{}).get('dignity',0)>=75:comp+=2.0
    return comp

def marriage_score(ch):
    """D7-based marriage potential (0-8 raw → 0-100%)."""
    d7=ch['d7'];d1=ch['planets'];raw=0
    lagna=ch['lagna']
    d7_7l_sign=S[(S.index(d7['asc'])+6)%12]
    d7_7l=SL[d7_7l_sign]
    d7_7l_h=d7[d7_7l]['house'] if d7_7l in d7 else -1
    d7_7l_dig=d7[d7_7l]['dignity'] if d7_7l in d7 else 0
    venus_d7_h=d7['Venus']['house']
    venus_d7_dig=d7['Venus']['dignity']
    if d7_7l_dig==100:raw+=3
    elif d7_7l_dig>=75:raw+=2
    if venus_d7_dig>=75:raw+=2
    if d7_7l_h in(1,4,7,10):raw+=2
    if venus_d7_h in(1,4,7,10):raw+=1
    d1_7l=SL[S[(S.index(lagna)+6)%12]]
    d1_7l_h=d1[d1_7l]['house'] if d1_7l in d1 else -1
    if d1_7l_h in(1,4,7,10):raw+=1
    return to_pct(raw, 0, 9)

def children_score(ch):
    """D5-based children potential (raw → 0-100%)."""
    d5=ch['d5']; raw=0
    d5_5l_sign=S[(S.index(d5['asc'])+4)%12]
    d5_5l=SL[d5_5l_sign]
    d5_5l_h=d5[d5_5l]['house'] if d5_5l in d5 else -1
    d5_5l_dig=d5[d5_5l]['dignity'] if d5_5l in d5 else 0
    jup_d5_h=d5['Jupiter']['house']
    jup_d5_dig=d5['Jupiter']['dignity']
    sat_d5_h=d5['Saturn']['house']
    sat_aspects_5=1 if((sat_d5_h+4)%12+1==5 or(sat_d5_h+6)%12+1==5 or(sat_d5_h+9)%12+1==5)else 0
    if jup_d5_dig==100:raw+=3
    elif jup_d5_dig>=75:raw+=2
    if d5_5l_dig>=75:raw+=2
    if jup_d5_h in(1,4,5,7,9,10):raw+=1
    if sat_aspects_5:raw-=2
    return to_pct(raw, -2, 7)

charts={k:compute(k) for k in PD}
with open('dataset/p_series_shadbala_av.json') as f: sb_data=json.load(f)

rows=[]
for name_key in PD:
    ch=charts[name_key]; sb=sb_data.get('P'+str(list(PD.keys()).index(name_key)+1),{}).get('d1',{})
    # Match shadbala by name
    pid_map = {'Bappa':'P1','Upulakshi':'P2','Senith':'P3','Niromi':'P4','Senath':'P5',
               'Dewli':'P6','Sineth':'P7','Lakshi Amma':'P8','Lalith Uncle':'P9'}
    sb=sb_data.get(pid_map[name_key],{}).get('d1',{})
    avg_sb=sum(p.get('shadbala_rupas',0) for p in sb.values())/max(len(sb),1) if sb else 0
    comp=composite(ch); career=score_career(ch)
    marry=marriage_score(ch); kids=children_score(ch)
    comp_pct=to_pct(comp)
    mps=[yn for pl,yn in[('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if ch['planets'][pl]['dignity']>=75 and ch['planets'][pl]['house']in(1,4,7,10)]
    rows.append((comp_pct, name_key, ch, career, comp, avg_sb, marry, kids, mps))

rows.sort(key=lambda x:-x[0])

print("="*115)
print("  NEXUS P-SERIES RANKING — ALL SCORES IN %")
print("="*115)
hdr = f"\n  {'#':<3s}{'Name':<16s}{'Age':>4s}{'Lagna':<8s}{'Career':<17s}{'Degree':<30s}{'Role':<20s}{'Total%':>7s}{'Marry%':>7s}{'Kids%':>7s}"
print(hdr)
print("  "+"-"*113)

for i,(comp_pct,name_key,ch,career,raw_comp,avg_sb,marry,kids,mps) in enumerate(rows):
    p=ch['planets']
    market=SL_MARKET[career]
    role=market['jobs'][0]
    deg=market['degree']
    mp_str=' ⭐'+','.join(mps) if mps else ''
    print(f"  {i+1:<3d}{ch['name']:<16s}{ch['age']:>4d}{ch['lagna']:<8s}{career:<17s}{deg[:29]:<30s}{role:<20s}{comp_pct:>6d}%{marry:>6d}%{kids:>6d}%{mp_str}")

# ── Per-person detail ──
print(f"\n{'='*115}")
print(f"  DETAILED ANALYSIS")
print(f"{'='*115}")
for i,(comp_pct,name_key,ch,career,raw_comp,avg_sb,marry,kids,mps) in enumerate(rows):
    p=ch['planets']
    market=SL_MARKET[career]
    print(f"\n  {i+1}. {ch['name']} ({ch['lagna']} {ch['asc_deg']:.1f}°)")
    print(f"     Total: {comp_pct}% | Marriage: {marry}% | Children: {kids}% | Avg Shadbala: {avg_sb:.1f} R")
    print(f"     D1 10L: {ch['d1_10l']} H{ch['d1_10l_h']}({p[ch['d1_10l']]['sign']}) | D10 10L: {ch['d10_10l']} H{ch['d10_10l_h']}")
    print(f"     Saturn: {p['Saturn']['sign']} H{p['Saturn']['house']} | Career: {career}")
    if mps: print(f"     Mahapurusha: {', '.join(mps)}")
    print(f"     🎓 {market['degree']}")
    print(f"     💼 {', '.join(market['jobs'])}")
    # D7/D5 insight
    d7_7l_sign=S[(S.index(ch['d7']['asc'])+6)%12]
    d7_7l=SL[d7_7l_sign]
    d7_7l_h=ch['d7'][d7_7l]['house'] if d7_7l in ch['d7'] else '?'
    d5_5l_sign=S[(S.index(ch['d5']['asc'])+4)%12]
    d5_5l=SL[d5_5l_sign]
    jup_d5_h=ch['d5']['Jupiter']['house']
    print(f"     D7 7L: {d7_7l} H{d7_7l_h} | D5 5L: {d5_5l} | Jup D5: H{jup_d5_h}")

# ── Rank by Marriage ──
print(f"\n{'─'*80}")
print(f"  MARRIAGE POTENTIAL RANKING (D7 Saptamsha)")
rows_marry = sorted(rows, key=lambda x:-x[6])
for i,(comp_pct,name_key,ch,career,raw_comp,avg_sb,marry,kids,mps) in enumerate(rows_marry):
    bar = '█' * (marry // 5)
    print(f"  {i+1}. {ch['name']:<16s} {marry:>3d}% {bar}")

# ── Rank by Children ──
print(f"\n{'─'*80}")
print(f"  CHILDREN POTENTIAL RANKING (D5 Panchamsha)")
rows_kids = sorted(rows, key=lambda x:-x[7])
for i,(comp_pct,name_key,ch,career,raw_comp,avg_sb,marry,kids,mps) in enumerate(rows_kids):
    bar = '█' * (kids // 5)
    print(f"  {i+1}. {ch['name']:<16s} {kids:>3d}% {bar}")
