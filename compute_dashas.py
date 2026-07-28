#!/usr/bin/env python3
"""Compute Vimshottari Dasha for all 6 persons using AppliedJyotish methodology.
Lahiri Ayanamsa, Vimshottari from Moon Nakshatra, Placidus houses."""

from datetime import datetime, timedelta

def add_days(start, years):
    return start + timedelta(days=int(years * 365.25))

# Nakshatra definitions (Lahiri - starting from Aries 0°)
nakshatras = [
    ("Ashwini", 0.0, "Ketu"),
    ("Bharani", 13.333, "Venus"),
    ("Krittika", 26.667, "Sun"),
    ("Rohini", 40.0, "Moon"),
    ("Mrigashira", 53.333, "Mars"),
    ("Ardra", 66.667, "Rahu"),
    ("Punarvasu", 80.0, "Jupiter"),
    ("Pushya", 93.333, "Saturn"),
    ("Ashlesha", 106.667, "Mercury"),
    ("Magha", 120.0, "Ketu"),
    ("Purva Phalguni", 133.333, "Venus"),
    ("Uttara Phalguni", 146.667, "Sun"),
    ("Hasta", 160.0, "Moon"),
    ("Chitra", 173.333, "Mars"),
    ("Swati", 186.667, "Rahu"),
    ("Vishakha", 200.0, "Jupiter"),
    ("Anuradha", 213.333, "Saturn"),
    ("Jyeshtha", 226.667, "Mercury"),
    ("Mula", 240.0, "Ketu"),
    ("Purva Ashadha", 253.333, "Venus"),
    ("Uttara Ashadha", 266.667, "Sun"),
    ("Shravana", 280.0, "Moon"),
    ("Dhanishtha", 293.333, "Mars"),
    ("Shatabhisha", 306.667, "Rahu"),
    ("Purva Bhadrapada", 320.0, "Jupiter"),
    ("Uttara Bhadrapada", 333.333, "Saturn"),
    ("Revati", 346.667, "Mercury"),
]

# Sign base longitudes (Lahiri — Aries starts at 0°)
sign_bases = {
    'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
    'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
    'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330
}

# Vimshottari sequence and years
vim_order = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
vim_years = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18,
             'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

def get_nakshatra(moon_longitude):
    """Given Moon's sidereal longitude in degrees, return nakshatra name, lord, balance."""
    nak_span = 360.0 / 27  # 13.3333...
    for i, (name, start, lord) in enumerate(nakshatras):
        if moon_longitude >= start and moon_longitude < start + nak_span:
            elapsed = moon_longitude - start
            remaining = nak_span - elapsed
            balance_frac = remaining / nak_span
            balance_years = vim_years[lord] * balance_frac
            return name, lord, balance_years
    # If exactly 360°, last nakshatra
    name, start, lord = nakshatras[-1]
    elapsed = moon_longitude - start
    balance_years = vim_years[lord] * (1 - elapsed / nak_span)
    return name, lord, balance_years

def compute_mahadasha(birth_dt, start_lord, balance_years):
    """Generate mahadasha sequence from birth."""
    start_idx = vim_order.index(start_lord)
    md_list = []
    current = birth_dt
    for i in range(9):
        lord = vim_order[(start_idx + i) % 9]
        yrs = balance_years if i == 0 else vim_years[lord]
        start = current
        end = add_days(start, yrs)
        age_s = (start - birth_dt).days / 365.25
        age_e = (end - birth_dt).days / 365.25
        md_list.append((lord, start, end, yrs, age_s, age_e))
        current = end
    return md_list

def compute_antardasha(md_lord, md_start, md_years):
    """Generate antardasha sequence for a mahadasha."""
    ad_list = []
    ad_start = md_start
    for ad_lord in vim_order:
        ad_yrs = (md_years * vim_years[ad_lord]) / 120
        ad_end = add_days(ad_start, ad_yrs)
        ad_list.append((ad_lord, ad_start, ad_end, ad_yrs))
        ad_start = ad_end
    return ad_list

# =====================================================
# PERSON DATA (from repo files & AppliedJyotish PDF)
# =====================================================

