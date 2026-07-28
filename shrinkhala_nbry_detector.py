#!/usr/bin/env python3
"""
SHRINKHALA LOOPS + NEECHA BHANGA DETECTION
Run across ALL saved charts
"""
import json, os
from collections import defaultdict

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']

def get_sign(pn, chart):
    """Get the sign a planet is in, handling different chart formats"""
    planets = chart.get('planets', {})
    if pn in planets:
        return planets[pn].get('sign', None)
    return None

def detect_shrinkhala(planets_data):
    """
    Detect Shrinkhala (chain) loops.
    A shrinkhala is a closed chain of mutual reception involving 3+ planets.
    Planet A in sign of B, B in sign of C, C in sign of A = Shrinkhala.
    """
    # Build: for each planet, what other planets' signs is it in?
    # "planet P is in the sign of Q" means P's sign is ruled by Q
    in_sign_of = {}
    for pn in P7:
        sign = planets_data.get(pn, {}).get('sign')
        if sign:
            lord = SL.get(sign)
            if lord and lord != pn:  # exclude own sign
                in_sign_of[pn] = lord
    
    # Find loops of length 3+
    loops = []
    for start in P7:
        if start not in in_sign_of: continue
        # DFS to find loops
        def find_loop(current, path, depth):
            if depth > 7: return  # max chain length
            if current == start and depth >= 3:
                loops.append(path[:])
                return
            if current in path[:-1]: return  # already visited (not start)
            nxt = in_sign_of.get(current)
            if nxt and nxt not in path[:-1]:
                find_loop(nxt, path + [nxt], depth + 1)
        
        find_loop(in_sign_of[start], [start, in_sign_of[start]], 2)
    
    # Deduplicate (rotations of same loop)
    unique = []
    seen_sets = set()
    for loop in loops:
        # Rotate to canonical form (start with alphabetically first)
        min_i = min(range(len(loop)), key=lambda i: loop[i])
        rotated = loop[min_i:] + loop[:min_i]
        key = tuple(rotated)
        if key not in seen_sets:
            seen_sets.add(key)
            unique.append(rotated)
    
    return unique

