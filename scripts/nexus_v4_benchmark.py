#!/usr/bin/env python3
"""
NEXUS BENCHMARK PIPELINE v4.0
20,000-chart scale framework — Full point scoring + Shrinkhala 2-5 + NBRY + D9
Runs across all ~878 existing charts with outcome labels where available
"""
import swisseph as swe, json, math, os
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN_SIGNS = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
FRIENDS = {'Sun':['Moon','Mars','Jupiter'],'Moon':['Sun','Mercury'],'Mars':['Sun','Moon','Jupiter'],'Mercury':['Sun','Venus'],'Jupiter':['Sun','Moon','Mars'],'Venus':['Mercury','Saturn'],'Saturn':['Mercury','Venus']}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
BENEFICS = {'Jupiter','Venus','Mercury','Moon'}
MALEFICS = {'Sun','Mars','Saturn','Rahu','Ketu'}
KENDRA = {1,4,7,10}
TRIKONA = {1,5,9}
DUSTHANA = {6,8,12}

# ============================================================
# 1. LOAD ALL CHARTS
# ============================================================
def load_all():
    charts = []
    data_dir = 'dataset'
    sources = [
        ('p1p9_absolute_final_rerank.json', 'list'),
        ('benchmark_10_domain.json', 'list'),
        ('benchmark_12_nexus_v2.json', 'list'),
        ('celebrity_112_nexus_v2.json', 'list'),
        ('varga_dasha_10.json', 'list'),
    ]
    for fn, fmt in sources:
        path = os.path.join(data_dir, fn)
        if not os.path.exists(path): continue
        try:
            with open(path) as f: data = json.load(f)
            items = data if isinstance(data, list) else list(data.values())
            for c in items:
                if isinstance(c, dict) and 'planets' in c:
                    c['_tier'] = 'A' if 'ascendant' in c else 'B'
                    c['_file'] = fn
                    charts.append(c)
        except: pass
    
    # Billionaire
    path = os.path.join(data_dir, 'billionaire_noon_analysis.json')
    if os.path.exists(path):
        with open(path) as f: data = json.load(f)
        for c in data.get('charts', []):
            c['_tier'] = 'B'; c['_file'] = 'billionaire'
            charts.append(c)
    
    # Historical
    path = os.path.join(data_dir, 'historical_groups_final.json')
    if os.path.exists(path):
        with open(path) as f: data = json.load(f)
        for gname, gcharts in data.items():
            for c in gcharts:
                c['_tier'] = 'B'; c['_file'] = 'historical'; c['_group'] = gname
                if 'planets' not in c:
                    c['planets'] = {'Moon': {'nakshatra': c.get('moon_nak','?'), 'sign': c.get('moon_sign','?')},
                                    'Rahu': {'sign': c.get('rahu_sign','?')}, 'Sun': {'sign': c.get('sun_sign','?')}}
                charts.append(c)
    
    # Deep research
    path = os.path.join(data_dir, 'deep_research_groups.json')
    if os.path.exists(path):
        with open(path) as f: data = json.load(f)
        for gname, gcharts in data.items():
            for c in gcharts:
                c['_tier'] = 'B'; c['_file'] = 'deep'; c['_group'] = gname
                if 'planets' not in c:
                    c['planets'] = {'Moon': {'nakshatra': c.get('moon_nak','?'), 'sign': c.get('moon_sign','?')}}
                charts.append(c)
    
    seen = set(); unique = []
    for c in charts:
        nm = c.get('name', c.get('_name',''))
        if nm and nm not in seen: seen.add(nm); unique.append(c)
        elif not nm: unique.append(c)
    return unique

# ============================================================
# 2. CHART NORMALIZATION
# ============================================================
def get_planets(chart):
    p = chart.get('planets', {})
    result = {}
    for pn in P7:
        if pn in p: result[pn] = {'sign': p[pn].get('sign'), 'dignity': p[pn].get('dignity',0), 'house': p[pn].get('house'), 'nakshatra': p[pn].get('nakshatra')}
    for pn in ['Rahu','Ketu']:
        if pn in p: result[pn] = {'sign': p[pn].get('sign'), 'dignity':0, 'house': p[pn].get('house'), 'nakshatra': p[pn].get('nakshatra')}
    return result

