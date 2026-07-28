#!/usr/bin/env python3
"""
NEXUS v3.0 — 5-LOOP SHRINKHALA DISCOVERY ENGINE
Across ALL saved charts. Rockefeller case study.
Honest: detect, don't assume.
"""
import swisseph as swe, json, os, math
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}

def get_sign_planet_data(planets_dict):
    """Extract sign-per-planet for Shrinkhala detection"""
    result = {}
    for pn in P7:
        if pn in planets_dict:
            result[pn] = planets_dict[pn].get('sign')
    return result

def detect_all_shrinkhala(signs_of):
    """
    Detect ALL Shrinkhala loops of any length (2+).
    Returns list of (loop_list, length).
    A 5-Loop Shrinkhala = length 5 closed chain.
    """
    # Build: planet → which planet's sign it's in
    in_sign_of = {}
    for pn in P7:
        sign = signs_of.get(pn)
        if sign:
            lord = SL.get(sign)
            if lord and lord != pn:
                in_sign_of[pn] = lord
    
    all_loops = []
    
    # DFS for all cycles
    def dfs(start, current, path, depth):
        if depth > 7: return
        if current == start and depth >= 2:
            all_loops.append(path[:])
            return
        if current in path[:-1]: return
        nxt = in_sign_of.get(current)
        if nxt and nxt not in path[1:-1]:
            dfs(start, nxt, path + [nxt], depth + 1)
    
    for start in P7:
        if start in in_sign_of:
            dfs(start, in_sign_of[start], [start, in_sign_of[start]], 2)
    
    # Deduplicate
    unique = []
    seen = set()
    for loop in all_loops:
        min_i = min(range(len(loop)), key=lambda i: loop[i])
        rotated = tuple(loop[min_i:] + loop[:min_i])
        if rotated not in seen:
            seen.add(rotated)
            unique.append(list(rotated))
    
    return [(loop, len(loop)) for loop in unique]

def compute_shrinkhala_strength(loop, planets_dict):
    """Score a Shrinkhala loop 0-100"""
    score = 50  # base
    involved = set(loop)
    
    # Bonus for benefics
    benefics = {'Jupiter','Venus','Mercury','Moon'}
    malefics = {'Sun','Mars','Saturn','Rahu','Ketu'}
    score += len(involved & benefics) * 8
    score -= len(involved & malefics) * 3
    
    # Dignity of involved planets
    for pn in involved:
        if pn in planets_dict:
            dig = planets_dict[pn].get('dignity', 0)
            if dig == 100: score += 10
            elif dig == 75: score += 5
            elif dig == -100: score -= 8
    
    # Length bonus
    score += len(loop) * 5
    
    return min(100, max(0, score))

def load_all_charts():
    """Load every chart from all saved JSON files"""
    all_charts = []
    dataset_dir = '/home/user/dataset'
    
    files_to_load = [
        'p1p9_absolute_final_rerank.json',
        'benchmark_10_domain.json',
        'benchmark_12_nexus_v2.json',
        'celebrity_112_nexus_v2.json',
        'varga_dasha_10.json',
    ]
    
    for fn in files_to_load:
        path = os.path.join(dataset_dir, fn)
        if not os.path.exists(path): continue
        try:
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                all_charts.extend(data)
            elif isinstance(data, dict):
                all_charts.extend(list(data.values()) if not any(isinstance(v,dict) and 'planets' in v for v in data.values()) else [v for v in data.values() if isinstance(v,dict) and 'planets' in v])
        except: pass
    
    # Billionaire charts
    path = os.path.join(dataset_dir, 'billionaire_noon_analysis.json')
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        if 'charts' in data:
            for c in data['charts']:
                c['_category'] = 'Billionaire'
                all_charts.append(c)
    
    # Deep research groups
    path = os.path.join(dataset_dir, 'deep_research_groups.json')
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        for gname, charts in data.items():
            for c in charts:
                c['_category'] = gname
                # Convert to planet format
                if 'planets' not in c:
                    c['planets'] = {}
                    if 'moon_nak' in c:
                        c['planets']['Moon'] = {'nakshatra': c['moon_nak'], 'sign': c.get('moon_sign','?')}
                all_charts.append(c)
    
    # Deduplicate by name
    seen_names = set()
    unique = []
    for c in all_charts:
        name = c.get('name', c.get('_name', ''))
        if name and name not in seen_names:
            seen_names.add(name)
            unique.append(c)
    
    return unique

