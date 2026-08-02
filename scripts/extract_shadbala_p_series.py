#!/usr/bin/env python3
"""NEXUS v4.0 — jyotishganit Shadbala + Ashtakavarga Feature Extractor for P1-P9"""
import json, time
from datetime import datetime, timezone, timedelta
from jyotishganit import calculate_birth_chart, get_birth_chart_json

P_SERIES = {
    'P1': ('Polgahawela Bappa', 1962, 5, 27, 3, 38, 54, 7.3381, 80.3003, 5.5),
    'P2': ('Upulakshi', 1997, 3, 14, 9, 38, 0, 6.9355, 79.8487, 5.5),
    'P3': ('Senith', 1995, 8, 7, 21, 18, 0, 6.9355, 79.8487, 5.5),
    'P4': ('Niromi', 1967, 4, 25, 8, 17, 37, 6.9355, 79.8487, 5.5),
    'P5': ('Senath', 2001, 5, 14, 16, 8, 40, 6.9355, 79.8487, 5.5),
    'P6': ('Dewli', 2005, 10, 8, 8, 22, 0, 6.9097, 79.8900, 5.5),
    'P7': ('Sineth', 2005, 4, 5, 16, 5, 48, 6.9271, 79.8612, 5.5),
    'P8': ('Lakshi Amma', 1963, 11, 16, 9, 4, 15, 7.486, 80.362, 5.5),
    'P9': ('Lalith Uncle', 1970, 8, 31, 21, 55, 30, 7.2931, 80.635, 5.5),
}

results = {}
for pid, (name, y, m, d, h, mi, s, lat, lon, tz) in P_SERIES.items():
    t0 = time.time()
    birth_dt = datetime(y, m, d, h, mi, s)
    chart = calculate_birth_chart(
        birth_date=birth_dt, latitude=lat, longitude=lon,
        timezone_offset=tz, name=name
    )
    data = get_birth_chart_json(chart)
    t1 = time.time()

    # Extract D1 planets
    d1_planets = {}
    for house in data['d1Chart']['houses']:
        for occ in house.get('occupants', []):
            pname = occ['celestialBody']
            sb = occ.get('shadbala', {})
            sb_inner = sb.get('Shadbala', {})
            d1_planets[pname] = {
                'sign': occ['sign'],
                'house': occ['house'],
                'longitude': float(occ['signDegrees']),
                'nakshatra': occ['nakshatra'],
                'pada': occ['pada'],
                'dignity': occ['dignities']['dignity'] if 'dignities' in occ else '?',
                'shadbala_rupas': float(sb_inner.get('Rupas', 0)),
                'shadbala_total': float(sb_inner.get('Total', 0)),
                'ishtabala': float(sb.get('Ishtabala', 0)),
                'kashtabala': float(sb.get('Kashtabala', 0)),
            }

    # Extract Ashtakavarga SAV
    av = data['ashtakavarga']
    sav = {k: int(v) for k, v in av['sav'].items()}

    # Extract Bhinnashtakavarga per planet
    bhav = {}
    for planet_key in ['sunBhav', 'moonBhav', 'marsBhav', 'mercuryBhav', 'jupiterBhav', 'venusBhav', 'saturnBhav']:
        if planet_key in av:
            bhav[planet_key] = {k: int(v) for k, v in av[planet_key].items()}

    # Dasha current
    dashas = data.get('dashas', {})
    current = dashas.get('current', {}).get('mahadashas', {})
    current_md = list(current.keys())[0] if current else '?'
    current_ad = '?'
    if current_md in current:
        ads = current[current_md].get('antardashas', {})
        current_ad = list(ads.keys())[0] if ads else '?'

    # Divisional chart ascendants
    div_ascs = {}
    for dname, dchart in data.get('divisionalCharts', {}).items():
        asc_data = dchart.get('houses', [{}])[0]
        div_ascs[dname] = asc_data.get('sign', '?')

    results[pid] = {
        'name': name,
        'lagna': data['d1Chart']['houses'][0]['sign'],
        'd1': d1_planets,
        'sav': sav,
        'bhav': bhav,
        'current_md': current_md,
        'current_ad': current_ad,
        'div_ascs': div_ascs,
        'compute_time_s': round(t1 - t0, 2),
    }
    lagna = data['d1Chart']['houses'][0]['sign']
    print(f"  {pid} {name}: {t1-t0:.1f}s — Lagna: {lagna} | MD: {current_md}/{current_ad} | SAV total: {sum(sav.values())}")

# Save
with open('dataset/p_series_shadbala_av.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved: dataset/p_series_shadbala_av.json ({len(results)} charts)")

# Summary table
print(f"\n{'ID':<4s} {'Name':<18s} {'Lagna':<12s} {'MD':<10s} {'AD':<10s} {'SAV Σ':>6s} {'Avg SB':>7s} {'I/K':>6s}")
print('-' * 80)
for pid, r in results.items():
    d1 = r['d1']
    sav_sum = sum(r['sav'].values())
    sbs = [p['shadbala_rupas'] for p in d1.values() if p['shadbala_rupas'] > 0]
    avg_sb = sum(sbs) / len(sbs) if sbs else 0
    ishta_sum = sum(p['ishtabala'] for p in d1.values())
    kashta_sum = sum(p['kashtabala'] for p in d1.values())
    print(f"{pid:<4s} {r['name']:<18s} {r.get('lagna','?'):<12s} {r['current_md']:<10s} {r['current_ad']:<10s} {sav_sum:>6d} {avg_sb:>6.1f} {ishta_sum/kashta_sum:>5.1f}" if kashta_sum else f"{pid:<4s} {r['name']:<18s} {sav_sum:>6d} {avg_sb:>6.1f}")