def get_asc(chart):
    a = chart.get('ascendant', chart.get('asc'))
    if isinstance(a, str): return a
    if isinstance(a, dict): return a.get('sign')
    return None

def get_houses(chart):
    asc = get_asc(chart)
    if not asc: return None
    ai = SIGNS.index(asc)
    return {h: SL[SIGNS[(ai+h-1)%12]] for h in range(1,13)}

def compute_dignity(pn, sign):
    if sign in OWN_SIGNS.get(pn,[]): return 75
    if EXALT.get(pn) == sign: return 100
    if DEBIL.get(pn) == sign: return -100
    return 0

# ============================================================
# 3. SHRINKHALA/PARIVARTANA DETECTION (2-5 loops)
# ============================================================
def detect_shrinkhala(p, houses):
    """Detect all exchange loops 2-5, each planet appears exactly once"""
    signs_of = {}
    for pn in P7:
        if pn in p and p[pn].get('sign'):
            signs_of[pn] = p[pn]['sign']
    
    in_sign_of = {}
    for pn, sign in signs_of.items():
        lord = SL.get(sign)
        if lord and lord != pn:
            in_sign_of[pn] = lord
    
    all_loops = []
    
    def dfs(start, current, path, depth_limit):
        if len(path) > depth_limit: return
        if current == start and len(path) >= 2:
            all_loops.append(path[:])
            return
        if current in path[:-1]: return
        nxt = in_sign_of.get(current)
        if nxt and nxt not in path[1:-1]:
            dfs(start, nxt, path + [nxt], depth_limit)
    
    for start in P7:
        if start in in_sign_of:
            for depth in [2,3,4,5]:
                dfs(start, in_sign_of[start], [start, in_sign_of[start]], depth)
    
    unique = []; seen_sets = set()
    for loop in all_loops:
        mi = min(range(len(loop)), key=lambda i: loop[i])
        rot = tuple(loop[mi:] + loop[:mi])
        if rot not in seen_sets:
            seen_sets.add(rot); unique.append(list(rot))
    
    results = []
    for loop in unique:
        length = len(loop)
        houses_involved = set()
        lords_involved = set()
        for pl in loop:
            h = p[pl].get('house')
            if h: houses_involved.add(h)
            # Which house lord is this planet?
            if houses:
                for hnum, lord in houses.items():
                    if lord == pl: lords_involved.add(hnum)
        
        nature = 'Benefic' if all(pl in BENEFICS for pl in loop) else ('Malefic' if all(pl in MALEFICS for pl in loop) else 'Mixed')
        has_dusthana = bool(houses_involved & DUSTHANA)
        has_kendra_trikona = bool(houses_involved & (KENDRA | TRIKONA))
        
        results.append({
            'length': length,
            'planets': loop,
            'houses_involved': sorted(list(houses_involved)),
            'lords_involved': sorted(list(lords_involved)),
            'nature': nature,
            'has_dusthana': has_dusthana,
            'has_kendra_trikona': has_kendra_trikona,
        })
    
    return results

