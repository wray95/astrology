#!/usr/bin/env python3
"""
P1-P7 DASHA RECOMPUTE + RERANK
- Geocentric Moon (Skyfield JPL DE421 + quadratic Lahiri ayanamsa)
- Ketu-first antardasha/pratyantar (fixed Vimshottari order)
- All times in local timezone
- Verifies against known references where available
"""

import json, math
from datetime import datetime, timedelta

# ===== Engine functions (standalone — no skyfield import at module level) =====

NAKSHATRA_SPAN = 360.0 / 27
VIM_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VIM_YEARS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
             'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

nakshatras = [
    ("Ashwini", 0.0, "Ketu"), ("Bharani", 13.333333, "Venus"),
    ("Krittika", 26.666667, "Sun"), ("Rohini", 40.0, "Moon"),
    ("Mrigashira", 53.333333, "Mars"), ("Ardra", 66.666667, "Rahu"),
    ("Punarvasu", 80.0, "Jupiter"), ("Pushya", 93.333333, "Saturn"),
    ("Ashlesha", 106.666667, "Mercury"), ("Magha", 120.0, "Ketu"),
    ("Purva Phalguni", 133.333333, "Venus"), ("Uttara Phalguni", 146.666667, "Sun"),
    ("Hasta", 160.0, "Moon"), ("Chitra", 173.333333, "Mars"),
    ("Swati", 186.666667, "Rahu"), ("Vishakha", 200.0, "Jupiter"),
    ("Anuradha", 213.333333, "Saturn"), ("Jyeshtha", 226.666667, "Mercury"),
    ("Mula", 240.0, "Ketu"), ("Purva Ashadha", 253.333333, "Venus"),
    ("Uttara Ashadha", 266.666667, "Sun"), ("Shravana", 280.0, "Moon"),
    ("Dhanishtha", 293.333333, "Mars"), ("Shatabhisha", 306.666667, "Rahu"),
    ("Purva Bhadrapada", 320.0, "Jupiter"), ("Uttara Bhadrapada", 333.333333, "Saturn"),
    ("Revati", 346.666667, "Mercury"),
]

SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def lahiri_ayanamsa(jd_ut):
    JD_J2000 = 2451545.0
    T = (jd_ut - JD_J2000) / 36525.0
    precession_as = 5029.0966 * T + 1.11161 * T * T - 0.000154 * T * T * T
    ayan_j2000_deg = 23 + 51 / 60 + 25 / 3600
    return ayan_j2000_deg + precession_as / 3600.0

