#!/usr/bin/env python3
"""
NEXUS v3.0 — Industry CSV Ingester
Reads any industry CSV, computes 159 features, appends to astro_v3_matrix.npz.
Supports: column-name normalization, city→lat/lon geocoding, noon-birth.
Usage: python scripts/ingest_industry_csv.py <csv_path> [industry_label]
"""
import swisseph as swe, csv, os, sys, numpy as np
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon',
      'Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars',
      'Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EXALT = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo',
         'Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces',
         'Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],
       'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],
       'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
VIM = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),
        ('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),
        ('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),
        ('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),
        ('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),
        ('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),
        ('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),
        ('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),
        ('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]

# Major city geocoding (~200 cities)
CITY_GEO = {
    'chicago':(41.88,-87.63),'new york':(40.71,-74.01),'new york city':(40.71,-74.01),
    'los angeles':(34.05,-118.24),'san francisco':(37.77,-122.42),
    'boston':(42.36,-71.06),'washington':(38.91,-77.04),'washington dc':(38.91,-77.04),
    'london':(51.51,-0.13),'paris':(48.86,2.35),'berlin':(52.52,13.40),
    'mumbai':(19.08,72.88),'delhi':(28.61,77.23),'bangalore':(12.97,77.59),
    'chennai':(13.08,80.27),'kolkata':(22.57,88.36),
    'colombo':(6.93,79.85),'tokyo':(35.68,139.76),'seoul':(37.57,126.98),
    'beijing':(39.90,116.41),'shanghai':(31.23,121.47),'hong kong':(22.32,114.17),
    'singapore':(1.35,103.82),'sydney':(-33.87,151.21),'melbourne':(-37.81,144.96),
    'toronto':(43.65,-79.38),'vancouver':(49.28,-123.12),'montreal':(45.50,-73.57),
    'moscow':(55.76,37.62),'istanbul':(41.01,28.98),'dubai':(25.20,55.27),
    'rome':(41.90,12.50),'milan':(45.46,9.19),'madrid':(40.42,-3.70),
    'barcelona':(41.39,2.16),'amsterdam':(52.37,4.90),'stockholm':(59.33,18.07),
    'oslo':(59.91,10.75),'copenhagen':(55.68,12.57),'helsinki':(60.17,24.94),
    'vienna':(48.21,16.37),'zurich':(47.38,8.54),'geneva':(46.20,6.14),
    'brussels':(50.85,4.35),'dublin':(53.35,-6.26),'edinburgh':(55.95,-3.19),
    'lisbon':(38.72,-9.14),'athens':(37.98,23.73),'warsaw':(52.23,21.01),
    'prague':(50.09,14.42),'budapest':(47.50,19.04),'bucharest':(44.43,26.10),
    'mexico city':(19.43,-99.13),'buenos aires':(-34.60,-58.38),
    'sao paulo':(-23.55,-46.63),'rio de janeiro':(-22.91,-43.20),
    'lima':(-12.05,-77.04),'santiago':(-33.45,-70.67),'bogota':(4.71,-74.07),
    'cairo':(30.04,31.24),'cape town':(-33.92,18.42),'johannesburg':(-26.20,28.05),
    'lagos':(6.52,3.38),'nairobi':(-1.29,36.82),'tel aviv':(32.09,34.78),
    'jerusalem':(31.77,35.21),'tehran':(35.69,51.39),'bangkok':(13.75,100.50),
    'kuala lumpur':(3.14,101.69),'jakarta':(-6.21,106.85),'manila':(14.60,120.98),
    'taipei':(25.03,121.56),'auckland':(-36.85,174.76),
    'fargo':(46.88,-96.79),'kansas city':(39.10,-94.58),
    'st. louis':(38.63,-90.20),'st louis':(38.63,-90.20),
    'philadelphia':(39.95,-75.17),'pittsburgh':(40.44,-79.99),
    'detroit':(42.33,-83.05),'cleveland':(41.50,-81.69),
    'atlanta':(33.75,-84.39),'miami':(25.76,-80.19),
    'dallas':(32.78,-96.80),'houston':(29.76,-95.37),
    'phoenix':(33.45,-112.07),'denver':(39.74,-104.99),
    'seattle':(47.61,-122.33),'portland':(45.52,-122.68),
    'san diego':(32.72,-117.16),'minneapolis':(44.98,-93.27),
    'baltimore':(39.29,-76.61),'charlotte':(35.23,-80.84),
    'new orleans':(29.95,-90.07),'nashville':(36.16,-86.78),
    'salt lake city':(40.76,-111.89),'las vegas':(36.17,-115.14),
    'austin':(30.27,-97.74),'madison':(43.07,-89.40),
    'ann arbor':(42.28,-83.74),'cambridge':(42.37,-71.11),
    'princeton':(40.36,-74.66),'berkeley':(37.87,-122.27),
    'stanford':(37.43,-122.17),'palo alto':(37.44,-122.14),
    'new haven':(41.31,-72.93),'providence':(41.82,-71.41),
    'ithaca':(42.44,-76.50),'evanston':(42.04,-87.69),
    'pasadena':(34.15,-118.14),'irvine':(33.68,-117.83),
    'la jolla':(32.84,-117.27),'santa monica':(34.02,-118.49),
    'tucson':(32.22,-110.97),'tempe':(33.43,-111.94),
    'oxford':(51.75,-1.26),'cambridge uk':(52.21,0.12),
    'manchester':(53.48,-2.24),'birmingham uk':(52.49,-1.89),
    'glasgow':(55.87,-4.26),'lyon':(45.76,4.84),'marseille':(43.30,5.37),
    'hamburg':(53.55,9.99),'munich':(48.14,11.58),'frankfurt':(50.11,8.68),
    'cologne':(50.94,6.96),'heidelberg':(49.41,8.69),'bonn':(50.74,7.10),
    'florence':(43.77,11.26),'naples':(40.85,14.27),'turin':(45.07,7.69),
    'bologna':(44.49,11.34),'kyiv':(50.45,30.52),'odessa':(46.48,30.72),
    'durban':(-29.86,31.02),'pretoria':(-25.75,28.19),
    'ankara':(39.93,32.86),'izmir':(38.42,27.14),
    'antwerp':(51.22,4.40),'rotterdam':(51.92,4.48),
    'gothenburg':(57.71,11.97),'malmo':(55.60,13.00),
    'osaka':(34.69,135.50),'kyoto':(35.01,135.77),
    'nagoya':(35.18,136.91),'yokohama':(35.44,139.64),
    'busan':(35.18,129.08),'incheon':(37.46,126.71),
    'guangzhou':(23.13,113.26),'shenzhen':(22.54,114.06),
    'tianjin':(39.34,117.36),'chongqing':(29.56,106.55),
    'nanjing':(32.06,118.80),'wuhan':(30.59,114.31),
    'chengdu':(30.57,104.07),'xian':(34.26,108.94),
    'ahmedabad':(23.02,72.57),'pune':(18.52,73.86),
    'hyderabad':(17.38,78.49),'jaipur':(26.92,75.79),
    'lucknow':(26.85,80.95),'kanpur':(26.45,80.33),
    'nagpur':(21.15,79.09),'indore':(22.72,75.86),
    'bhopal':(23.26,77.41),'surat':(21.17,72.83),
    'kochi':(9.93,76.27),'kozhikode':(11.26,75.78),
    'thiruvananthapuram':(8.52,76.94),'trivandrum':(8.52,76.94),
    'visakhapatnam':(17.69,83.22),'vijayawada':(16.51,80.62),
    'patna':(25.59,85.14),'ranchi':(23.36,85.33),
    'guwahati':(26.14,91.74),'bhubaneswar':(20.27,85.84),
    'chandigarh':(30.73,76.78),'dehradun':(30.32,78.03),
    'shimla':(31.10,77.17),'srinagar':(34.08,74.80),
    'kandy':(7.29,80.63),'galle':(6.05,80.22),
    'jaffna':(9.66,80.01),'negombo':(7.21,79.84),
    'kurunegala':(7.49,80.36),'anuradhapura':(8.31,80.41),
    'ratnapura':(6.68,80.40),'badulla':(6.99,81.06),
    'batticaloa':(7.72,81.70),'trincomalee':(8.57,81.23),
    'polgahawela':(7.34,80.30),'sri jayawardenepura kotte':(6.91,79.89),
}

COL_MAPS = {
    'default': {'name':'Full Name','date':'Birth Date (YYYY-MM-DD)','city':'Birth City',
                'state':'Birth State/Province (if applicable)','country':'Birth Country',
                'profession':'Primary Profession','area':'Primary Research Area','contrib':'Major Contribution'},
    'consumer': {'name':'Name','date':'BirthDate','city':'BirthCity',
                 'state':'BirthStateProvince','country':'BirthCountry',
                 'profession':'PrimaryField','area':None,'contrib':'MainContribution'},
}


def geo_lookup(city_name, country=''):
    if not city_name: return (20.0, 77.0)
    key = city_name.strip().lower()
    if key in CITY_GEO: return CITY_GEO[key]
    for part in key.split(','):
        p = part.strip()
        if p in CITY_GEO: return CITY_GEO[p]
    return (20.0, 77.0)


def compute_chart(bd_str, lat, lon):
    dt = datetime.strptime(bd_str.strip() + 'T12:00:00', '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone(timedelta(hours=0)))
    jd = swe.julday(dt.year, dt.month, dt.day, 12)
    ayan = swe.get_ayanamsa(jd)
    asc_trop, _ = swe.houses_ex(jd, lat, lon, b'A')
    asc_sid = (asc_trop[0] - ayan) % 360
    asc_idx = int(asc_sid // 30)
    planets = {}
    for pn, pid in {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}.items():
        lt, _ = swe.calc_ut(jd, pid)
        sid = (lt[0] - ayan) % 360
        sgn = SIGNS[int(sid // 30)]
        h = (SIGNS.index(sgn) - asc_idx) % 12 + 1
        dgn = 100 if (pn in EXALT and EXALT[pn]==sgn) else (75 if (pn in OWN and sgn in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==sgn) else 0))
        planets[pn] = {'sign':sgn,'house':h,'dignity':dgn,'sid':sid}
    # D9
    v9l = (asc_sid * 9) % 360; v9li = SIGNS.index(SIGNS[int(v9l // 30)])
    d9 = {}
    for pn in P7:
        vl = (planets[pn]['sid'] * 9) % 360; vs = SIGNS[int(vl // 30)]
        vh = (SIGNS.index(vs) - v9li) % 12 + 1
        dgn9 = 100 if (pn in EXALT and EXALT[pn]==vs) else (75 if (pn in OWN and vs in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==vs) else 0))
        d9[pn] = {'sign':vs,'house':vh,'dignity':dgn9}
    # D10
    v10l = (asc_sid * 10) % 360; v10li = SIGNS.index(SIGNS[int(v10l // 30)])
    d10 = {}
    for pn in P7:
        vl = (planets[pn]['sid'] * 10) % 360; vs = SIGNS[int(vl // 30)]
        vh = (SIGNS.index(vs) - v10li) % 12 + 1
        d10[pn] = {'sign':vs,'house':vh}
    d10_10l_sign = SIGNS[(v10li + 9) % 12]
    d10_10l = SL[d10_10l_sign]
    d10_10l_h = d10[d10_10l]['house'] if d10_10l in d10 else 0
    # Dasha
    ms = planets['Moon']['sid']; ml = '?'; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + 13.334: bal = VIM_YRS[l] * (1 - (ms - s) / 13.334); ml = l; break
    rd = datetime(2026, 7, 31, tzinfo=timezone(timedelta(hours=0)))
    yfb = (rd - dt).total_seconds() / (365.25 * 86400)
    mli = VIM.index(ml) if ml in VIM else 0; elapsed = 0; rem = bal; md2 = '?'
    for _ in range(9):
        if elapsed + rem > yfb: md2 = VIM[mli]; break
        elapsed += rem; mli = (mli + 1) % 9; rem = VIM_YRS[VIM[mli]]
    # Saturn transit
    jd_now = swe.julday(2026, 7, 31, 12); ayan_t = swe.get_ayanamsa(jd_now)
    lt_sat, _ = swe.calc_ut(jd_now, 6); sat_now = (lt_sat[0] - ayan_t) % 360
    natal_sat_deg = SIGNS.index(planets['Saturn']['sign']) * 30 + (planets['Saturn']['sid'] % 30)
    sat_dist = min(abs(sat_now - natal_sat_deg), 360 - abs(sat_now - natal_sat_deg))
    sat_ret = 1 if sat_dist < 3 else 0
    # Jupiter transit
    lt_jup, _ = swe.calc_ut(jd_now, 5); jup_now = (lt_jup[0] - ayan_t) % 360
    jup_house = (SIGNS.index(SIGNS[int(jup_now // 30)]) - asc_idx) % 12 + 1
    # Shrinkhala
    g = {}
    for pn in P7:
        lord = SL[planets[pn]['sign']]
        if lord != pn: g[pn] = lord
    loops5 = []; visited = set()
    for start in P7:
        path = []; curr = start
        while curr in g and curr not in path: path.append(curr); curr = g[curr]
        if curr in path:
            cycle = path[path.index(curr):]; t = tuple(sorted(cycle))
            if 2 <= len(cycle) <= 5 and t not in visited: visited.add(t); loops5.append(cycle)
    shrinkhala_present = 1 if loops5 else 0
    shrinkhala_max = max([len(l) for l in loops5]) if loops5 else 0
    # Raja
    hinv = {}
    for pn in P7: hinv.setdefault(planets[pn]['house'], []).append(pn)
    raja = 0
    for kh in [1,4,7,10]:
        for tr in [1,5,9]:
            for kl in hinv.get(kh, []):
                for ccl in hinv.get(tr, []):
                    if kl != ccl and planets[kl]['house'] == planets[ccl]['house']: raja += 1
    raja = min(raja, 10)
    # Gaj-Kesari
    mh = planets['Moon']['house']; jh = planets['Jupiter']['house']
    gk = 1 if (mh + 3) % 12 + 1 == jh or (mh + 6) % 12 + 1 == jh or (mh + 9) % 12 + 1 == jh or mh == jh else 0
    # Budha-Aditya
    ba = 1 if planets['Sun']['house'] == planets['Mercury']['house'] else 0
    # NBRY
    nbr = 0
    for pl in P7:
        if planets[pl]['dignity'] == -100:
            c = 0
            dl2 = SL[DEBIL[pl]]
            if dl2 in planets and planets[dl2]['house'] in [1,4,7,10]: c += 1
            el2 = SL[EXALT[pl]]
            if el2 in planets:
                eh2 = planets[el2]['house']; dh2 = planets[pl]['house']
                if (eh2 + 6) % 12 + 1 == dh2 or (eh2 + 4) % 12 + 1 == dh2: c += 1
            if planets[pl]['house'] in [1,4,7,10]: c += 1; nbr = max(nbr, c)
    nbry_flag = 1 if nbr >= 2 else 0
    # MP
    mp_yogas = {}
    for pl, yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        mp_yogas[yn] = 1 if planets[pl]['dignity'] >= 75 and planets[pl]['house'] in [1,4,7,10] else 0
    mp_shrinkhala = 1 if (any(mp_yogas.values()) and shrinkhala_present) else 0
    return {
        'planets':planets,'d9':d9,'d10':d10,
        'd10_10l':d10_10l,'d10_10l_h':d10_10l_h,
        'asc':SIGNS[asc_idx],'asc_idx':asc_idx,
        'dasha_md':md2,'sat_dist':sat_dist,'sat_ret':sat_ret,
        'shrinkhala_present':shrinkhala_present,'shrinkhala_max':shrinkhala_max,
        'raja':raja,'gk':gk,'ba':ba,'nbry':nbry_flag,
        'mp_yogas':mp_yogas,'mp_shrinkhala':mp_shrinkhala,'jup_house':jup_house,
    }


def chart_to_features(ch, FNAMES):
    p = ch['planets']; d9 = ch['d9']; fmap = {}
    for pn in P7:
        fmap[f'{pn}_H{p[pn]["house"]}'] = 1
        if p[pn]['dignity'] == 100: fmap[f'{pn}_ex_D1'] = 1
        if p[pn]['dignity'] == -100: fmap[f'{pn}_deb_D1'] = 1
        if p[pn]['dignity'] >= 75: fmap[f'{pn}_own_D1'] = 1
        if p[pn]['house'] in [1,4,7,10]: fmap[f'{pn}_kendra'] = 1
    for pn in P7:
        if pn in d9:
            if d9[pn]['dignity'] == 100: fmap[f'{pn}_ex_D9'] = 1
            if d9[pn]['dignity'] >= 75: fmap[f'{pn}_own_D9'] = 1
            if p[pn]['sign'] == d9[pn]['sign']: fmap[f'{pn}_varg'] = 1
    fmap['D10_Kendra'] = 1 if ch['d10_10l_h'] in [1,4,7,10] else 0
    fmap['D10_Dusthana'] = 1 if ch['d10_10l_h'] in [6,8,12] else 0
    fmap[f'{ch["dasha_md"]}_MD'] = 1
    fmap['GajKesari'] = ch['gk']; fmap['BudhaAditya'] = ch['ba']; fmap['Raja'] = ch['raja']
    fmap['Shrinkhala'] = ch['shrinkhala_present']; fmap['Shrinkhala_max'] = ch['shrinkhala_max']
    fmap['NBRY'] = ch['nbry']; fmap['Sat_Ret'] = ch['sat_ret']; fmap['MP_Shrinkhala'] = ch['mp_shrinkhala']
    for yn, val in ch['mp_yogas'].items(): fmap[yn] = val
    if ch['jup_house'] in [5, 9]: fmap[f'Jup_{ch["jup_house"]}H'] = 1
    vec = np.zeros(len(FNAMES), dtype=np.float32)
    for i, fn in enumerate(FNAMES): vec[i] = fmap.get(fn, 0)
    return vec


def detect_format(headers):
    if 'Full Name' in headers or 'Birth Date (YYYY-MM-DD)' in headers: return 'default'
    if 'Name' in headers and 'BirthDate' in headers: return 'consumer'
    return 'default'


def read_csv_rows(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f); headers = reader.fieldnames
        fmt = detect_format(headers); cm = COL_MAPS[fmt]
        rows = []
        for row in reader:
            name = row.get(cm['name'],'').strip()
            date = row.get(cm['date'],'').strip()
            city = row.get(cm['city'],'').strip()
            country = row.get(cm['country'],'').strip()
            if not date: continue
            rows.append({'name':name,'date':date,'city':city,'country':country})
    return rows, fmt


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_industry_csv.py <csv_path> [industry_label]"); sys.exit(1)
    csv_path = sys.argv[1]
    industry_label = sys.argv[2] if len(sys.argv) > 2 else 'UNKNOWN'
    IMAP = {'TECH':'TECH','LOGISTICS':'LOGISTICS','HOSPITALITY':'HOSPITALITY',
            'CREATIVE':'CREATIVE','RESEARCH':'RESEARCH','MARKETING':'MARKETING','CONSUMER':'MARKETING'}
    industry_code = IMAP.get(industry_label.upper(), 'UNKNOWN')
    print(f"=== NEXUS v3 Industry CSV Ingester ===")
    print(f"  File: {csv_path}  |  Label: {industry_label} → {industry_code}")

    v3_path = '/home/user/astrology/dataset/astro_v3_matrix.npz'
    v3 = np.load(v3_path, allow_pickle=True)
    X_old = v3['X']; industries_old = v3['industries']; sources_old = v3['sources']
    FNAMES = list(v3['feature_names']); q_mask_old = v3['q_mask']
    print(f"  Existing v3: {X_old.shape[0]} charts × {X_old.shape[1]} features")

    rows, fmt = read_csv_rows(csv_path)
    print(f"  Read {len(rows)} rows (format: {fmt})")

    new_X = []; errors = 0
    for i, row in enumerate(rows):
        try:
            lat, lon = geo_lookup(row['city'], row.get('country',''))
            ch = compute_chart(row['date'], lat, lon)
            vec = chart_to_features(ch, FNAMES)
            new_X.append(vec)
        except Exception as e:
            errors += 1
            if errors <= 5: print(f"  WARN row {i}: {row['name']} — {e}")

    print(f"  Computed: {len(new_X)} charts | Errors: {errors}")
    if not new_X: print("  No charts. Aborting."); sys.exit(1)

    X_new = np.array(new_X, dtype=np.float32)
    ind_new = np.array([industry_code] * len(new_X), dtype='<U11')
    src_new = np.array(['SYNTH'] * len(new_X), dtype='<U5')
    qm_new = np.zeros(len(new_X), dtype=bool)

    X_all = np.vstack([X_old, X_new])
    ind_all = np.concatenate([industries_old, ind_new])
    src_all = np.concatenate([sources_old, src_new])
    qm_all = np.concatenate([q_mask_old, qm_new])

    np.savez_compressed(v3_path, X=X_all, industries=ind_all, sources=src_all,
                        feature_names=np.array(FNAMES), q_mask=qm_all)

    print(f"\n=== SAVED: {X_all.shape[0]} charts × {X_all.shape[1]} features ===")
    print(f"  Sources: {dict(zip(*np.unique(src_all, return_counts=True)))}")
    print(f"  Industries: {dict(zip(*np.unique(ind_all, return_counts=True)))}")
    print(f"  Q-series: {qm_all.sum()} | Synthetic: {(~qm_all).sum()} | +{len(new_X)} from {os.path.basename(csv_path)}")


if __name__ == '__main__':
    main()