# ============================================================
# 4. YOGA DETECTION
# ============================================================
def detect_all_yogas(chart, p, houses):
    good = []; bad = []
    asc = get_asc(chart)
    ai = SIGNS.index(asc) if asc else None
    
    # --- GOOD YOGAS ---
    # Pancha Mahapurusha
    mp = {'Mars':('Ruchaka','Military/industrial power'),'Mercury':('Bhadra','Intellect/commerce'),
          'Jupiter':('Hamsa','Wisdom/spiritual authority'),'Venus':('Malavya','Luxury/arts/beauty'),
          'Saturn':('Sasa','Discipline/endurance')}
    for pl,(yn,desc) in mp.items():
        if pl in p and p[pl].get('dignity',0) >= 75 and p[pl].get('house') in [1,4,7,10]:
            good.append(f'{yn} ({pl})')
    
    # Gaja-Kesari
    if 'Jupiter' in p and 'Moon' in p:
        jh,mh = p['Jupiter'].get('house'), p['Moon'].get('house')
        if jh and mh and ((mh+6)%12+1==jh or (jh+6)%12+1==mh or ((jh+4)%12+1==mh) or ((jh+8)%12+1==mh)):
            good.append('Gaja-Kesari')
    
    # Budha-Aditya
    if 'Sun' in p and 'Mercury' in p and p['Sun'].get('house') and p['Sun']['house']==p['Mercury'].get('house'):
        good.append('Budha-Aditya')
    
    # Dhana Yogas
    if houses:
        h2l = houses[2]; h5l = houses[5]; h9l = houses[9]; h11l = houses[11]; ll = houses[1]
        if h2l in p and h11l in p and p[h2l].get('house')==p[h11l].get('house'):
            good.append('Dhana (2L+11L)')
        if h5l in p and h9l in p and p[h5l].get('house')==p[h9l].get('house'):
            good.append('Lakshmi (5L+9L)')
        if ll in p and h9l in p and p[ll].get('house')==p[h9l].get('house'):
            good.append('Dhana (LL+9L)')
    
    # Raja Yogas
    if houses:
        for kh in [1,4,7,10]:
            for ch in [1,5,9]:
                kl = houses[kh]; cl = houses[ch]
                if kl==cl: continue
                if kl in p and cl in p and p[kl].get('house')==p[cl].get('house'):
                    good.append(f'Raja ({kl}L{kh}+{cl}L{ch})')
    
    # VRY
    if houses:
        for dh in [6,8,12]:
            dhl = houses[dh]
            if dhl in p and p[dhl].get('house') in [6,8,12]:
                good.append(f'Vipareeta Raja ({dhl} L{dh})')
    
    # Parivartana detected as Shrinkhala 2-loop
    loops = detect_shrinkhala(p, houses)
    for loop in loops:
        if loop['length'] == 2 and loop['nature'] == 'Benefic':
            good.append(f'Parivartana ({loop["planets"][0]}↔{loop["planets"][1]})')
    
    # --- BAD YOGAS ---
    # Kemadruma
    if 'Moon' in p and houses:
        mh = p['Moon'].get('house')
        if mh:
            before = (mh+10)%12+1; after = (mh+1)%12+1
            has_before = any(p[pl].get('house')==before for pl in P7 if pl in p and pl!='Moon')
            has_after = any(p[pl].get('house')==after for pl in P7 if pl in p and pl!='Moon')
            if not has_before and not has_after:
                cancelled = any(p[pl].get('house') and ((p[pl]['house']+6)%12+1==mh) for pl in P7 if pl in p)
                bad.append('Kemadruma' if not cancelled else 'Kemadruma (cancelled)')
    
    # Debilitated without NBRY
    for pl in P7:
        if pl in p and p[pl].get('dignity',0)==-100:
            # Check NBRY
            has_nbry = False
            dl = SL[DEBIL[pl]]
            el = SL[EXALT[pl]]
            if dl in p and p[dl].get('house') in [1,4,7,10]: has_nbry = True
            if el in p:
                eh = p[el].get('house'); dh = p[pl].get('house')
                if eh and dh:
                    if (eh+6)%12+1==dh or ((eh+4)%12+1==dh) or ((eh+7)%12+1==dh) or ((eh+8)%12+1==dh):
                        has_nbry = True
            if has_nbry:
                good.append(f'Neecha Bhanga ({pl})')
            else:
                bad.append(f'Debilitated ({pl})')
    
    # Malefic conjunctions
    if 'Mars' in p and 'Saturn' in p and p['Mars'].get('house') and p['Mars']['house']==p['Saturn'].get('house'):
        bad.append('Mars+Saturn conjunction')
    if 'Rahu' in p and 'Saturn' in p and p['Rahu'].get('house') and p['Rahu']['house']==p['Saturn'].get('house'):
        bad.append('Rahu+Saturn (Guru Chandal if Jupiter absent)')
    
    # Benefic lords in dusthana
    if houses:
        for b in BENEFICS:
            if b in houses.values():
                for hnum, lord in houses.items():
                    if lord == b and hnum in DUSTHANA:
                        actual = p.get(lord, {}).get('house')
                        if actual and actual in DUSTHANA:
                            bad_has_vry = (lord in p and p[lord].get('house') in DUSTHANA and houses.get(p[lord].get('house')) == lord)
                            if not bad_has_vry:
                                bad.append(f'{b} (benefic lord) in H{hnum}')
    
    return good, bad

