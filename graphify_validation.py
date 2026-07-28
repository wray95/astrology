#!/usr/bin/env python3
"""
GRAPHIFY: Classical Yoga Claims → Statistical Validation
Cross-reference ALL our labeled data against classical astrological claims
Build a truth table + network graph of yoga→outcome relationships
"""
import json, math
from collections import defaultdict, Counter

# ============================================================
# 1. LOAD ALL LABELED DATA
# ============================================================
print("="*100)
print("GRAPHIFY: Classical Astrology Claims → Statistical Cross-Validation")
print("="*100)

# Load domain charts (10: VC/Academic/Fraud with full vargas)
with open('/home/user/dataset/benchmark_10_domain.json') as f:
    domain_10 = json.load(f)

# Load 112 celebrity charts (111 computed)
with open('/home/user/dataset/celebrity_112_nexus_v2.json') as f:
    celeb_112 = json.load(f)

# Load 12 AA benchmark
with open('/home/user/dataset/benchmark_12_nexus_v2.json') as f:
    benchmark_12 = json.load(f)

# Load P1-P9 multivarga
with open('/home/user/dataset/p1p9_multivarga_reranked.json') as f:
    p1p9 = json.load(f)

# Billionaire vs criminal stats
with open('/home/user/dataset/billionaire_noon_analysis.json') as f:
    billionaire_99 = json.load(f)

print(f"Loaded: {len(domain_10)} domain | {len(celeb_112)} celebrity | {len(benchmark_12)} AA benchmark | {len(p1p9)} P1-P9")

# ============================================================
# 2. CLASSICAL CLAIMS → TESTABLE HYPOTHESES
# ============================================================
CLASSICAL_CLAIMS = [
    # (id, category, classical_claim, yoga_type, detection_rule, source)
    ("C1", "Wealth", "2L+11L conjunction = steady wealth", "Dhana", "2L+11L same house", "Phaladeepika Ch.6"),
    ("C2", "Wealth", "5L+9L conjunction = Lakshmi Yoga (great fortune)", "Dhana", "5L+9L same house", "Phaladeepika Ch.6"),
    ("C3", "Wealth", "LL+9L conjunction = self-made wealth", "Dhana", "LL+9L same house", "Saravali"),
    ("C4", "Wealth", "11L exalted or own = strong gains", "WealthLord", "11L dignity >= 75", "BPHS"),
    ("C5", "Wealth", "Jupiter in 2H or 11H = wealth through wisdom", "BeneficWealth", "Jupiter in [2,11]", "Jataka Parijata"),
    ("C6", "Wealth", "Venus in 2H or 11H = wealth through luxury/arts", "BeneficWealth", "Venus in [2,11]", "Jataka Parijata"),
    ("C7", "Wealth", "Debilitated 11L = wealth obstruction", "WealthObstruction", "11L dignity = -100", "Phaladeepika"),
    
    ("P1", "Power", "Kendra-Kona lord conjunction = Raja Yoga (power)", "Raja", "Kendra lord + Kona lord same house", "BPHS Ch.36"),
    ("P2", "Power", "Mahapurusha Yoga = exceptional achievement", "MP", "Planet own/exalt in kendra", "BPHS Ch.37"),
    ("P3", "Power", "Ruchaka (Mars) = military/industrial power", "MP-Mars", "Mars own/exalt in kendra", "BPHS"),
    ("P4", "Power", "Malavya (Venus) = luxury/arts empire", "MP-Venus", "Venus own/exalt in kendra", "BPHS"),
    ("P5", "Power", "Hamsa (Jupiter) = wisdom/spiritual authority", "MP-Jupiter", "Jupiter own/exalt in kendra", "BPHS"),
    
    ("R1", "Resilience", "NBRY: debilitated planet + deb lord in kendra = rise after fall", "NBRY", "Planet deb + deb lord in kendra", "Phaladeepika"),
    ("R2", "Resilience", "VRY: dusthana lord in dusthana = success through adversity", "VRY", "6/8/12 Lord in 6/8/12", "Phaladeepika"),
    
    ("M1", "Marriage", "Jupiter aspect on 7H = protected marriage", "Marriage", "Jupiter aspects 7H", "Jataka Parijata"),
    ("M2", "Marriage", "Venus in own/exalt = happy marriage", "Marriage", "Venus dignity >= 75", "BPHS"),
    ("M3", "Marriage", "7L in dusthana = troubled marriage", "MarriageObstruction", "7L in [6,8,12]", "Phaladeepika"),
    
    ("F1", "Fame", "Multiple planets in 10H = widespread fame", "Fame", "3+ planets in 10H (D1 or D10)", "Jataka Parijata"),
    ("F2", "Fame", "Sun+Moon in kendra = bright public image", "Fame", "Sun+Moon both in kendra", "Saravali"),
    ("F3", "Fame", "Rahu in 10H = unconventional fame", "Fame", "Rahu in 10H", "Jataka Parijata"),
    
    ("E1", "Education", "5L in 5H or 9H = strong education", "Education", "5L in [5,9]", "BPHS"),
    ("E2", "Education", "Mercury+Jupiter conjunction = scholarly success", "Education", "Mer+Jup same house", "Saravali"),
]

