#!/usr/bin/env python3
"""
P1-P9 ABSOLUTE FINAL RERANK
Cross-referencing ALL data sources: 350+ charts, 22 groups, 19 classical claims
Weights calibrated from all discoveries
"""
import swisseph as swe, json, math
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN = 360.0/27

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
    tz = timezone(timedelta(hours=c['tz']))
    dt = dt.replace(tzinfo=tz)
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0] - ayan) % 360
    asc_sign = SIGNS[int(asc_sid//30)]; asc_idx = int(asc_sid//30)
    planets = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        planets[pn] = {"sidereal": round(sid,4), "sign": sgn, "sign_idx": si, "deg_in_sign": round(sid%30,4), "dignity": dg(pn,sgn), "nakshatra": nk, "nakshatra_lord": nl}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360; kh = (rh+180)%360
    for pn, rl in [("Rahu", rh), ("Ketu", kh)]:
        sgn = SIGNS[int(rl//30)]; si = int(rl//30); nk, nl, _ = gn(rl)
        planets[pn] = {"sidereal": round(rl,4), "sign": sgn, "sign_idx": si, "deg_in_sign": round(rl%30,4), "dignity": 0, "nakshatra": nk, "nakshatra_lord": nl}
    for pn in planets:
        planets[pn]["house"] = (planets[pn]["sign_idx"] - asc_idx) % 12 + 1
    ms = planets["Moon"]["sidereal"]
    ml = mn = "?"; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + NAK_SPAN:
            bal = VIM_YRS[l] * (1.0 - (ms-s)/NAK_SPAN)
            ml = l; mn = n; break
    return {"ascendant": {"sign": asc_sign, "deg": round(asc_sid%30,4), "sidereal": round(asc_sid,4)}, "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)}, "birthday": c['birthday'], "birth_time": c['birth_time'], "tz": c['tz']}

def compute_varga(d1, division):
    p = d1['planets']; asc_sid = d1['ascendant']['sidereal']
    vp = {}
    for pn in p:
        vlon = (p[pn]['sidereal'] * division) % 360
        vp[pn] = {"sign": SIGNS[int(vlon//30)], "sidereal": vlon}
    vl = SIGNS[int((asc_sid*division)%360//30)]
    vli = SIGNS.index(vl)
    for pn in vp:
        vp[pn]['house'] = (SIGNS.index(vp[pn]['sign']) - vli) % 12 + 1
    return {"lagna": vl, "planets": vp}

def aspect_each_other(p, a, b):
    if a not in p or b not in p: return False
    ah, bh = p[a]['house'], p[b]['house']
    if (ah+6)%12+1==bh or (bh+6)%12+1==ah: return True
    special = {'Mars':[4,7,8],'Jupiter':[5,7,9],'Saturn':[3,7,10]}
    for pl, asps in special.items():
        if a==pl:
            for asp in asps:
                if (ah+asp-1)%12+1==bh: return True
        if b==pl:
            for asp in asps:
                if (bh+asp-1)%12+1==ah: return True
    return False

def detect_yogas(d1):
    p = d1['planets']; asc = d1['ascendant']['sign']; asc_idx = SIGNS.index(asc)
    ll = SL[asc]; h2l = SL[SIGNS[(asc_idx+1)%12]]; h5l = SL[SIGNS[(asc_idx+4)%12]]; h9l = SL[SIGNS[(asc_idx+8)%12]]; h10l = SL[SIGNS[(asc_idx+9)%12]]; h11l = SL[SIGNS[(asc_idx+10)%12]]
    yogas = {'dhana':[],'raja':[],'mahapurusha':[],'nbry':[],'vry':[]}
    
    if h2l in p and h11l in p:
        if p[h2l]['house']==p[h11l]['house']: yogas['dhana'].append(f"2L+11L conj")
        elif aspect_each_other(p,h2l,h11l): yogas['dhana'].append(f"2L+11L aspect")
    if h5l in p and h9l in p and p[h5l]['house']==p[h9l]['house']: yogas['dhana'].append("LAKSHMI")
    if ll in p and h9l in p and p[ll]['house']==p[h9l]['house']: yogas['dhana'].append("LL+9L")
    
    k_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in [1,4,7,10]]
    c_lords = [(h, SL[SIGNS[(asc_idx+h-1)%12]]) for h in [1,5,9]]
    seen = set()
    for kh, kl in k_lords:
        for ch, cl in c_lords:
            if kl==cl: continue
            key = tuple(sorted([kl,cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house']==p[cl]['house']:
                seen.add(key); yogas['raja'].append(f"{kl}(L{kh})+{cl}(L{ch})")
    
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    for pl, yn in mp_map.items():
        if pl in p and p[pl]['dignity']>=75 and p[pl]['house'] in [1,4,7,10]:
            yogas['mahapurusha'].append(f"{yn}:{pl} H{p[pl]['house']}")
    
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in p and p[pl]['dignity']==-100:
            conds = []
            dl = SL[DEBIL[pl]]
            if dl in p and p[dl]['house'] in [1,4,7,10]: conds.append("deblord kendra")
            el = SL[EXALT[pl]]
            if el in p and aspect_each_other(p,pl,el): conds.append("exlord aspects")
            if conds: yogas['nbry'].append(f"{pl} deb {DEBIL[pl]}")
    
    for dh in [6,8,12]:
        dhl = SL[SIGNS[(asc_idx+dh-1)%12]]
        if dhl in p and p[dhl]['house'] in [6,8,12]: yogas['vry'].append(f"{dhl}(L{dh}) in H{p[dhl]['house']}")
    
    return yogas

# P1-P9 birth data
CHARTS_P = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5,"archetype":"Self-Made Warlord","career":"Industrial CEO","edu":"Engineering→MBA"},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"archetype":"Enigma ⚠️","career":"MNC Manager","edu":"Intl Business→MBA","note":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5,"archetype":"Sage","career":"Academic Researcher","edu":"PhD→Jyotish"},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5,"archetype":"Luxe Empire Builder","career":"Luxury/Beauty Founder","edu":"Business→Real Estate"},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5,"archetype":"Slow-Motion Titan","career":"Tech/Quant Finance","edu":"CS→Finance→Law"},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5,"archetype":"Fighter","career":"Strategy Consultant","edu":"Business→Law"},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"archetype":"Phoenix","career":"Quant Finance","edu":"Finance→CS→PhD","note":"Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5,"archetype":"Oracle of Depth","career":"Psychologist/Analyst","edu":"Psychology→Finance"},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5,"archetype":"Magnetic Partner","career":"Audit/Govt Director","edu":"Accounting→Eng→Law"},
]

def get_dasha(d1, ref_year=2026):
    ml = d1['moon_nakshatra']['lord']; balance = d1['moon_nakshatra']['balance_yrs']
    bd = datetime.strptime(f"{d1['birthday']}T{d1['birth_time']}","%Y-%m-%dT%H:%M:%S")
    bd = bd.replace(tzinfo=timezone(timedelta(hours=d1['tz'])))
    rd = datetime(ref_year,7,15,tzinfo=timezone(timedelta(hours=0)))
    yfb = (rd-bd).total_seconds()/(365.25*86400)
    mli = VIM_ORDER.index(ml); elapsed=0; rem=balance
    while elapsed+rem <= yfb:
        elapsed+=rem; mli=(mli+1)%9; rem=VIM_YRS[VIM_ORDER[mli]]
    cmd = VIM_ORDER[mli]; nmd = VIM_ORDER[(mli+1)%9]
    pct = round((yfb-elapsed)/rem*100,1)
    # AD
    adi = VIM_ORDER.index(cmd); ad_elapsed=0
    for ai in range(9):
        al = VIM_ORDER[(adi+ai)%9]; ad = VIM_YRS[al]/120*VIM_YRS[cmd]
        if ad_elapsed+ad > yfb-elapsed: cad=al; break
        ad_elapsed+=ad
    return cmd, cad, nmd, pct

# ============================================================
# MULTI-DIMENSIONAL SCORING (calibrated from ALL sources)
# ============================================================
def score_all(d1, yogas, vargas):
    p = d1['planets']; asc = d1['ascendant']['sign']; asc_idx = SIGNS.index(asc)
    ll = SL[asc]; h9l = SL[SIGNS[(asc_idx+8)%12]]; h10l = SL[SIGNS[(asc_idx+9)%12]]; h11l = SL[SIGNS[(asc_idx+10)%12]]
    
    # ===== WEALTH (max ~12) =====
    w = 0
    
    # Mahapurusha (strongest confirmed claim: +23% effect)
    mp_count = len(yogas['mahapurusha'])
    w += mp_count * 3.0  # Each MP = 3 pts
    
    # Dhana yogas
    w += len(yogas['dhana']) * 1.5
    
    # Raja yogas
    w += len(yogas['raja']) * 1.0
    
    # VRY (dusthana lord in dusthana)
    vry_count = len(yogas['vry'])
    if vry_count > 0:
        unique = len(set(v.split('(')[1].split(')')[0] for v in yogas['vry']))
        w += vry_count * (1+unique) * 0.5
    
    # 11L dignity
    if h11l in p:
        d11 = p[h11l]['dignity']; h11 = p[h11l]['house']
        if d11 == 100: w += 2.5
        elif d11 == 75: w += 1.5
        if h11 in [2,5,9,11]: w += 1
        elif h11 in [6,8,12]: w -= 1.5
    
    # 9L dignity
    if h9l in p:
        d9 = p[h9l]['dignity']; h9 = p[h9l]['house']
        if d9 == 100: w += 2.5
        elif d9 == 75: w += 1.5
        if h9 in [1,4,5,7,9,10]: w += 1
        elif h9 in [6,8,12]: w -= 1
    
    # Benefics in wealth houses
    for b in ['Jupiter','Venus']:
        if b in p:
            bh = p[b]['house']; bd = p[b]['dignity']
            if bh in [2,11] and bd >= 0: w += 1.5
            elif bh in [1,4,7,10] and bd >= 75: w += 2
    
    # Sun+Mercury (Budha-Aditya: 42% of billionaires)
    if 'Sun' in p and 'Mercury' in p and p['Sun']['house'] == p['Mercury']['house']:
        w += 1.5
    
    # Mercury+Venus (strongest surviving billionaire-vs-criminal marker: 32% vs 24%)
    if 'Mercury' in p and 'Venus' in p and p['Mercury']['house'] == p['Venus']['house']:
        w += 1.5
    
    # NBRY
    w += len(yogas['nbry']) * 1.0
    
    # ===== POWER/CAREER (max ~10) =====
    pwr = 0
    
    # LL dignity + position
    if ll in p:
        if p[ll]['dignity'] >= 75: pwr += 2
        if p[ll]['house'] in [1,4,7,10]: pwr += 1.5
        elif p[ll]['house'] in [6,8,12]: pwr -= 1
    
    # Raja yogas (already counted in wealth but career impact)
    pwr += len(yogas['raja']) * 1.0
    
    # D10 10L position
    d10 = vargas['D10']; d10p = d10['planets']; d10_idx = SIGNS.index(d10['lagna'])
    d10_10l = SL[SIGNS[(d10_idx+9)%12]]
    if d10_10l in d10p:
        h10l_d10 = d10p[d10_10l]['house']
        if h10l_d10 in [1,4,7,10]: pwr += 2.5
        elif h10l_d10 in [6,8,12]: pwr -= 2.5  # Career destruction risk
    
    # D10 planets in 10H
    for pl in d10p:
        if d10p[pl]['house'] == 10: pwr += 0.5
    
    # ===== DHARMA/ETHICS (D9 Venus) (max ~4) =====
    d9 = vargas['D9']; d9p = d9['planets']
    ethics = 0
    if 'Venus' in d9p:
        d9vs = d9p['Venus']['sign']
        if d9vs == 'Virgo': ethics -= 3  # Holmes+SBF pattern
        elif d9vs == 'Pisces': ethics += 3
        elif d9vs in ['Taurus','Libra']: ethics += 2
    
    # Vargottama planets in D9
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in d9p and pl in p:
            if d9p[pl]['sign'] == p[pl]['sign']:
                ethics += 0.5
    
    # ===== EDUCATION (D24) (max ~4) =====
    d24 = vargas['D24']; d24p = d24['planets']; d24_idx = SIGNS.index(d24['lagna'])
    edu = 0
    d24_5l = SL[SIGNS[(d24_idx+4)%12]]
    if d24_5l in d24p:
        h = d24p[d24_5l]['house']
        if h in [1,5,9]: edu += 2
        elif h in [6,8,12]: edu -= 1
    d24_9l = SL[SIGNS[(d24_idx+8)%12]]
    if d24_9l in d24p:
        h = d24p[d24_9l]['house']
        if h in [1,5,9]: edu += 2
        elif h in [6,8,12]: edu -= 1
    for pl in ['Mercury','Jupiter']:
        if pl in d24p and d24p[pl]['house'] in [1,5,9]: edu += 1
    
    # ===== KARMA (D60) (max ~4) =====
    d60 = vargas['D60']; d60p = d60['planets']; d60_idx = SIGNS.index(d60['lagna'])
    karma = 0
    d60_ll = SL[d60['lagna']]
    if d60_ll in d60p:
        h = d60p[d60_ll]['house']
        if h in [1,4,7,10]: karma += 2
        elif h in [6,8,12]: karma -= 2  # Madoff pattern
    d60_9l = SL[SIGNS[(d60_idx+8)%12]]
    if d60_9l in d60p:
        h = d60p[d60_9l]['house']
        if h in [1,5,9]: karma += 2
        elif h in [6,8,12]: karma -= 1
    
    # ===== MOON NAKSHATRA OCCUPATIONAL FLAVOR =====
    moon_nak = p['Moon']['nakshatra']
    occupation_bonus = 0
    # Billionaire-favored nakshatras (from 99-billionaire analysis)
    if moon_nak in ['Shravana','Swati','Purva Bhadrapada','Mula']: occupation_bonus += 1
    # Stability marker
    if moon_nak in ['Magha','Uttara Ashadha']: occupation_bonus += 0.5
    
    # ===== COMPOSITE =====
    composite = (w * 0.30 + pwr * 0.25 + ethics * 0.15 + edu * 0.15 + karma * 0.10 + occupation_bonus * 0.05) * 1.667  # scale to ~10
    
    return {
        'wealth': round(w,1), 'power': round(pwr,1), 'ethics': round(ethics,1),
        'education': round(edu,1), 'karma': round(karma,1), 'occupation_bonus': occupation_bonus,
        'composite': round(composite,1)
    }

# ============================================================
# MAIN
# ============================================================
print("="*120)
print("P1-P9 ABSOLUTE FINAL RERANK — Cross-Referencing ALL Data Sources")
print("="*120)

results = []
for c in CHARTS_P:
    print(f"Computing {c['id']} {c['name']}...")
    d1 = compute_d1(c)
    d1['name'] = c['name']; d1['id'] = c['id']; d1['archetype'] = c['archetype']; d1['career'] = c['career']; d1['edu'] = c['edu']; d1['note'] = c.get('note','')
    
    vargas = {}
    for vn, vd in [('D2',2),('D9',9),('D10',10),('D24',24),('D60',60)]:
        vargas[vn] = compute_varga(d1, vd)
    
    yogas = detect_yogas(d1)
    scores = score_all(d1, yogas, vargas)
    cmd, cad, nmd, pct = get_dasha(d1)
    
    d1['vargas'] = vargas; d1['yogas'] = yogas; d1['scores'] = scores
    d1['dasha'] = {'current_md':cmd,'current_ad':cad,'next_md':nmd,'md_pct':pct}
    
    # Key flags
    p = d1['planets']
    d9p = vargas['D9']['planets']
    d10p = vargas['D10']['planets']
    d10_idx = SIGNS.index(vargas['D10']['lagna'])
    d10_10l = SL[SIGNS[(d10_idx+9)%12]]
    
    d1['flags'] = {
        'sun_mer_conj': p['Sun']['house'] == p['Mercury']['house'],
        'mer_ven_conj': p['Mercury']['house'] == p['Venus']['house'],
        'd9_venus': d9p['Venus']['sign'] if 'Venus' in d9p else '?',
        'd10_10l_house': d10p[d10_10l]['house'] if d10_10l in d10p else 0,
        'moon_nak': p['Moon']['nakshatra'],
        'd60_ll_house': vargas['D60']['planets'][SL[vargas['D60']['lagna']]]['house'] if SL[vargas['D60']['lagna']] in vargas['D60']['planets'] else 0,
    }
    
    results.append(d1)

results.sort(key=lambda x: -x['scores']['composite'])

print(f"\n{'='*120}")
print(f"FINAL RANKED TABLE")
print(f"{'='*120}")
print(f"{'Rk':<4} {'ID':<4} {'Name':<20} {'Lagna':<8} {'Moon':<18} {'MP':>3} {'Dha':>3} {'Raj':>3} {'W$':>5} {'Pwr':>5} {'Eth':>5} {'Edu':>5} {'Kar':>5} {'Comp':>6} {'D9♀':<10} {'D10 10L':<8} {'Dasha':<16} {'⚠️'}")
print("-"*140)

for i, c in enumerate(results, 1):
    s = c['scores']; y = c['yogas']; f = c['flags']
    moon = c['planets']['Moon']
    asc = c['ascendant']['sign']
    dasha_str = f"{c['dasha']['current_md']}/{c['dasha']['current_ad']}"
    
    flags = []
    if f['d10_10l_house'] in [6,8,12]: flags.append('D10⚠️')
    if f['d9_venus'] == 'Virgo': flags.append('D9♀DEB')
    if c.get('note'): flags.append(c['note'][:12])
    
    print(f"{i:<4} {c['id']:<4} {c['name']:<20} {asc:<8} {moon['nakshatra']:<18} "
          f"{len(y['mahapurusha']):>3} {len(y['dhana']):>3} {len(y['raja']):>3} "
          f"{s['wealth']:>5.1f} {s['power']:>5.1f} {s['ethics']:>5.1f} {s['education']:>5.1f} {s['karma']:>5.1f} "
          f"{s['composite']:>6.1f} {f['d9_venus']:<10} H{f['d10_10l_house']:<7} {dasha_str:<16} {' '.join(flags)}")

# Rank shift
old_ranks = {"P4":1,"P9":2,"P5":3,"P8":4,"P1":5,"P2":6,"P7":7,"P6":8,"P3":9}
print(f"\n{'='*120}")
print("RANK SHIFT vs ORIGINAL RANKING")
print(f"{'='*120}")
for i, c in enumerate(results, 1):
    old = old_ranks.get(c['id'], 99)
    shift = old - i
    arrow = "↑" if shift > 0 else ("↓" if shift < 0 else "—")
    print(f"  {c['id']} {c['name']:<20} Old:{old} → New:{i} ({arrow}{abs(shift)}) | {c['archetype']} | {c['career']}")

# Top dimension leaders
print(f"\n{'='*120}")
print("DIMENSION LEADERS")
print(f"{'='*120}")
for dim, label in [('wealth','💰 Wealth'),('power','👑 Power'),('ethics','🕉️ Ethics'),('education','📚 Education'),('karma','🔄 Karma'),('composite','⭐ Composite')]:
    sd = sorted(results, key=lambda x: -x['scores'][dim])
    print(f"  {label}: " + " > ".join(f"{c['id']}({c['scores'][dim]:.1f})" for c in sd[:3]))

# Key finding summary
print(f"\n{'='*120}")
print("KEY FINDINGS FROM CROSS-REFERENCE")
print(f"{'='*120}")
for c in results:
    f = c['flags']; s = c['scores']
    findings = []
    if f['sun_mer_conj']: findings.append("🌸 Budha-Aditya (42% billionaires)")
    if f['mer_ven_conj']: findings.append("💰 Mer+Ven conj (32% vs 24%)")
    if f['moon_nak'] in ['Shravana','Swati','Purva Bhadrapada']: findings.append(f"🌙 {f['moon_nak']} (billionaire nakshatra)")
    if f['moon_nak'] == 'Mula': findings.append(f"🔥 Mula Moon (astronaut/transformer)")
    if f['d9_venus'] == 'Virgo': findings.append("⛔ D9 Venus DEBIL (Holmes/SBF pattern)")
    if f['d9_venus'] in ['Pisces','Taurus','Libra']: findings.append(f"✓ D9 Venus {f['d9_venus']}")
    if f['d10_10l_house'] in [6,8,12]: findings.append(f"⚠️ D10 10L H{f['d10_10l_house']} (career risk)")
    if f['d10_10l_house'] in [1,4,7,10]: findings.append(f"✓ D10 10L kendra")
    
    print(f"\n  {c['id']} {c['name']} (Score={s['composite']} | {c['archetype']})")
    if findings:
        for fi in findings: print(f"    {fi}")
    else:
        print(f"    (no standout markers)")

# Save
with open('/home/user/dataset/p1p9_absolute_final_rerank.json','w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → /home/user/dataset/p1p9_absolute_final_rerank.json")