def detect_nbry(chart):
    """
    Detect Neecha Bhanga Raj Yoga with all 8 classical conditions.
    Returns list of (planet, conditions_met, details)
    """
    # Need ascendant for house-based conditions
    asc_sign = None
    if 'ascendant' in chart:
        asc_sign = chart['ascendant'].get('sign')
    elif 'asc' in chart:
        asc_sign = chart['asc']
    
    if not asc_sign: return []
    
    planets = chart.get('planets', {})
    asc_idx = SIGNS.index(asc_sign)
    
    # Map houses
    house_of = {}
    for pn in planets:
        if 'house' in planets[pn]:
            house_of[pn] = planets[pn]['house']
        elif 'sign_idx' in planets[pn] and asc_idx is not None:
            house_of[pn] = (planets[pn]['sign_idx'] - asc_idx) % 12 + 1
    
    nbry_results = []
    
    for pl in P7:
        if pl not in planets: continue
        dign = planets[pl].get('dignity', 0)
        if dign != -100: continue  # Not debilitated
        
        deb_sign = DEBIL[pl]
        deb_lord = SL[deb_sign]  # Lord of debilitation sign
        ex_sign = EXALT[pl]
        ex_lord = SL[ex_sign]  # Lord of exaltation sign
        
        conditions = []
        details = {}
        
        # 1. Debilitation lord in kendra from Lagna
        if deb_lord in house_of and house_of[deb_lord] in [1,4,7,10]:
            conditions.append("C1:deblord-kendra-lagna")
            details['deblord_house'] = house_of[deb_lord]
        
        # 2. Debilitation lord in kendra from Moon
        if 'Moon' in planets and deb_lord in house_of:
            moon_sign = planets['Moon'].get('sign')
            moon_idx = SIGNS.index(moon_sign) if moon_sign else None
            if moon_idx is not None:
                deb_lord_sign = planets[deb_lord].get('sign')
                deb_lord_idx = SIGNS.index(deb_lord_sign) if deb_lord_sign else None
                if deb_lord_idx is not None:
                    house_from_moon = (deb_lord_idx - moon_idx) % 12 + 1
                    if house_from_moon in [1,4,7,10]:
                        conditions.append("C2:deblord-kendra-moon")
                        details['deblord_house_moon'] = house_from_moon
        
        # 3. Exaltation lord in kendra from Lagna
        if ex_lord in house_of and house_of[ex_lord] in [1,4,7,10]:
            conditions.append("C3:exlord-kendra-lagna")
            details['exlord_house'] = house_of[ex_lord]
        
        # 4. Exaltation lord aspects debilitated planet
        # (We check if they're in mutual aspect houses)
        if ex_lord in house_of and pl in house_of:
            eh = house_of[ex_lord]; dh = house_of[pl]
            # 7th aspect (all planets)
            if (eh + 6) % 12 + 1 == dh or (dh + 6) % 12 + 1 == eh:
                conditions.append("C4:exlord-aspects-7th")
            # Special aspects
            special = {'Mars': [4,7,8], 'Jupiter': [5,7,9], 'Saturn': [3,7,10]}
            if ex_lord in special:
                for asp in special[ex_lord]:
                    if (eh + asp - 1) % 12 + 1 == dh:
                        conditions.append("C4:exlord-aspects-special")
                        break
        
        # 5. The debilitated planet is in kendra from Lagna
        if pl in house_of and house_of[pl] in [1,4,7,10]:
            conditions.append("C5:debplanet-kendra-lagna")
        
        # 6. The debilitated planet is in kendra from Moon
        if pl in house_of and 'Moon' in planets:
            moon_sign = planets['Moon'].get('sign')
            if moon_sign:
                moon_idx = SIGNS.index(moon_sign)
                pl_sign = planets[pl].get('sign')
                pl_idx = SIGNS.index(pl_sign)
                hfm = (pl_idx - moon_idx) % 12 + 1
                if hfm in [1,4,7,10]:
                    conditions.append("C6:debplanet-kendra-moon")
        
        # 7. The planet is aspected by Jupiter
        if 'Jupiter' in house_of and pl in house_of:
            jh = house_of['Jupiter']; dh = house_of[pl]
            if (jh + 6) % 12 + 1 == dh:
                conditions.append("C7:jupiter-7th-aspect")
            for asp in [5,7,9]:
                if (jh + asp - 1) % 12 + 1 == dh:
                    conditions.append("C7:jupiter-special-aspect")
                    break
        
        # 8. The planet is conjunct or aspected by a friendly planet
        # Venus and Mercury are mutual friends; Jupiter friends with Sun/Moon/Mars
        friends = {
            'Sun': ['Moon','Mars','Jupiter'],
            'Moon': ['Sun','Mercury'],
            'Mars': ['Sun','Moon','Jupiter'],
            'Mercury': ['Sun','Venus'],
            'Jupiter': ['Sun','Moon','Mars'],
            'Venus': ['Mercury','Saturn'],
            'Saturn': ['Mercury','Venus'],
        }
        for friend in friends.get(pl, []):
            if friend in house_of and friend in planets:
                fh = house_of[friend]; dh = house_of[pl]
                if fh == dh:  # conjunction
                    conditions.append(f"C8:friend-conj-{friend}")
                    break
                if (fh + 6) % 12 + 1 == dh:
                    conditions.append(f"C8:friend-7th-{friend}")
                    break
        
        if conditions:
            nbry_results.append({
                'planet': pl,
                'deb_sign': deb_sign,
                'house': house_of.get(pl, '?'),
                'conditions': conditions,
                'confidence': min(len(conditions), 4)  # cap at 4
            })
    
    return nbry_results

def detect_parivartana(planets_data):
    """Detect Parivartana Yoga (mutual exchange)"""
    exchanges = []
    for i, p1 in enumerate(P7):
        for p2 in P7[i+1:]:
            s1 = planets_data.get(p1, {}).get('sign')
            s2 = planets_data.get(p2, {}).get('sign')
            if s1 and s2:
                l1 = SL.get(s1); l2 = SL.get(s2)
                if l1 == p2 and l2 == p1:
                    exchanges.append((p1, p2, s1, s2))
    return exchanges