# ============================================================
# 3. COMPUTE YOGA PRESENCE FOR ALL CHARTS WITH HOUSES
# ============================================================
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}

# Create a unified labeled dataset from all sources
# Each entry: {name, group, has_wealth, has_power, has_fame, has_education, ...}
def extract_features(chart, has_houses=True):
    """Extract yoga presence for a chart"""
    f = {}
    if 'error' in chart: return f
    
    p = chart.get('planets', {})
    asc_sign = None
    if 'ascendant' in chart:
        asc_sign = chart['ascendant'].get('sign')
    elif 'asc' in chart:
        asc_sign = chart['asc']
    
    if not asc_sign or not p:
        return f
    
    asc_idx = SIGNS.index(asc_sign)
    ll = SL[asc_sign]
    
    # House lords
    lords = {h: SL[SIGNS[(asc_idx+h-1)%12]] for h in range(1,13)}
    
    # C1: 2L+11L conjunction
    h2l, h11l = lords[2], lords[11]
    f['C1'] = (h2l in p and h11l in p and p[h2l]['house'] == p[h11l]['house'])
    
    # C2: 5L+9L Lakshmi
    h5l, h9l = lords[5], lords[9]
    f['C2'] = (h5l in p and h9l in p and p[h5l]['house'] == p[h9l]['house'])
    
    # C3: LL+9L
    f['C3'] = (ll in p and h9l in p and p[ll]['house'] == p[h9l]['house'])
    
    # C4: 11L exalted/own
    f['C4'] = (h11l in p and p[h11l]['dignity'] >= 75)
    
    # C5: Jupiter in 2/11
    f['C5'] = ('Jupiter' in p and p['Jupiter']['house'] in [2,11])
    
    # C6: Venus in 2/11
    f['C6'] = ('Venus' in p and p['Venus']['house'] in [2,11])
    
    # C7: 11L debilitated
    f['C7'] = (h11l in p and p[h11l]['dignity'] == -100)
    
    # P1: Any Raj Yoga (kendra-kona lord conjunction)
    raja = False
    kendra_lords = {h: lords[h] for h in [1,4,7,10]}
    kona_lords = {h: lords[h] for h in [1,5,9]}
    for kh, kl in kendra_lords.items():
        for ch, cl in kona_lords.items():
            if kl == cl: continue
            if kl in p and cl in p and p[kl]['house'] == p[cl]['house']:
                raja = True
    f['P1'] = raja
    
    # P2: Any Mahapurusha
    mp_map = {'Mars':'Ruchaka','Mercury':'Bhadra','Jupiter':'Hamsa','Venus':'Malavya','Saturn':'Sasa'}
    f['P2'] = False
    f['P3'] = False  # Ruchaka
    f['P4'] = False  # Malavya
    f['P5'] = False  # Hamsa
    for pl, yname in mp_map.items():
        if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1,4,7,10]:
            f['P2'] = True
            if pl == 'Mars': f['P3'] = True
            if pl == 'Venus': f['P4'] = True
            if pl == 'Jupiter': f['P5'] = True
    
    # R1: NBRY
    DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
    f['R1'] = False
    for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pl in p and p[pl]['dignity'] == -100:
            deb_lord = SL[DEBIL[pl]]
            if deb_lord in p and p[deb_lord]['house'] in [1,4,7,10]:
                f['R1'] = True
    
    # R2: VRY
    f['R2'] = False
    for dh in [6,8,12]:
        dhl = lords[dh]
        if dhl in p and p[dhl]['house'] in [6,8,12]:
            f['R2'] = True
    
    # M1: Jupiter aspect on 7H
    f['M1'] = False
    if 'Jupiter' in p:
        jh = p['Jupiter']['house']
        # Jupiter aspects 5,7,9 from itself
        for asp in [5,7,9]:
            if (jh + asp - 1) % 12 + 1 == 7:
                f['M1'] = True
    
    # M2: Venus dignity
    f['M2'] = ('Venus' in p and p['Venus']['dignity'] >= 75)
    
    # M3: 7L in dusthana
    h7l = lords[7]
    f['M3'] = (h7l in p and p[h7l]['house'] in [6,8,12])
    
    # F1: 3+ planets in 10H
    count_10h = sum(1 for pl in p if p[pl]['house'] == 10)
    f['F1'] = count_10h >= 3
    
    # F2: Sun+Moon in kendra
    f['F2'] = ('Sun' in p and 'Moon' in p and p['Sun']['house'] in [1,4,7,10] and p['Moon']['house'] in [1,4,7,10])
    
    # F3: Rahu in 10H
    f['F3'] = ('Rahu' in p and p['Rahu']['house'] == 10)
    
    # E1: 5L in 5 or 9
    f['E1'] = (h5l in p and p[h5l]['house'] in [5,9])
    
    # E2: Mercury+Jupiter conjunction
    f['E2'] = ('Mercury' in p and 'Jupiter' in p and p['Mercury']['house'] == p['Jupiter']['house'])
    
    return f

