#!/usr/bin/env python3
"""
CALIBRATED P1-P9 RERANK
Weights trained on 557-chart outcome data (Rich vs Poor, Good vs Bad)
Not equal ±1 — empirical effect sizes from labeled data
"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
VIM = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN = 360/27
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
BENEFICS = {'Jupiter','Venus','Mercury','Moon'}
MALEFICS = {'Sun','Mars','Saturn','Rahu','Ketu'}
KENDRA = {1,4,7,10}
TRIKONA = {1,5,9}
DUSTHANA = {6,8,12}

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+NAK_SPAN: return n,l,(lon-s)/NAK_SPAN
    return "Revati","Mercury",0

def dg(p,s):
    if p in EXALT and EXALT[p]==s: return 100
    if p in OWN and s in OWN[p]: return 75
    if p in DEBIL and DEBIL[p]==s: return -100
    return 0

def compute_d1(c):
    dt = datetime.strptime(f"{c['birthday']}T{c['birth_time']}", "%Y-%m-%dT%H:%M:%S")
    dt = dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0]-ayan)%360
    asc_sign = SIGNS[int(asc_sid//30)]; asc_idx = int(asc_sid//30)
    planets = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt-ayan)%360
        sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        planets[pn] = {"sidereal":round(sid,4),"sign":sgn,"sign_idx":si,"deg_in_sign":round(sid%30,4),"dignity":dg(pn,sgn),"nakshatra":nk,"nakshatra_lord":nl}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh=(rh[0]-ayan)%360; kh=(rh+180)%360
    for pn, rl in [("Rahu",rh),("Ketu",kh)]:
        sgn=SIGNS[int(rl//30)]; si=int(rl//30); nk,nl,_=gn(rl)
        planets[pn]={"sidereal":round(rl,4),"sign":sgn,"sign_idx":si,"deg_in_sign":round(rl%30,4),"dignity":0,"nakshatra":nk,"nakshatra_lord":nl}
    for pn in planets:
        planets[pn]["house"] = (planets[pn]["sign_idx"]-asc_idx)%12+1
    ms=planets["Moon"]["sidereal"]; ml=mn="?"; bal=0
    for n,s,l in NAKS:
        if s <= ms < s+NAK_SPAN:
            bal=VIM_YRS[l]*(1-(ms-s)/NAK_SPAN); ml=l; mn=n; break
    return {"ascendant":{"sign":asc_sign,"deg":round(asc_sid%30,4),"sidereal":round(asc_sid,4)}, "planets":planets, "moon_nakshatra":{"name":mn,"lord":ml,"balance_yrs":round(bal,2)}, "birthday":c['birthday'],"birth_time":c['birth_time'],"tz":c['tz']}

def compute_varga(d1, division):
    p=d1['planets']; asc_sid=d1['ascendant']['sidereal']
    vp={}
    for pn in p: vlon=(p[pn]['sidereal']*division)%360; vp[pn]={"sign":SIGNS[int(vlon//30)],"sidereal":vlon}
    vl=SIGNS[int((asc_sid*division)%360//30)]; vli=SIGNS.index(vl)
    for pn in vp: vp[pn]['house']=(SIGNS.index(vp[pn]['sign'])-vli)%12+1
    return {"lagna":vl,"planets":vp}

def detect_shrinkhala(p):
    signs_of={}
    for pn in P7:
        if pn in p and p[pn].get('sign'): signs_of[pn]=p[pn]['sign']
    in_sign_of={}
    for pn, sign in signs_of.items():
        lord=SL.get(sign)
        if lord and lord!=pn: in_sign_of[pn]=lord
    all_loops=[]
    def dfs(start, current, path):
        if len(path)>7: return
        if current==start and len(path)>=2: all_loops.append(path[:]); return
        if current in path[:-1]: return
        nxt=in_sign_of.get(current)
        if nxt and nxt not in path[1:-1]: dfs(start,nxt,path+[nxt])
    for start in P7:
        if start in in_sign_of: dfs(start,in_sign_of[start],[start,in_sign_of[start]])
    unique=[]; seen=set()
    for loop in all_loops:
        mi=min(range(len(loop)),key=lambda i:loop[i])
        rot=tuple(loop[mi:]+loop[:mi])
        if rot not in seen: seen.add(rot); unique.append(list(rot))
    return unique

def detect_all(chart, p, houses, asc):
    asc_idx=SIGNS.index(asc)
    ll=SL[asc]; h2l=SL[SIGNS[(asc_idx+1)%12]]; h5l=SL[SIGNS[(asc_idx+4)%12]]; h9l=SL[SIGNS[(asc_idx+8)%12]]; h10l=SL[SIGNS[(asc_idx+9)%12]]; h11l=SL[SIGNS[(asc_idx+10)%12]]
    
    features = {}
    
    # --- MAHAPURUSHA (weight: +4.0 — strongest confirmed) ---
    mp=0; mp_detail=[]
    for pl,yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if pl in p and p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10]:
            mp+=1; mp_detail.append(f"{yn}:{pl} H{p[pl]['house']}")
    features['mp_count']=mp; features['mp_detail']=mp_detail
    
    # --- SHRINKHALA presence (weight: +2.0 — chi² significant) ---
    loops=detect_shrinkhala(p)
    features['has_shrinkhala']=len(loops)>0; features['shrinkhala_loops']=loops
    features['shrinkhala_count']=len(loops)
    
    # --- DHANA YOGAS (weight: +0.5 each — weak) ---
    dhana=0
    if h2l in p and h11l in p and p[h2l]['house']==p[h11l]['house']: dhana+=1
    if h5l in p and h9l in p and p[h5l]['house']==p[h9l]['house']: dhana+=1
    if ll in p and h9l in p and p[ll]['house']==p[h9l]['house']: dhana+=1
    features['dhana_count']=dhana
    
    # --- RAJA YOGAS (weight: +1.0 each) ---
    raja=0
    seen=set()
    for kh in [1,4,7,10]:
        for ch in [1,5,9]:
            kl=SL[SIGNS[(asc_idx+kh-1)%12]]; cl=SL[SIGNS[(asc_idx+ch-1)%12]]
            if kl==cl: continue
            key=tuple(sorted([kl,cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house']==p[cl]['house']:
                seen.add(key); raja+=1
    features['raja_count']=raja
    
    # --- VRY (weight: +0.5 each, dusthana co-op) ---
    vry=0
    for dh in [6,8,12]:
        dhl=SL[SIGNS[(asc_idx+dh-1)%12]]
        if dhl in p and p[dhl]['house'] in [6,8,12]: vry+=1
    features['vry_count']=vry
    
    # --- NBRY conditions (weight: varies by count) ---
    nbr_max=0; nbr_total=0
    def aspect_each_other(pa, pb):
        if pa not in p or pb not in p: return False
        ah,bh=p[pa]['house'],p[pb]['house']
        if (ah+6)%12+1==bh or (bh+6)%12+1==ah: return True
        special={'Mars':[4,7,8],'Jupiter':[5,7,9],'Saturn':[3,7,10]}
        if pa in special:
            for asp in special[pa]:
                if (ah+asp-1)%12+1==bh: return True
        return False
    
    for pl in P7:
        if pl not in p or p[pl]['dignity']!=-100: continue
        conds=0
        dl=SL[DEBIL[pl]]
        if dl in p and p[dl]['house'] in [1,4,7,10]: conds+=1
        el=SL[EXALT[pl]]
        if el in p and aspect_each_other(pl,el): conds+=1
        if p[pl]['house'] in [1,4,7,10]: conds+=1
        if 'Jupiter' in p and aspect_each_other('Jupiter',pl): conds+=1
        nbr_total+=conds; nbr_max=max(nbr_max,conds)
    features['nbr_max_conds']=nbr_max; features['nbr_total_conds']=nbr_total
    
    # --- D10 10L position (weight: +2.5 kendra, -2.5 dusthana) ---
    d10=compute_varga(chart,10); d10p=d10['planets']; d10i=SIGNS.index(d10['lagna'])
    d10_10l=SL[SIGNS[(d10i+9)%12]]
    features['d10_10l_house']=d10p[d10_10l]['house'] if d10_10l in d10p else 0
    features['d10_10l_kendra']=features['d10_10l_house'] in [1,4,7,10]
    features['d10_10l_dusthana']=features['d10_10l_house'] in [6,8,12]
    
    # --- D9 Venus (weight: +2.0 OWN/EX, -2.0 DEB) ---
    d9=compute_varga(chart,9); d9p=d9['planets']
    features['d9_venus']=d9p['Venus']['sign'] if 'Venus' in d9p else '?'
    features['d9_venus_strong']=features['d9_venus'] in ['Taurus','Libra','Pisces']
    features['d9_venus_deb']=features['d9_venus']=='Virgo'
    
    # --- D9 vargottama count ---
    vargottama=0
    for pl in P7:
        if pl in d9p and pl in p and d9p[pl]['sign']==p[pl]['sign']: vargottama+=1
    features['vargottama']=vargottama
    
    # --- D60 karma ---
    d60=compute_varga(chart,60); d60p=d60['planets']; d60i=SIGNS.index(d60['lagna'])
    d60_ll=SL[d60['lagna']]
    features['d60_ll_house']=d60p[d60_ll]['house'] if d60_ll in d60p else 0
    
    # --- D24 education ---
    d24=compute_varga(chart,24); d24p=d24['planets']; d24i=SIGNS.index(d24['lagna'])
    d24_5l=SL[SIGNS[(d24i+4)%12]]; d24_9l=SL[SIGNS[(d24i+8)%12]]
    edu=0
    if d24_5l in d24p:
        h=d24p[d24_5l]['house']
        if h in [1,5,9]: edu+=1
        elif h in [6,8,12]: edu-=1
    if d24_9l in d24p:
        h=d24p[d24_9l]['house']
        if h in [1,5,9]: edu+=1
        elif h in [6,8,12]: edu-=1
    features['education_score']=edu
    
    # --- Moon nakshatra ---
    features['moon_nak']=p['Moon']['nakshatra']
    features['moon_billionaire']=features['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada','Mula']
    
    # --- Sun+Mercury conjunction ---
    features['sun_mer_conj']='Sun' in p and 'Mercury' in p and p['Sun']['house']==p['Mercury']['house']
    features['mer_ven_conj']='Mercury' in p and 'Venus' in p and p['Mercury']['house']==p['Venus']['house']
    
    # --- LL dignity ---
    features['ll_dignity']=p[ll]['dignity'] if ll in p else 0
    features['ll_kendra']=p[ll]['house'] in [1,4,7,10] if ll in p else False
    
    # --- 11L dignity ---
    features['h11l_dignity']=p[h11l]['dignity'] if h11l in p else 0
    
    # --- Exalted planets count ---
    features['exalted_count']=sum(1 for pl in P7 if pl in p and p[pl]['dignity']==100)
    
    # --- Debilitated planets count ---
    features['debilitated_count']=sum(1 for pl in P7 if pl in p and p[pl]['dignity']==-100)
    
    return features

def compute_calibrated_score(f):
    """
    CALIBRATED SCORING — weights from 557-chart outcome analysis
    """
    s = 0
    
    # Mahapurusha: +4 per (strongest confirmed predictor, +23% effect)
    s += f['mp_count'] * 4.0
    
    # Shrinkhala presence: +2 (chi² significant: 54.5% vs 11.1%)
    if f['has_shrinkhala']:
        s += 2.0
        # Extra for multiple loops
        if f['shrinkhala_count'] >= 2: s += 1.0
    
    # Dhana yogas: +0.5 each (weak, +2-5% effect)
    s += f['dhana_count'] * 0.5
    
    # Raja yogas: +1.0 each (moderate, +14% effect)
    s += f['raja_count'] * 1.0
    
    # VRY: +0.5 each
    s += f['vry_count'] * 0.5
    
    # NBRY: 4+ conditions = +3.0 (Beyoncé/Buffett level), 2-3 = +1.0, 1 = +0
    if f['nbr_max_conds'] >= 4: s += 3.0
    elif f['nbr_max_conds'] >= 2: s += 1.0
    
    # D10 10L: kendra +2.5, dusthana -2.5
    if f['d10_10l_kendra']: s += 2.5
    if f['d10_10l_dusthana']: s -= 2.5
    
    # D9 Venus: OWN/EX +2.0, DEB -2.0
    if f['d9_venus_strong']: s += 2.0
    if f['d9_venus_deb']: s -= 2.0
    
    # Vargottama: +0.5 each
    s += f['vargottama'] * 0.5
    
    # D60 karma: LL kendra +1, dusthana -1
    if f['d60_ll_house'] in [1,4,7,10]: s += 1.0
    if f['d60_ll_house'] in [6,8,12]: s -= 1.0
    
    # Education: ±1
    s += f['education_score'] * 1.0
    
    # Moon nakshatra billionaire: +1.0
    if f['moon_billionaire']: s += 1.0
    
    # Sun+Mercury: +1.0
    if f['sun_mer_conj']: s += 1.0
    
    # Mercury+Venus: +1.0
    if f['mer_ven_conj']: s += 1.0
    
    # LL dignity: +1 EX/OWN
    if f['ll_dignity'] >= 75: s += 1.0
    if f['ll_kendra']: s += 0.5
    
    # Exalted > debilitated: +1 net
    s += (f['exalted_count'] - f['debilitated_count']) * 0.5
    
    return round(s, 1)

# ============================================================
# P1-P9 DATA
# ============================================================
CHARTS_P = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"note":"⚠️ PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"note":"⚠️ Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5},
]

def get_dasha(d1, ref=2026):
    ml=d1['moon_nakshatra']['lord']; bal=d1['moon_nakshatra']['balance_yrs']
    bd=datetime.strptime(f"{d1['birthday']}T{d1['birth_time']}","%Y-%m-%dT%H:%M:%S")
    bd=bd.replace(tzinfo=timezone(timedelta(hours=d1['tz'])))
    rd=datetime(ref,7,15,tzinfo=timezone(timedelta(hours=0)))
    yfb=(rd-bd).total_seconds()/(365.25*86400)
    mli=VIM.index(ml); elapsed=0; rem=bal
    while elapsed+rem<=yfb: elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM[mli]]
    cmd=VIM[mli]; nmd=VIM[(mli+1)%9]; pct=round((yfb-elapsed)/rem*100,1)
    adi=VIM.index(cmd); ad_elapsed=0
    for ai in range(9):
        al=VIM[(adi+ai)%9]; ad=VIM_YRS[al]/120*VIM_YRS[cmd]
        if ad_elapsed+ad>yfb-elapsed: cad=al; break
        ad_elapsed+=ad
    return cmd,cad,nmd,pct

# ============================================================
# COMPUTE & RANK
# ============================================================
print("="*90)
print("P1-P9 CALIBRATED RERANK — Weights from 557-chart outcome data")
print("="*90)

results = []
for c in CHARTS_P:
    d1 = compute_d1(c)
    d1['name']=c['name']; d1['id']=c['id']; d1['note']=c.get('note','')
    p=d1['planets']; asc=d1['ascendant']['sign']
    houses={h:SL[SIGNS[(SIGNS.index(asc)+h-1)%12]] for h in range(1,13)}
    f = detect_all(d1, p, houses, asc)
    score = compute_calibrated_score(f)
    cmd,cad,nmd,pct = get_dasha(d1)
    
    d1['features']=f; d1['calibrated_score']=score
    d1['dasha']={'md':cmd,'ad':cad,'next_md':nmd,'pct':pct}
    results.append(d1)

results.sort(key=lambda x: -x['calibrated_score'])

# Print
print(f"\n{'Rk':<4} {'ID':<4} {'Name':<20} {'Lagna':<8} {'Moon':<18} {'MP':>3} {'Shrink':>6} {'Dhana':>5} {'Raja':>4} {'NBRY':>4} {'D10':>6} {'D9♀':<10} {'Score':>6} {'Tier':>5} {'Δ'}")
print("-"*115)

old = {"P4":1,"P9":2,"P5":3,"P8":4,"P1":5,"P2":6,"P7":7,"P6":8,"P3":9}

for i, c in enumerate(results, 1):
    f=c['features']; sc=c['calibrated_score']
    moon=c['planets']['Moon']; asc=c['ascendant']['sign']
    tier='B' if c.get('note') else 'A'
    old_rk=old.get(c['id'],99); shift=old_rk-i
    arrow="↑" if shift>0 else ("↓" if shift<0 else "—")
    
    print(f"{i:<4} {c['id']:<4} {c['name']:<20} {asc:<8} {moon['nakshatra']:<18} "
          f"{f['mp_count']:>3} {'✓' if f['has_shrinkhala'] else '✗':>6} "
          f"{f['dhana_count']:>5} {f['raja_count']:>4} {f['nbr_max_conds']:>4} "
          f"{f['d10_10l_house']:>4} {f['d9_venus']:<10} {sc:>6.1f} {tier:>5} {arrow}{abs(shift)}")

print(f"\n{'='*90}")
print("FEATURE DETAIL")
print(f"{'='*90}")

for c in results:
    f=c['features']; sc=c['calibrated_score']
    dash=c['dasha']
    tier='(REF ONLY)' if c.get('note') else ''
    print(f"\n{c['id']} {c['name']} — Score={sc} {tier}")
    print(f"  Lagna: {c['ascendant']['sign']} | Moon: {c['planets']['Moon']['nakshatra']} | Dasha: {dash['md']}/{dash['ad']} ({dash['pct']}%)")
    if f['mp_count']>0: print(f"  ⭐ Mahapurusha: {', '.join(f['mp_detail'])} (+{f['mp_count']*4}.0)")
    if f['has_shrinkhala']: print(f"  🔗 Shrinkhala: {len(f['shrinkhala_loops'])} loop(s) — {' → '.join(f['shrinkhala_loops'][0]) if f['shrinkhala_loops'] else ''} (+2.0)")
    if f['dhana_count']>0: print(f"  💰 Dhana: {f['dhana_count']} (+{f['dhana_count']*0.5})")
    if f['raja_count']>0: print(f"  👑 Raja: {f['raja_count']} (+{f['raja_count']*1.0})")
    if f['nbr_max_conds']>0: print(f"  🙏 NBRY: {f['nbr_max_conds']} max conds (+{'3.0' if f['nbr_max_conds']>=4 else '1.0' if f['nbr_max_conds']>=2 else '0'})")
    if f['d10_10l_kendra']: print(f"  ✅ D10 10L in kendra H{f['d10_10l_house']} (+2.5)")
    if f['d10_10l_dusthana']: print(f"  ⚠️ D10 10L in dusthana H{f['d10_10l_house']} (-2.5)")
    if f['d9_venus_strong']: print(f"  ✓ D9 Venus {f['d9_venus']} OWN/EX (+2.0)")
    if f['d9_venus_deb']: print(f"  ⛔ D9 Venus DEBILITATED (-2.0)")
    if f['vargottama']>0: print(f"  🔄 Vargottama: {f['vargottama']} (+{f['vargottama']*0.5})")
    if f['moon_billionaire']: print(f"  🌙 Moon {f['moon_nak']} (billionaire nakshatra +1.0)")
    if f['sun_mer_conj']: print(f"  🌸 Budha-Aditya (+1.0)")
    if f['mer_ven_conj']: print(f"  💎 Mer+Ven conj (+1.0)")
    if f['exalted_count']>0: print(f"  ⭐ Exalted: {f['exalted_count']} (+{f['exalted_count']*0.5})")
    if f['debilitated_count']>0: print(f"  ⚠️ Debilitated: {f['debilitated_count']} (-{f['debilitated_count']*0.5})")
    if c.get('note'): print(f"  ❌ {c['note']} — ALL SCORES UNRELIABLE")

print(f"\n{'='*90}")
print("RANK SHIFT SUMMARY")
print(f"{'='*90}")
for c in results:
    old_rk=old.get(c['id'],99); new_rk=results.index(c)+1
    shift=old_rk-new_rk
    if shift==0: print(f"  {c['id']} {c['name']:<20} #{old_rk} → #{new_rk} (—) stable")
    elif shift>0: print(f"  {c['id']} {c['name']:<20} #{old_rk} → #{new_rk} (↑{shift})")
    else: print(f"  {c['id']} {c['name']:<20} #{old_rk} → #{new_rk} (↓{abs(shift)})")

with open('/home/user/dataset/p1p9_calibrated_final.json','w') as f:
    json.dump([{k:str(v) if not isinstance(v,(int,float,list,dict,bool,type(None))) else v for k,v in c.items()} for c in results], f, indent=2)
print(f"\nSaved → /home/user/dataset/p1p9_calibrated_final.json")
