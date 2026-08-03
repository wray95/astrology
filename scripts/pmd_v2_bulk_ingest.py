#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
PMD v2.0 — BULK INGEST: 150K CAREER CSV → PUBLIC MILESTONE DATASET
═══════════════════════════════════════════════════════════════════════════════

Ingests all 150,000 birth dates from the career CSV.
Computes natal Saturn, Jupiter, Moon, Rahu positions (pyswisseph, Lahiri).
Saves to compressed JSON (PMD v2.0).
Each person = one row with career sector as event.
"""
import swisseph as swe, json, gzip, csv, time, numpy as np
from datetime import datetime, timezone, timedelta, date

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
S = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# Cache: computed positions by (y,m,d) to avoid recomputing same dates
cache = {}

def natal_planets(y, m, d):
    """Get sidereal (Lahiri) positions for all 7 planets + Rahu."""
    key = (y, m, d)
    if key in cache:
        return cache[key]
    
    jd = swe.julday(y, m, d, 12)
    ayan = swe.get_ayanamsa(jd)
    
    result = {}
    for pn, pid in [('Sun',0),('Moon',1),('Mars',4),('Mercury',2),('Jupiter',5),('Venus',3),('Saturn',6)]:
        lt, _ = swe.calc_ut(jd, pid)
        sid = (lt[0] - ayan) % 360
        result[pn] = {'sid': round(float(sid), 4), 'sign': S[int(sid // 30)], 'deg': round(sid % 30, 2)}
    
    # Rahu (mean node)
    lt_r, _ = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_sid = (lt_r[0] - ayan) % 360
    result['Rahu'] = {'sid': round(float(rahu_sid), 4), 'sign': S[int(rahu_sid // 30)], 'deg': round(rahu_sid % 30, 2)}
    
    cache[key] = result
    return result

def saturn_moon_relation(np_dict):
    """Saturn-Moon contact analysis."""
    sat = np_dict['Saturn']; moon = np_dict['Moon']
    sep = abs((sat['sid'] - moon['sid'] + 180) % 360 - 180)
    return {
        'separation_deg': round(float(sep), 1),
        'same_sign': sat['sign'] == moon['sign'],
        'tight_conj': sep < 15,
        'moon_in_saturn_sign': moon['sign'] in ('Capricorn', 'Aquarius'),
        'saturn_in_moon_sign': sat['sign'] == 'Cancer',
        'acceleration_score': (3 if sep < 15 else (2 if sat['sign']==moon['sign'] else (2 if moon['sign'] in ('Capricorn','Aquarius') else (1 if sat['sign']=='Cancer' else 0)))),
    }

print("=" * 75)
print("  PMD v2.0 — 150K BULK INGEST")
print("=" * 75)

CSV_PATH = "/home/user/uploads/q series every_career_in_the_world_150k.csv"
BATCH_SIZE = 5000

# Read and process
all_events = []; errors = 0; t0 = time.time()

with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        try:
            date_str = row['Birth Date (YYYY-MM-DD)'].strip()
            y, m, d = int(date_str[:4]), int(date_str[5:7]), int(date_str[8:10])
            if not (1800 <= y <= 2020): continue
            
            sector = row.get('Career Sector', '').strip()
            profession = row.get('Profession', '').strip()
            country = row.get('Country', '').strip()
            name = row.get('Full Name', '').strip()
            
            # Compute natal positions
            np_data = natal_planets(y, m, d)
            sm_rel = saturn_moon_relation(np_data)
            
            event = {
                'person': name,
                'dob': f'{y:04d}-{m:02d}-{d:02d}',
                'event': f'Career: {sector}',
                'event_date': f'{y:04d}-{m:02d}-{d:02d}',  # placeholder: career sector as event
                'category': 'CAREER',
                'event_type': 'career_sector',
                'career_sector': sector,
                'profession': profession,
                'country': country,
                'source': 'career_csv_150k',
                'confidence': 'Synthetic',
                # Natal planets
                'natal_saturn_sign': np_data['Saturn']['sign'],
                'natal_saturn_deg': np_data['Saturn']['deg'],
                'natal_jupiter_sign': np_data['Jupiter']['sign'],
                'natal_jupiter_deg': np_data['Jupiter']['deg'],
                'natal_moon_sign': np_data['Moon']['sign'],
                'natal_moon_deg': np_data['Moon']['deg'],
                'natal_sun_sign': np_data['Sun']['sign'],
                'natal_rahu_sign': np_data['Rahu']['sign'],
                # Saturn-Moon
                'saturn_moon_sep_deg': sm_rel['separation_deg'],
                'saturn_moon_conjunction': sm_rel['tight_conj'],
                'moon_in_saturn_sign': sm_rel['moon_in_saturn_sign'],
                'sat_moon_accel_score': sm_rel['acceleration_score'],
            }
            all_events.append(event)
            
        except Exception as e:
            errors += 1
        
        # Progress
        if (i + 1) % 25000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  {i+1:>7,}/{150000} rows | {elapsed:.0f}s | {rate:.0f} rows/s | {len(cache):,} cached dates | {errors} errors")

t1 = time.time()
print(f"\n  ✅ COMPLETE: {len(all_events):,} events in {t1-t0:.0f}s ({(len(all_events))/(t1-t0):.0f} rows/s)")
print(f"  Errors: {errors} | Cached dates: {len(cache):,}")

# ── SAVE ──
OUT_PATH = 'dataset/public_milestone_dataset_v2.json.gz'
with gzip.open(OUT_PATH, 'wt', encoding='utf-8') as f:
    json.dump({
        'version': '2.0',
        'description': 'PMD v2.0 — 150K career CSV ingested with natal Saturn/Jupiter/Moon/Rahu positions (Lahiri)',
        'total_events': len(all_events),
        'fields': list(all_events[0].keys()) if all_events else [],
        'events': all_events,
    }, f, default=str)

size_mb = __import__('os').path.getsize(OUT_PATH) / 1024 / 1024
print(f"  📄 Saved: {OUT_PATH} ({size_mb:.1f} MB)")

# ── QUICK STATS ──
from collections import Counter
sat_counts = Counter(e['natal_saturn_sign'] for e in all_events)
jup_counts = Counter(e['natal_jupiter_sign'] for e in all_events)
moon_counts = Counter(e['natal_moon_sign'] for e in all_events)
sector_counts = Counter(e['career_sector'] for e in all_events)
sm_conj = sum(1 for e in all_events if e['saturn_moon_conjunction'])
moon_in_sat = sum(1 for e in all_events if e['moon_in_saturn_sign'])

print(f"\n─── DISTRIBUTIONS ───")
print(f"  Career sectors: {len(sector_counts)}")
print(f"  Top sectors: {sector_counts.most_common(8)}")
print(f"\n  Saturn signs: {dict(sat_counts.most_common())}")
print(f"  Saturn-Moon conjunctions: {sm_conj:,} ({sm_conj/len(all_events)*100:.1f}%)")
print(f"  Moon in Saturn signs: {moon_in_sat:,} ({moon_in_sat/len(all_events)*100:.1f}%)")

# Chi-square uniformity test
from scipy import stats
n_per_sign = [sat_counts.get(s, 0) for s in S]
chi2, p = stats.chisquare(n_per_sign)
print(f"  Saturn sign uniformity: χ²={chi2:.0f}, p={p:.6f} {'⚠️ NOT UNIFORM' if p<0.05 else '✅ UNIFORM'}")

# Saturn×Sector contingency table
sectors = [s for s,_ in sector_counts.most_common(15)]
table = np.zeros((12, len(sectors)))
for e in all_events:
    si = S.index(e['natal_saturn_sign'])
    sj = sectors.index(e['career_sector']) if e['career_sector'] in sectors else -1
    if sj >= 0: table[si, sj] += 1

chi2_s, p_s, dof_s, _ = stats.chi2_contingency(table + 1)
print(f"  Saturn × Sector: χ²={chi2_s:.0f}, p={p_s:.6f}, dof={dof_s} {'⭐ SIGNIFICANT' if p_s<0.05 else '— not significant'}")

print(f"\n  ✅ PMD v2.0 complete. {len(all_events):,} events with natal planet positions.")
print(f"  Ready for Saturn window, Jupiter return, and Dasha analysis.")
