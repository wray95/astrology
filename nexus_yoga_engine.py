#!/usr/bin/env python3
"""
NEXUS VEDIC YOGA DETECTION ENGINE v2.0
— Detects ALL classical yogas across 13K+ charts
— Statistical validation
— P1-P7 comparison and reranking
"""
import json, os, math, time
from collections import defaultdict, Counter
from datetime import datetime, timedelta

# ============================================================
# CONSTANTS
# ============================================================
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
P7 = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

SIGN_LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
              "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
              "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}

DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
MULATRIKONA = {"Sun":"Leo","Moon":"Taurus","Mars":"Aries","Mercury":"Virgo",
               "Jupiter":"Sagittarius","Venus":"Libra","Saturn":"Aquarius"}

KENDRA_HOUSES = {1,4,7,10}
KONA_HOUSES = {1,5,9}
DUSTHANA_HOUSES = {6,8,12}
UPACHAYA_HOUSES = {3,6,10,11}

# ============================================================
# HELPERS
# ============================================================
def load_all_charts(dataset_dir="/home/user/dataset"):
    batches = sorted([f for f in os.listdir(dataset_dir) if f.startswith('famous_')])
    charts = []
    for bf in batches:
        with open(f'{dataset_dir}/{bf}') as f:
            charts.extend(json.load(f))
    return charts

def planet_sign(chart, p):
    return chart['planets'][p]['sign']

def planet_house(chart, p):
    return chart['planets'][p]['house']

def planet_dignity(chart, p):
    return chart['planets'][p]['dignity']

def planet_sidereal(chart, p):
    return chart['planets'][p]['sidereal']

def d9_sign(chart, p):
    return chart['d9'][p]['sign']

def d9_dignity(chart, p):
    return chart['d9'][p]['dignity']

def is_exalted(chart, p):
    return planet_dignity(chart, p) == 100 or (p in EXALT and planet_sign(chart, p) == EXALT[p])

def is_debilitated(chart, p):
    return planet_dignity(chart, p) == -100 or (p in DEBIL and planet_sign(chart, p) == DEBIL[p])

def is_own(chart, p):
    return planet_dignity(chart, p) == 75 or (p in OWN and planet_sign(chart, p) in OWN[p])