# Moon positions from best available sources
persons = [
    {
        "id": "P1",
        "name": "Bappa",
        "birth": datetime(1962, 5, 27, 3, 38, 54),
        "birthplace": "Polgahawela/Colombo, Sri Lanka",
        "moon_sign": "TBD",      # Need from repo data
        "moon_deg": None,         # Will compute from available data
        "lagna": "Aries",
        "gender": "Male",
        "source_note": "Repo famous_people_birth_data.json / p1234_classification.json",
    },
    {
        "id": "P2",
        "name": "Upulakshi",
        "birth": datetime(1997, 3, 14, 12, 0, 0),  # PLACEHOLDER time!
        "birthplace": "Colombo, Sri Lanka",
        "moon_sign": "TBD",
        "moon_deg": None,
        "lagna": "Aries (notes) / Taurus (computed)",  
        "gender": "Female",
        "source_note": "REGISTRY TIME 12:00 = PLACEHOLDER. Real TOB unknown.",
    },
    {
        "id": "P3",
        "name": "Senith",
        "birth": datetime(1995, 8, 7, 21, 18, 0),
        "birthplace": "Colombo, Sri Lanka",
        "moon_sign": "TBD",
        "moon_deg": None,
        "lagna": "Pisces",
        "gender": "Male",
        "source_note": "Repo p3 data / astro-seek link",
    },
    {
        "id": "P4",
        "name": "Niromi",
        "birth": datetime(1967, 4, 25, 8, 17, 37),
        "birthplace": "Colombo, Sri Lanka",
        "moon_sign": "TBD",
        "moon_deg": None,
        "lagna": "Taurus (Vargottama)",
        "gender": "Female",
        "source_note": "Repo famous_people_birth_data.json",
    },
    {
        "id": "P5",
        "name": "Senath",
        "birth": datetime(2001, 5, 14, 16, 8, 40),
        "birthplace": "Colombo, Sri Lanka",
        # From astro-seek Colombo recompute: Moon = Capricorn 20.87° (Shravana)
        # But earlier repos had different values. We'll use the recomputed.
        "moon_sign": "Capricorn",
        "moon_deg": 290.87,  # 270 + 20.87
        "lagna": "Virgo",
        "gender": "Male",
        "source_note": "Astro-seek Colombo recompute (senath_recompute.md)",
    },
    {
        "id": "P6",
        "name": "Dewli",
        "birth": datetime(2005, 10, 8, 8, 22, 3),
        "birthplace": "Sri Jayawardenepura Kotte, Sri Lanka",
        # From AppliedJyotish PDF: Moon Scorpio 16°51'30" = 226.858°
        "moon_sign": "Scorpio",
        "moon_deg": 226.858,  # 210 + 16.858
        "lagna": "Libra 26°01'",
        "gender": "Female",
        "source_note": "AppliedJyotish PDF (authoritative)",
    },
]

# For persons with unknown Moon degrees, I need to get them from the repo data.
# Let me check what data is available.
print("=" * 80)
print("VIMSHOTTARI DASHA — AppliedJyotish Methodology (Lahiri Ayanamsa)")
print("=" * 80)

# Process known persons (P5 and P6 have Moon degrees)
for p in persons:
    if p["moon_deg"] is None:
        print(f"\n⚠️  {p['id']} {p['name']}: Moon position UNKNOWN. Skipping.")
        print(f"   Source: {p['source_note']}")
        continue
    
    moon_lon = p["moon_deg"]
    nak_name, nak_lord, balance = get_nakshatra(moon_lon)
    
    print(f"\n{'='*80}")
    print(f"{p['id']} {p['name']} | {p['birth'].strftime('%d %b %Y %H:%M')} | {p['birthplace']}")
    print(f"Lagna: {p['lagna']} | Moon: {p['moon_sign']} {moon_lon:.2f}°")
    print(f"Nakshatra: {nak_name} ({nak_lord}-ruled) | Balance: {balance:.2f}y of {nak_lord} MD")
    print(f"{'='*80}")
    
    # Mahadasha
    md_list = compute_mahadasha(p["birth"], nak_lord, balance)
    now = datetime(2026, 7, 24)
    
    print(f"\n{'MAHADASHA':12s} {'START':>12s} {'END':>12s} {'YRS':>6s} {'AGE':>8s} {'STATUS'}")
    print("-" * 65)
    
    for lord, start, end, yrs, age_s, age_e in md_list:
        is_now = "◀ NOW" if start <= now < end else ""
        print(f"{lord:12s} {start.strftime('%Y-%m-%d'):>12s} {end.strftime('%Y-%m-%d'):>12s} {yrs:5.1f}y {age_s:3.0f}-{age_e:3.0f}  {is_now}")
    
    # Find current MD and show Antardasha
    current_md = None
    for lord, start, end, yrs, age_s, age_e in md_list:
        if start <= now < end:
            current_md = (lord, start, end, yrs)
            break
    
    if current_md:
        lord, md_start, md_end, md_yrs = current_md
        print(f"\n{lord} MAHADASHA — ANTARDASHA ({md_start.strftime('%Y-%m-%d')} → {md_end.strftime('%Y-%m-%d')})")
        print("-" * 60)
        
        ad_list = compute_antardasha(lord, md_start, md_yrs)
        for ad_lord, ad_start, ad_end, ad_yrs in ad_list:
            is_ad_now = "◀ NOW" if ad_start <= now < ad_end else ""
            print(f"  {ad_lord:10s} {ad_start.strftime('%Y-%m-%d')} → {ad_end.strftime('%Y-%m-%d')}  {ad_yrs:.2f}y  {is_ad_now}")
    
    # Last 3 MDs for brevity
    print(f"\n  ... continuing ...")
    for lord, start, end, yrs, age_s, age_e in md_list[-3:]:
        print(f"  {lord:12s} {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}  {yrs:.1f}y  Age {age_s:.0f}-{age_e:.0f}")