# ============================================================
# 5. NET ASTROLOGICAL SCORE
# ============================================================
def compute_nas(chart, p, houses, good_yogas, bad_yogas):
    pos = 0; neg = 0
    
    # +1 Exalted, Vargottama (from D9 if available), Neecha Bhanga
    for pl in P7:
        if pl not in p: continue
        dig = p[pl].get('dignity',0)
        if dig == 100: pos += 1
        if dig == 75: pos += 1
        if dig == -100:
            # Check if NBRY covers it
            if any(f'Neecha Bhanga ({pl})' in y for y in good_yogas):
                pos += 1  # upgraded
            else:
                neg += 1
    
    # +1 each major good yoga (dedup)
    good_set = set()
    for y in good_yogas:
        base = y.split(' (')[0]
        if base not in good_set:
            good_set.add(base); pos += 1
    
    # +1 for 1st/5th/9th/10th lord in Kendra/Trikona
    if houses:
        for lord_h in [1,5,9,10]:
            lord = houses[lord_h]
            if lord in p and p[lord].get('house') in (KENDRA | TRIKONA):
                pos += 1
    
    # -1 each major bad yoga
    bad_set = set()
    for y in bad_yogas:
        base = y.split(' (')[0]
        if base not in bad_set and 'cancelled' not in y:
            bad_set.add(base); neg += 1
    
    # -1 benefic lords in 6/8/12 without VRY
    if houses:
        for b in BENEFICS:
            for hnum, lord in houses.items():
                if lord == b and hnum in DUSTHANA:
                    if lord in p and p[lord].get('house') in DUSTHANA:
                        if not any('Vipareeta' in y and lord in y for y in good_yogas):
                            neg += 1; break
    
    # Shrinkhala scoring
    loops = detect_shrinkhala(p, houses)
    for loop in loops:
        if loop['length'] in [2,3] and loop['has_kendra_trikona'] and not loop['has_dusthana']:
            pos += 1
        elif loop['has_dusthana']:
            neg += 1
    
    nas = pos - neg
    return {'positive_points': pos, 'negative_points': neg, 'net_astrological_score': nas}

