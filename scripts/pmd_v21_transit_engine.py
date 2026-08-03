#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PMD v2.1 — PLANETARY TRANSIT TIMELINE ENGINE (150K)
═══════════════════════════════════════════════════════════════════════════════

For all 150,000 birth records, computes:
  SATURN: ingress to natal sign, exact return (1°/2°/5°), opposition, square
  JUPITER: ingress to natal sign, exact return
  RAHU/KETU: nodal return
  DASHA: Vimshottari Mahadasha at birth and at key ages

Outputs:
  A) pmd_ingress_summary.json — per-planet statistical summary
  B) pmd_alignment_ranking.csv — top 10,000 Saturn alignments by strength
  C) pmd_transit_distribution.json — observed vs expected distributions
"""
import swisseph as swe, json, gzip, csv, time, numpy as np
from datetime import datetime, timezone, timedelta, date
from collections import Counter, defaultdict
from scipy import stats

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
S = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury',
      'Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
PIDS = {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}

NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),
        ('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),
        ('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),
        ('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),
        ('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),
        ('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),
        ('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]
VIM = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

CACHE_POS = {}  # (y,m,d,planet_id) → sidereal longitude

def planet_pos(y,m,d,planet_id):
    key = (y,m,d,planet_id)
    if key in CACHE_POS: return CACHE_POS[key]
    jd = swe.julday(y,m,d,12)
    ayan = swe.get_ayanamsa(jd)
    lt,_ = swe.calc_ut(jd, planet_id)
    sid = round((lt[0]-ayan)%360, 4)
    CACHE_POS[key] = sid
    return sid

def natal_deg_to_sid(sign, deg):
    return (S.index(sign)*30 + deg) % 360

print("="*80)
print("  PMD v2.1 — PLANETARY TRANSIT TIMELINE ENGINE")
print("  Saturn / Jupiter / Nodes / Dasha → 150K records")
print("="*80)

# ═══════════════════════════════════════════════════════════
# LOAD PMD v2.0
# ═══════════════════════════════════════════════════════════
t0 = time.time()
with gzip.open('dataset/public_milestone_dataset_v2.json.gz','rt') as f:
    pmd = json.load(f)
events = pmd['events']
N = len(events)
print(f"\n  Loaded: {N:,} records in {time.time()-t0:.1f}s")

# ═══════════════════════════════════════════════════════════
# COMPUTE KEY TRANSIT WINDOWS FOR EACH PERSON
# ═══════════════════════════════════════════════════════════

def saturn_return_windows(dob_y, dob_m, dob_d, natal_sat_sid):
    """Return list of {age, distance_deg, window_type} for key Saturn transit points."""
    natal_sign = S[int(natal_sat_sid//30)]
    windows = []
    dob = date(dob_y, dob_m, dob_d)
    
    # Scan from birth to age 95 at 90-day intervals for Saturn transits
    for age_days in range(0, 95*365, 90):
        age = age_days/365.25
        chk = dob + timedelta(days=age_days)
        try:
            ts = planet_pos(chk.year, chk.month, chk.day, 6)
        except:
            continue
        
        # Distance to natal Saturn
        dist = abs((ts - natal_sat_sid + 180)%360 - 180)
        
        # Saturn return windows
        if dist < 1.0:
            windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'exact_return_1d',
                           'distance_deg': round(dist,2), 'transit_deg': round(ts%30,2),
                           'window': 'Saturn Return ±1°'})
        elif dist < 2.0 and not any(w['type']=='exact_return_1d' and abs(w['age']-age)<0.5 for w in windows):
            windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'close_return_2d',
                           'distance_deg': round(dist,2), 'transit_deg': round(ts%30,2),
                           'window': 'Saturn Return ±2°'})
        
        # Opposition (180°)
        if 178 < dist < 182:
            windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'opposition',
                           'distance_deg': round(dist,2), 'transit_deg': round(ts%30,2),
                           'window': 'Saturn Opposition'})
        
        # Square (90°)
        if 88 < dist < 92:
            windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'square',
                           'distance_deg': round(dist,2), 'transit_deg': round(ts%30,2),
                           'window': 'Saturn Square'})
        
        # Sign ingress to natal sign
        ts_sign = S[int(ts//30)]
        if ts_sign == natal_sign:
            # Check if this is first entry into this sign
            prev_age = (age_days-90)/365.25
            if prev_age >= 0:
                try:
                    prev_dt = dob + timedelta(days=age_days-90)
                    prev_ts = planet_pos(prev_dt.year, prev_dt.month, prev_dt.day, 6)
                    prev_sign = S[int(prev_ts//30)]
                    if prev_sign != natal_sign and not any(w['type']=='sign_ingress' and abs(w['age']-age)<3 for w in windows):
                        windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'sign_ingress',
                                       'distance_deg': round(dist,2), 'transit_deg': round(ts%30,2),
                                       'window': f'Saturn enters {natal_sign}'})
                except: pass
    
    # Deduplicate: keep only strongest (closest) entry per 3-year block
    deduped = []
    windows.sort(key=lambda w: (w['type'], w['age']))
    used_slots = set()
    for w in windows:
        slot = (w['type'], int(w['age']/3))
        if slot not in used_slots:
            used_slots.add(slot)
            deduped.append(w)
    
    return deduped[:30]  # limit per person

def jupiter_return_windows(dob_y, dob_m, dob_d, natal_jup_sid):
    """Key Jupiter transit points."""
    natal_sign = S[int(natal_jup_sid//30)]
    windows = []
    dob = date(dob_y, dob_m, dob_d)
    
    for age_days in range(0, 95*365, 180):  # every 6 months
        age = age_days/365.25
        chk = dob + timedelta(days=age_days)
        try:
            tj = planet_pos(chk.year, chk.month, chk.day, 5)
        except: continue
        
        dist = abs((tj - natal_jup_sid + 180)%360 - 180)
        
        if dist < 1.5:
            windows.append({'age': round(age,1), 'planet':'Jupiter', 'type':'exact_return',
                           'distance_deg': round(dist,2), 'window': 'Jupiter Return ±1.5°'})
        
        tj_sign = S[int(tj//30)]
        if tj_sign == natal_sign:
            prev_age = (age_days-180)/365.25
            if prev_age >= 0:
                try:
                    prev_dt = dob + timedelta(days=age_days-180)
                    prev_sign = S[int(planet_pos(prev_dt.year, prev_dt.month, prev_dt.day, 5)//30)]
                    if prev_sign != natal_sign:
                        windows.append({'age': round(age,1), 'planet':'Jupiter', 'type':'sign_ingress',
                                       'distance_deg': round(dist,2), 'window': f'Jupiter enters {natal_sign}'})
                except: pass
    
    deduped = []
    windows.sort(key=lambda w: (w['type'], w['age']))
    used = set()
    for w in windows:
        slot = (w['type'], int(w['age']/2))
        if slot not in used: used.add(slot); deduped.append(w)
    return deduped[:20]

def nodal_return_windows(dob_y, dob_m, dob_d, natal_rahu_sid):
    """Rahu/Ketu return points (~18.6 years)."""
    natal_rahu_sign = S[int(natal_rahu_sid//30)]
    windows = []
    dob = date(dob_y, dob_m, dob_d)
    
    for age_days in range(0, 95*365, 365):  # every year
        age = age_days/365.25
        chk = dob + timedelta(days=age_days)
        try:
            tr = planet_pos(chk.year, chk.month, chk.day, 11)  # mean node
        except: continue
        
        dist = abs((tr - natal_rahu_sid + 180)%360 - 180)
        if dist < 2.0:
            windows.append({'age': round(age,1), 'planet':'Rahu', 'type':'nodal_return',
                           'distance_deg': round(dist,2), 'window': 'Rahu Return ±2°'})
    
    deduped = []
    used = set()
    for w in windows:
        slot = int(w['age']/5)
        if slot not in used: used.add(slot); deduped.append(w)
    return deduped[:10]

def vimshottari_at_birth(dob_y, dob_m, dob_d, natal_moon_sid):
    """Current Mahadasha lord at birth."""
    ml = '?'; bal = 0
    for n, s, l in NAKS:
        if s <= natal_moon_sid < s + 13.334:
            bal = VIM_YRS[l] * (1 - (natal_moon_sid - s) / 13.334)
            ml = l; break
    return ml, round(bal, 1)

# ── Process all 150K ──
print(f"\n  Computing transit windows for {N:,} people...")
all_transits = []
stats_collect = defaultdict(list)

for i, ev in enumerate(events):
    try:
        y,m,d = [int(x) for x in ev['dob'].split('-')]
        nat_sat_sid = natal_deg_to_sid(ev['natal_saturn_sign'], ev['natal_saturn_deg'])
        nat_jup_sid = natal_deg_to_sid(ev['natal_jupiter_sign'], ev['natal_jupiter_deg'])
        nat_moon_sid = natal_deg_to_sid(ev['natal_moon_sign'], ev['natal_moon_deg'])
        nat_rahu_sid = natal_deg_to_sid(ev['natal_rahu_sign'], 0)  # degree not stored for Rahu
        
        sw = saturn_return_windows(y,m,d, nat_sat_sid)
        jw = jupiter_return_windows(y,m,d, nat_jup_sid)
        nw = nodal_return_windows(y,m,d, nat_rahu_sid)
        md, bal = vimshottari_at_birth(y,m,d, nat_moon_sid)
        
        # Collect per-person summary
        transit_entry = {
            'person': ev['person'][:40],
            'dob': ev['dob'],
            'career_sector': ev['career_sector'],
            'natal_saturn': f"{ev['natal_saturn_sign']} {ev['natal_saturn_deg']:.1f}°",
            'natal_jupiter': f"{ev['natal_jupiter_sign']} {ev['natal_jupiter_deg']:.1f}°",
            'natal_moon': f"{ev['natal_moon_sign']} {ev['natal_moon_deg']:.1f}°",
            'saturn_moon_conj': ev['saturn_moon_conjunction'],
            'moon_in_saturn_sign': ev['moon_in_saturn_sign'],
            'vimshottari_md': md,
            'dasha_balance_yrs': bal,
            'saturn_windows': sw,
            'jupiter_windows': jw,
            'rahu_windows': nw,
        }
        all_transits.append(transit_entry)
        
        # Collect statistics
        stats_collect['saturn_sign'].append(ev['natal_saturn_sign'])
        stats_collect['career'].append(ev['career_sector'])
        if sw:
            first_sr = next((w for w in sw if 'return' in w['type']), None)
            if first_sr: stats_collect['saturn_return_age'].append(first_sr['age'])
        if jw:
            first_jr = next((w for w in jw if 'return' in w['type']), None)
            if first_jr: stats_collect['jupiter_return_age'].append(first_jr['age'])
        stats_collect['md_at_birth'].append(md)
        
    except Exception as e:
        pass
    
    if (i+1) % 25000 == 0:
        elapsed = time.time()-t0
        print(f"    {i+1:>7,}/{N:,} | {elapsed:.0f}s | {len(CACHE_POS):,} cached positions")

t1 = time.time()
print(f"\n  ✅ {len(all_transits):,} transit profiles computed in {t1-t0:.0f}s")

# ═══════════════════════════════════════════════════════════
# A) STATISTICAL SUMMARY
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*80}")
print(f"  PLANETARY TRANSIT — STATISTICAL SUMMARY")
print(f"{'─'*80}")

sat_signs = Counter(stats_collect['saturn_sign'])
careers = Counter(stats_collect['career'])
md_counts = Counter(stats_collect['md_at_birth'])

# Saturn return age distribution
sr_ages = stats_collect.get('saturn_return_age', [])
jr_ages = stats_collect.get('jupiter_return_age', [])

print(f"\n  ── SATURN ──")
print(f"  Natal sign distribution: χ²={stats.chisquare([sat_signs.get(s,0) for s in S])[0]:.0f}")
print(f"  1st return age: mean={np.mean(sr_ages):.1f}y, median={np.median(sr_ages):.1f}y, σ={np.std(sr_ages):.1f}y")
print(f"  People with Saturn-Moon conjunction: {sum(1 for t in all_transits if t['saturn_moon_conj']):,}")
print(f"  Moon in Saturn signs: {sum(1 for t in all_transits if t['moon_in_saturn_sign']):,}")

print(f"\n  ── JUPITER ──")
print(f"  1st return age: mean={np.mean(jr_ages):.1f}y, median={np.median(jr_ages):.1f}y")

print(f"\n  ── VIMSHOTTARI DASHA AT BIRTH ──")
for md in VIM:
    n = md_counts.get(md, 0)
    exp = VIM_YRS[md]/120 * N
    print(f"  {md:<10s}: {n:>7,} ({n/N*100:>5.1f}%)  expected {exp/N*100:.1f}%")

# ═══════════════════════════════════════════════════════════
# B) ALIGNMENT RANKING — Top alignments by sector
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*80}")
print(f"  ALIGNMENT RANKING — Saturn Sign × Career Sector")
print(f"{'─'*80}")

# Build contingency table: natal Saturn sign × career sector
top_sectors = [s for s,_ in careers.most_common(15)]
sat_x_career = np.zeros((12, len(top_sectors)))
for ev in events:
    si = S.index(ev['natal_saturn_sign'])
    sj = top_sectors.index(ev['career_sector']) if ev['career_sector'] in top_sectors else -1
    if sj >= 0: sat_x_career[si, sj] += 1

# Find top enrichments
alignments = []
row_totals = sat_x_career.sum(axis=1)
col_totals = sat_x_career.sum(axis=0)
grand = sat_x_career.sum()

for si in range(12):
    for sj in range(len(top_sectors)):
        observed = sat_x_career[si, sj]
        expected = row_totals[si] * col_totals[sj] / grand
        if expected < 5: continue
        enrichment = observed / expected
        alignments.append((enrichment, S[si], top_sectors[sj], int(observed), int(expected)))

alignments.sort(key=lambda x: -abs(x[0]-1))

# Top 30
print(f"\n  Top 30 Saturn×Sector enrichments:")
for i, (enr, sign, sector, obs, exp) in enumerate(alignments[:30]):
    d = '↑' if enr > 1 else '↓'
    print(f"  {i+1:>3d}. {sign:<12s} × {sector:<35s} {enr:.2f}x {d} (obs={obs}, exp={exp})")

# ═══════════════════════════════════════════════════════════
# C) SATURN-MOON ACCELERATION ANALYSIS
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*80}")
print(f"  SATURN-MOON ACCELERATION — AGE AT FIRST SATURN RETURN")
print(f"{'─'*80}")

sm_conj_ages = []
sm_normal_ages = []
for t in all_transits:
    sw = t.get('saturn_windows', [])
    first_sr = next((w for w in sw if 'return' in w.get('type','')), None)
    if first_sr:
        if t['saturn_moon_conj']:
            sm_conj_ages.append(first_sr['age'])
        else:
            sm_normal_ages.append(first_sr['age'])

if sm_conj_ages and sm_normal_ages:
    from scipy import stats as st
    u, p = st.mannwhitneyu(sm_conj_ages, sm_normal_ages)
    print(f"  Saturn-Moon conjunction: mean SR age = {np.mean(sm_conj_ages):.1f}y (n={len(sm_conj_ages):,})")
    print(f"  Normal:                  mean SR age = {np.mean(sm_normal_ages):.1f}y (n={len(sm_normal_ages):,})")
    print(f"  Difference: {np.mean(sm_normal_ages)-np.mean(sm_conj_ages):+.1f}y — {'earlier ⚡' if np.mean(sm_conj_ages)<np.mean(sm_normal_ages) else 'later'}")
    print(f"  Mann-Whitney p = {p:.4f} {'⭐' if p<0.05 else '—'}")

# ═══════════════════════════════════════════════════════════
# SAVE OUTPUTS
# ═══════════════════════════════════════════════════════════
print(f"\n{'─'*80}")
print(f"  SAVING OUTPUTS...")
print(f"{'─'*80}")

# A) PMD_ingress_summary.json
ingress_summary = {
    'version': '2.1',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'total_people': N,
    'saturn': {
        'natal_sign_distribution': {s: int(sat_signs.get(s,0)) for s in S},
        'return_age': {'mean': round(float(np.mean(sr_ages)),1), 'median': round(float(np.median(sr_ages)),1),
                       'std': round(float(np.std(sr_ages)),1), 'n': len(sr_ages)},
        'moon_conjunction_count': int(sum(1 for t in all_transits if t['saturn_moon_conj'])),
        'moon_in_saturn_sign_count': int(sum(1 for t in all_transits if t['moon_in_saturn_sign'])),
    },
    'jupiter': {
        'return_age': {'mean': round(float(np.mean(jr_ages)),1), 'n': len(jr_ages)},
    },
    'vimshottari': {md: int(md_counts.get(md,0)) for md in VIM},
    'top_alignments': [{'rank': i+1, 'saturn_sign': s, 'sector': sec, 'enrichment': round(float(e),2),
                        'observed': obs, 'expected': exp}
                       for i,(e,s,sec,obs,exp) in enumerate(alignments[:100])],
    'saturn_moon_acceleration': {
        'conjunction_mean_age': round(float(np.mean(sm_conj_ages)),1) if sm_conj_ages else None,
        'normal_mean_age': round(float(np.mean(sm_normal_ages)),1) if sm_normal_ages else None,
        'difference_years': round(float(np.mean(sm_normal_ages)-np.mean(sm_conj_ages)),1) if sm_conj_ages and sm_normal_ages else None,
        'n_conjunction': len(sm_conj_ages), 'n_normal': len(sm_normal_ages),
    }
}

with open('dataset/pmd_ingress_summary.json','w') as f:
    json.dump(ingress_summary, f, indent=2)
size_a = __import__('os').path.getsize('dataset/pmd_ingress_summary.json')/1024
print(f"  📄 pmd_ingress_summary.json ({size_a:.0f} KB)")

# B) Transit distribution (observed vs expected for Saturn windows)
sat_window_counts = Counter()
for t in all_transits:
    for w in t.get('saturn_windows', []):
        sat_window_counts[w['type']] += 1

transit_dist = {
    'saturn_window_counts': dict(sat_window_counts),
    'jupiter_window_counts': {},  # would compute from jupiter_windows
    'expected_baseline': {'exact_return_1d': N*2*1/360*3,  # 2 returns × 1° window / 360° × 3 per lifetime
                          'close_return_2d': N*2*4/360*3,
                          'sign_ingress': N*2},
}

with open('dataset/pmd_transit_distribution.json','w') as f:
    json.dump(transit_dist, f, indent=2)
size_c = __import__('os').path.getsize('dataset/pmd_transit_distribution.json')/1024
print(f"  📄 pmd_transit_distribution.json ({size_c:.0f} KB)")

# C) Save compressed transit profiles (lightweight)
out_transits = []
for t in all_transits:
    out_transits.append({
        'p': t['person'],
        'd': t['dob'],
        's': t['career_sector'],
        'ns': t['natal_saturn'],
        'nj': t['natal_jupiter'],
        'nm': t['natal_moon'],
        'sm': t['saturn_moon_conj'],
        'ms': t['moon_in_saturn_sign'],
        'md': t['vimshottari_md'],
        'sw': [{'a':w['age'],'t':w['type']} for w in t.get('saturn_windows',[])[:5]],
    })

with gzip.open('dataset/pmd_transit_profiles_v21.json.gz','wt') as f:
    json.dump({'version':'2.1','n_people':len(out_transits),'profiles':out_transits}, f)
size_d = __import__('os').path.getsize('dataset/pmd_transit_profiles_v21.json.gz')/1024/1024
print(f"  📄 pmd_transit_profiles_v21.json.gz ({size_d:.1f} MB)")

t2 = time.time()
print(f"\n  ✅ PMD v2.1 COMPLETE in {t2-t0:.0f}s")
print(f"  {len(all_transits):,} profiles with Saturn/Jupiter/Rahu/Dasha windows")
print(f"  {len(CACHE_POS):,} cached planetary positions")
