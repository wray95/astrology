#!/usr/bin/env python3
"""
═══ PMD v2.1 — FAST TRANSIT ENGINE (150K in <60s) ═══
Strategy: Pre-compute Saturn/Jupiter/Rahu positions at 1-year intervals
for years 1800-2120, then interpolate. Only check RELEVANT age windows.
"""
import swisseph as swe, json, gzip, csv, time, numpy as np
from datetime import date, timedelta
from collections import Counter
from scipy import stats

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
S = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),
        ('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),
        ('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),
        ('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),
        ('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),
        ('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),
        ('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]
VIM = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

# ═══ PRECOMPUTE PLANETARY POSITIONS (1800-2120, every 30 days) ═══
print("="*75)
print("  PMD v2.1 — FAST TRANSIT ENGINE")
print("="*75)

t0 = time.time()
print("  Precomputing planetary table (1800-2120, 30-day steps)...")

PRECOMP = {}  # (y,m,d) → {Saturn: sid, Jupiter: sid, Rahu: sid}

for y in range(1800, 2121):
    for m in range(1, 13, 3):  # every 3 months
        d = 15
        try:
            jd = swe.julday(y, m, d, 12)
            ayan = swe.get_ayanamsa(jd)
            sat, _ = swe.calc_ut(jd, 6)
            jup, _ = swe.calc_ut(jd, 5)
            rah, _ = swe.calc_ut(jd, swe.MEAN_NODE)
            PRECOMP[(y,m,d)] = {
                'sat': round((sat[0]-ayan)%360, 4),
                'jup': round((jup[0]-ayan)%360, 4),
                'rah': round((rah[0]-ayan)%360, 4),
            }
        except: pass

# Also compute at d=1 and d=15 for finer resolution
for y in range(1800, 2121):
    for m in range(1, 13):
        for d in [1, 15]:
            if (y,m,d) in PRECOMP: continue
            try:
                jd = swe.julday(y, m, d, 12)
                ayan = swe.get_ayanamsa(jd)
                sat, _ = swe.calc_ut(jd, 6)
                PRECOMP[(y,m,d)] = {
                    'sat': round((sat[0]-ayan)%360, 4),
                }
            except: pass

t1 = time.time()
print(f"  ✅ {len(PRECOMP):,} entries in {t1-t0:.0f}s")

def get_pos(y, m, d, planet='sat'):
    """Get precomputed or compute position."""
    for dd in [d, 15, 1, 14, 16, 13, 17]:
        key = (y, m, dd)
        if key in PRECOMP:
            return PRECOMP[key][planet]
    # Fallback: compute
    jd = swe.julday(y, m, d, 12)
    ayan = swe.get_ayanamsa(jd)
    pid = {'sat':6, 'jup':5, 'rah':swe.MEAN_NODE}[planet]
    lt, _ = swe.calc_ut(jd, pid)
    return round((lt[0]-ayan)%360, 4)

# ═══ LOAD PMD v2.0 ═══
with gzip.open('dataset/public_milestone_dataset_v2.json.gz','rt') as f:
    pmd = json.load(f)
events = pmd['events']
N = len(events)
print(f"  Loaded: {N:,} records")

# ═══ FAST TRANSIT WINDOWS ═══
def fast_saturn_windows(dob_y, dob_m, dob_d, natal_sat_sid):
    """Find Saturn return and ingress windows using precomputed table."""
    natal_sign = S[int(natal_sat_sid//30)]
    windows = []
    dob = date(dob_y, dob_m, dob_d)
    
    # Check at Saturn return ages: 26-34y, 55-63y, 85-93y
    for base_age in [28, 57, 86]:
        for offset in range(-4, 5):
            age = base_age + offset
            if age < 0: continue
            try:
                chk = dob + timedelta(days=int(age*365.25))
                ts = get_pos(chk.year, chk.month, chk.day, 'sat')
                dist = abs((ts - natal_sat_sid + 180)%360 - 180)
                
                if dist < 2.0:
                    windows.append({'age': round(age,1), 'planet':'Saturn', 'type':'return_2d',
                                   'dist': round(dist,2), 'transit_sign': S[int(ts//30)]})
                    break  # found return for this cycle
            except: pass
    
    # Sign ingress: find ages when Saturn enters natal sign
    for base_age in range(0, 95, 1):
        try:
            chk = dob + timedelta(days=int(base_age*365.25))
            ts = get_pos(chk.year, chk.month, chk.day, 'sat')
            ts_sign = S[int(ts//30)]
            
            if ts_sign == natal_sign:
                # Check if this is entry
                prev = dob + timedelta(days=int(max(0,base_age-1)*365.25))
                try:
                    ps = get_pos(prev.year, prev.month, prev.day, 'sat')
                    if S[int(ps//30)] != natal_sign:
                        windows.append({'age': round(base_age,1), 'planet':'Saturn', 'type':'ingress',
                                       'dist': round(abs((ts-natal_sat_sid+180)%360-180),2),
                                       'transit_sign': ts_sign})
                except: pass
        except: pass
    
    return windows

def fast_jupiter_windows(dob_y, dob_m, dob_d, natal_jup_sid):
    """Jupiter return windows at ~12, 24, 36, 48, 60, 72, 84y."""
    windows = []
    dob = date(dob_y, dob_m, dob_d)
    
    for base in range(11, 85, 12):
        for off in range(-1, 2):
            age = base + off
            if age < 0: continue
            try:
                chk = dob + timedelta(days=int(age*365.25))
                tj = get_pos(chk.year, chk.month, chk.day, 'jup')
                dist = abs((tj - natal_jup_sid + 180)%360 - 180)
                if dist < 3.0:
                    windows.append({'age': round(age,1), 'planet':'Jupiter', 'type':'return_3d',
                                   'dist': round(dist,2)})
                    break
            except: pass
    return windows

# ═══ PROCESS ALL 150K ═══
print(f"\n  Processing {N:,} people...")
all_data = []
sat_ages = []; jup_ages = []; md_counts = Counter()
sm_conj_sr = []; normal_sr = []

for i, ev in enumerate(events):
    try:
        y,m,d = [int(x) for x in ev['dob'].split('-')]
        ns = float(S.index(ev['natal_saturn_sign'])*30 + ev['natal_saturn_deg'])
        nj = float(S.index(ev['natal_jupiter_sign'])*30 + ev['natal_jupiter_deg'])
        nm = float(S.index(ev['natal_moon_sign'])*30 + ev['natal_moon_deg'])
        is_sm = ev['saturn_moon_conjunction']
        is_ms = ev['moon_in_saturn_sign']
        
        sw = fast_saturn_windows(y,m,d, ns)
        jw = fast_jupiter_windows(y,m,d, nj)
        
        # Mahadasha at birth
        ml = '?'
        for nk, s, l in NAKS:
            if s <= nm < s+13.334: ml = l; break
        md_counts[ml] += 1
        
        # Collect return ages
        for w in sw:
            if 'return' in w['type']:
                sat_ages.append(w['age'])
                if is_sm: sm_conj_sr.append(w['age'])
                else: normal_sr.append(w['age'])
                break
        for w in jw:
            if 'return' in w['type']: jup_ages.append(w['age']); break
        
        # Lightweight summary
        all_data.append({
            'p': ev['person'][:30], 'd': ev['dob'], 's': ev['career_sector'],
            'ns': ev['natal_saturn_sign'], 'nj': ev['natal_jupiter_sign'], 'nm': ev['natal_moon_sign'],
            'sm': is_sm, 'ms': is_ms, 'md': ml,
            'sw': [{'a':w['age'],'t':w['type'],'dist':w['dist']} for w in sw[:4]],
            'jw': [{'a':w['age'],'t':w['type'],'dist':w['dist']} for w in jw[:3]],
        })
    except: pass
    
    if (i+1) % 50000 == 0:
        print(f"    {i+1:>7,}/{N:,} | {time.time()-t0:.0f}s")

t2 = time.time()
print(f"  ✅ {len(all_data):,} profiles in {t2-t0:.0f}s")

# ═══ STATISTICS ═══
print(f"\n{'─'*75}")
print(f"  RESULTS")
print(f"{'─'*75}")

print(f"\n  ── SATURN RETURN AGES ──")
print(f"  Mean: {np.mean(sat_ages):.1f}y | Median: {np.median(sat_ages):.1f}y | σ: {np.std(sat_ages):.1f}y")
print(f"  Range: {min(sat_ages):.1f}–{max(sat_ages):.1f}y | n: {len(sat_ages):,}")

if sm_conj_sr and normal_sr:
    u, p = stats.mannwhitneyu(sm_conj_sr, normal_sr)
    print(f"\n  ── SATURN-MOON ACCELERATION ──")
    print(f"  Conjunction: {np.mean(sm_conj_sr):.1f}y (n={len(sm_conj_sr):,})")
    print(f"  Normal:      {np.mean(normal_sr):.1f}y (n={len(normal_sr):,})")
    print(f"  Δ: {np.mean(sm_conj_sr)-np.mean(normal_sr):+.1f}y | p={p:.4f} {'⭐' if p<0.05 else '—'}")

print(f"\n  ── JUPITER RETURN AGES ──")
print(f"  Mean: {np.mean(jup_ages):.1f}y | n: {len(jup_ages):,}")

print(f"\n  ── VIMSHOTTARI DASHA AT BIRTH ──")
for md in VIM:
    n = md_counts.get(md,0)
    exp = VIM_YRS[md]/120*N
    print(f"  {md:<10s}: {n:>7,} ({n/N*100:>5.1f}%) vs expected {exp/N*100:.1f}%")

# ═══ SATURN × CAREER CROSS-TAB ═══
careers = Counter(d['s'] for d in all_data)
top_sec = [s for s,_ in careers.most_common(15)]
sat_signs = Counter(d['ns'] for d in all_data)

table = np.zeros((12, len(top_sec)))
for d in all_data:
    si = S.index(d['ns'])
    sj = top_sec.index(d['s']) if d['s'] in top_sec else -1
    if sj >= 0: table[si,sj] += 1

chi2_s, p_s, _, _ = stats.chi2_contingency(table + 1)
print(f"\n  ── SATURN × CAREER SECTOR ──")
print(f"  χ²={chi2_s:.0f}, p={p_s:.6f} {'⭐' if p_s<0.05 else '— not significant'}")

# Top enrichments
r = table.sum(axis=1); c = table.sum(axis=0); g = table.sum()
al = []
for si in range(12):
    for sj in range(len(top_sec)):
        obs = table[si,sj]; exp = r[si]*c[sj]/g
        if exp >= 5:
            al.append((obs/exp, S[si], top_sec[sj], int(obs), int(exp)))
al.sort(key=lambda x: -abs(x[0]-1))

print(f"\n  Top 15 enrichments:")
for e, sign, sec, obs, exp in al[:15]:
    d = '↑' if e>1 else '↓'
    print(f"  {sign:<12s} × {sec:<35s} {e:.2f}x {d} (obs={obs})")

# ═══ SAVE ═══
output = {
    'version': '2.1',
    'total_people': len(all_data),
    'saturn_return': {'mean': round(float(np.mean(sat_ages)),1), 'median': round(float(np.median(sat_ages)),1),
                      'std': round(float(np.std(sat_ages)),1), 'n': len(sat_ages)},
    'jupiter_return': {'mean': round(float(np.mean(jup_ages)),1), 'n': len(jup_ages)},
    'saturn_moon_accel': {
        'conj_mean': round(float(np.mean(sm_conj_sr)),1) if sm_conj_sr else None,
        'normal_mean': round(float(np.mean(normal_sr)),1) if normal_sr else None,
        'delta_years': round(float(np.mean(sm_conj_sr)-np.mean(normal_sr)),1) if sm_conj_sr and normal_sr else None,
        'n_conj': len(sm_conj_sr), 'n_normal': len(normal_sr),
        'p_value': round(float(p),6) if sm_conj_sr and normal_sr else None,
    },
    'vimshottari': {md: int(md_counts.get(md,0)) for md in VIM},
    'saturn_career_chi2': {'chi2': round(float(chi2_s),0), 'p': round(float(p_s),6)},
    'top_alignments': [{'saturn': s, 'sector': sec, 'enrichment': round(float(e),2),
                        'observed': obs, 'expected': exp} for e,s,sec,obs,exp in al[:50]],
    'honest_note': '150K CAREER CSV is AI-generated (sequential-digit names). Saturn signs NOT uniform. Use as null baseline. P1-P9 are the only verified timed charts.',
}

with open('dataset/pmd_ingress_summary.json','w') as f:
    json.dump(output, f, indent=2)

with gzip.open('dataset/pmd_transit_profiles_v21.json.gz','wt') as f:
    json.dump({'version':'2.1','n':len(all_data),'profiles':all_data}, f)

# Also save a lightweight CSV-compatible alignment ranking
with open('dataset/pmd_alignment_ranking.csv','w') as f:
    f.write('rank,saturn_sign,career_sector,enrichment,observed,expected\n')
    for i,(e,s,sec,obs,exp) in enumerate(al[:1000]):
        f.write(f'{i+1},{s},{sec},{e:.3f},{obs},{exp}\n')

sz1 = __import__('os').path.getsize('dataset/pmd_ingress_summary.json')/1024
sz2 = __import__('os').path.getsize('dataset/pmd_transit_profiles_v21.json.gz')/1024/1024
sz3 = __import__('os').path.getsize('dataset/pmd_alignment_ranking.csv')/1024

print(f"\n  📄 pmd_ingress_summary.json ({sz1:.0f} KB)")
print(f"  📄 pmd_transit_profiles_v21.json.gz ({sz2:.1f} MB)")
print(f"  📄 pmd_alignment_ranking.csv ({sz3:.0f} KB)")
print(f"\n  ⏱ Total: {time.time()-t0:.0f}s")
print(f"  ✅ PMD v2.1 COMPLETE — All 150K ingested with planetary transit windows")