# ============================================================
# MAIN
# ============================================================
print("="*100)
print("NEXUS v3.0 — 5-LOOP SHRINKHALA DISCOVERY ENGINE")
print("="*100)

all_charts = load_all_charts()
print(f"\nLoaded {len(all_charts)} unique charts\n")

# ============================================================
# 1. SHRINKHALA DETECTION ACROSS ALL CHARTS
# ============================================================
print("="*100)
print("PART 1: SHRINKHALA DETECTION — ALL CHARTS")
print("="*100)

shrinkhala_charts = []
loop_lengths = Counter()
all_loops_detail = []

for c in all_charts:
    name = c.get('name', c.get('_name', '?'))
    category = c.get('_category', c.get('category', c.get('_source', '?')))
    planets = c.get('planets', {})
    
    signs_of = get_sign_planet_data(planets)
    if not signs_of: continue
    
    loops = detect_all_shrinkhala(signs_of)
    
    for loop, length in loops:
        strength = compute_shrinkhala_strength(loop, planets)
        loop_lengths[length] += 1
        
        # Find what signs the planets are in
        loop_detail = []
        for pn in loop:
            sign = planets.get(pn, {}).get('sign', '?')
            dig = planets.get(pn, {}).get('dignity', 0)
            loop_detail.append(f"{pn}({sign},dig={dig})")
        
        all_loops_detail.append({
            'name': name,
            'category': category,
            'loop': ' → '.join(loop),
            'loop_detail': ' → '.join(loop_detail),
            'length': length,
            'strength': strength,
            'is_5loop': length == 5,
        })
        
        if length >= 5:
            shrinkhala_charts.append({
                'name': name,
                'category': category,
                'loop': loop,
                'length': length,
                'strength': strength,
                'detail': loop_detail,
            })

print(f"\nTotal Shrinkhala loops found: {len(all_loops_detail)}")
print(f"\nLoop length distribution:")
for length in sorted(loop_lengths.keys()):
    print(f"  {length}-Loop: {loop_lengths[length]} found")

if shrinkhala_charts:
    shrinkhala_charts.sort(key=lambda x: -x['strength'])
    print(f"\n{'='*60}")
    print(f"5+ LOOP SHRINKHALA CHARTS: {len(shrinkhala_charts)} found")
    print(f"{'='*60}")
    for s in shrinkhala_charts[:20]:
        print(f"\n  {s['name']} ({s['category']})")
        print(f"  Loop (len={s['length']}): {' → '.join(s['loop'])}")
        print(f"  Strength: {s['strength']}/100")
        for d in s['detail']:
            print(f"    {d}")
else:
    print(f"\n⚠️ ZERO 5-Loop Shrinkhala formations found in {len(all_charts)} charts.")
    print(f"   This yoga is either extremely rare or requires specific conditions")
    print(f"   that do not occur in real birth charts at the planet-sign level.")

# ============================================================
# 2. ROCKEFELLER CASE STUDY
# ============================================================
print(f"\n{'='*100}")
print("PART 2: JOHN D. ROCKEFELLER — CASE STUDY")
print(f"{'='*100}")

