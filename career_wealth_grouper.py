#!/usr/bin/env python3
"""
CAREER & WEALTH PLANET-SIGN GROUPER
~1,300 charts. Maps every planet-sign → career group + wealth outcome.
Ranks strongest associations with effect sizes.
"""
import json, os, math
from collections import defaultdict, Counter

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']

# Load all data
def load_all():
    charts = []
    data_dir = 'dataset'
    for fn in os.listdir(data_dir):
        if not fn.endswith('.json'): continue
        path = os.path.join(data_dir, fn)
        try:
            with open(path) as f: data = json.load(f)
            def extract(items):
                if isinstance(items, list):
                    for r in items:
                        if isinstance(r, dict):
                            name = r.get('name','')
                            planets = r.get('planets',{})
                            cat = r.get('_group','') or r.get('_category','') or r.get('category','')
                            outcomes = r.get('outcomes',{})
                            if name and planets:
                                charts.append({'name':name,'planets':planets,'category':cat,'outcomes':outcomes})
                elif isinstance(items, dict):
                    if 'charts' in items:
                        for r in items['charts']:
                            if isinstance(r, dict):
                                charts.append({'name':r.get('name',''),'planets':r.get('planets',{}),'category':r.get('_category','')})
                    else:
                        for k,v in items.items():
                            if isinstance(v, list):
                                for r in v:
                                    if isinstance(r, dict):
                                        charts.append({'name':r.get('name',''),'planets':r.get('planets',{}),'category':k})
            extract(data)
        except: pass
    
    # Deduplicate
    seen = set(); unique = []
    for c in charts:
        nm = c['name']
        if nm and nm not in seen: seen.add(nm); unique.append(c)
    return unique

charts = load_all()
print(f"Loaded {len(charts)} unique charts")

# ============================================================
# CAREER CLASSIFICATION
# ============================================================
CAREER_KEYWORDS = {
    'Business/Finance': ['billionaire','tycoon','philanthropist','investor','venture','entrepreneur','ceo','executive','founder','business','finance','industrialist','trader','banker'],
    'Science/Medicine': ['scientist','physicist','mathematician','physician','doctor','chemist','biologist','astronomer','medical','nobel','polymath','researcher','inventor','engineer'],
    'Technology': ['tech founder','programmer','computer','software','coder','hacker','developer','cryptographer'],
    'Arts/Entertainment': ['actor','actress','musician','composer','writer','poet','artist','painter','sculptor','director','film','cinema','singer','dancer','entertainer','playwright','novelist','author'],
    'Politics/Military': ['dictator','president','politician','king','emperor','ruler','general','commander','warrior','military','admiral','soldier','statesman','governor','senator','prime minister','leader','revolutionary','president'],
    'Athletics': ['athlete','olympic','runner','swimmer','boxer','football','basketball','tennis','golf','gymnast','wrestler','chess','sprinter','marathon','sport'],
    'Criminal': ['criminal','mafia','drug lord','serial killer','fraud','terrorist','assassin','outlaw','gangster','hitman','pirate','thief','convict','bankruptcy'],
    'Humanitarian/Spiritual': ['activist','humanitarian','saint','guru','philosopher','religious','spiritual','monk','priest','prophet','sage','martyr','reformer','suffragist'],
    'Exploration/Aviation': ['explorer','astronaut','aviator','pilot','cosmonaut','navigator','adventurer','mountaineer'],
}

def classify_career(chart):
    cat = chart.get('category','').lower()
    name = chart.get('name','').lower()
    text = cat + ' ' + name
    
    scores = {}
    for career, keywords in CAREER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0: scores[career] = score
    
    if scores:
        return max(scores, key=scores.get)
    
    # Check outcomes
    outcomes = chart.get('outcomes',{})
    wealth = outcomes.get('wealth_status','')
    if wealth == 'Rich': return 'Business/Finance'
    social = outcomes.get('social_impact','')
    if social == 'Bad': return 'Criminal'
    if social == 'Good': return 'Humanitarian/Spiritual'
    
    return 'Other'

# Classify all
career_groups = defaultdict(list)
for c in charts:
    career = classify_career(c)
    c['career'] = career
    career_groups[career].append(c)

print(f"\nCareer groups:")
for g, items in sorted(career_groups.items(), key=lambda x: -len(x[1])):
    print(f"  {g:<30} {len(items):>5}")

# ============================================================
# PLANET-SIGN → CAREER CROSS-TABULATION
# ============================================================
print(f"\n{'='*100}")
print("PLANET-SIGN → CAREER ASSOCIATIONS (ranked by overrepresentation)")
print(f"{'='*100}")

# For each planet-sign → career pair, compute rate vs baseline
all_results = []

for planet in PLANETS:
    for sign in SIGNS:
        # Charts with this planet-sign
        has_ps = [c for c in charts if c['planets'].get(planet,{}).get('sign') == sign]
        n_ps = len(has_ps)
        if n_ps < 5: continue
        
        for career, items in career_groups.items():
            if len(items) < 5: continue
            
            # How many with this planet-sign are in this career?
            in_career = sum(1 for c in has_ps if c.get('career') == career)
            rate_in = in_career / n_ps * 100
            
            # Baseline rate of this career
            rate_base = len(items) / len(charts) * 100
            
            # Effect
            effect = rate_in - rate_base
            ratio = rate_in / rate_base if rate_base > 0 else 0
            
            if ratio > 1.5 and in_career >= 3:
                all_results.append({
                    'planet': planet,
                    'sign': sign,
                    'career': career,
                    'n_total': n_ps,
                    'n_career': in_career,
                    'rate_in': rate_in,
                    'rate_base': rate_base,
                    'effect': effect,
                    'ratio': ratio,
                })

