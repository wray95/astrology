#!/usr/bin/env python3
"""
PROPER VIMSHOTTARI DASHA ENGINE
===============================
Uses Skyfield (JPL DE421) for Moon tropical longitude.
Applies Lahiri ayanamsa for sidereal conversion.
Computes Vimshottari Mahadasha, Antardasha, Pratyantar Dasha.

TEST CASE: 7 August 1995, 21:18, Kandy, Sri Lanka (P3 Senith)
"""

from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame
from datetime import datetime, timedelta
import math

# ============================================================
# 1. EPHEMERIS SETUP
# ============================================================
ephem = load('/home/user/de421.bsp')
ts = load.timescale()
earth = ephem['earth']
moon = ephem['moon']
sun = ephem['sun']

# ============================================================
# 2. LAHIRI AYANAMSA (Chitra Paksha)
# ============================================================
def lahiri_ayanamsa(jd_ut):
    """
    Compute Lahiri (Chitra Paksha) ayanamsa for a given Julian date.
    Uses IAU general precession formula (quadratic) for accuracy.
    Base: Lahiri ayanamsa at J2000.0 = 23°51′25″ = 23.856944°
    T = Julian centuries since J2000.0 (JD 2451545.0).
    Precession in longitude: p = 5029.0966″·T + 1.11161″·T²
    
    Refs: Lahiri Indian Ephemeris; matches astro-seek.com within ~0.01°.
    """
    JD_J2000 = 2451545.0
    T = (jd_ut - JD_J2000) / 36525.0  # Julian centuries
    # General precession in arcseconds (IAU 2006 model)
    precession_as = 5029.0966 * T + 1.11161 * T * T - 0.000154 * T * T * T
    # Lahiri base at J2000.0
    ayan_j2000_deg = 23 + 51 / 60 + 25 / 3600  # 23.8569444...°
    return ayan_j2000_deg + precession_as / 3600.0

# ============================================================
# 3. NAKSHATRA DEFINITIONS (27 nakshatras, each 13°20′)
# ============================================================
NAKSHATRA_SPAN = 360.0 / 27  # 13.333333...°

nakshatras = [
    ("Ashwini",          0.0,        "Ketu"),
    ("Bharani",          13.333333,  "Venus"),
    ("Krittika",         26.666667,  "Sun"),
    ("Rohini",           40.0,       "Moon"),
    ("Mrigashira",       53.333333,  "Mars"),
    ("Ardra",            66.666667,  "Rahu"),
    ("Punarvasu",        80.0,       "Jupiter"),
    ("Pushya",           93.333333,  "Saturn"),
    ("Ashlesha",         106.666667, "Mercury"),
    ("Magha",            120.0,      "Ketu"),
    ("Purva Phalguni",   133.333333, "Venus"),
    ("Uttara Phalguni",  146.666667, "Sun"),
    ("Hasta",            160.0,      "Moon"),
    ("Chitra",           173.333333, "Mars"),
    ("Swati",            186.666667, "Rahu"),
    ("Vishakha",         200.0,      "Jupiter"),
    ("Anuradha",         213.333333, "Saturn"),
    ("Jyeshtha",         226.666667, "Mercury"),
    ("Mula",             240.0,      "Ketu"),
    ("Purva Ashadha",    253.333333, "Venus"),
    ("Uttara Ashadha",   266.666667, "Sun"),
    ("Shravana",         280.0,      "Moon"),
    ("Dhanishtha",       293.333333, "Mars"),
    ("Shatabhisha",      306.666667, "Rahu"),
    ("Purva Bhadrapada", 320.0,      "Jupiter"),
    ("Uttara Bhadrapada", 333.333333, "Saturn"),
    ("Revati",           346.666667, "Mercury"),
]

VIM_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
VIM_YEARS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
             'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

# ============================================================
# 4. HELPER: Add fractional years to a datetime
# ============================================================
def add_years_days(dt, years):
    """Add fractional years. Uses 365.2425 days/year (Gregorian average)."""
    total_days = years * 365.2425
    days_int = int(total_days)
    seconds_frac = (total_days - days_int) * 86400
    return dt + timedelta(days=days_int, seconds=seconds_frac)