# ============================================================
# 6. OUTCOME CLASSIFICATION
# ============================================================
def classify_outcome(chart):
    name = (chart.get('name') or '').lower()
    cat = (chart.get('_category') or chart.get('category') or chart.get('_group') or '').lower()
    src = (chart.get('_file') or '').lower()
    
    wealth = 'Neutral'; social = 'Neutral'
    
    # Known billionaires
    billionaire_set = {'elon musk','jeff bezos','bill gates','mark zuckerberg','warren buffett','bernard arnault',
                       'larry ellison','larry page','sergey brin','steve ballmer','michael bloomberg','carlos slim',
                       'amancio ortega','mukesh ambani','gautam adani','jensen huang','michael dell','phil knight',
                       'richard branson','jack ma','masayoshi son','john d. rockefeller','andrew carnegie','j.p. morgan',
                       'cornelius vanderbilt','henry ford','thomas edison','oprah winfrey','steve jobs','peter thiel',
                       'marc andreessen','vinod khosla','beyonce','paul graham','jan koum','brian chesky',
                       'evan spiegel','dustin moskovitz','eduardo saverin','palmer luckey','john collison',
                       'patrick collison','whitney wolfe herd','melanie perkins','changpeng zhao','vitalik buterin',
                       'satya nadella','sundar pichai','tim cook','sheryl sandberg','marissa mayer','susan wojcicki',
                       'bhavish aggarwal','vijay shekhar sharma','sachin bansal','binny bansal','byju raveendran',
                       'ritesh agarwal','falguni nayar','radhakishan damani','kumar mangalam birla','uday kotak',
                       'azim premji','reed hastings','marc benioff','reid hoffman','daniel ek','bobby murphy',
                       'joe gebbia','nathan blecharczyk','travis kalanick','garrett camp','dara khosrowshahi',
                       'andy jassy','arvind krishna','shantanu narayen','lisa su','safra catz','ginni rometty',
                       'meg whitman','chuck feeney','howard hughes','j.p. morgan','andrew mellon','john jacob astor',
                       'hetty green','john d. rockefeller','mansa musa','cosimo de medici','sam walton',
                       'ray kroc','estee lauder','coco chanel','madam c.j. walker','giorgio armani','bernard arnault',
                       'francois pinault','alain wertheimer','gerard wertheimer','giovanni ferrero',
                       'leonardo del vecchio','silvio berlusconi','james ratcliffe','ray dalio','ken griffin',
                       'stephen schwarzman','david rubenstein','leon black','carl icahn','george soros',
                       'ben horowitz','john doerr','satoshi nakamoto','kalyan krishnamurthy',
                       'deepinder goyal','sriharsha majety','kunal bahl','rohit bansal',
                       'aliko dangote','folorunsho alakija','kiran mazumdar-shaw','masayoshi son',
                       'tadashi yanai','dieter schwarz','klaus-michael kuehne','stefan quandt','susanne klatten',
                       'alwaleed bin talal','mike adenuga','patrice motsepe','nicky oppenheimer',
                       'johann rupert','nassef sawiris','naguib sawiris','yuri milner',
                       'roman abramovich','vladimir potanin','alexei mordashov','viktor vekselberg',
                       'leonid mikhelson','vagit alekperov','german khan','mikhail prokhorov',
                       'robert kuok','charoen sirivadhanabhakdi','li ka-shing','lee shau kee',
                       'henry sy','manuel villar','enrique razon','lucio tan','andrew tan',
                       'tony tan caktiong','ramon ang','ismael cruz',}
    
    criminal_set = {'pablo escobar','al capone','john dillinger','ted bundy','griselda blanco','lucky luciano',
                    'meyer lansky','bugsy siegel','john gotti','whitey bulger','jeffrey dahmer','john wayne gacy',
                    'richard ramirez','aileen wuornos','charles manson','bernard madoff','kenneth lay',
                    'jeffrey skilling','dennis kozlowski','jordan belfort','sam bankman-fried','elizabeth holmes',
                    'adolf hitler','joseph stalin','benito mussolini','pol pot','idi amin','saddam hussein',
                    'osama bin laden','ted kaczynski','anders behring breivik','adam lanza','dylan klebold',
                    'eric harris','jesse james','billy the kid','ned kelly','bonnie parker','clyde barrow',
                    'guy fawkes','gilles de rais','elizabeth bathory','ivan the terrible','vlad the impaler',
                    'caligula','nero','commodus','caracalla','elagabalus','king john of england',
                    'leopold ii of belgium','mobutu sese seko','ferdinand marcos','jean-bedel bokassa',
                    'francisco pizarro','hernan cortes','tomás de torquemada','empress cixi',
                    'maximilien robespierre','ranavalona i','scott rothstein','marc dreier','tom petters',
                    'ruja ignatova','caroline ellison','alex mashinsky','do kwon','barry minkow',
                    'nick leeson','jerome kerviel','kweku adoboli','martin shkreli','allen stanford',
                    'charles ponzi','victor lustig','frank abagnale','richard scrushy','bernard ebbers',
                    'john rigas','lou pearlman','trevor milton','adam neumann','sammy gravano',
                    'paul castellano','carlo gambino','frank costello','vito genovese','tony accardo',
                    'sam giancana','santo trafficante','carlos marcello','henry hill','richard kuklinski',
                    'arthur shawcross','ed gein','albert fish','david berkowitz','dennis rader','gary ridgway',
                    'h.h. holmes','jim jones','david koresh','marshall applewhite','shoko asahara',
                    'timothy mcveigh','terry nichols','dzokhar tsarnaev','tamerlan tsarnaev',
                    'seung-hui cho','lee harvey oswald','john wilkes booth','gavrilo princip',
                    'joseph goebbels','heinrich himmler','hermann goring','reinhard heydrich','adolf eichmann',
                    'nicolae ceausescu','enver hoxha','slobodan milosevic','radovan karadzic','ratko mladic',
                    'charles taylor','muammar gaddafi','robert mugabe','omar al-bashir','mengistu haile mariam',
                    'jeffrey epstein','ghislaine maxwell','keith raniere','allison mack',
                    'rodney alcala','dean corll','wayne williams','randy kraft','william bonin',
                    'robert hansen','belle gunness','harold shipman','fred west','rosemary west',
                    'peter sutcliffe','ian brady','myra hindley','andrei chikatilo',
                    'joaquin guzman','ismael zambada','amado carrillo','miguel angel felix',
                    'ernesto fonseca','rafael caro quintero','osiel cardenas','nemesio oseguera',
                    'arturo beltran leyva','carlos lehder','raineri','sunny balwani','billy mcfarland',
                    'anna sorokin','simon leviev',}
    
    # Match by name
    for bn in billionaire_set:
        if bn in name: wealth = 'Rich'; break
    
    # Also check category tags
    if any(w in cat for w in ['billionaire','tycoon','philanthropist']): wealth = 'Rich'
    if any(w in cat for w in ['bankruptcy','fraud','criminal']): wealth = 'Poor'
    
    for cn in criminal_set:
        if cn in name: social = 'Bad'; break
    
    if any(w in cat for w in ['criminal','fraud','dictator','notorious','serial killer']): social = 'Bad'
    if any(w in cat for w in ['activist','humanitarian','philanthropist']): social = 'Good'
    
    # Override for known good people
    good_set = {'mother teresa','martin luther king','nelson mandela','mahatma gandhi','rosa parks',
                'harriet tubman','frederick douglass','cesar chavez','desmond tutu','florence nightingale',
                'malala yousafzai','saint francis','albert schweitzer','dag hammarskjold',
                'raoul wallenberg','nicholas winton','irena sendler','witold pilecki','chiune sugihara',
                'gino bartali','sophie scholl','ruby bridges','claudette colvin','steve biko',
                'thomas sankara','patrice lumumba','oscar romero','father damien','chico mendes',
                'rigoberta menchu','sojourner truth','susan b. anthony','john brown',
                'vinoba bhave','bernadette soubirous','saint nicholas',}
    for gn in good_set:
        if gn in name: social = 'Good'
    
    return {'wealth_status': wealth, 'social_impact': social}

