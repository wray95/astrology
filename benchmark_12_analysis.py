#!/usr/bin/env python3
"""Refined 12-chart benchmark: cleaner yoga detection, discriminative scoring"""
import json

with open('dataset/benchmark_12_computed.json') as f:
    charts = json.load(f)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}

def aspect_each_other(p, a, b, asc_idx):
    """Check if planets a and b aspect each other (7th aspect for all, plus special for Mars/Jup/Sat)"""
    if a not in p or b not in p: return False
    ah, bh = p[a]['house'], p[b]['house']
    # All planets aspect 7th from themselves
    if (ah + 6) % 12 + 1 == bh: return True  # a aspects b
    if (bh + 6) % 12 + 1 == ah: return True  # b aspects a
    # Special aspects
    special = {'Mars': [4,7,8], 'Jupiter': [5,7,9], 'Saturn': [3,7,10]}
    for pl, aspects in special.items():
        if a == pl:
            for asp in aspects:
                if (ah + asp - 1) % 12 + 1 == bh:
                    return True
        if b == pl:
            for asp in aspects:
                if (bh + asp - 1) % 12 + 1 == ah:
                    return True
    return False

def detect_meaningful_yogas(chart):
    p = chart['planets']
    asc = chart['ascendant']['sign']
    asc_idx = SIGNS.index(asc)
    yogas = {}
    
    ll = SL[asc]
    h2l, h5l, h9l, h10l, h11l = [SL[SIGNS[(asc_idx+h-1)%12]] for h in [2,5,9,10,11]]
    
    # --- DHANA (Wealth) ---
    dhana = []
    # 2L+11L conjunction
    if h2l in p and h11l in p and p[h2l]['house'] == p[h11l]['house']:
        dhana.append(f"2L({h2l})+11L({h11l}) conj H{p[h2l]['house']}")
    # 2L+11L mutual aspect
    elif h2l in p and h11l in p and aspect_each_other(p, h2l, h11l, asc_idx):
        dhana.append(f"2L({h2l})+11L({h11l}) mutual aspect")
    # 5L+9L conjunction (Lakshmi)
    if h5l in p and h9l in p and p[h5l]['house'] == p[h9l]['house']:
        dhana.append(f"LAKSHMI: 5L({h5l})+9L({h9l}) conj")
    yogas['dhana'] = dhana
    
    # --- RAJA (Power) ---
    raja = []
    kendra_houses = [1,4,7,10]
    kona_houses = [1,5,9]
    kendra_lords = {h: SL[SIGNS[(asc_idx+h-1)%12]] for h in kendra_houses}
    kona_lords = {h: SL[SIGNS[(asc_idx+h-1)%12]] for h in kona_houses}
    
    # Kendra-Kona lord conjunction (strict: same house)
    seen = set()
    for kh, kl in kendra_lords.items():
        for ch, cl in kona_lords.items():
            if kl == cl: continue
            key = tuple(sorted([kl,cl]))
            if key in seen: continue
            if kl in p and cl in p and p[kl]['house'] == p[cl]['house']:
                seen.add(key)
                raja.append(f"K-K conj: {kl}(L{kh})+{cl}(L{ch}) H{p[kl]['house']}")
    yogas['raja'] = raja
    
    # --- MAHAPURUSHA ---
    mp = []
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    for pl, yname in mp_map.items():
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            mp.append(f"{yname}: {pl} H{p[pl]['house']} {p[pl]['sign']}")
    yogas['mahapurusha'] = mp
    
    # --- NBRY ---
    nbry = []
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in p and p[pl]['dignity'] == -100:
            deb_lord = SL[DEBIL[pl]]
            ex_lord = SL[EXALT[pl]]
            conds = []
            if deb_lord in p:
                if p[deb_lord]['house'] in [1,4,7,10]:
                    conds.append(f"deblord({deb_lord}) in kendra")
                moon_sign = p['Moon']['sign']
                moon_idx = SIGNS.index(moon_sign)
                if (p[deb_lord]['sign_idx'] - moon_idx) % 12 in [0,3,6,9]:
                    conds.append(f"deblord in kendra fm Moon")
            if ex_lord in p:
                if aspect_each_other(p, pl, ex_lord, asc_idx):
                    conds.append(f"exlord({ex_lord}) aspects {pl}")
            if conds:
                nbry.append(f"{pl} deb({DEBIL[pl]}) H{p[pl]['house']}: " + "; ".join(conds))
    yogas['nbry'] = nbry
    
    # --- VIPAREETA ---
    vry = []
    for dh in [6,8,12]:
        dhl = SL[SIGNS[(asc_idx+dh-1)%12]]
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            vry.append(f"{dhl}(L{dh}) in H{p[dhl]['house']}")
    yogas['vry'] = vry
    
    # --- Key planet positions ---
    key_pos = {}
    for pl in ['Jupiter','Venus','Saturn','Mars']:
        if pl in p:
            key_pos[pl] = {'house': p[pl]['house'], 'sign': p[pl]['sign'], 'dignity': p[pl]['dignity']}
    
    # 11L status
    h11l_status = {}
    if h11l in p:
        h11l_status = {'planet': h11l, 'house': p[h11l]['house'], 'dignity': p[h11l]['dignity']}
    
    # 9L status
    h9l_status = {}
    if h9l in p:
        h9l_status = {'planet': h9l, 'house': p[h9l]['house'], 'dignity': p[h9l]['dignity']}
    
    # LL status
    ll_status = {'planet': ll, 'house': p[ll]['house'], 'dignity': p[ll]['dignity']} if ll in p else {}
    
    return {'yogas': yogas, 'key_pos': key_pos, 'h11l': h11l_status, 'h9l': h9l_status, 'll': ll_status}