def house_lord(chart, house):
    """Return planet that rules the sign in a given house (whole-sign)."""
    asc_idx = int(chart['ascendant']['sidereal'] // 30)
    house_sign_idx = (asc_idx + house - 1) % 12
    house_sign = SIGNS[house_sign_idx]
    lord_name = SIGN_LORDS[house_sign]
    return lord_name

def planets_in_house(chart, house):
    return [p for p in P7 if planet_house(chart, p) == house]

def mutual_aspect(chart, p1, p2):
    """Check if two planets are 7 houses apart (mutual aspect)."""
    h1, h2 = planet_house(chart, p1), planet_house(chart, p2)
    return abs(h1 - h2) in {1, 7} or (min(h1,h2) == 1 and max(h1,h2) == 7)

def conjunct(chart, p1, p2):
    return planet_house(chart, p1) == planet_house(chart, p2)

# ============================================================
# YOGA DETECTION ENGINE
# ============================================================
class YogaDetector:
    
    @staticmethod
    def detect_all(chart):
        yogas = {}
        for method_name in dir(YogaDetector):
            if method_name.startswith('_yoga_'):
                name = method_name[6:]
                result = getattr(YogaDetector, method_name)(chart)
                if result:
                    yogas[name] = result
        return yogas
    
    # ======== RAJA YOGAS ========
    
    @staticmethod
    def _yoga_dka(chart):
        """Dharma Karma Adhipati: 9L and 10L conjunct or mutual aspect."""
        lords = {h: house_lord(chart, h) for h in range(1,13)}
        l9, l10 = lords[9], lords[10]
        if l9 != l10 and (conjunct(chart, l9, l10) or mutual_aspect(chart, l9, l10)):
            score = 60 + planet_dignity(chart, l9)//2 + planet_dignity(chart, l10)//2
            return {"planets":[l9,l10],"score":score,"active":True}
        return None
    
    @staticmethod
    def _yoga_gajakesari(chart):
        """Gajakesari: Jupiter in Kendra from Moon."""
        if 'Jupiter' not in chart['planets']: return None
        moon_house = planet_house(chart, 'Moon')
        jup_house = planet_house(chart, 'Jupiter')
        kendras_from_moon = {(moon_house + k - 1) % 12 + 1 for k in [1,4,7,10]}
        if jup_house in kendras_from_moon:
            score = 80 + planet_dignity(chart, 'Jupiter')//3
            return {"score":score,"active":True}
        return None
    
    @staticmethod
    def _yoga_mahapurusha(chart):
        """Panch Mahapurusha: 5 types based on planet in own/exalted in Kendra."""
        results = []
        for p, yoga_name in [("Mercury","Bhadra"),("Jupiter","Hamsa"),
                              ("Mars","Ruchaka"),("Venus","Malavaya"),("Saturn","Sasa")]:
            if p not in chart['planets']: continue
            h = planet_house(chart, p)
            if h in KENDRA_HOUSES and (is_own(chart, p) or is_exalted(chart, p)):
                score = 90 + planet_dignity(chart, p)//3
                # Retrogade bonus
                results.append({"yoga":yoga_name,"planet":p,"house":h,"score":score})
        return results if results else None
    
    @staticmethod
    def _yoga_neecha_bhanga(chart):
        """Neecha Bhanga Raja Yoga: debilitated planet with cancellation."""
        results = []
        for p in P7:
            if p not in chart['planets']: continue
            if not is_debilitated(chart, p): continue
            
            conditions = []
            # C1: Lord of debilitation sign in Kendra
            deb_sign = planet_sign(chart, p)
            lord = SIGN_LORDS[deb_sign]
            if lord in chart['planets'] and planet_house(chart, lord) in KENDRA_HOUSES:
                conditions.append("C1_deb_lord_kendra")
            # C2: Planet exalted in that sign is in Kendra
            for ep, es in EXALT.items():
                if es == deb_sign and ep in chart['planets']:
                    if planet_house(chart, ep) in KENDRA_HOUSES:
                        conditions.append("C2_exalted_in_kendra")
            # C3: Depositor mutual aspect with debilitated
            if lord in chart['planets'] and mutual_aspect(chart, p, lord):
                conditions.append("C3_depositor_aspect")
            # C4: Exalted planet conjunct with debilitated
            for ep, es in EXALT.items():
                if es == deb_sign and ep in chart['planets'] and ep != p:
                    if conjunct(chart, p, ep):
                        conditions.append("C4_exalted_conjunct")
            # C5: Debilitated itself in Kendra
            if planet_house(chart, p) in KENDRA_HOUSES:
                conditions.append("C5_deb_in_kendra")
            # C6: Retrograde (check if JD suggests retro)
            # C7: Conjunct exalted
            for ep in P7:
                if ep in chart['planets'] and ep != p and is_exalted(chart, ep):
                    if conjunct(chart, p, ep):
                        conditions.append("C7_conjunct_exalted")
                        break
            
            count = len(set(conditions))
            if count >= 1:
                score = 60 + count * 40  # 1 cond = 100, 2 cond = 140, etc.
                d9_exalted = d9_dignity(chart, p) == 100
                results.append({
                    "planet":p,"sign":deb_sign,"conditions":conditions,
                    "count":count,"score":min(score, 200),
                    "d9_exalted":d9_exalted,"full_nbry":count >= 2
                })
        return results if results else None
    
    @staticmethod
    def _yoga_vipareeta_raja(chart):
        """Vipareeta Raja: dusthana lord in dusthana."""
        results = []
        for h in DUSTHANA_HOUSES:
            lord = house_lord(chart, h)
            if lord in chart['planets'] and planet_house(chart, lord) in DUSTHANA_HOUSES:
                results.append({"house":h,"lord":lord,"placed_in":planet_house(chart, lord)})
        return results if results else None
    
    # ======== DHANA YOGAS ========
    
    @staticmethod
    def _yoga_dhana(chart):
        """Dhana Yoga: 1L-2L, 1L-11L, 2L-11L, or 5L-9L connection."""
        lords = {h: house_lord(chart, h) for h in range(1,13)}
        pairs = [(1,2),(1,11),(2,11),(5,9)]
        results = []
        for h1, h2 in pairs:
            l1, l2 = lords[h1], lords[h2]
            if l1 != l2 and l1 in chart['planets'] and l2 in chart['planets']:
                if conjunct(chart, l1, l2) or mutual_aspect(chart, l1, l2):
                    score = max(planet_dignity(chart, l1), planet_dignity(chart, l2))
                    results.append({"houses":f"{h1}L-{h2}L","planets":[l1,l2],"score":score+50})
        return results if results else None
    
    @staticmethod
    def _yoga_lakshmi(chart):
        """Lakshmi: 9L + Venus in own/exalted in Kendra/Kona + strong Lagna lord."""
        lords = {h: house_lord(chart, h) for h in range(1,13)}
        l9 = lords[9]
        l1 = lords[1]
        score = 0
        if l9 in chart['planets'] and planet_house(chart, l9) in KENDRA_HOUSES | KONA_HOUSES:
            score += 30
        if 'Venus' in chart['planets'] and is_exalted(chart, 'Venus'):
            score += 50
        if 'Venus' in chart['planets'] and is_own(chart, 'Venus'):
            score += 30
        if l1 in chart['planets'] and planet_dignity(chart, l1) >= 75:
            score += 30
        if score >= 60:
            return {"score":score,"active":True}
        return None
    
    # ======== MOON YOGAS ========
    
    @staticmethod
    def _yoga_sunapha(chart):
        """Sunapha: planets (other than Moon/Sun) in 2nd from Moon."""
        moon_h = planet_house(chart, 'Moon')
        h2 = (moon_h + 1) % 12 + 1
        planets = [p for p in P7 if p not in ('Sun','Moon') and planet_house(chart, p) == h2]
        return {"planets":planets,"active":len(planets) > 0} if planets else None
    
    @staticmethod
    def _yoga_anapha(chart):
        """Anapha: planets (other than Moon/Sun) in 12th from Moon."""
        moon_h = planet_house(chart, 'Moon')
        h12 = (moon_h + 11) % 12 + 1
        planets = [p for p in P7 if p not in ('Sun','Moon') and planet_house(chart, p) == h12]
        return {"planets":planets,"active":len(planets) > 0} if planets else None
    
    @staticmethod
    def _yoga_durudhara(chart):
        """Durudhara: planets in BOTH 2nd and 12th from Moon."""
        s = YogaDetector._yoga_sunapha(chart)
        a = YogaDetector._yoga_anapha(chart)
        if s and a and s['active'] and a['active']:
            return {"active":True}
        return None
    
    @staticmethod
    def _yoga_kemadruma(chart):
        """Kemadruma: NO planets in 2nd/12th from Moon (except Sun)."""
        s = YogaDetector._yoga_sunapha(chart)
        a = YogaDetector._yoga_anapha(chart)
        no_sunapha = not s or not s['active']
        no_anapha = not a or not a['active']
        if no_sunapha and no_anapha:
            # Also check kendra from Moon for cancellation
            moon_h = planet_house(chart, 'Moon')
            cancel = any(planet_house(chart, p) in {(moon_h+k-1)%12+1 for k in [1,4,7,10]}
                        for p in P7 if p in chart['planets'] and p != 'Moon')
            return {"active":True,"cancelled":cancel}
        return None
    
    # ======== PLANETARY COMBINATION YOGAS ========
    
    @staticmethod
    def _yoga_budha_aditya(chart):
        """Budha Aditya: Sun + Mercury conjunct."""
        if 'Sun' in chart['planets'] and 'Mercury' in chart['planets']:
            if conjunct(chart, 'Sun', 'Mercury'):
                score = 60 + (planet_dignity(chart,'Sun') + planet_dignity(chart,'Mercury'))//4
                return {"score":score,"active":True}
        return None
    
    @staticmethod
    def _yoga_chandra_mangala(chart):
        """Chandra Mangala: Moon + Mars conjunct or mutual aspect."""
        if conjunct(chart, 'Moon', 'Mars') or mutual_aspect(chart, 'Moon', 'Mars'):
            return {"active":True}
        return None
    
    @staticmethod
    def _yoga_saraswati(chart):
        """Saraswati: Jupiter + Mercury + Venus in Kendra/Kona from Lagna, strong."""
        count = 0
        for p in ['Jupiter','Mercury','Venus']:
            if p in chart['planets'] and planet_house(chart, p) in KENDRA_HOUSES | KONA_HOUSES:
                if planet_dignity(chart, p) >= 0:
                    count += 1
        if count >= 2:
            return {"count":count,"active":True}
        return None
    
    # ======== PARIVARTANA (EXCHANGE) YOGAS ========
    
    @staticmethod
    def _yoga_parivartana(chart):
        """Detect all sign exchanges (2+ planet loops)."""
        # Build sign→planet map
        sign_planets = defaultdict(list)
        for p in P7:
            if p in chart['planets']:
                sign_planets[planet_sign(chart, p)].append(p)
        
        exchanges = []
        for s1, p1_list in sign_planets.items():
            for p1 in p1_list:
                lord1 = SIGN_LORDS[s1]
                if lord1 in chart['planets']:
                    lord1_sign = planet_sign(chart, lord1)
                    lord1_lord = SIGN_LORDS[lord1_sign]
                    if lord1_lord == p1 and lord1 != p1:
                        # Two-planet exchange
                        exchanges.append({"planets":[p1,lord1],"type":"2-planet"})
        
        # Deduplicate
        seen = set()
        unique = []
        for e in exchanges:
            key = tuple(sorted(e['planets']))
            if key not in seen:
                seen.add(key)
                # Classify
                h1, h2 = planet_house(chart, e['planets'][0]), planet_house(chart, e['planets'][1])
                lords = {h: house_lord(chart, h) for h in range(1,13)}
                is_kendra_kona = (h1 in KENDRA_HOUSES and h2 in KONA_HOUSES) or (h2 in KENDRA_HOUSES and h1 in KONA_HOUSES)
                has_dusthana = h1 in DUSTHANA_HOUSES or h2 in DUSTHANA_HOUSES
                
                e['houses'] = [h1, h2]
                e['maha'] = is_kendra_kona and not has_dusthana
                e['dainya'] = has_dusthana
                e['kahala'] = planet_house(chart, house_lord(chart, 1)) in KENDRA_HOUSES
                e['score'] = 80 if is_kendra_kona else 50
                unique.append(e)
        
        return unique if unique else None
    
    # ======== SHRINKHALA ========
    
    @staticmethod
    def _yoga_shrinkhala(chart):
        """Shrinkhala: N consecutive planets within span threshold."""
        sorted_p = sorted([(p, planet_sidereal(chart,p)) for p in P7 if p in chart['planets']],
                         key=lambda x: x[1])
        for count, thresh in [(4,75),(5,90),(7,120)]:
            for i in range(len(sorted_p) - count + 1):
                subset = sorted_p[i:i+count]
                span = (subset[-1][1] - subset[0][1]) % 360
                if span <= thresh:
                    return {"active":True,"planets":[s[0] for s in subset],"span":round(span,2),"count":count}
        return None
    
    # ======== SANYASA / MOKSHA ========
    
    @staticmethod
    def _yoga_sanyasa(chart):
        """Sanyasa indicators: 4+ planets in one house, Saturn + Ketu connection."""
        house_counts = Counter(planet_house(chart, p) for p in P7 if p in chart['planets'])
        indicators = []
        if max(house_counts.values()) >= 4:
            indicators.append("4_planets_one_house")
        if 'Saturn' in chart['planets'] and 'Ketu' in chart['planets']:
            if conjunct(chart, 'Saturn', 'Ketu') or mutual_aspect(chart, 'Saturn', 'Ketu'):
                indicators.append("saturn_ketu_connected")
        if 'Moon' in chart['planets'] and 'Saturn' in chart['planets']:
            if mutual_aspect(chart, 'Moon', 'Saturn'):
                indicators.append("moon_saturn_aspect")
        if indicators:
            return {"indicators":indicators,"active":len(indicators)>=2}
        return None
    
    # ======== NEXUS COMPOSITE ========
    
    @staticmethod
    def compute_nexus_score(chart):
        """Composite strength score: D1 dignity + D9 dignity + yoga bonus + dignity"""
        d1_avg = chart['d1_avg_dignity']
        d9_avg = chart['d9_avg_dignity']
        
        # Count high-value yogas
        yogas = chart.get('_yogas', {})
        yoga_bonus = 0
        
        # Mahapurusha bonus
        mp = yogas.get('mahapurusha')
        if mp and len(mp) > 0:
            yoga_bonus += 30 * len(mp)
        
        # Neecha Bhanga bonus
        nb = yogas.get('neecha_bhanga')
        if nb:
            yoga_bonus += sum(20 for n in nb if n.get('full_nbry'))
            yoga_bonus += sum(10 for n in nb if not n.get('full_nbry'))
        
        # DKA
        if yogas.get('dka'):
            yoga_bonus += 25
        
        # Gajakesari
        if yogas.get('gajakesari'):
            yoga_bonus += 20
        
        # Parivartana
        pv = yogas.get('parivartana')
        if pv and len(pv) > 0:
            yoga_bonus += 15 * len([e for e in pv if e.get('maha')])
        
        # Lakshmi
        if yogas.get('lakshmi'):
            yoga_bonus += 25
        
        # Dhana
        dh = yogas.get('dhana')
        if dh and len(dh) > 0:
            yoga_bonus += 10 * len(dh)
        
        # Debilitation penalty
        deb_penalty = 0
        for p in P7:
            if p in chart['planets'] and is_debilitated(chart, p):
                # Only penalize if NO neecha bhanga
                nb_planets = [n['planet'] for n in (nb or [])]
                if p not in nb_planets:
                    deb_penalty -= 30
        
        nexus = d1_avg * 0.5 + d9_avg * 0.3 + yoga_bonus * 0.2 + deb_penalty * 0.3
        return round(max(0, nexus + 25), 1)


# ============================================================
# BATCH PROCESSING
# ============================================================
def process_all(charts):
    """Add yoga detection to all charts, compute stats."""
    yoga_counts = defaultdict(int)
    yoga_people = defaultdict(list)
    
    for idx, chart in enumerate(charts):
        yogas = YogaDetector.detect_all(chart)
        chart['_yogas'] = yogas
        chart['_nexus_score'] = YogaDetector.compute_nexus_score(chart)
        
        for yoga_name in yogas:
            yoga_counts[yoga_name] += 1
            yoga_people[yoga_name].append(chart['name'])
        
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx+1:,}/{len(charts):,}")
    
    return yoga_counts, yoga_people