# ============================================================
# 7. CAREER GROUPING
# ============================================================
def classify_career(chart):
    cat = (chart.get('_category') or chart.get('category') or chart.get('_group') or '').lower()
    name = (chart.get('name') or '').lower()
    
    groups = {
        'Business/Finance': ['billionaire','tycoon','philanthropist','investor','venture capitalist','entrepreneur',
                             'business','finance','founder','ceo','executive','tech founder','late bloomer founder'],
        'Science/Tech': ['scientist','physicist','mathematician','computer scientist','physician','medical pioneer',
                         'inventor','engineer','chemist','biologist','astronomer','polymath','nobel'],
        'Arts/Entertainment': ['actor','musician','composer','writer','poet','artist','film director','singer',
                               'entertainer','author','playwright','painter','sculptor','architect'],
        'Politics/Military': ['dictator','statesman','leader','politician','military commander','warrior',
                              'ancient ruler','pirate','sea warrior','outlaw','daimyo','indian warrior king',
                              'spy','traitor','assassin'],
        'Athletics': ['athlete','sports','olympic','boxer','football','basketball','tennis','racing'],
        'Humanitarian/Religion': ['activist','humanitarian','religious','saint','spiritual','guru','philosopher'],
        'Exploration/Aviation': ['explorer','astronaut','aviator','pilot','cosmonaut','navigator'],
        'Criminal': ['criminal','fraud','serial killer','mafia','drug lord','terrorist','corporate fraud',
                     'notorious criminal','bankrupt athlete'],
        'Martial Arts': ['martial arts','martial arts master','samurai','ninja'],
        'Other': [],
    }
    
    for group, keywords in groups.items():
        for kw in keywords:
            if kw in cat or kw in name: return group
    
    return 'Other'