all_results.sort(key=lambda x: -x['ratio'])

print(f"\n{'Planet':<8} {'Sign':<12} {'Career':<25} {'N':>5} {'Rate':>7} {'Base':>7} {'Ratio':>6} {'Effect'}")
print("-"*85)
for r in all_results[:40]:
    bar = '█' * min(int(r['effect']), 20)
    print(f"{r['planet']:<8} {r['sign']:<12} {r['career']:<25} {r['n_career']:>5} {r['rate_in']:>6.1f}% {r['rate_base']:>6.1f}% {r['ratio']:>5.1f}x {bar}")

# ============================================================
# PLANET-SIGN → WEALTH
# ============================================================
print(f"\n{'='*100}")
print("PLANET-SIGN → WEALTH ASSOCIATIONS")
print(f"{'='*100}")

# Identify rich vs poor
rich_charts = [c for c in charts if c.get('outcomes',{}).get('wealth_status') == 'Rich' or 
               any(w in c.get('category','').lower() for w in ['billionaire','tycoon','philanthropist'])]
poor_charts = [c for c in charts if c.get('outcomes',{}).get('wealth_status') == 'Poor']

# Also use named billionaires from our master list
billionaire_names = {c['name'].lower() for c in charts if any(w in c.get('category','').lower() for w in ['billionaire'])}
billionaire_names.update({'john d. rockefeller','andrew carnegie','j.p. morgan','cornelius vanderbilt','henry ford',
                          'thomas edison','oprah winfrey','steve jobs','bill gates','jeff bezos','elon musk',
                          'warren buffett','mark zuckerberg','larry ellison','larry page','sergey brin',
                          'bernard arnault','amancio ortega','carlos slim','mukesh ambani','gautam adani',
                          'richard branson','jack ma','masayoshi son','peter thiel','marc andreessen',
                          'ray dalio','george soros','carl icahn','howard hughes','walt disney',
                          'michael bloomberg','phil knight','ray kroc','sam walton','estee lauder',
                          'coco chanel','madam c.j. walker','jensen huang'})

rich_all = [c for c in charts if c['name'].lower() in billionaire_names]
rich_all += [c for c in charts if c.get('outcomes',{}).get('wealth_status') == 'Rich']

# Deduplicate rich
seen_rich = set()
rich_final = []
for c in rich_all:
    nm = c['name']
    if nm not in seen_rich: seen_rich.add(nm); rich_final.append(c)

n_rich = len(rich_final)
n_all = len(charts)
base_rich = n_rich / n_all * 100

print(f"Rich: {n_rich}/{n_all} ({base_rich:.1f}%)")

wealth_results = []
for planet in PLANETS:
    for sign in SIGNS:
        has_ps = [c for c in charts if c['planets'].get(planet,{}).get('sign') == sign]
        n_ps = len(has_ps)
        if n_ps < 5: continue
        
        rich_count = sum(1 for c in has_ps if c['name'].lower() in {r['name'].lower() for r in rich_final})
        rate_rich = rich_count / n_ps * 100
        ratio = rate_rich / base_rich if base_rich > 0 else 0
        
        if ratio > 1.3 and rich_count >= 2:
            wealth_results.append({
                'planet': planet, 'sign': sign,
                'n_total': n_ps, 'n_rich': rich_count,
                'rate': rate_rich, 'ratio': ratio,
            })

wealth_results.sort(key=lambda x: -x['ratio'])
print(f"\n{'Planet':<8} {'Sign':<12} {'Rich':>5} {'Total':>6} {'Rate':>7} {'Ratio':>6}")
print("-"*55)
for r in wealth_results[:25]:
    print(f"{r['planet']:<8} {r['sign']:<12} {r['n_rich']:>5} {r['n_total']:>6} {r['rate']:>6.1f}% {r['ratio']:>5.1f}x")

# ============================================================
# CAREER MATRIX SUMMARY
# ============================================================
print(f"\n{'='*100}")
print("CAREER × PLANET MATRIX — Most Discriminating Planet per Career")
print(f"{'='*100}")

for career in sorted(career_groups.keys(), key=lambda x: -len(career_groups[x])):
    if len(career_groups[career]) < 5: continue
    items = career_groups[career]
    n = len(items)
    
    # Which planet signs are most overrepresented?
    scores = []
    for planet in PLANETS:
        for sign in SIGNS:
            in_career = sum(1 for c in items if c['planets'].get(planet,{}).get('sign') == sign)
            in_all = sum(1 for c in charts if c['planets'].get(planet,{}).get('sign') == sign)
            if in_all < 5: continue
            rate_career = in_career / n * 100
            rate_all = in_all / len(charts) * 100
            ratio = rate_career / rate_all if rate_all > 0 else 0
            if ratio > 1.3 and in_career >= 2:
                scores.append((planet, sign, ratio, in_career))
    
    scores.sort(key=lambda x: -x[2])
    top = scores[:3]
    if top:
        print(f"\n{career} (n={n}):")
        for planet, sign, ratio, count in top:
            print(f"  {planet} in {sign:<12} {ratio:.1f}x overrepresented ({count}/{n})")

# ============================================================
# SAVE
# ============================================================
out = {
    'total_charts': len(charts),
    'career_groups': {g: len(items) for g, items in career_groups.items()},
    'top_planet_sign_career': [{'planet':r['planet'],'sign':r['sign'],'career':r['career'],'ratio':round(r['ratio'],1),'n':r['n_career']} for r in all_results[:50]],
    'top_planet_sign_wealth': [{'planet':r['planet'],'sign':r['sign'],'ratio':round(r['ratio'],1),'n_rich':r['n_rich']} for r in wealth_results[:30]],
}
with open('dataset/career_wealth_map.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved → dataset/career_wealth_map.json")