def discriminative_score(yogas, h11l, h9l, ll, key_pos):
    """Discriminative score — designed to separate ultra-wealthy from merely successful"""
    s = 0
    
    # --- Wealth channel (max 4 pts) ---
    if yogas['dhana']:
        s += min(len(yogas['dhana']), 3)
    
    # 11L strong
    if h11l.get('dignity', 0) == 100:
        s += 2  # 11L exalted = very strong wealth
    elif h11l.get('dignity', 0) == 75:
        s += 1
    
    # 9L strong (bhagya)
    if h9l.get('dignity', 0) == 100:
        s += 2
    elif h9l.get('dignity', 0) == 75:
        s += 1
    
    # 11L in 2/5/9/11 (wealth houses) — no penalty for 6/8/12
    if h11l.get('house') in [2,5,9,11]:
        s += 1
    elif h11l.get('house') in [6,8,12]:
        s -= 1  # 11L dusthana = wealth obstruction
    
    # --- Power channel (max 3 pts) ---
    if yogas['raja']:
        s += min(len(yogas['raja']), 3)
    
    if yogas['mahapurusha']:
        s += len(yogas['mahapurusha']) * 2
    
    # --- Obstruction removal ---
    if yogas['vry']:
        s += len(yogas['vry'])
    
    if yogas['nbry']:
        s += len(yogas['nbry'])
    
    # --- Planet quality ---
    # Jupiter/Venus in 1/4/7/10 and dignified
    for pl in ['Jupiter','Venus']:
        if pl in key_pos:
            if key_pos[pl]['house'] in [1,4,7,10] and key_pos[pl]['dignity'] >= 75:
                s += 2
    
    # LL strength
    if ll.get('dignity', 0) >= 75:
        s += 1
    if ll.get('house') in [1,4,7,10]:
        s += 1
    
    return s

print("="*110)
print("REFINED 12-CHART BENCHMARK: Discriminative Yoga Analysis")
print("="*110)

CATEGORY_BANDS = {
    'Billionaire': (5, 12),
    'Wealth/Inherited': (4, 10),
    'Creative/Success': (3, 8),
    'Actor': (2, 7),
    'Athlete': (2, 6),
    'Religious': (1, 6),
    'Power/Historical': (5, 12),
    'Military/Criminal': (3, 9),
}

results = []
for c in charts:
    if 'error' in c: continue
    yd = detect_meaningful_yogas(c)
    ds = discriminative_score(yd['yogas'], yd['h11l'], yd['h9l'], yd['ll'], yd['key_pos'])
    band = CATEGORY_BANDS.get(c['category'], (1,15))
    match = "✓" if band[0] <= ds <= band[1] else ("↑" if ds > band[1] else "↓")
    results.append((c, yd, ds, match))

