#!/usr/bin/env python3
"""Check P7 Sineth: geocentric vs topocentric Moon position."""
from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame
from datetime import datetime, timedelta

ephem = load(''de421.bsp'')
ts = load.timescale()
earth = ephem['earth']
moon = ephem['moon']

def lahiri_ayanamsa(jd_ut):
    JD_J2000 = 2451545.0
    ayan_j2000 = 23 + 51/60 + 25/3600  # 23°51′25″
    years_since_j2000 = (jd_ut - JD_J2000) / 365.25
    precession_per_year = 50.27 / 3600
    return ayan_j2000 + years_since_j2000 * precession_per_year

# P7 Sineth
birth_local = datetime(2005, 4, 5, 16, 5, 48)
birth_utc = birth_local - timedelta(hours=6)
lat, lon = 6.9271, 79.8612

t = ts.utc(birth_utc.year, birth_utc.month, birth_utc.day,
           birth_utc.hour, birth_utc.minute, birth_utc.second)

# TOPOCENTRIC — from Colombo surface
observer = earth + wgs84.latlon(lat, lon)
topo = observer.at(t).observe(moon)
topo_ecl = topo.frame_latlon(ecliptic_frame)
topo_trop = topo_ecl[1].degrees
if topo_trop < 0: topo_trop += 360

# GEOCENTRIC — from Earth center (Vedic standard)
geo = earth.at(t).observe(moon)
geo_ecl = geo.frame_latlon(ecliptic_frame)
geo_trop = geo_ecl[1].degrees
if geo_trop < 0: geo_trop += 360

ayan = lahiri_ayanamsa(t.tt)

topo_sid = (topo_trop - ayan) % 360
geo_sid = (geo_trop - ayan) % 360

# Expected from Drik Panchang
expected = 307.162  # Aquarius 7°09′44″

print("=" * 70)
print("P7 SINETH — TOPOCENTRIC vs GEOCENTRIC MOON")
print("=" * 70)
print(f"  Topocentric tropical: {topo_trop:.6f}°")
print(f"  Geocentric tropical:  {geo_trop:.6f}°")
print(f"  Parallax shift:       {abs(topo_trop - geo_trop):.6f}° ({abs(topo_trop - geo_trop)*60:.2f} arcmin)")
print(f"  Lahiri Ayanamsa:      {ayan:.6f}°")
print()
print(f"  Topocentric sidereal: {topo_sid:.6f}°  ← WRONG (Dhanishtha)")
print(f"  Geocentric sidereal:  {geo_sid:.6f}°   ← CORRECT (Shatabhisha)")
print(f"  Drik Panchang:        307.162° (Aquarius 7°09′44″)")
print(f"  Topo error:           {abs(topo_sid - expected):.4f}° ({abs(topo_sid - expected)*60:.1f} arcmin)")
print(f"  Geo error:            {abs(geo_sid - expected):.4f}° ({abs(geo_sid - expected)*60:.1f} arcmin)")
print()

# Nakshatra for geocentric
NAKSHATRA_SPAN = 360.0 / 27
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
VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
             "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

for name, start, lord in nakshatras:
    end = start + NAKSHATRA_SPAN
    if geo_sid >= start and geo_sid < end:
        pos_in_nak = geo_sid - start
        elapsed_frac = pos_in_nak / NAKSHATRA_SPAN
        remaining_frac = 1.0 - elapsed_frac
        balance = VIM_YEARS[lord] * remaining_frac
        print(f"Nakshatra (geocentric): {name} | Lord: {lord}")
        print(f"  Position in nak: {pos_in_nak:.4f}°")
        print(f"  Elapsed: {elapsed_frac:.6f} ({elapsed_frac*100:.2f}%)")
        print(f"  Remaining: {remaining_frac:.6f} ({remaining_frac*100:.2f}%)")
        print(f"  Balance at birth: {balance:.4f}y of {lord} MD ({VIM_YEARS[lord]}y full)")
        break

# Build full Mahadasha sequence
print()
print("=" * 70)
print("CORRECT P7 SINETH MAHADASHA (geocentric Moon)")
print("=" * 70)

def add_years_days(dt, years):
    total_days = years * 365.2425
    days_int = int(total_days)
    seconds_frac = (total_days - days_int) * 86400
    return dt + timedelta(days=days_int, seconds=seconds_frac)

start_lord = lord
start_idx = VIM_ORDER.index(start_lord)
current_dt = birth_local

print(f"  {'Lord':10s} {'Start':>21s} {'End':>21s} {'Years':>8s} {'Age Range':>14s}")
print(f"  {'-'*72}")
now = datetime(2026, 7, 26)
for i in range(9):
    lord_i = VIM_ORDER[(start_idx + i) % 9]
    yrs = balance if i == 0 else VIM_YEARS[lord_i]
    start = current_dt
    end = add_years_days(start, yrs)
    age_s = (start - birth_local).total_seconds() / (365.2425 * 86400)
    age_e = (end - birth_local).total_seconds() / (365.2425 * 86400)
    flag = " ◀ NOW" if start <= now < end else ""
    print(f"  {lord_i:10s} {start.strftime('%Y-%m-%d %H:%M:%S'):>21s} {end.strftime('%Y-%m-%d %H:%M:%S'):>21s} {yrs:7.4f}y {age_s:4.1f}–{age_e:.1f}{flag}")
    current_dt = end
    if start <= now < end:
        current_md = (lord_i, start, end, yrs)

# Current Antardasha
if current_md:
    md_lord, md_start, md_end, md_yrs = current_md
    print(f"\n  {md_lord} MAHADASHA — ANTARDASHA:")
    ad_start = md_start
    for ad_lord in VIM_ORDER:
        ad_yrs = (md_yrs * VIM_YEARS[ad_lord]) / 120.0
        ad_end = add_years_days(ad_start, ad_yrs)
        flag = " ◀ NOW" if ad_start <= now < ad_end else ""
        print(f"    {ad_lord:10s} {ad_start.strftime('%Y-%m-%d %H:%M:%S')} → {ad_end.strftime('%Y-%m-%d %H:%M:%S')}  {ad_yrs:.4f}y{flag}")
        ad_start = ad_end
