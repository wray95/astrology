#!/usr/bin/env python3
"""NEXUS P-Series Ranking → Sri Lankan Degrees (Metro Campus/ESOFT) + Job Market"""
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
    'IT/Tech': ['Software Engineer','Data Scientist','Network Eng','QA Engineer','DevOps'],
    'Banking': ['Banker','Financial Analyst','Accountant','Auditor','Investment Adv'],
    'Logistics': ['Logistics Mgr','Supply Chain Analyst','Freight Forwarder','Shipping'],
    'Tourism': ['Hotel Manager','Chef','Travel Agent','Event Manager'],
    'BPO': ['CSR','Call Center Mgr','BPO Team Lead','KPO Analyst'],
    'Construction': ['Civil Engineer','QS','Architect','Project Mgr'],
    'Apparel': ['Garment Tech','Merchandiser','QC','Production Mgr'],
    'Education': ['Lecturer','Tuition Master','Academic Coord','Principal'],
    'Healthcare': ['Doctor','Nurse','Pharmacist','Radiographer'],
    'Government': ['Admin Officer','SLAS','SLPS','Foreign Service'],
}

DEGREE_MAP = {
    'IT/Tech': ['BSc Software Eng (Metro)','BSc Data Science (Metro)','BSc IT (ESOFT)'],
    'Banking': ['BBA (Metro)','BSc Business Mgmt (ESOFT)'],
    'Logistics': ['BBA (Metro)','BSc QS (Metro)'],
    'Tourism': ['BBA (Metro)'],
    'BPO': ['BSc IT (ESOFT)','HND Computing (ESOFT)'],
    'Construction': ['BSc QS (Metro)','BSc Civil Eng'],
    'Apparel': ['BBA (Metro)'],
    'Education': ['BSc IT (Metro/ESOFT)','BA in Education'],
    'Healthcare': ['BSc Psychology (Metro)','MBBS'],
    'Government': ['BBA (Metro)','LLB (Metro)'],
}