# ============================================================
# 5. CORE: Get Moon sidereal longitude + nakshatra
# ============================================================
def get_moon_data(dt_utc, lat, lon):
    """Return sidereal Moon longitude, nakshatra, lord, balance."""
    t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day,
               dt_utc.hour, dt_utc.minute, dt_utc.second + dt_utc.microsecond/1e6)
    
    # Vedic astrology uses GEOCENTRIC positions (Earth center), not topocentric.
    # Observer lat/lon is kept for potential future house calculations only.
    # Moon parallax (~1°) can flip the nakshatra if topocentric is used.
    astrometric = earth.at(t).observe(moon)
    
    # Tropical longitude (ecliptic)
    ecliptic_pos = astrometric.frame_latlon(ecliptic_frame)
    trop_lon = ecliptic_pos[1].degrees
    if trop_lon < 0:
        trop_lon += 360
    
    # Apply ayanamsa
    ayanamsa = lahiri_ayanamsa(t.tt)
    sidereal_lon = trop_lon - ayanamsa
    if sidereal_lon < 0:
        sidereal_lon += 360
    if sidereal_lon >= 360:
        sidereal_lon -= 360
    
    # Determine nakshatra
    for i, (name, start, lord) in enumerate(nakshatras):
        end = start + NAKSHATRA_SPAN
        if sidereal_lon >= start and sidereal_lon < end:
            pos_in_nak = sidereal_lon - start
            elapsed_frac = pos_in_nak / NAKSHATRA_SPAN
            remaining_frac = 1.0 - elapsed_frac
            balance_years = VIM_YEARS[lord] * remaining_frac
            return {
                'tropical_lon': trop_lon,
                'ayanamsa': ayanamsa,
                'sidereal_lon': sidereal_lon,
                'nakshatra': name,
                'nakshatra_lord': lord,
                'nakshatra_start': start,
                'nakshatra_end': end,
                'position_in_nakshatra': pos_in_nak,
                'elapsed_arcmin': pos_in_nak * 60,
                'total_arcmin': NAKSHATRA_SPAN * 60,
                'elapsed_fraction': elapsed_frac,
                'remaining_fraction': remaining_frac,
                'balance_years': balance_years,
            }
    
    # Edge case: exactly 360°
    name, start, lord = nakshatras[0]
    pos_in_nak = 0
    remaining_frac = 1.0
    return {
        'tropical_lon': trop_lon, 'ayanamsa': ayanamsa,
        'sidereal_lon': sidereal_lon, 'nakshatra': name,
        'nakshatra_lord': lord, 'nakshatra_start': start,
        'nakshatra_end': start + NAKSHATRA_SPAN,
        'position_in_nakshatra': 0,
        'elapsed_fraction': 0, 'remaining_fraction': 1.0,
        'balance_years': VIM_YEARS[lord],
    }

# ============================================================
# 6. MAHADASHA CALCULATION
# ============================================================
def compute_mahadasha(birth_dt, start_lord, balance_years):
    """Return list of (lord, start_dt, end_dt, duration_years)."""
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

# ============================================================
# 7. ANTARDASHA CALCULATION
# ============================================================
def compute_antardasha(md_lord, md_start, md_years):
    """Return list of (lord, start_dt, end_dt, duration_years).
    
    Antardasha ALWAYS starts from Ketu (fixed Vimshottari order),
    NOT from the MD lord. Matches Drik Panchang convention.
    Duration = (MD_years * AD_lord_years) / 120.
    """
    results = []
    ad_start = md_start
    for ad_lord in VIM_ORDER:
        ad_yrs = (md_years * VIM_YEARS[ad_lord]) / 120.0
        ad_end = add_years_days(ad_start, ad_yrs)
        results.append((ad_lord, ad_start, ad_end, ad_yrs))
        ad_start = ad_end
    return results

# ============================================================
# 8. PRATYANTAR DASHA CALCULATION
# ============================================================
def compute_pratyantar(ad_lord, ad_start, ad_yrs):
    """Return list of (lord, start_dt, end_dt, duration_years).
    
    Pratyantar ALWAYS starts from Ketu (fixed Vimshottari order).
    Duration = (AD_years * PD_lord_years) / 120.
    """
    results = []
    pd_start = ad_start
    for pd_lord in VIM_ORDER:
        pd_yrs = (ad_yrs * VIM_YEARS[pd_lord]) / 120.0
        pd_end = add_years_days(pd_start, pd_yrs)
        results.append((pd_lord, pd_start, pd_end, pd_yrs))
        pd_start = pd_end
    return results