# ============================================================
# 8. RUN EVERYTHING
# ============================================================
print("="*100)
print("NEXUS BENCHMARK PIPELINE v4.0 — 20K-Scale Framework")
print("="*100)

charts = load_all()
print(f"\nLoaded {len(charts)} unique charts")
print(f"Tier A (timed): {sum(1 for c in charts if c.get('_tier')=='A')}")
print(f"Tier B (reference): {sum(1 for c in charts if c.get('_tier')=='B')}")

# Process all
output = []
stats = defaultdict(lambda: {'count':0,'rich':0,'poor':0,'good':0,'bad':0,'total_nas':0,
                              'has_2loop':0,'has_3loop':0,'has_4loop':0,'has_5loop':0})

for i, c in enumerate(charts):
    if i % 200 == 0: print(f"  Processing {i}/{len(charts)}...")
    
    p = get_planets(c)
    houses = get_houses(c) if c.get('_tier') == 'A' else None
    outcome = classify_outcome(c)
    career = classify_career(c)
    name = c.get('name', c.get('_name', '?'))
    
    loops = detect_shrinkhala(p, houses) if len([pl for pl in P7 if pl in p]) >= 3 else []
    good_yogas, bad_yogas = detect_all_yogas(c, p, houses) if houses else ([], [])
    nas = compute_nas(c, p, houses, good_yogas, bad_yogas)
    
    result = {
        'person_id': f"{career[:4]}_{i:04d}",
        'name': name,
        'career_group': career,
        'tier': c.get('_tier', 'B'),
        'outcomes': outcome,
        'shrinkhala_loops': loops,
        'yogas_detected': {
            'good_yogas': good_yogas[:10],
            'bad_yogas': bad_yogas[:10],
        },
        'scoring': nas,
        'correlation_notes': f"{name}: NAS={nas['net_astrological_score']} | {outcome['wealth_status']}/{outcome['social_impact']} | {career}",
    }
    
    output.append(result)
    
    # Stats
    s = stats[career]
    s['count'] += 1
    if outcome['wealth_status'] == 'Rich': s['rich'] += 1
    if outcome['wealth_status'] == 'Poor': s['poor'] += 1
    if outcome['social_impact'] == 'Good': s['good'] += 1
    if outcome['social_impact'] == 'Bad': s['bad'] += 1
    s['total_nas'] += nas['net_astrological_score']
    for loop in loops:
        if loop['length'] == 2: s['has_2loop'] += 1
        elif loop['length'] == 3: s['has_3loop'] += 1
        elif loop['length'] == 4: s['has_4loop'] += 1
        elif loop['length'] == 5: s['has_5loop'] += 1

# ============================================================
# 9. REPORTS
# ============================================================
print(f"\n{'='*100}")
print("CAREER GROUP STATISTICS")
print(f"{'='*100}")
print(f"{'Career Group':<30} {'N':>5} {'Rich%':>7} {'Poor%':>7} {'Good%':>7} {'Bad%':>7} {'AvgNAS':>7} {'2Lp':>5} {'3Lp':>5} {'4Lp':>5} {'5Lp':>5}")
print("-"*100)