def compute(pid):
    name,y,m,d,h,mi,s,lat,lon,tz = PD[pid]
    ist=timezone(timedelta(hours=tz))
    dt=datetime(y,m,d,h,mi,s,tzinfo=ist)
    utc=dt.astimezone(timezone.utc)
    jd=swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60+utc.second/3600)
    ayan=swe.get_ayanamsa(jd)
    asc_trop,_=swe.houses_ex(jd,lat,lon,b'A')
    asc_sid=(asc_trop[0]-ayan)%360; asc_idx=int(asc_sid//30)
    planets={}
    for pn,pid2 in [('Sun',0),('Moon',1),('Mars',4),('Mercury',2),('Jupiter',5),('Venus',3),('Saturn',6)]:
        lt,_=swe.calc_ut(jd,pid2)
        sid=(lt[0]-ayan)%360
        sgn=S[int(sid//30)]; h=(int(sid//30)-asc_idx)%12+1
        dgn=100 if(pn in EX and EX[pn]==sgn)else(75 if(pn in OW and sgn in OW[pn])else(-100 if(pn in DB and DB[pn]==sgn)else 0))
        planets[pn]={'sign':sgn,'house':h,'dignity':dgn,'sid':sid}
    # D9
    v9l=(asc_sid*9)%360; v9li=int(v9l//30)
    d9={}
    for pn in P7:
        vl=(planets[pn]['sid']*9)%360; vs=S[int(vl//30)]
        vh=(S.index(vs)-v9li)%12+1
        dgn9=100 if(pn in EX and EX[pn]==vs)else(75 if(pn in OW and vs in OW[pn])else(-100 if(pn in DB and DB[pn]==vs)else 0))
        d9[pn]={'sign':vs,'house':vh,'dignity':dgn9,'varg':planets[pn]['sign']==vs}
    # D10
    v10l=(asc_sid*10)%360; v10li=int(v10l//30)
    d10_10l_sign=S[(v10li+9)%12]; d10l=SL[d10_10l_sign]
    d10={}
    for pn in P7:
        vl=(planets[pn]['sid']*10)%360; vs=S[int(vl//30)]
        vh=(S.index(vs)-v10li)%12+1
        d10[pn]={'sign':vs,'house':vh}
    d10h=d10[d10l]['house']
    d1_10l=SL[S[(asc_idx+9)%12]]; d1h=planets[d1_10l]['house']
    return {'name':name,'lagna':S[asc_idx],'asc_idx':asc_idx,'asc_deg':asc_sid%30,
            'planets':planets,'d9':d9,'d10':d10,'d1_10l':d1_10l,'d1_10l_h':d1h,
            'd10_10l':d10l,'d10_10l_h':d10h,'age':2026-y}

def score(ch, sb):
    p=ch['planets']; sc={k:0 for k in SL_MARKET}
    # Saturn sign
    ss=p['Saturn']['sign']
    if ss=='Gemini':sc['Logistics']+=3
    if ss in('Capricorn','Aquarius'):sc['Construction']+=2;sc['Government']+=1
    if ss=='Pisces':sc['Education']+=2;sc['Tourism']+=1
    # 10L
    d1l=ch['d1_10l'];d1h=ch['d1_10l_h'];d10h=ch['d10_10l_h']
    if d1l=='Mercury':sc['IT/Tech']+=3;sc['BPO']+=2;sc['Education']+=2
    if d1l=='Venus':sc['Tourism']+=2;sc['Apparel']+=1
    if d1l=='Mars':sc['Construction']+=2;sc['Logistics']+=2
    if d1l=='Jupiter':sc['Education']+=3;sc['Government']+=2;sc['Banking']+=2
    if d1l=='Saturn':sc['Construction']+=3;sc['Government']+=2
    if d1l=='Sun':sc['Government']+=3
    if d1l=='Moon':sc['Healthcare']+=2;sc['Tourism']+=2
    # Kendra/Dusthana
    if d1h in(1,4,7,10):sc['Government']+=1
    if d10h in(1,4,7,10):
        for k in sc:sc[k]+=1
    elif d10h in(6,8,12):
        sc['BPO']+=1;sc['Logistics']+=1
    # 10H stellium
    if sum(1 for pn in P7 if p[pn]['house']==10)>=3:sc['Education']+=3
    # Shadbala
    sb2=sb.get('d1',{})
    if sb2:
        bp=max(sb2.items(),key=lambda x:x[1].get('shadbala_rupas',0))[0]
        if bp=='Mercury':sc['IT/Tech']+=1;sc['BPO']+=1
        if bp=='Jupiter':sc['Education']+=1
        if bp=='Saturn':sc['Construction']+=1
        if bp=='Sun':sc['Government']+=1
    return sc

def composite(ch,sb):
    p=ch['planets'];comp=0
    # MP
    for pl in[('Mars',''),('Mercury',''),('Jupiter',''),('Venus',''),('Saturn','')]:
        if p[pl[0]]['dignity']>=75 and p[pl[0]]['house'] in(1,4,7,10):comp+=4.0
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
    d9=ch.get('d9',{})
    if d9.get('Venus',{}).get('dignity',0)>=75:comp+=2.0
    # Shadbala
    sb2=sb.get('d1',{})
    if sb2:
        avg_sb=sum(pd.get('shadbala_rupas',0)for pd in sb2.values())/max(len(sb2),1)
        comp+=(avg_sb-6.5)*0.5
    return comp

def best_degree(sc):
    ds={}
    if sc.get('IT/Tech',0)>=2:ds['BSc SE (Metro)']=sc['IT/Tech'];ds['BSc DS (Metro)']=sc['IT/Tech']-0.5
    if sc.get('Banking',0)>=2:ds['BBA (Metro)']=sc['Banking']
    if sc.get('Education',0)>=2:ds['BSc IT (Metro/ESOFT)']=sc['Education']
    if sc.get('Construction',0)>=2:ds['BSc QS (Metro)']=sc['Construction']
    if sc.get('Healthcare',0)>=2:ds['BSc Psychology (Metro)']=sc['Healthcare']
    if sc.get('Government',0)>=2:ds['BBA (Metro)']=max(ds.get('BBA (Metro)',0),sc['Government'])
    if sc.get('Logistics',0)>=2:ds['BBA (Metro)']=max(ds.get('BBA (Metro)',0),sc['Logistics'])
    if not ds:ds['BSc IT (ESOFT)']=1
    return max(ds,key=ds.get)

# MAIN
with open('dataset/p_series_shadbala_av.json') as f: sb_data=json.load(f)

charts={pid:compute(pid) for pid in PD}

rows=[]
for pid in PD:
    ch=charts[pid];sb=sb_data.get(pid,{})
    sc=score(ch,sb);comp=composite(ch,sb)
    deg=best_degree(sc)
    top3=sorted(sc.items(),key=lambda x:-x[1])[:3]
    rows.append((comp,pid,ch,sc,deg,top3))

rows.sort(key=lambda x:-x[0])

print("="*92)
print("  NEXUS P1-P9 — SRI LANKAN DEGREE & CAREER CALIBRATION".center(92))
print("  (Metro Campus Colombo / ESOFT Metro Campus / SL Job Market)".center(92))
print("="*92)
print(f"\n{'#':<3s}{'ID':<4s}{'Name':<15s}{'Age':>4s}{'Lagna':<8s}{'°':>5s}{'D1 10L':<8s}{'D10 10L':<10s}")
print(f"  {'Top SL Sector':<20s}{'🎓 Best Degree':<30s}{'💼 Role':<25s}{'Score':>6s}")
print("-"*100)

for i,(comp,pid,ch,sc,deg,top3) in enumerate(rows):
    p=ch['planets'];sb=sb_data.get(pid,{}).get('d1',{})
    avg_sb=sum(pd.get('shadbala_rupas',0)for pd in sb.values())/max(len(sb),1)if sb else 0
    d1s=f"{ch['d1_10l']} H{ch['d1_10l_h']}"
    d10s=f"{ch['d10_10l']} H{ch['d10_10l_h']}"
    role=SL_MARKET.get(top3[0][0],['General'])[0]
    print(f"{i+1:<3d}{pid:<4s}{ch['name']:<15s}{ch['age']:>4d}{ch['lagna']:<8s}{ch['asc_deg']:>4.1f}°{d1s:<8s}{d10s:<10s}")
    print(f"  {top3[0][0]:<20s}{deg:<30s}{role:<25s}{comp:>5.1f}")
    if i<8: print()

# Detailed per-person
print(f"\n{'='*92}")
print(f"  PER-PERSON CAREER PATHWAY")
print(f"{'='*92}")

for i,(comp,pid,ch,sc,deg,top3) in enumerate(rows):
    p=ch['planets'];sb=sb_data.get(pid,{}).get('d1',{})
    avg_sb=sum(pd.get('shadbala_rupas',0)for pd in sb.values())/max(len(sb),1)if sb else 0
    
    # Shrinkhala loops
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
    
    # MP
    mps=[yn for pl,yn in[('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]if p[pl]['dignity']>=75 and p[pl]['house']in(1,4,7,10)]
    
    print(f"\n  {i+1}. {pid} {ch['name']} [{ch['lagna']} {ch['asc_deg']:.1f}°] → Composite: {comp:.1f}")
    print(f"     D1 10L: {ch['d1_10l']} H{ch['d1_10l_h']}({p[ch['d1_10l']]['sign']}) | D10 10L: {ch['d10_10l']} H{ch['d10_10l_h']}")
    print(f"     Saturn: {p['Saturn']['sign']} H{p['Saturn']['house']} | Avg Shadbala: {avg_sb:.1f} Rupas")
    if mps: print(f"     Mahapurusha: {', '.join(mps)}")
    if loops: print(f"     Shrinkhala: {'→'.join(loops[0])}")
    print(f"     Markets: {' | '.join(f'{s}({v:.0f})' for s,v in top3)}")
    print(f"     🎓 {deg} → {', '.join(SL_MARKET[top3[0][0]][:3])}")

# P7 DEEP DIVE
print(f"\n{'='*92}")
print(f"  P7 SINETH — D9/D10 COMPOSITE DEEP DIVE")
print(f"{'='*92}")
ch7=charts['P7'];p7=ch7['planets'];d9=ch7['d9'];sb7=sb_data.get('P7',{}).get('d1',{})
print(f"\n  Lagna: Leo {ch7['asc_deg']:.1f}° | Saturn: {p7['Saturn']['sign']} H{p7['Saturn']['house']}")
print(f"  D1 10L: {ch7['d1_10l']} H{ch7['d1_10l_h']} | D10 10L: {ch7['d10_10l']} H{ch7['d10_10l_h']}")
print(f"\n  D1 → D9 → D10 mapping:")
for pn in P7:
    varg='⭐VARG' if d9[pn]['varg'] else ''
    d1s=f"{p7[pn]['sign']} H{p7[pn]['house']}"
    d9s=f"{d9[pn]['sign']} H{d9[pn]['house']}"
    d10s=f"{ch7['d10'][pn]['sign']} H{ch7['d10'][pn]['house']}"
    tag='EX' if d9[pn]['dignity']==100 else('OWN' if d9[pn]['dignity']==75 else('DEB' if d9[pn]['dignity']==-100 else''))
    print(f"  {pn:8s}: D1 {d1s:20s} → D9 {d9s:20s} {tag:>4s} {varg:>8s} → D10 {d10s:20s}")

# 8H stellium (4 planets!)
h8_count = sum(1 for pn in P7 if p7[pn]['house']==8)
print(f"\n  ⚡ 8H Stellium: {int(h8_count)} planets — {'TRANSFORMATIVE CAREER PATH' if h8_count>=3 else ''}")
print(f"  📍 SL Career: Logistics/Finance backend analyst or Banking/IT intersection")
print(f"  🎓 Metro/ESOFT: BSc SE (Metro) or BSc IT (ESOFT) — data/analytics pathway")

# Save
with open('dataset/p_series_sl_career.json','w') as f:
    out={}
    for comp,pid,ch,sc,deg,top3 in rows:
        sb=sb_data.get(pid,{}).get('d1',{})
        out[pid]={
            'name':ch['name'],'lagna':ch['lagna'],'asc_deg':round(ch['asc_deg'],1),
            'age':ch['age'],'d1_10l':f"{ch['d1_10l']} H{ch['d1_10l_h']}",
            'd10_10l':f"{ch['d10_10l']} H{ch['d10_10l_h']}",
            'saturn':p7['Saturn']['sign'] if pid=='P7' else ch['planets']['Saturn']['sign'],
            'composite':round(comp,1),
            'top_sectors':[(s,round(v,1)) for s,v in top3],
            'degree':deg,
            'shadbala_avg':round(sum(pd.get('shadbala_rupas',0)for pd in sb.values())/max(len(sb),1),1)if sb else 0
        }
    json.dump(out,f,indent=2)
print(f"\n✅ Saved: dataset/p_series_sl_career.json")