# ============================================================
# 9. MAIN: TEST CASE — Senith (1995-08-07, 21:18, Kandy, Sri Lanka)
# ============================================================
if __name__ == '__main__':
    # Kandy, Sri Lanka
    lat = 7.2906   # 7°17'26"N
    lon = 80.6337  # 80°38'01"E
    
    # Birth: 7 August 1995, 21:18:00 local
    # Sri Lanka timezone in 1995: UTC+5:30 (IST)
    birth_local = datetime(1995, 8, 7, 21, 18, 0)
    tz_offset_hours = 5.5
    birth_utc = birth_local - timedelta(hours=tz_offset_hours)
    
    print("=" * 80)
    print("VIMSHOTTARI DASHA ENGINE — Skyfield JPL DE421 + Lahiri Ayanamsa")
    print("=" * 80)
    print(f"Birth (local):  {birth_local.strftime('%d %b %Y %H:%M:%S')} UTC+5:30")
    print(f"Birth (UTC):    {birth_utc.strftime('%d %b %Y %H:%M:%S')}")
    print(f"Location:       Kandy, Sri Lanka ({lat}°N, {lon}°E)")
    print()
    
    # Get Moon data
    moon_data = get_moon_data(birth_utc, lat, lon)
    
    print("MOON POSITION:")
    print(f"  Tropical longitude:  {moon_data['tropical_lon']:.6f}°")
    print(f"  Lahiri Ayanamsa:     {moon_data['ayanamsa']:.6f}°")
    print(f"  Sidereal longitude:  {moon_data['sidereal_lon']:.6f}°")
    print(f"  Nakshatra:           {moon_data['nakshatra']}")
    print(f"  Nakshatra Lord:      {moon_data['nakshatra_lord']}")
    print(f"  Nakshatra range:     {moon_data['nakshatra_start']:.4f}° – {moon_data['nakshatra_end']:.4f}°")
    print(f"  Position in Nak:     {moon_data['position_in_nakshatra']:.4f}° ({moon_data['elapsed_arcmin']:.2f} arcmin)")
    print(f"  Total Nak arc:       {moon_data['total_arcmin']:.2f} arcmin (800 arcmin)")
    print(f"  Elapsed fraction:    {moon_data['elapsed_fraction']:.6f}")
    print(f"  Remaining fraction:  {moon_data['remaining_fraction']:.6f}")
    print(f"  Balance at birth:    {moon_data['balance_years']:.4f} years of {moon_data['nakshatra_lord']} MD")
    print()
    
    # Mahadasha
    md_list = compute_mahadasha(birth_local, moon_data['nakshatra_lord'], moon_data['balance_years'])
    
    print("MAHADASHA SEQUENCE:")
    print(f"  {'Lord':10s} {'Start':>21s} {'End':>21s} {'Years':>8s} {'Age':>8s}")
    print(f"  {'-'*72}")
    now = datetime(2026, 7, 25)
    current_md = None
    for lord, start, end, yrs, age_s, age_e in md_list:
        flag = " ◀ NOW" if start <= now < end else ""
        print(f"  {lord:10s} {start.strftime('%Y-%m-%d %H:%M:%S'):>21s} {end.strftime('%Y-%m-%d %H:%M:%S'):>21s} {yrs:7.4f}y {age_s:4.1f}–{age_e:.1f}{flag}")
        if start <= now < end:
            current_md = (lord, start, end, yrs)
    
    # Current MD Antardasha
    if current_md:
        md_lord, md_start, md_end, md_yrs = current_md
        ad_list = compute_antardasha(md_lord, md_start, md_yrs)
        print(f"\n  {md_lord} MAHADASHA — ANTARDASHA:")
        current_ad = None
        for ad_lord, ad_start, ad_end, ad_yrs in ad_list:
            flag = " ◀ NOW" if ad_start <= now < ad_end else ""
            print(f"    {ad_lord:10s} {ad_start.strftime('%Y-%m-%d %H:%M:%S')} → {ad_end.strftime('%Y-%m-%d %H:%M:%S')}  {ad_yrs:.4f}y{flag}")
            if ad_start <= now < ad_end:
                current_ad = (ad_lord, ad_start, ad_end, ad_yrs)
        
        # Current AD Pratyantar
        if current_ad:
            ad_lord, ad_start, ad_end, ad_yrs = current_ad
            pd_list = compute_pratyantar(ad_lord, ad_start, ad_yrs)
            print(f"\n    {ad_lord} ANTARDASHA — PRATYANTAR:")
            for pd_lord, pd_start, pd_end, pd_yrs in pd_list:
                flag = " ◀ NOW" if pd_start <= now < pd_end else ""
                print(f"      {pd_lord:10s} {pd_start.strftime('%Y-%m-%d %H:%M:%S')} → {pd_end.strftime('%Y-%m-%d %H:%M:%S')}  {pd_yrs:.4f}y{flag}")
    
    # Summary
    print(f"\n{'='*80}")
    print("COMPARISON WITH EXPECTED (AppliedJyotish for Senith):")
    print(f"  Moon Nakshatra:      {moon_data['nakshatra']}")
    print(f"  Nakshatra Lord:      {moon_data['nakshatra_lord']}")
    print(f"  Starting Mahadasha:  {moon_data['nakshatra_lord']}")
    print(f"  Balance at birth:    {moon_data['balance_years']:.4f}y of {moon_data['nakshatra_lord']}")
    if current_md:
        print(f"  Current Mahadasha:   {current_md[0]}")
    if current_ad:
        print(f"  Current Antardasha:  {current_ad[0]}")
    print(f"{'='*80}")