sorted_groups = sorted(stats.items(), key=lambda x: -x[1]['count'])
for gname, s in sorted_groups:
    n = s['count']
    if n < 3: continue
    print(f"{gname:<30} {n:>5} {s['rich']/n*100:>6.1f}% {s['poor']/n*100:>6.1f}% "
          f"{s['good']/n*100:>6.1f}% {s['bad']/n*100:>6.1f}% "
          f"{s['total_nas']/n:>6.1f} {s['has_2loop']:>5} {s['has_3loop']:>5} {s['has_4loop']:>5} {s['has_5loop']:>5}")

# NAS vs Outcome correlation
print(f"\n{'='*100}")
print("NET ASTROLOGICAL SCORE vs OUTCOME")
print(f"{'='*100}")

rich_out = [r for r in output if r['outcomes']['wealth_status'] == 'Rich']
poor_out = [r for r in output if r['outcomes']['wealth_status'] == 'Poor']
good_out = [r for r in output if r['outcomes']['social_impact'] == 'Good']
bad_out = [r for r in output if r['outcomes']['social_impact'] == 'Bad']
neutral_out = [r for r in output if r['outcomes']['wealth_status'] == 'Neutral' and r['outcomes']['social_impact'] == 'Neutral']

if rich_out:
    print(f"  Rich (n={len(rich_out)}): avg NAS = {sum(r['scoring']['net_astrological_score'] for r in rich_out)/len(rich_out):.1f}")
if poor_out:
    print(f"  Poor (n={len(poor_out)}): avg NAS = {sum(r['scoring']['net_astrological_score'] for r in poor_out)/len(poor_out):.1f}")
if good_out:
    print(f"  Good (n={len(good_out)}): avg NAS = {sum(r['scoring']['net_astrological_score'] for r in good_out)/len(good_out):.1f}")
if bad_out:
    print(f"  Bad (n={len(bad_out)}): avg NAS = {sum(r['scoring']['net_astrological_score'] for r in bad_out)/len(bad_out):.1f}")
if neutral_out:
    print(f"  Neutral (n={len(neutral_out)}): avg NAS = {sum(r['scoring']['net_astrological_score'] for r in neutral_out)/len(neutral_out):.1f}")

# Top scorers
print(f"\n{'='*100}")
print("TOP 20 NET ASTROLOGICAL SCORES")
print(f"{'='*100}")
output.sort(key=lambda x: -x['scoring']['net_astrological_score'])
for i, r in enumerate(output[:20], 1):
    print(f"  {i:>2}. {r['name']:<30} NAS={r['scoring']['net_astrological_score']:>4} | {r['career_group']:<25} | {r['outcomes']['wealth_status']}/{r['outcomes']['social_impact']}")

# Bottom
print(f"\nBOTTOM 20:")
for i, r in enumerate(output[-20:], 1):
    print(f"  {i:>2}. {r['name']:<30} NAS={r['scoring']['net_astrological_score']:>4} | {r['career_group']:<25} | {r['outcomes']['wealth_status']}/{r['outcomes']['social_impact']}")

# Shrinkhala stats
print(f"\n{'='*100}")
print("SHRINKHALA LOOP STATISTICS")
print(f"{'='*100}")
total_2 = sum(1 for r in output if any(l['length']==2 for l in r['shrinkhala_loops']))
total_3 = sum(1 for r in output if any(l['length']==3 for l in r['shrinkhala_loops']))
total_4 = sum(1 for r in output if any(l['length']==4 for l in r['shrinkhala_loops']))
total_5 = sum(1 for r in output if any(l['length']==5 for l in r['shrinkhala_loops']))
print(f"  2-Loop (Parivartana): {total_2} charts ({total_2/len(output)*100:.1f}%)")
print(f"  3-Loop: {total_3} charts ({total_3/len(output)*100:.1f}%)")
print(f"  4-Loop: {total_4} charts ({total_4/len(output)*100:.1f}%)")
print(f"  5-Loop: {total_5} charts ({total_5/len(output)*100:.1f}%)")

# Save
with open('dataset/nexus_v4_benchmark.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved → dataset/nexus_v4_benchmark.json")
print(f"Total records: {len(output)}")
