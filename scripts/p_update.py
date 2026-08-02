#!/usr/bin/env python3
"""
═════════════════════════════════════════════════════════
NEXUS P-SERIES RANKING — EVERY TURN DISPLAY
SL Degrees (Metro/ESOFT) + Career + Composite Score
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
    'P1':('Polgahawela Bappa',1962,5,27,3,38,54,7.3381,80.3003,5.5),
    'P2':('Upulakshi',1997,3,14,9,38,0,6.9355,79.8487,5.5),
    'P3':('Senith',1995,8,7,21,18,0,6.9355,79.8487,5.5),
    'P4':('Niromi',1967,4,25,8,17,37,6.9355,79.8487,5.5),
    'P5':('Senath',2001,5,14,16,8,40,6.9355,79.8487,5.5),
    'P6':('Dewli',2005,10,8,8,22,0,6.9097,79.8900,5.5),
    'P7':('Sineth',2005,4,5,16,5,48,6.9271,79.8612,5.5),
    'P8':('Lakshi Amma',1963,11,16,9,4,15,7.486,80.362,5.5),
    'P9':('Lalith Uncle',1970,8,31,21,55,30,7.2931,80.635,5.5),
}

SL_MARKET = {
    'IT/Tech': {'jobs':['Software Engineer','Data Scientist','Network Eng','QA Engineer','DevOps'],'degree':'BSc SE/DS (Metro) / BSc IT (ESOFT)'},
    'Banking': {'jobs':['Banker','Financial Analyst','Accountant','Auditor'],'degree':'BBA (Metro) / BSc Business (ESOFT)'},
    'Logistics': {'jobs':['Logistics Mgr','SCM Analyst','Freight Forwarder','Shipping'],'degree':'BBA (Metro) / BSc QS (Metro)'},
    'Tourism': {'jobs':['Hotel Manager','Chef','Travel Agent','Event Mgr'],'degree':'BSc Psychology (Metro) / BBA (Metro)'},
    'BPO': {'jobs':['CSR','Call Center Mgr','BPO Lead','KPO Analyst'],'degree':'BSc IT (ESOFT) / HND Computing (ESOFT)'},
    'Construction': {'jobs':['Civil Engineer','QS','Architect','Project Mgr'],'degree':'BSc QS (Metro) / BSc Civil Eng'},
    'Education': {'jobs':['Lecturer','Tuition Master','Academic Coord','Principal'],'degree':'BSc IT (Metro/ESOFT) / BA Education'},
    'Healthcare': {'jobs':['Doctor','Nurse','Pharmacist','Radiographer'],'degree':'BSc Psychology (Metro) / MBBS'},
    'Government': {'jobs':['Admin Officer','SLAS','SLPS','Foreign Service'],'degree':'BBA (Metro) / LLB (Metro)'},
}

def compute(pid):
    name,y,m,d,h,mi,s,lat,lon,tz = PD[pid]
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
        dgn=100 if(pn in EX and EX[pn]==sgn)else(75 if(pn in OW and sgn in OW[pn])else(-100 if(pn in DB and DB[pn]==sgn)else 0))
        planets[pn]={'sign':sgn,'house':h,'dignity':dgn,'sid':sid}
    # D9
    v9l=(asc_sid*9)%360; v9li=int(v9l//30)
    d9={}
    for pn in P7:
        vl=(planets[pn]['sid']*9)%360; vs=S[int(vl//30)]; vh=(S.index(vs)-v9li)%12+1
        dgn9=100 if(pn in EX and EX[pn]==vs)else(75 if(pn in OW and vs in OW[pn])else(-100 if(pn in DB and DB[pn]==vs)else 0))
        d9[pn]={'sign':vs,'house':vh,'dignity':dgn9}
    # D10
    v10l=(asc_sid*10)%360; v10li=int(v10l//30)
    d10_10l_sign=S[(v10li+9)%12]; d10l=SL[d10_10l_sign]
    d10={}
    for pn in P7:
        vl=(planets[pn]['sid']*10)%360; vs=S[int(vl//30)]; vh=(S.index(vs)-v10li)%12+1
        d10[pn]={'sign':vs,'house':vh}
    d10h=d10[d10l]['house']
    d1_10l=SL[S[(asc_idx+9)%12]]; d1h=planets[d1_10l]['house']
    return {'name':name,'lagna':lagna,'asc_deg':asc_sid%30,'planets':planets,'d9':d9,
            'd1_10l':d1_10l,'d1_10l_h':d1h,'d10_10l':d10l,'d10_10l_h':d10h,'age':2026-y}

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
    # MP
    for pl in[('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if p[pl[0]]['dignity']>=75 and p[pl[0]]['house']in(1,4,7,10):comp+=4.0
    # Shrinkhala
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
    # D10 10L
    if ch['d10_10l_h']in(1,4,7,10):comp+=2.5
    elif ch['d10_10l_h']in(6,8,12):comp-=2.5
    # Raja
    hinv={}
    for pn in P7:hinv.setdefault(p[pn]['house'],[]).append(pn)
    raja=0
    for kh in[1,4,7,10]:
        for tr in[1,5,9]:
            for kl in hinv.get(kh,[]):
                for cl in hinv.get(tr,[]):
                    if kl!=cl and p[kl]['house']==p[cl]['house']:raja+=1
    comp+=min(raja,5)*1.0
    # D9 Venus own
    if ch['d9'].get('Venus',{}).get('dignity',0)>=75:comp+=2.0
    return comp

charts={pid:compute(pid) for pid in PD}

# Load Shadbala
with open('dataset/p_series_shadbala_av.json') as f: sb_data=json.load(f)

rows=[]
for pid in PD:
    ch=charts[pid];sb=sb_data.get(pid,{}).get('d1',{})
    sc=score_career(ch);comp=composite(ch)
    avg_sb=sum(p.get('shadbala_rupas',0) for p in sb.values())/max(len(sb),1) if sb else 0
    mps=[yn for pl,yn in[('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')] if ch['planets'][pl]['dignity']>=75 and ch['planets'][pl]['house']in(1,4,7,10)]
    rows.append((comp,pid,ch,sc,avg_sb,mps))

rows.sort(key=lambda x:-x[0])

print("="*100)
print("  NEXUS P1-P9 RANKING — EVERY TURN — SRI LANKAN DEGREES + CAREER CALIBRATION")
print("="*100)
print(f"\n  {'#':<3s}{'ID':<4s} {'Name':<15s}{'Age':>4s}{'Lagna':<8s}{'°':>5s}{'D1 10L':<8s}{'D10 10L':<10s}{'Top SL Sector':<17s}{'🎓 Degree':<30s}{'💼 Role':<22s}{'Score':>6s}")
print("  "+"-"*97)

for i,(comp,pid,ch,sc,sb,mps) in enumerate(rows):
    p=ch['planets']
    d1s=f"{ch['d1_10l']}H{ch['d1_10l_h']}"
    d10s=f"{ch['d10_10l']}H{ch['d10_10l_h']}"
    market=SL_MARKET[sc]
    role=market['jobs'][0]
    deg=market['degree']
    mp_str='⭐'+','.join(mps) if mps else ''
    print(f"  {i+1:<3d}{pid:<4s}{ch['name']:<15s}{ch['age']:>4d}{ch['lagna']:<8s}{ch['asc_deg']:>4.1f}°{d1s:<8s}{d10s:<10s}{sc:<17s}{deg:<30s}{role:<22s}{comp:>5.1f} {mp_str}")

print(f"\n  {'='*100}")
print(f"  DEGREE & CAREER PATHWAY DETAIL")
print(f"  {'='*100}")
for i,(comp,pid,ch,sc,sb,mps) in enumerate(rows):
    p=ch['planets']
    market=SL_MARKET[sc]
    print(f"\n  {i+1}. {pid} {ch['name']} ({ch['lagna']} {ch['asc_deg']:.1f}°)   Score: {comp:.1f}")
    print(f"     D1 10L: {ch['d1_10l']} H{ch['d1_10l_h']}({p[ch['d1_10l']]['sign']}) | D10 10L: {ch['d10_10l']} H{ch['d10_10l_h']}")
    print(f"     Saturn: {p['Saturn']['sign']} H{p['Saturn']['house']} | Avg Shadbala: {sb:.1f} Rupas")
    if mps: print(f"     Mahapurusha: {', '.join(mps)}")
    print(f"     🎓 {market['degree']}")
    print(f"     💼 {', '.join(market['jobs'])}")