# Sort by score
results.sort(key=lambda x: -x[2])

print(f"\n{'Rank':<5} {'Name':<22} {'Category':<20} {'Asc':<8} {'Moon':<20} {'Dhana':>6} {'Raja':>4} {'MP':>4} {'NBRY':>4} {'Score':>5} {'Band':>10} {'Δ':>4}")
print("-"*115)

for i, (c, yd, ds, match) in enumerate(results, 1):
    asc = c['ascendant']['sign']
    moon = c['planets']['Moon']
    moon_str = f"{moon['nakshatra'][:12]}"
    y = yd['yogas']
    band = CATEGORY_BANDS.get(c['category'], (0,0))
    band_str = f"{band[0]}-{band[1]}"
    
    print(f"{i:<5} {c['name']:<22} {c['category']:<20} {asc:<8} {moon_str:<20} {len(y['dhana']):>6} {len(y['raja']):>4} {len(y['mahapurusha']):>4} {len(y['nbry']):>4} {ds:>5} {band_str:>10} {match:>4}")

# Hit rate
hits = sum(1 for _,_,_,m in results if m == '✓')
print(f"\nIn-band accuracy: {hits}/{len(results)} ({100*hits/len(results):.0f}%)")

# --- DETAIL CARDS ---
print("\n" + "="*110)
print("DETAIL CARDS — Key Yoga Summary")
print("="*110)

WEALTH_RANKS = {
    'Billionaire': 5,
    'Wealth/Inherited': 4,
    'Creative/Success': 3,
    'Actor': 3,
    'Athlete': 2,
    'Religious': 1,
    'Power/Historical': 4,
    'Military/Criminal': 2,
}

# Rank correlation
ranks_pred = [r[2] for r in results]
ranks_known = [WEALTH_RANKS.get(r[0]['category'], 2) for r in results]

from math import isnan

def spearman_rank(pred, known):
    """Simple Spearman correlation"""
    n = len(pred)
    # Sort indices
    pred_ranks = [sorted(pred, reverse=True).index(x)+1 for x in pred]
    known_ranks = [sorted(known, reverse=True).index(x)+1 for x in known]
    d2 = sum((a-b)**2 for a,b in zip(pred_ranks, known_ranks))
    return 1 - (6*d2)/(n*(n**2-1))

rho = spearman_rank(ranks_pred, ranks_known)
print(f"\nSpearman ρ (score vs known wealth rank): {rho:.3f}")

for i, (c, yd, ds, match) in enumerate(results, 1):
    y = yd['yogas']
    print(f"\n--- #{i} {c['name']} | {c['category']} | Score={ds} {match} ---")
    print(f"  Lagna: {c['ascendant']['sign']} {c['ascendant']['deg']:.1f}° | Moon: {c['planets']['Moon']['sign']} {c['planets']['Moon']['nakshatra']} | "
          f"LL: {yd['ll']['planet']} H{yd['ll']['house']}(dig={yd['ll']['dignity']}) | "
          f"9L: {yd['h9l'].get('planet','?')} H{yd['h9l'].get('house','?')}(dig={yd['h9l'].get('dignity','?')}) | "
          f"11L: {yd['h11l'].get('planet','?')} H{yd['h11l'].get('house','?')}(dig={yd['h11l'].get('dignity','?')})")
    if y['dhana']:
        print(f"  💰 Dhana: {', '.join(y['dhana'])}")
    if y['raja']:
        print(f"  👑 Raja:  {', '.join(y['raja'])}")
    if y['mahapurusha']:
        print(f"  ⭐ MP:    {', '.join(y['mahapurusha'])}")
    if y['nbry']:
        print(f"  🔄 NBRY:  {', '.join(y['nbry'])}")
    if y['vry']:
        print(f"  🌀 VRY:   {', '.join(y['vry'])}")

print(f"\n{'='*110}")
print(f"N = {len(results)} | Spearman ρ = {rho:.3f} | In-band = {hits}/{len(results)} ({100*hits/len(results):.0f}%)")