# Build labeled dataset
labeled = []

# Domain 10
for c in domain_10:
    if 'error' in c: continue
    feat = extract_features(c)
    if not feat: continue
    cat = c.get('category', '')
    label = {
        'name': c['name'],
        'wealth': 'Fraud' not in cat and 'Academic' not in cat,
        'power': 'Fraud' in cat or 'Venture' in cat,
        'fame': True,
        'education': 'Academic' in cat or 'Professor' in cat,
        'criminal': 'Fraud' in cat or 'Bankruptcy' in cat,
        'group': 'domain10',
    }
    labeled.append({**feat, **label})

# Benchmark 12
for c in benchmark_12:
    if 'error' in c: continue
    feat = extract_features(c)
    if not feat: continue
    cat = c.get('category', '')
    label = {
        'name': c['name'],
        'wealth': cat in ['Billionaire', 'Wealth/Inherited', 'Creative/Success', 'Power/Historical'],
        'power': cat in ['Power/Historical', 'Billionaire', 'Military/Criminal'],
        'fame': True,
        'education': cat in ['Religious'],
        'criminal': cat in ['Military/Criminal'],
        'group': 'benchmark12',
    }
    labeled.append({**feat, **label})

# P1-P9 (subjective labels)
for c in p1p9:
    feat = extract_features(c)
    if not feat: continue
    cid = c.get('id', '')
    label = {
        'name': c['name'],
        'wealth': cid in ['P4', 'P9', 'P1', 'P5'],
        'power': cid in ['P4', 'P9', 'P1', 'P5', 'P8'],
        'fame': cid in ['P4', 'P9'],
        'education': cid in ['P3', 'P8', 'P5', 'P7'],
        'criminal': False,
        'group': 'p1p9',
    }
    labeled.append({**feat, **label})

# Celeb 112 (infer from known categories)
for c in celeb_112:
    feat = extract_features(c)
    if not feat: continue
    name = c.get('name', '')
    country = c.get('country', '')
    # Heuristic labels based on what we know
    label = {
        'name': name,
        'wealth': name in ['Bill Gates', 'Warren Buffett', 'Elon Musk', 'Beyonce', 'Oprah Winfrey'],
        'power': name in ['Adolf Hitler', 'Winston Churchill'],
        'fame': True,
        'education': name in ['Albert Einstein', 'Marie Curie', 'Stephen Hawking'],
        'criminal': name in ['Adolf Hitler'],
        'group': 'celeb112',
    }
    labeled.append({**feat, **label})

print(f"\nLabeled dataset: {len(labeled)} charts with yoga features + outcome labels")

# ============================================================
# 4. CROSS-VALIDATION: Each Classical Claim Against Data
# ============================================================

print(f"\n{'='*100}")
print("CLASSICAL CLAIM VALIDATION MATRIX")
print(f"{'='*100}")