def get_moon_geocentric(birth_utc, lat, lon):
    """Geocentric Moon: sidereal longitude, nakshatra, lord, balance."""
    from skyfield.api import load
    from skyfield.framelib import ecliptic_frame
    
    ephem = load('/home/user/de421.bsp')
    ts = load.timescale()
    earth = ephem['earth']
    moon = ephem['moon']
    
    t = ts.utc(birth_utc.year, birth_utc.month, birth_utc.day,
               birth_utc.hour, birth_utc.minute, birth_utc.second + birth_utc.microsecond/1e6)
    
    geo = earth.at(t).observe(moon)
    ecl = geo.frame_latlon(ecliptic_frame)
    trop_lon = ecl[1].degrees
    if trop_lon < 0: trop_lon += 360
    
    ayan = lahiri_ayanamsa(t.tt)
    sid = (trop_lon - ayan) % 360
    sign_idx = int(sid // 30)
    sign_deg = sid - sign_idx * 30
    
    for name, start, lord in nakshatras:
        end = start + NAKSHATRA_SPAN
        if sid >= start and sid < end:
            pos_in_nak = sid - start
            elapsed = pos_in_nak / NAKSHATRA_SPAN
            balance = VIM_YEARS[lord] * (1.0 - elapsed)
            return {
                'sidereal': sid, 'sign': SIGN_NAMES[sign_idx],
                'sign_deg': sign_deg, 'nakshatra': name, 'lord': lord,
                'elapsed': elapsed, 'balance': balance, 'ayanamsa': ayan
            }
    # edge: exactly 360°
    return {
        'sidereal': sid, 'sign': SIGN_NAMES[sign_idx], 'sign_deg': sign_deg,
        'nakshatra': nakshatras[0][0], 'lord': nakshatras[0][2],
        'elapsed': 0, 'balance': VIM_YEARS[nakshatras[0][2]], 'ayanamsa': ayan
    }

def add_years_days(dt, years):
    total_days = years * 365.2425
    days_int = int(total_days)
    seconds_frac = (total_days - days_int) * 86400
    return dt + timedelta(days=days_int, seconds=seconds_frac)

def compute_mahadasha(birth_dt, start_lord, balance_years):
    start_idx = VIM_ORDER.index(start_lord)
    results = []
    current_dt = birth_dt
    for i in range(9):
        lord = VIM_ORDER[(start_idx + i) % 9]
        yrs = balance_years if i == 0 else VIM_YEARS[lord]
        start = current_dt
        end = add_years_days(start, yrs)
        age_s = (start - birth_dt).total_seconds() / (365.2425 * 86400)
        age_e = (end - birth_dt).total_seconds() / (365.2425 * 86400)
        results.append((lord, start, end, yrs, age_s, age_e))
        current_dt = end
    return results

def compute_antardasha(md_start, md_years):
    """Ketu-first antardasha."""
    results = []
    ad_start = md_start
    for ad_lord in VIM_ORDER:
        ad_yrs = (md_years * VIM_YEARS[ad_lord]) / 120.0
        ad_end = add_years_days(ad_start, ad_yrs)
        results.append((ad_lord, ad_start, ad_end, ad_yrs))
        ad_start = ad_end
    return results

def compute_pratyantar(ad_start, ad_yrs):
    """Ketu-first pratyantar."""
    results = []
    pd_start = ad_start
    for pd_lord in VIM_ORDER:
        pd_yrs = (ad_yrs * VIM_YEARS[pd_lord]) / 120.0
        pd_end = add_years_days(pd_start, pd_yrs)
        results.append((pd_lord, pd_start, pd_end, pd_yrs))
        pd_start = pd_end
    return results

def find_current(dt_utc, md_list):
    for md in md_list:
        if md[1] <= dt_utc < md[2]:
            return md
    return None

# ===== Chart definitions =====

CHARTS = [
    {
        'id': 'P1', 'name': 'Polgahawela Bappa',
        'birth_local': datetime(1962, 5, 27, 3, 38, 54),
        'tz_hours': 5.5,  # UTC+5:30
        'lat': 7.3381, 'lon': 80.3003, 'city': 'Polgahawela, Sri Lanka',
        'ref_lagna': 'Aries',
        'ref_moon_nak': 'Shatabhisha', 'ref_moon_lord': 'Rahu',
        'ref_current_md': 'Ketu', 'ref_current_ad': 'Jupiter',
        'notes': 'Rodden B. Venus↔Mercury Parivartana (Dainya). Ruchaka (Mars Aries 1H).'
    },
    {
        'id': 'P2', 'name': 'Upulakshi',
        'birth_local': datetime(1997, 3, 14, 12, 0, 0),
        'tz_hours': 6.0,  # UTC+6 (SL 1996-2006)
        'lat': 6.9355, 'lon': 79.8487, 'city': 'Colombo, Sri Lanka',
        'ref_lagna': 'Taurus',
        'ref_moon_nak': 'Rohini', 'ref_moon_lord': 'Moon',
        'ref_current_md': 'Rahu', 'ref_current_ad': 'Jupiter',
        'notes': '⚠️ PLACEHOLDER TOB (12:00 noon). Rodden B. Jupiter↔Saturn Parivartana (Dainya).'
    },
    {
        'id': 'P3', 'name': 'Senith',
        'birth_local': datetime(1995, 8, 7, 21, 18, 0),
        'tz_hours': 5.5,  # UTC+5:30
        'lat': 6.9355, 'lon': 79.8487, 'city': 'Colombo, Sri Lanka',
        'ref_lagna': 'Pisces',
        'ref_moon_nak': 'Mula', 'ref_moon_lord': 'Ketu',
        'ref_current_md': 'Moon', 'ref_current_ad': 'Venus',
        'notes': 'Rodden B. 5-loop Shrinkala (bond=25). AppliedJyotish verified.'
    },
    {
        'id': 'P4', 'name': 'Niromi',
        'birth_local': datetime(1967, 4, 25, 8, 17, 37),
        'tz_hours': 5.5,  # UTC+5:30
        'lat': 6.9355, 'lon': 79.8487, 'city': 'Colombo, Sri Lanka',
        'ref_lagna': 'Taurus',
        'ref_moon_nak': 'Swati', 'ref_moon_lord': 'Rahu',
        'ref_current_md': 'Ketu', 'ref_current_ad': 'Saturn',
        'notes': 'Rodden B. No Parivartana. Malavaya (Venus exalted). Dhana 5.0.'
    },
    {
        'id': 'P5', 'name': 'Senath',
        'birth_local': datetime(2001, 5, 14, 16, 8, 40),
        'tz_hours': 6.0,  # UTC+6 (SL 1996-2006)
        'lat': 6.9355, 'lon': 79.8487, 'city': 'Colombo, Sri Lanka',
        'ref_lagna': 'Virgo',
        'ref_moon_nak': 'Shravana', 'ref_moon_lord': 'Moon',
        'ref_current_md': 'Rahu', 'ref_current_ad': 'Saturn',
        'notes': 'Rodden B. Venus↔Jupiter MAHA Parivartana. 12+ yogas. Malavya.'
    },
    {
        'id': 'P6', 'name': 'Dewli',
        'birth_local': datetime(2005, 10, 8, 8, 22, 0),
        'tz_hours': 6.0,  # UTC+6
        'lat': 6.9097, 'lon': 79.8900, 'city': 'Sri Jayawardenepura Kotte, Sri Lanka',
        'ref_lagna': 'Libra',
        'ref_moon_nak': 'Jyeshtha', 'ref_moon_lord': 'Mercury',
        'ref_current_md': 'Ketu', 'ref_current_ad': 'Jupiter',
        'notes': 'Rodden B. No Parivartana. Ruchaka (Mars retro Aries 7H). AppliedJyotish verified.'
    },
    {
        'id': 'P7', 'name': 'Sineth',
        'birth_local': datetime(2005, 4, 5, 16, 5, 48),
        'tz_hours': 6.0,  # UTC+6 (SL 1996-2006)
        'lat': 6.9271, 'lon': 79.8612, 'city': 'Colombo, Sri Lanka',
        'ref_lagna': None,  # unknown (need Colombo coordinates)
        'ref_moon_nak': 'Purva Bhadrapada', 'ref_moon_lord': 'Jupiter',
        'ref_current_md': 'Saturn', 'ref_current_ad': 'Jupiter',
        'ref_balance': 9.0,  # MoonAstro confirmed
        'notes': 'NEW CHART. MoonAstro confirmed: Jupiter MD at birth (9y balance), Saturn MD now, Mercury MD Apr 2033.'
    },
]

now = datetime(2026, 7, 26)

print("=" * 78)
print("P1–P7 VIMSHOTTARI DASHA RECOMPUTE — Skyfield Geocentric + Quadratic Ayanamsa")
print("=" * 78)
print(f"Date: {now.strftime('%d %b %Y')}")
print()

results = []

for ch in CHARTS:
    pid = ch['id']
    name = ch['name']
    birth_local = ch['birth_local']
    tz_hours = ch['tz_hours']
    lat, lon = ch['lat'], ch['lon']
    birth_utc = birth_local - timedelta(hours=tz_hours)
    
    # Get Moon data
    moon = get_moon_geocentric(birth_utc, lat, lon)
    
    # Mahadasha
    md_list = compute_mahadasha(birth_local, moon['lord'], moon['balance'])
    
    # Current
    now_local = now  # approximate
    current_md = find_current(now_local, md_list)
    
    current_ad = None
    current_pd = None
    if current_md:
        ad_list = compute_antardasha(current_md[1], current_md[3])
        for ad in ad_list:
            if ad[1] <= now_local < ad[2]:
                current_ad = ad
                break
        if current_ad:
            pd_list = compute_pratyantar(current_ad[1], current_ad[3])
            for pd in pd_list:
                if pd[1] <= now_local < pd[2]:
                    current_pd = pd
                    break
    
    # Verification
    nak_ok = moon['nakshatra'] == ch['ref_moon_nak']
    lord_ok = moon['lord'] == ch['ref_moon_lord']
    md_ok = current_md and current_md[0] == ch['ref_current_md']
    ad_ok = current_ad and current_ad[0] == ch['ref_current_ad']
    all_ok = nak_ok and lord_ok and md_ok and ad_ok
    
    # Special: P7 has known balance
    if pid == 'P7':
        balance_ok = abs(moon['balance'] - ch['ref_balance']) < 1.0
        all_ok = all_ok and balance_ok
    
    results.append({
        'chart': ch, 'moon': moon, 'md_list': md_list,
        'current_md': current_md, 'current_ad': current_ad, 'current_pd': current_pd,
        'checks': {'nak': nak_ok, 'lord': lord_ok, 'md': md_ok, 'ad': ad_ok, 'all': all_ok}
    })
    
    # Print
    print(f"─── {pid} {name} ───")
    print(f"  Birth: {birth_local.strftime('%d %b %Y %H:%M')} UTC+{tz_hours:.1f} | {ch['city']}")
    print(f"  Moon:  {moon['sign']} {moon['sign_deg']:.2f}° → {moon['nakshatra']} ({moon['lord']})")
    print(f"  Balance: {moon['balance']:.2f}y of {moon['lord']} MD")
    if pid == 'P7':
        print(f"  Balance ref: ~{ch['ref_balance']:.1f}y ({'✓' if balance_ok else '✗ MISMATCH'})")
    
    # MD table (compact)
    print(f"  MD: ", end="")
    for i, (lord, start, end, yrs, age_s, age_e) in enumerate(md_list):
        f = " ◀" if current_md and lord == current_md[0] else ""
        print(f"{lord}{f}", end=" → " if i < 8 else "")
    print()
    
    # Current
    if current_md:
        print(f"  Now ({now.strftime('%b %Y')}): {current_md[0]} MD", end="")
        if current_ad:
            print(f" / {current_ad[0]} AD", end="")
        if current_pd:
            print(f" / {current_pd[0]} PD", end="")
        print()
    
    # Checks
    check_strs = []
    if nak_ok: check_strs.append("Nak ✓")
    else: check_strs.append(f"NAK ✗ (got {moon['nakshatra']}, ref {ch['ref_moon_nak']})")
    if lord_ok: check_strs.append("Lord ✓")
    else: check_strs.append(f"LORD ✗ (got {moon['lord']}, ref {ch['ref_moon_lord']})")
    if md_ok: check_strs.append("MD ✓")
    else: check_strs.append(f"MD ✗ (got {current_md[0] if current_md else '?'}, ref {ch['ref_current_md']})")
    if ad_ok: check_strs.append("AD ✓")
    else: check_strs.append(f"AD ✗ (got {current_ad[0] if current_ad else '?'}, ref {ch['ref_current_ad']})")
    print(f"  Verify: {' | '.join(check_strs)}")
    
    if all_ok:
        print(f"  STATUS: ✅ VERIFIED")
    else:
        print(f"  STATUS: ❌ MISMATCH — NEEDS INVESTIGATION")
    print()

# ===== RANKING =====
print("=" * 78)
print("RANKING — DASHA VERIFICATION QUALITY")
print("=" * 78)
print(f"  {'ID':4s} {'Name':22s} {'Nak':5s} {'Lord':6s} {'MD':8s} {'AD':8s} {'Status':8s}")
print(f"  {'-'*64}")

ranked = sorted(results, key=lambda r: (
    r['checks']['all'],
    r['checks']['nak'] + r['checks']['lord'] + r['checks']['md'] + r['checks']['ad']
), reverse=True)

for rank, r in enumerate(ranked, 1):
    ch = r['chart']
    c = r['checks']
    status = "✅ FULL" if c['all'] else "❌ FAIL"
    print(f"  {rank}. {ch['id']:4s} {ch['name']:22s} "
          f"{'✓' if c['nak'] else '✗':5s} "
          f"{'✓' if c['lord'] else '✗':6s} "
          f"{r['current_md'][0] if r['current_md'] else '?':8s} "
          f"{r['current_ad'][0] if r['current_ad'] else '?':8s} "
          f"{status:8s}")

print()
passed = sum(1 for r in results if r['checks']['all'])
print(f"Passed: {passed}/{len(results)}")
print(f"Failed: {len(results) - passed}/{len(results)}")