# ============================================================
# P1-P7 COMPARISON
# ============================================================
P7_CHARTS = [
    {"id":"P1","name":"Polgahawela Bappa","born":"1962-05-27","ref_md":"Ketu","ref_ad":"Jupiter"},
    {"id":"P2","name":"Upulakshi","born":"1997-03-14","ref_md":"Rahu","ref_ad":"Jupiter","warn":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","born":"1995-08-07","ref_md":"Moon","ref_ad":"Venus"},
    {"id":"P4","name":"Niromi","born":"1967-04-25","ref_md":"Ketu","ref_ad":"Saturn"},
    {"id":"P5","name":"Senath","born":"2001-05-14","ref_md":"Rahu","ref_ad":"Saturn"},
    {"id":"P6","name":"Dewli","born":"2005-10-08","ref_md":"Ketu","ref_ad":"Jupiter"},
    {"id":"P7","name":"Sineth","born":"2005-04-05","ref_md":"Saturn","ref_ad":"Jupiter","warn":"LAGNA UNKNOWN"},
]

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    os.makedirs("/home/user/database", exist_ok=True)
    os.makedirs("/home/user/analysis", exist_ok=True)
    
    t0 = time.time()
    print(f"=== NEXUS VEDIC YOGA DETECTION ENGINE ===")
    print(f"Loading charts...")
    charts = load_all_charts()
    print(f"Loaded {len(charts):,} charts")
    
    print(f"Detecting yogas...")
    yoga_counts, yoga_people = process_all(charts)
    
    # Statistics
    total = len(charts)
    
    # Yoga frequency stats
    yoga_stats = {}
    for name, count in sorted(yoga_counts.items(), key=lambda x: -x[1]):
        rate = count / total * 100
        people_sample = yoga_people[name][:5]
        yoga_stats[name] = {
            "count": count,
            "frequency_pct": round(rate, 2),
            "sample_people": people_sample
        }
    
    # Neecha Bhanga stats
    nb_charts = [c for c in charts if c['_yogas'].get('neecha_bhanga')]
    nb_full = [c for c in nb_charts if any(n.get('full_nbry') for n in c['_yogas']['neecha_bhanga'])]
    
    # Mahapurusha stats
    mp_charts = [c for c in charts if c['_yogas'].get('mahapurusha')]
    
    # Nexus score distribution
    nexus_scores = [c['_nexus_score'] for c in charts]
    nexus_sorted = sorted(nexus_scores)
    p25, p50, p75, p90 = (nexus_sorted[int(total*0.25)],
                          nexus_sorted[int(total*0.50)],
                          nexus_sorted[int(total*0.75)],
                          nexus_sorted[int(total*0.90)])
    
    nexus_stats = {
        "min": round(min(nexus_scores), 1),
        "p25": round(p25, 1),
        "median": round(p50, 1),
        "p75": round(p75, 1),
        "p90": round(p90, 1),
        "max": round(max(nexus_scores), 1),
        "top_10": sorted([(c['name'], c['_nexus_score']) for c in charts],
                        key=lambda x: -x[1])[:10]
    }
    
    # Save yoga stats
    with open("/home/user/analysis/yoga_statistics.json", "w") as f:
        json.dump({"yoga_frequencies": yoga_stats, "total_charts": total}, f, indent=2)
    
    with open("/home/user/analysis/neecha_bhanga_results.json", "w") as f:
        nb_data = {
            "total_with_debilitation": len(nb_charts),
            "total_with_full_nbry": len(nb_full),
            "pct_full_nbry": round(len(nb_full)/total*100, 2),
            "sample": [{"name":c['name'],"neecha_bhanga":c['_yogas']['neecha_bhanga']}
                       for c in nb_full[:20]]
        }
        json.dump(nb_data, f, indent=2)
    
    with open("/home/user/analysis/nexus_comparison.json", "w") as f:
        json.dump(nexus_stats, f, indent=2)
    
    # P1-P7 comparison (using chart_houses.json data)
    # Build P1-P7 from the real P1-P7 charts we computed earlier
    user_comparison = []
    
    # Find P1-P7 in our dataset if they exist, or load from reference
    p7_names = {"Polgahawela Bappa":"P1","Upulakshi":"P2","Senith":"P3",
                "Niromi":"P4","Senath":"P5","Dewli":"P6","Sineth":"P7"}
    
    p7_charts = [c for c in charts if c['name'] in p7_names]
    
    for pc in p7_charts:
        pid = p7_names.get(pc['name'], "?")
        yogas = pc['_yogas']
        nexus = pc['_nexus_score']
        
        # Find percentile
        better_than = sum(1 for s in nexus_scores if s < nexus)
        percentile = round(better_than / total * 100, 1)
        
        # Key yogas
        key_yogas = []
        for yname in ['mahapurusha','neecha_bhanga','dka','gajakesari','dhana',
                       'budha_aditya','lakshmi','parivartana','vipareeta_raja']:
            y = yogas.get(yname)
            if y:
                if isinstance(y, list) and len(y) > 0:
                    key_yogas.append(f"{yname}:{len(y)}")
                elif isinstance(y, dict) and y.get('active'):
                    key_yogas.append(yname)
                elif isinstance(y, dict) and not y.get('active') and yname == 'sanyasa':
                    pass
        
        entry = {
            "id": pid,
            "name": pc['name'],
            "nexus_score": nexus,
            "percentile": percentile,
            "key_yogas": key_yogas,
            "d1_dignity": pc['d1_avg_dignity'],
            "d9_dignity": pc['d9_avg_dignity'],
        }
        user_comparison.append(entry)
    
    user_comparison.sort(key=lambda x: x['nexus_score'], reverse=True)
    
    with open("/home/user/analysis/user_chart_comparison.json", "w") as f:
        json.dump(user_comparison, f, indent=2)
    
    # ============================================================
    # SUMMARY
    # ============================================================
    elapsed = time.time() - t0
    
    # Reranking output
    print(f"\n{'='*70}")
    print(f"NEXUS YOGA ENGINE — COMPLETE")
    print(f"{'='*70}")
    print(f"Charts processed: {total:,}")
    print(f"Yoga types detected: {len(yoga_counts)}")
    print(f"Time: {elapsed:.1f}s")
    
    print(f"\n=== YOGA FREQUENCIES (Top 15) ===")
    for name, count in sorted(yoga_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {name:<25s} {count:>6,d} ({count/total*100:5.1f}%)")
    
    print(f"\n=== NEECHA BHANGA ===")
    print(f"  Charts with debilitated planets: {len(nb_charts):,} ({len(nb_charts)/total*100:.1f}%)")
    print(f"  Full NBRY (2+ conditions):      {len(nb_full):,} ({len(nb_full)/total*100:.2f}%)")
    
    print(f"\n=== NEXUS SCORE DISTRIBUTION ===")
    print(f"  Min: {nexus_stats['min']}, P25: {nexus_stats['p25']}, Median: {nexus_stats['median']}")
    print(f"  P75: {nexus_stats['p75']}, P90: {nexus_stats['p90']}, Max: {nexus_stats['max']}")
    
    print(f"\n=== P1-P7 NEXUS RERANK ===")
    for rank, entry in enumerate(user_comparison, 1):
        pid = entry['id']
        nexus = entry['nexus_score']
        pct = entry['percentile']
        yogas = entry['key_yogas']
        print(f"  {rank}. {pid:4s} {entry['name']:22s} NEXUS={nexus:.0f} (>{pct}%) | {', '.join(yogas)}")
    
    # Save full charts with yogas (sample)
    sample_size = min(500, len(charts))
    sample = charts[:sample_size]
    with open("/home/user/database/charts_with_yogas_sample.json", "w") as f:
        json.dump(sample, f, indent=1)
    
    print(f"\nOutputs written to /home/user/database/ and /home/user/analysis/")