results = []
for claim_id, category, claim_text, yoga_type, rule, source in CLASSICAL_CLAIMS:
    # Determine which outcome this yoga is supposed to predict
    outcome_map = {
        'Wealth': 'wealth',
        'Power': 'power',
        'Resilience': 'power',  # proxy
        'Marriage': None,  # no marriage data in this set
        'Fame': 'fame',
        'Education': 'education',
    }
    outcome = outcome_map.get(category)
    if outcome is None: continue
    
    # Split labels into yoga-present and yoga-absent
    has_yoga = [l for l in labeled if claim_id in l and l[claim_id]]
    no_yoga = [l for l in labeled if claim_id in l and not l[claim_id]]
    
    if len(has_yoga) < 3 or len(no_yoga) < 3:
        continue
    
    # Outcome rates
    has_outcome = sum(1 for l in has_yoga if l.get(outcome, False))
    no_outcome = sum(1 for l in no_yoga if l.get(outcome, False))
    
    rate_with = has_outcome / len(has_yoga) * 100 if has_yoga else 0
    rate_without = no_outcome / len(no_yoga) * 100 if no_yoga else 0
    
    effect = rate_with - rate_without
    ratio = rate_with / rate_without if rate_without > 0 else float('inf')
    
    # Simple significance: is the effect > 10%?
    sig = "★★★" if abs(effect) > 30 else ("★★" if abs(effect) > 15 else ("★" if abs(effect) > 5 else "—"))
    direction = "✓ CONFIRMED" if effect > 10 else ("✗ REFUTED" if effect < -10 else "~ WEAK")
    
    results.append({
        'id': claim_id, 'category': category, 'claim': claim_text, 'source': source,
        'rate_with': rate_with, 'rate_without': rate_without, 'effect': effect,
        'ratio': ratio, 'n_yoga': len(has_yoga), 'n_noyoga': len(no_yoga),
        'sig': sig, 'direction': direction
    })

# Sort by absolute effect
results.sort(key=lambda x: -abs(x['effect']))

print(f"\n{'ID':<5} {'Cat':<10} {'Claim':<55} {'Yoga%':>6} {'NoYoga%':>7} {'Δ':>7} {'Ratio':>6} {'N':>5} {'Verdict'}")
print("-"*125)
for r in results:
    print(f"{r['id']:<5} {r['category']:<10} {r['claim']:<55} {r['rate_with']:>5.0f}% {r['rate_without']:>6.0f}% {r['effect']:>+6.0f}% {r['ratio']:>5.1f}x {r['n_yoga']+r['n_noyoga']:>5} {r['sig']} {r['direction']}")

# Summary
confirmed = [r for r in results if 'CONFIRMED' in r['direction']]
refuted = [r for r in results if 'REFUTED' in r['direction']]
weak = [r for r in results if 'WEAK' in r['direction']]
print(f"\nSUMMARY: {len(confirmed)} confirmed | {len(refuted)} refuted | {len(weak)} weak/inconclusive")

# ============================================================
# 5. GRAPHIFY — Network of Yoga→Outcome Relationships
# ============================================================
print(f"\n{'='*100}")
print("GRAPHIFY: Yoga → Outcome Network")
print(f"{'='*100}")

# Build adjacency matrix
# Nodes: Classical claims (C1-C7, P1-P5, R1-R2, M1-M3, F1-F3, E1-E2) + Outcomes
OUTCOMES = ['Wealth', 'Power', 'Fame', 'Education', 'Criminal']

# For each outcome, which yogas are most predictive?
print(f"\n{'Outcome':<14} {'Top Predictive Yogas (effect size)'}")
print("-"*80)
for out in OUTCOMES:
    # Find yogas that predict this outcome
    predictions = []
    for r in results:
        # Map category to outcome
        cat_to_out = {'Wealth': 'wealth', 'Power': 'power', 'Fame': 'fame', 'Education': 'education'}
        mapped = cat_to_out.get(r['category'])
        if mapped is None: continue
        
        # This yoga predicts the mapped outcome
        predictions.append((r['id'], r['claim'][:40], r['effect'], r['direction']))
    
    # Also check: which yogas correlate with 'criminal' label
    if out == 'Criminal':
        for claim_id, category, claim_text, yoga_type, rule, source in CLASSICAL_CLAIMS:
            has_yoga = [l for l in labeled if claim_id in l and l[claim_id]]
            no_yoga = [l for l in labeled if claim_id in l and not l[claim_id]]
            if len(has_yoga) < 3: continue
            crim_with = sum(1 for l in has_yoga if l.get('criminal', False)) / len(has_yoga) * 100
            crim_without = sum(1 for l in no_yoga if l.get('criminal', False)) / len(no_yoga) * 100
            eff = crim_with - crim_without
            predictions.append((claim_id, claim_text[:40], eff, "CRIM" if eff > 10 else "ANTI" if eff < -10 else "—"))
    
    predictions.sort(key=lambda x: -abs(x[2]))
    for pid, claim, eff, direction in predictions[:5]:
        print(f"  {out:<14} ← {pid} {claim:<42} Δ={eff:+.0f}% {direction}")