# ============================================================
# LOAD ALL CHARTS
# ============================================================
print("="*100)
print("SHRINKHALA LOOPS + NEECHA BHANGA + PARIVARTANA — All Saved Charts")
print("="*100)

all_charts = []
sources = []

# P1-P9
path = '/home/user/dataset/p1p9_absolute_final_rerank.json'
if os.path.exists(path):
    with open(path) as f:
        charts = json.load(f)
        for c in charts:
            c['_source'] = 'P1-P9'; c['_name'] = f"{c.get('id','?')} {c.get('name','?')}"
        all_charts.extend(charts); sources.append(f"P1-P9 ({len(charts)})")

# Domain 10
path = '/home/user/dataset/benchmark_10_domain.json'
if os.path.exists(path):
    with open(path) as f:
        charts = json.load(f)
        for c in charts:
            c['_source'] = 'Domain10'; c['_name'] = c.get('name','?')
        all_charts.extend(charts); sources.append(f"Domain10 ({len(charts)})")

# Benchmark 12
path = '/home/user/dataset/benchmark_12_nexus_v2.json'
if os.path.exists(path):
    with open(path) as f:
        charts = json.load(f)
        for c in charts:
            c['_source'] = 'Bench12'; c['_name'] = c.get('name','?')
        all_charts.extend(charts); sources.append(f"Bench12 ({len(charts)})")

# Celebrity 112
path = '/home/user/dataset/celebrity_112_nexus_v2.json'
if os.path.exists(path):
    with open(path) as f:
        charts = json.load(f)
        for c in charts:
            c['_source'] = 'Celeb112'; c['_name'] = c.get('name','?')
        all_charts.extend(charts); sources.append(f"Celeb112 ({len(charts)})")

# Billionaire noon
path = '/home/user/dataset/billionaire_noon_analysis.json'
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
        if 'charts' in data:
            for c in data['charts']:
                c['_source'] = 'Billionaire'; c['_name'] = c.get('name','?')
            all_charts.extend(data['charts']); sources.append(f"Billionaire ({len(data['charts'])})")

print(f"Loaded: {', '.join(sources)}")
print(f"Total: {len(all_charts)} charts\n")

# ============================================================
# ANALYZE
# ============================================================
shrinkhala_found = []
nbry_found = []
parivartana_found = []

for c in all_charts:
    planets = c.get('planets', {})
    name = c.get('_name', c.get('name', '?'))
    source = c.get('_source', '?')
    
    # Normalize planets data
    norm = {}
    for pn in P7:
        if pn in planets:
            norm[pn] = {'sign': planets[pn].get('sign'), 'dignity': planets[pn].get('dignity', 0)}
    
    # Shrinkhala
    loops = detect_shrinkhala(norm)
    if loops:
        for loop in loops:
            shrinkhala_found.append({
                'name': name, 'source': source,
                'loop': ' → '.join(loop),
                'length': len(loop)
            })
    
    # Parivartana
    exchanges = detect_parivartana(norm)
    if exchanges:
        for ex in exchanges:
            parivartana_found.append({
                'name': name, 'source': source,
                'exchange': f"{ex[0]}↔{ex[1]} ({ex[2]}↔{ex[3]})"
            })
    
    # NBRY
    nbry = detect_nbry(c)
    if nbry:
        for n in nbry:
            nbry_found.append({
                'name': name, 'source': source,
                'planet': n['planet'],
                'conditions': len(n['conditions']),
                'detail': ', '.join(n['conditions'][:4])
            })

# ============================================================
# REPORT
# ============================================================
print(f"{'='*100}")
print(f"SHRINKHALA LOOPS FOUND: {len(shrinkhala_found)}")
print(f"{'='*100}")
if shrinkhala_found:
    shrinkhala_found.sort(key=lambda x: -x['length'])
    print(f"\n{'Name':<30} {'Source':<12} {'Len':>3} {'Loop'}")
    print("-"*90)
    for s in shrinkhala_found[:30]:
        print(f"{s['name']:<30} {s['source']:<12} {s['length']:>3} {s['loop']}")