# Compute Rockefeller chart
def compute_noon(bday, place, lat, lon):
    dt = datetime.strptime(f"{bday}T12:00:00", "%Y-%m-%dT%H:%M:%S")
    dt = dt.replace(tzinfo=timezone(timedelta(hours=-5)))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
    ayan = swe.get_ayanamsa(jd)
    p = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]
        dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
        p[pn] = {"sign":sgn,"dignity":dig,"sidereal":round(sid,2)}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360
    p["Rahu"] = {"sign":SIGNS[int(rh//30)],"dignity":0}
    p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"dignity":0}
    return p

rockefeller = compute_noon("1839-07-08", "Richford, New York, USA", 42.36, -76.20)

print(f"\nJohn D. Rockefeller — Born July 8, 1839, Richford, NY")
print(f"Reference Chart (noon, no birth time — time-dependent features unavailable)\n")

print("Planetary Positions:")
for pn in P7:
    d = rockefeller[pn]
    tag = ""
    if d['dignity'] == 100: tag = "⭐ EXALTED"
    elif d['dignity'] == 75: tag = "✓ OWN"
    elif d['dignity'] == -100: tag = "⚠️ DEBILITATED"
    print(f"  {pn:<10} {d['sign']:<12} {d['sidereal']:>7.1f}°  {tag}")

# Shrinkhala check
signs_of = get_sign_planet_data(rockefeller)
loops = detect_all_shrinkhala(signs_of)

print(f"\n--- SHRINKHALA ANALYSIS ---")
if loops:
    print(f"Shrinkhala loops found: {len(loops)}")
    for loop, length in loops:
        strength = compute_shrinkhala_strength(loop, rockefeller)
        is_5 = "★★★ 5-LOOP ★★★" if length >= 5 else f"{length}-loop"
        print(f"\n  {is_5}")
        print(f"  Loop: {' → '.join(loop)}")
        print(f"  Strength: {strength}/100")
        for pn in loop:
            print(f"    {pn} in {rockefeller[pn]['sign']} (ruled by {SL[rockefeller[pn]['sign']]})")
else:
    print(f"  RESULT: No Shrinkhala loop detected.")
    print(f"  Planet sign → lord mapping:")
    for pn in P7:
        sign = rockefeller[pn]['sign']
        lord = SL[sign]
        arrow = "→ itself" if lord == pn else f"→ {lord}'s sign"
        print(f"    {pn} in {sign} ({arrow})")

# Parivartana check
print(f"\n--- PARIVARTANA (MUTUAL EXCHANGE) ---")
exchanges = []
for i, p1 in enumerate(P7):
    for p2 in P7[i+1:]:
        if SL[rockefeller[p1]['sign']] == p2 and SL[rockefeller[p2]['sign']] == p1:
            exchanges.append((p1, p2, rockefeller[p1]['sign'], rockefeller[p2]['sign']))
if exchanges:
    for ex in exchanges:
        print(f"  {ex[0]}↔{ex[1]}: {ex[0]} in {ex[2]}, {ex[1]} in {ex[3]}")
else:
    print(f"  No Parivartana found.")

# Dignity summary
print(f"\n--- DIGNITY SUMMARY ---")
ex = [pn for pn in P7 if rockefeller[pn]['dignity']==100]
own = [pn for pn in P7 if rockefeller[pn]['dignity']==75]
deb = [pn for pn in P7 if rockefeller[pn]['dignity']==-100]
print(f"  Exalted: {', '.join(ex) if ex else 'none'}")
print(f"  Own sign: {', '.join(own) if own else 'none'}")
print(f"  Debilitated: {', '.join(deb) if deb else 'none'}")

# Conjunctions
print(f"\n--- CONJUNCTIONS ---")
conj = []
for i, p1 in enumerate(P7):
    for p2 in P7[i+1:]:
        if rockefeller[p1]['sign'] == rockefeller[p2]['sign']:
            conj.append(f"{p1}+{p2} in {rockefeller[p1]['sign']}")
if conj:
    for c in conj: print(f"  {c}")
else:
    print(f"  No conjunctions")

# ============================================================
# 3. COMPARATIVE STATISTICS
# ============================================================
print(f"\n{'='*100}")
print("PART 3: COMPARATIVE STATISTICS — Shrinkhala by Outcome Group")
print(f"{'='*100}")

# Group charts by category
groups = defaultdict(list)
for c in all_charts:
    cat = c.get('_category', c.get('category', c.get('_source', 'Unknown')))
    groups[cat].append(c)

print(f"\n{'Group':<30} {'N':>5} {'Any Shrinkhala':>15} {'Rate':>8}")
print("-"*65)
for gname, charts in sorted(groups.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    n = len(charts)
    has_any = 0
    for c in charts:
        planets = c.get('planets', {})
        signs = get_sign_planet_data(planets)
        if signs:
            loops = detect_all_shrinkhala(signs)
            if loops: has_any += 1
    rate = has_any/n*100 if n > 0 else 0
    bar = '█' * int(rate/2)
    print(f"{gname:<30} {n:>5} {has_any:>5} ({rate:>5.1f}%) {bar}")

# ============================================================
# 4. HONEST FINDINGS
# ============================================================
print(f"\n{'='*100}")
print("PART 4: HONEST FINDINGS")
print(f"{'='*100}")

total_loops = len(all_loops_detail)
five_loops = len([l for l in all_loops_detail if l['is_5loop']])
total_charts = len(all_charts)

print(f"""
NEXUS v3.0 SHRINKHALA ANALYSIS — COMPLETE

Charts analyzed: {total_charts}
Total Shrinkhala loops found: {total_loops}
5-Loop Shrinkhala: {five_loops}

FINDING: {'5-Loop Shrinkhala detected in ' + str(five_loops) + ' charts' if five_loops > 0 else 'ZERO 5-Loop Shrinkhala detected across all ' + str(total_charts) + ' charts.'}

ROCKEFELLER: {'Shrinkhala present' if loops else 'No Shrinkhala detected.'}

INTERPRETATION:
- Shrinkhala at ANY loop length is rare ({total_loops} found in {total_charts} charts = {total_loops/total_charts*100:.1f}%).
- 5-Loop Shrinkhala appears essentially nonexistent in real birth data.
- This does NOT mean the yoga is invalid — it may require:
  a) Specific planetary configurations that are astronomically rare
  b) Inclusion of outer planets (Uranus/Neptune/Pluto) in the chain
  c) House-level analysis (not just sign-level)
  d) Rahu/Ketu as sign-rulers (some traditions assign them)
  
RECOMMENDATION:
- Expand Shrinkhala definition to include Rahu/Ketu as chain participants
- Test 2-4 loop Shrinkhala for outcome correlation instead
- Use 5-Loop as a theoretical ideal, not a practical detection target
""")

# Save
with open('/home/user/dataset/shrinkhala_v3_report.json','w') as f:
    json.dump({
        'total_charts': total_charts,
        'total_loops': total_loops,
        'five_loop_count': five_loops,
        'loop_length_distribution': dict(loop_lengths),
        'rockefeller': {
            'has_shrinkhala': len(loops) > 0,
            'loops': [{'loop': ' → '.join(l), 'length': ln} for l, ln in loops],
            'planets': {pn: rockefeller[pn] for pn in P7},
        },
        'group_rates': {g: {'n': len(c), 'shrinkhala': sum(1 for c2 in c if detect_all_shrinkhala(get_sign_planet_data(c2.get('planets',{}))))} 
                       for g,c in groups.items() if len(c) >= 3},
        'all_loops_summary': [{'name': l['name'], 'category': l['category'], 'length': l['length'], 'strength': l['strength']} 
                             for l in sorted(all_loops_detail, key=lambda x: -x['strength'])[:50]],
    }, f, indent=2)

print(f"Saved → /home/user/dataset/shrinkhala_v3_report.json")
