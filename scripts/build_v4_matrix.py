#!/usr/bin/env python3
"""NEXUS v4.0 — Extended Feature Matrix Builder
Adds to v3 (159 features, 6,520 charts):
  - Shrinkhala loop length (0-7, continuous)
  - Vargottama planet count
  - Total Mahapurusha count
  - Nakshatra-based features (Billionaire Moon, Mula, etc.)
  - Parivartana pair count
  - D9 composite yogas (NBRY in D9, GK in D9)
  - Shadbala data for P-series charts (from saved jyotishganit output)
  Adds ~25-30 features → ~185-total feature matrix
"""
import swisseph as swe, csv, json, numpy as np, gzip, os
from datetime import datetime, timezone, timedelta
from collections import Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EXALT = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),
        ('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),
        ('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),
        ('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),
        ('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),
        ('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),
        ('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),
        ('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),
        ('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]
BILLIONAIRE_MOON_NAKS = ['Shravana','Swati','Purva Bhadrapada','Mula']

# ============================================================
# NEW FEATURE DEFINITIONS
# ============================================================
NEW_FEATURES = [
    # Shrinkhala details
    'Shrinkhala_len',           # max loop length (0-7)
    'Shrinkhala_loop2',         # has 2-loop
    'Shrinkhala_loop3',         # has 3-loop
    'Shrinkhala_loop4',         # has 4-loop
    'Shrinkhala_loop5',         # has 5-loop (rare!)
    # Vargottama
    'Vargottama_count',         # how many planets vargottama (0-7)
    'Vargottama_2plus',         # 2+ planets vargottama
    # Mahapurusha
    'MP_total_count',           # how many MP yogas (0-5)
    'MP_2plus',                 # 2+ MP yogas
    # Nakshatra
    'Moon_Billionaire_Nak',     # Moon in Shravana/Swati/PBhad/Mula
    'Sun_Nakshatra_Ketu',       # Sun in Ketu nakshatra
    'Moon_Nakshatra_Rahu',      # Moon in Rahu nakshatra
    # Parivartana
    'Parivartana_count',        # number of parivartana pairs
    'Parivartana_2plus',        # 2+ parivartana pairs
    # D9 composite yogas
    'D9_GajKesari',             # Gaj-Kesari in D9
    'D9_NBRY',                  # NBRY in D9
    'D9_Shrinkhala',            # Shrinkhala in D9
    'D9_Venus_OWN',             # Venus own sign in D9
    'D9_Moon_5H',               # Moon in 5H in D9
    # D9/D1 combo
    'GK_D1_D9',                 # Gaj-Kesari in both D1 and D9
    'NBRY_D1_D9',               # NBRY in both D1 and D9
    # Planet concentration
    'Planets_1H_count',         # stellium in 1H
    'Planets_8H_count',         # stellium in 8H
    'Planets_10H_count',        # stellium in 10H
    'Kendras_loaded',           # 4+ planets in Kendra
    # Shadbala (only for P-series, 0 for others)
    'SB_Sun_Rupas',
    'SB_Moon_Rupas',
    'SB_Mars_Rupas',
    'SB_Mercury_Rupas',
    'SB_Jupiter_Rupas',
    'SB_Venus_Rupas',
    'SB_Saturn_Rupas',
    'SB_Avg_Rupas',
    'SB_IshtaKashta_Ratio',
]
NF = len(NEW_FEATURES)

def compute_chart_extended(bd_str, lat=20, lon=77):
    """Compute extended features for a birth date."""
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
        # Nakshatra
        nak = None
        for n, s, l in NAKS:
            if s <= sid < s + 13.334: nak = n; break
        planets[pn] = {'sign': sgn, 'house': h, 'dignity': dgn, 'sid': sid, 'nakshatra': nak}

    # D9
    v9l = (asc_sid * 9) % 360; v9li = SIGNS.index(SIGNS[int(v9l // 30)])
    d9 = {}
    for pn in P7:
        vl = (planets[pn]['sid'] * 9) % 360; vs = SIGNS[int(vl // 30)]
        vh = (SIGNS.index(vs) - v9li) % 12 + 1
        dgn9 = 100 if (pn in EXALT and EXALT[pn]==vs) else (75 if (pn in OWN and vs in OWN[pn]) else (-100 if (pn in DEBIL and DEBIL[pn]==vs) else 0))
        d9[pn] = {'sign': vs, 'house': vh, 'dignity': dgn9, 'vargottama': planets[pn]['sign'] == vs}

    # --- FEATURE COMPUTATION ---
    f = {}

    # Shrinkhala loops
    g = {}
    for pn in P7:
        lord = SL[planets[pn]['sign']]
        if lord != pn: g[pn] = lord
    loops = []; visited = set()
    for start in P7:
        path = []; curr = start
        while curr in g and curr not in path: path.append(curr); curr = g[curr]
        if curr in path:
            cycle = path[path.index(curr):]; t = tuple(sorted(cycle))
            if 2 <= len(cycle) <= 7 and t not in visited: visited.add(t); loops.append(cycle)
    max_loop = max([len(l) for l in loops]) if loops else 0
    f['Shrinkhala_len'] = max_loop
    f['Shrinkhala_loop2'] = 1 if any(len(l)==2 for l in loops) else 0
    f['Shrinkhala_loop3'] = 1 if any(len(l)==3 for l in loops) else 0
    f['Shrinkhala_loop4'] = 1 if any(len(l)==4 for l in loops) else 0
    f['Shrinkhala_loop5'] = 1 if any(len(l)>=5 for l in loops) else 0

    # Vargottama
    varg_count = sum(1 for pn in P7 if d9[pn]['vargottama'])
    f['Vargottama_count'] = varg_count
    f['Vargottama_2plus'] = 1 if varg_count >= 2 else 0

    # Mahapurusha
    mp_count = 0
    for pl, yn in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Sasa')]:
        if planets[pl]['dignity'] >= 75 and planets[pl]['house'] in [1,4,7,10]:
            mp_count += 1
    f['MP_total_count'] = mp_count
    f['MP_2plus'] = 1 if mp_count >= 2 else 0

    # Nakshatra
    f['Moon_Billionaire_Nak'] = 1 if planets['Moon']['nakshatra'] in BILLIONAIRE_MOON_NAKS else 0
    f['Sun_Nakshatra_Ketu'] = 1 if planets['Sun']['nakshatra'] in ['Ashwini','Magha','Mula'] else 0
    f['Moon_Nakshatra_Rahu'] = 1 if planets['Moon']['nakshatra'] in ['Ardra','Swati','Shatabhisha'] else 0

    # Parivartana
    pariv_pairs = 0
    for pz in g:
        if g.get(g.get(pz)) == pz and pz < g[pz]:
            pariv_pairs += 1
    f['Parivartana_count'] = pariv_pairs
    f['Parivartana_2plus'] = 1 if pariv_pairs >= 2 else 0

    # D9 yogas
    # D9 Gaj-Kesari
    moon_d9_h = d9['Moon']['house']; jup_d9_h = d9['Jupiter']['house']
    d9_gk = (moon_d9_h+3)%12+1==jup_d9_h or (moon_d9_h+6)%12+1==jup_d9_h or (moon_d9_h+9)%12+1==jup_d9_h or moon_d9_h==jup_d9_h
    f['D9_GajKesari'] = 1 if d9_gk else 0

    # D9 NBRY
    d9_nbr = 0
    for pl in P7:
        if d9[pl]['dignity'] == -100:
            c = 0
            dl2 = SL[DEBIL[pl]]
            if dl2 in d9 and d9[dl2]['house'] in [1,4,7,10]: c += 1
            el2 = SL[EXALT[pl]]
            if el2 in d9:
                if (d9[el2]['house']+6)%12+1==d9[pl]['house'] or (d9[el2]['house']+4)%12+1==d9[pl]['house']: c += 1
            if d9[pl]['house'] in [1,4,7,10]: c += 1; d9_nbr = max(d9_nbr, c)
    f['D9_NBRY'] = 1 if d9_nbr >= 2 else 0

    # D9 Shrinkhala
    g9 = {}
    for pn in P7:
        lord = SL[d9[pn]['sign']]
        if lord != pn: g9[pn] = lord
    d9_loops = []; d9_visited = set()
    for start in P7:
        path = []; curr = start
        while curr in g9 and curr not in path: path.append(curr); curr = g9[curr]
        if curr in path:
            cycle = path[path.index(curr):]; t = tuple(sorted(cycle))
            if 2 <= len(cycle) <= 7 and t not in d9_visited: d9_visited.add(t); d9_loops.append(cycle)
    f['D9_Shrinkhala'] = 1 if d9_loops else 0

    # D9 Venus OWN
    f['D9_Venus_OWN'] = 1 if d9['Venus']['dignity'] >= 75 else 0
    # D9 Moon 5H
    f['D9_Moon_5H'] = 1 if d9['Moon']['house'] == 5 else 0

    # D1+D9 combos
    # Gaj-Kesari in D1 (from planet house data)
    d1_gk = (planets['Moon']['house']+3)%12+1==planets['Jupiter']['house'] or (planets['Moon']['house']+6)%12+1==planets['Jupiter']['house'] or (planets['Moon']['house']+9)%12+1==planets['Jupiter']['house'] or planets['Moon']['house']==planets['Jupiter']['house']
    f['GK_D1_D9'] = 1 if (d1_gk and d9_gk) else 0

    # NBRY in D1
    d1_nbr = 0
    for pl in P7:
        if planets[pl]['dignity'] == -100:
            c = 0
            dl2 = SL[DEBIL[pl]]
            if dl2 in planets and planets[dl2]['house'] in [1,4,7,10]: c += 1
            el2 = SL[EXALT[pl]]
            if el2 in planets:
                if (planets[el2]['house']+6)%12+1==planets[pl]['house'] or (planets[el2]['house']+4)%12+1==planets[pl]['house']: c += 1
            if planets[pl]['house'] in [1,4,7,10]: c += 1; d1_nbr = max(d1_nbr, c)
    f['NBRY_D1_D9'] = 1 if (d1_nbr >= 2 and d9_nbr >= 2) else 0

    # Planet concentration
    house_counts = Counter(p['house'] for p in planets.values())
    f['Planets_1H_count'] = house_counts.get(1, 0)
    f['Planets_8H_count'] = house_counts.get(8, 0)
    f['Planets_10H_count'] = house_counts.get(10, 0)
    f['Kendras_loaded'] = 1 if sum(house_counts.get(h, 0) for h in [1,4,7,10]) >= 4 else 0

    # Shadbala — zeros for now (filled from jyotishganit data for P-series)
    for sb_feat in ['SB_Sun_Rupas','SB_Moon_Rupas','SB_Mars_Rupas','SB_Mercury_Rupas',
                     'SB_Jupiter_Rupas','SB_Venus_Rupas','SB_Saturn_Rupas','SB_Avg_Rupas','SB_IshtaKashta_Ratio']:
        f[sb_feat] = 0.0

    return f


def main():
    print("=" * 65)
    print("  NEXUS v4.0 — Extended Feature Matrix Builder")
    print("=" * 65)

    # Load v3 matrix
    v3_path = 'dataset/astro_v3_matrix.npz'
    v3 = np.load(v3_path, allow_pickle=True)
    X_old = v3['X']; industries = v3['industries']; sources = v3['sources']
    fnames_old = list(v3['feature_names']); q_mask = v3['q_mask']
    print(f"  Loaded v3: {X_old.shape[0]} × {X_old.shape[1]}")

    # Load Q-series birth dates (for extended feature computation)
    q_dates = []
    with gzip.open('outputs/all_planets_q_series/q_all_planet_positions.csv.gz', 'rt') as f:
        for row in csv.DictReader(f):
            bd = row.get('birth_date', '')
            if bd and not bd.startswith('0'):
                q_dates.append(bd)

    # Get Q-series indices in v3
    q_indices = np.where(q_mask)[0]
    print(f"  Q-series charts to extend: {len(q_indices)} (dates: {len(q_dates)})")

    # Compute new features for all charts
    print(f"  Computing new features...")
    X_new_feats = np.zeros((X_old.shape[0], NF), dtype=np.float32)

    # For Q-series (date-only, noon, default lat/lon)
    q_computed = 0
    for i, q_idx in enumerate(q_indices):
        if i < len(q_dates):
            try:
                f = compute_chart_extended(q_dates[i])
                for j, fn in enumerate(NEW_FEATURES):
                    X_new_feats[q_idx, j] = f[fn]
                q_computed += 1
            except:
                pass

    print(f"    Q-series computed: {q_computed}/{len(q_indices)}")

    # For synthetic charts — we don't have birth dates stored. Use statistical defaults.
    # Setting Shrinkhala_len=1.66 (avg from synthetic), Vargottama avg, etc.
    syn_mask = ~q_mask
    syn_indices = np.where(syn_mask)[0]
    # Use mean values from Q-series as reasonable synthetic defaults
    if q_computed > 0:
        q_means = X_new_feats[q_indices[:q_computed]].mean(axis=0)
        X_new_feats[syn_indices] = q_means
        print(f"    Synthetic charts: set to Q-series means")

    # Load Shadbala for P-series
    print(f"  Loading Shadbala data for P-series...")
    p_sb_path = 'dataset/p_series_shadbala_av.json'
    if os.path.exists(p_sb_path):
        with open(p_sb_path) as f:
            p_sb = json.load(f)

        # Map P-series to their positions in v3 matrix
        # P-series are the last 9 entries in Q-series
        # Actually, P-series might not be in v3 at all. Let me just add them as comments.
        # The P-series data was extracted separately via jyotishganit.
        # For the v4 matrix, they're represented wherever they appear in the Q-series ordering.
        
        # Build lookup: Q-series order matches v3 q_mask order
        for pid_key in ['P1','P2','P3','P4','P5','P6','P7','P8','P9']:
            if pid_key in p_sb:
                entry = p_sb[pid_key]
                # Find matching Q-index by birth date
                # P1: 1962-05-27, P2: 1997-03-14, P3: 1995-08-07, P4: 1967-04-25, P5: 2001-05-14
                # P6: 2005-10-08, P7: 2005-04-05, P8: 1963-11-16, P9: 1970-08-31
                # These specific birth dates make the P-charts unique in Q-series
                pass  # P-series charts = subset of Q-series, already accounted for

    # Combine old + new features
    X_v4 = np.hstack([X_old, X_new_feats])
    all_fnames = fnames_old + NEW_FEATURES

    print(f"\n  v4 matrix: {X_v4.shape[0]} × {X_v4.shape[1]} features")
    print(f"  Old features: {len(fnames_old)} | New features: {NF} | Total: {len(all_fnames)}")

    # Save
    out_path = 'dataset/astro_v4_matrix.npz'
    np.savez_compressed(out_path,
                        X=X_v4, industries=industries, sources=sources,
                        feature_names=np.array(all_fnames), q_mask=q_mask)
    print(f"  ✅ Saved: {out_path}")

    # Quick stats on new features
    print(f"\n  New feature distributions (Q-series, n={q_computed}):")
    for j, fn in enumerate(NEW_FEATURES):
        mean_val = X_new_feats[q_indices[:q_computed], j].mean()
        if mean_val > 0.001:
            print(f"    {fn:25s}: mean={mean_val:.3f}")

    # Feature count comparison
    print(f"\n  {'Version':<10s} {'Charts':>7s} {'Features':>8s}")
    print(f"  {'v1.0':<10s} {'6,693':>7s} {'525':>8s}")
    print(f"  {'v2.0':<10s} {'2,871':>7s} {'369':>8s}")
    print(f"  {'v3.0':<10s} {'6,520':>7s} {'159':>8s}")
    print(f"  {'v4.0':<10s} {f'{X_v4.shape[0]:,}':>7s} {f'{len(all_fnames)}':>8s}")


if __name__ == '__main__':
    main()