else:
    print("  None found in any chart.")

print(f"\n{'='*100}")
print(f"PARIVARTANA YOGA (Mutual Exchange) FOUND: {len(parivartana_found)}")
print(f"{'='*100}")
if parivartana_found:
    print(f"\n{'Name':<30} {'Source':<12} {'Exchange'}")
    print("-"*70)
    for p in parivartana_found[:25]:
        print(f"{p['name']:<30} {p['source']:<12} {p['exchange']}")
else:
    print("  None found.")

print(f"\n{'='*100}")
print(f"NEECHA BHANGA RAJ YOGA FOUND: {len(nbry_found)}")
print(f"{'='*100}")
if nbry_found:
    nbry_found.sort(key=lambda x: -x['conditions'])
    print(f"\n{'Name':<30} {'Source':<12} {'Planet':<10} {'Cond':>4} {'Details'}")
    print("-"*100)
    for n in nbry_found:
        print(f"{n['name']:<30} {n['source']:<12} {n['planet']:<10} {n['conditions']:>4} {n['detail'][:55]}")
else:
    print("  None found.")

# Breakdown by source
print(f"\n{'='*100}")
print("SUMMARY BY SOURCE")
print(f"{'='*100}")
source_stats = defaultdict(lambda: {'total':0,'shrinkhala':0,'nbry':0,'parivartana':0})
for c in all_charts:
    src = c.get('_source','?')
    source_stats[src]['total'] += 1
for s in shrinkhala_found: source_stats[s['source']]['shrinkhala'] += 1
for n in nbry_found: source_stats[n['source']]['nbry'] += 1
for p in parivartana_found: source_stats[p['source']]['parivartana'] += 1

print(f"\n{'Source':<15} {'Total':>6} {'Shrinkhala':>11} {'NBRY':>6} {'Parivartana':>12}")
print("-"*55)
for src, stats in sorted(source_stats.items()):
    t = stats['total']
    print(f"{src:<15} {t:>6} {stats['shrinkhala']:>4} ({stats['shrinkhala']/max(t,1)*100:>5.1f}%) {stats['nbry']:>4} ({stats['nbry']/max(t,1)*100:>5.1f}%) {stats['parivartana']:>4} ({stats['parivartana']/max(t,1)*100:>5.1f}%)")

# P1-P9 specific
print(f"\n{'='*100}")
print("P1-P9 SPECIFIC")
print(f"{'='*100}")
for c in all_charts:
    if c.get('_source') != 'P1-P9': continue
    name = c.get('_name','?')
    planets = c.get('planets',{})
    
    # Shrinkhala
    norm = {}
    for pn in P7:
        if pn in planets:
            norm[pn] = {'sign': planets[pn].get('sign'), 'dignity': planets[pn].get('dignity', 0)}
    loops = detect_shrinkhala(norm)
    exchanges = detect_parivartana(norm)
    nbry = detect_nbry(c)
    
    print(f"\n{name}:")
    if loops:
        for loop in loops:
            print(f"  🔗 Shrinkhala: {' → '.join(loop)} (len={len(loop)})")
    if exchanges:
        for ex in exchanges:
            print(f"  🔄 Parivartana: {ex[0]}↔{ex[1]}")
    if nbry:
        for n in nbry:
            print(f"  🙏 NBRY: {n['planet']} deb {n['deb_sign']} | {n['conditions']} conditions: {', '.join(n['conditions'][:3])}")
    if not loops and not exchanges and not nbry:
        print(f"  (none)")

# Save
with open('/home/user/dataset/shrinkhala_nbry_report.json','w') as f:
    json.dump({
        'shrinkhala': shrinkhala_found,
        'nbry': nbry_found,
        'parivartana': parivartana_found,
        'source_stats': {k: dict(v) for k,v in source_stats.items()}
    }, f, indent=2)
print(f"\nSaved → /home/user/dataset/shrinkhala_nbry_report.json")