# ============================================================
# 6. ASCII GRAPH — Yoga Network Visualization
# ============================================================
print(f"\n{'='*100}")
print("YOGA NETWORK GRAPH (ASCII)")
print(f"{'='*100}")

# Build edges with weights
edges = []
for r in results:
    weight = abs(r['effect']) / 100  # normalize
    edges.append((r['id'], r['category'], r['effect'], r['direction']))

# Group nodes by category
categories = defaultdict(list)
for r in results:
    categories[r['category']].append(r)

print(f"\n{'OUTCOME':<15}", end="")
for cat in ['Wealth', 'Power', 'Fame', 'Education']:
    print(f"  ← {cat:<20}", end="")
print("\n" + "-"*100)

for cat in ['Wealth', 'Power', 'Fame', 'Education']:
    cat_results = sorted(categories[cat], key=lambda x: -abs(x['effect']))
    print(f"\n{cat} YOGAS:")
    for r in cat_results[:5]:
        bar_len = int(abs(r['effect']) / 2)
        bar = "█" * bar_len
        direction = "→" if r['effect'] > 0 else "←"
        color = "🟢" if r['effect'] > 10 else ("🔴" if r['effect'] < -10 else "⚪")
        print(f"  {color} {r['id']} [{r['claim'][:50]:<50}] {direction} {bar} {r['effect']:+.0f}%")

# ============================================================
# 7. CRIMINAL/BILLIONAIRE PLANETARY CONFIRMATION
# ============================================================
print(f"\n{'='*100}")
print("CRIMINAL vs BILLIONAIRE PLANETARY MARKER VALIDATION")
print(f"{'='*100}")

# From the earlier analysis, check these markers against our house-level data
print("\nChecking if criminal planet markers hold at house level:")

# Load the billionaire_vs_criminal stats  
# Moon Ardra = criminal (10x), Moon Jyeshtha = criminal (5x), Moon Ashwini = criminal (inf)
# Mars+Sat conjunction = criminal (2.1x)
# Mercury+Venus conjunction = billionaire (2.6x)
# Jupiter EXALTED = 0 criminals

for c in domain_10:
    if 'error' in c: continue
    p = c['planets']
    name = c['name']
    cat = c.get('category','')
    is_fraud = 'Fraud' in cat
    
    # Check markers
    moon = p.get('Moon', {})
    moon_nak = moon.get('nakshatra', '?')
    moon_deb = moon.get('dignity', 0) == -100
    
    mars_sat_conj = 'Mars' in p and 'Saturn' in p and p['Mars']['house'] == p['Saturn']['house']
    mer_ven_conj = 'Mercury' in p and 'Venus' in p and p['Mercury']['house'] == p['Venus']['house']
    
    bad_markers = sum([
        moon_nak in ['Ardra', 'Jyeshtha', 'Ashwini'],
        moon_deb,
        mars_sat_conj,
    ])
    good_markers = sum([mer_ven_conj])
    
    # Check: does fraudster have >0 bad markers? Does non-fraudster have good markers?
    expected = "CRIMINAL" if is_fraud else "LEGIT"
    predicted = "CRIMINAL" if bad_markers >= 1 else "LEGIT"
    match = "✓" if predicted == expected else "✗"
    
    print(f"  {match} {name:<22} | {cat:<28} | Bad:{bad_markers} Good:{good_markers} | "
          f"Moon:{moon_nak}({'DEB' if moon_deb else 'ok'}) | "
          f"{'Ma+Sa' if mars_sat_conj else ''} {'Me+Ve' if mer_ven_conj else ''}")

# ============================================================
# 8. FINAL TRUTH TABLE
# ============================================================
print(f"\n{'='*100}")
print("FINAL TRUTH TABLE: Classical Claims Ranked by Evidence Strength")
print(f"{'='*100}")

print(f"\n{'Rank':<5} {'ID':<5} {'Claim':<50} {'Effect':>7} {'Sig':>5} {'Verdict':<15} {'Source'}")
print("-"*110)

for i, r in enumerate(results, 1):
    print(f"{i:<5} {r['id']:<5} {r['claim']:<50} {r['effect']:>+6.0f}% {r['sig']:>5} {r['direction']:<15} {r['source']}")

# Save
with open('/home/user/dataset/classical_claims_validation.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved → /home/user/dataset/classical_claims_validation.json")
