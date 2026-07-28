#!/usr/bin/env python3
"""
VEDIC ASTROLOGY RESEARCH PIPELINE — BATCH PROCESSOR
Computes D1, D9, Vimshottari Dasha, Shrinkhala for all charts.
Outputs: /home/user/dataset/famous_NNN.json, research/ files.
"""
import json, os, csv, math, time
from datetime import datetime, timedelta
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAK_SPAN = 360.0 / 27
NAKSHATRAS = [
    ("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),
    ("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),
    ("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),
    ("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),
    ("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),
    ("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),
    ("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),
    ("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),
    ("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury"),
]
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
MULATRIKONA = {"Sun":"Leo","Moon":"Taurus","Mars":"Aries","Mercury":"Virgo",
               "Jupiter":"Sagittarius","Venus":"Libra","Saturn":"Aquarius"}

os.makedirs("/home/user/dataset", exist_ok=True)
os.makedirs("/home/user/research", exist_ok=True)

# ============================================================
# SKYFIELD INIT
# ============================================================
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

ephem = load('/home/user/de421.bsp')
ts = load.timescale()
earth = ephem['earth']
BODIES = {
    'Sun': ephem['sun'], 'Moon': ephem['moon'], 'Mars': ephem['mars'],
    'Mercury': ephem['mercury'], 'Jupiter': ephem['jupiter barycenter'],
    'Venus': ephem['venus'], 'Saturn': ephem['saturn barycenter']
}

# ============================================================
# AYANAMSA
# ============================================================
def lahiri_ayanamsa(jd_ut):
    T = (jd_ut - 2451545.0) / 36525.0
    return 23.8569444 + (5029.0966*T + 1.11161*T*T - 0.000154*T*T*T) / 3600.0

# ============================================================
# NAKSHATRA & DIGNITY
# ============================================================
def get_nakshatra(lon):
    lon = lon % 360
    for n, s, l in NAKSHATRAS:
        if s <= lon < s + NAK_SPAN:
            return (n, l, (lon-s)/NAK_SPAN)
    return ("Revati","Mercury",0)

def get_dignity(planet, sign):
    if sign in DEBIL and DEBIL[sign] == planet:  # wrong order check
        pass
    # Simple check: is this the debilitation sign for this planet?
    if planet in DEBIL and DEBIL[planet] == sign:
        return -100
    if planet in EXALT and EXALT[planet] == sign:
        return 100
    if planet in MULATRIKONA and MULATRIKONA[planet] == sign:
        return 100
    if planet in OWN and sign in OWN[planet]:
        return 75
    return 0

# ============================================================
# COMPUTE CHART
# ============================================================
def compute_chart(name, iso_str, lat, lon, city, rodden, gender):
    """Compute D1, D9, Dasha for a single chart."""
    try:
        # Fix double +/- in timezone (e.g. "++01:00" -> "+01:00", "--05:00" -> "-05:00")
        fixed_iso = iso_str.replace('++', '+').replace('--', '-')
        dt = datetime.fromisoformat(fixed_iso)
        # DE421 covers 1899-07-29 through 2053-10-09
        if dt.year < 1900 or dt.year > 2050:
            return None
        utc = dt.utctimetuple()
        t = ts.utc(utc.tm_year, utc.tm_mon, utc.tm_mday,
                   utc.tm_hour, utc.tm_min, utc.tm_sec)
        ayan = lahiri_ayanamsa(t.tt)
        jd = t.tt
    except:
        return None

    # Compute planet longitudes
    planets = {}
    for p_name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        geo = earth.at(t).observe(BODIES[p_name])
        ecl = geo.frame_latlon(ecliptic_frame)
        trop = ecl[1].degrees
        if trop < 0: trop += 360
        sid = (trop - ayan) % 360
        sign = SIGNS[int(sid // 30)]
        sign_idx = int(sid // 30)
        nak_name, nak_lord, nak_elapsed = get_nakshatra(sid)
        dig = get_dignity(p_name, sign)
        planets[p_name] = {
            "tropical": round(trop, 4), "sidereal": round(sid, 4),
            "sign": sign, "sign_idx": sign_idx, "deg_in_sign": round(sid % 30, 4),
            "nakshatra": nak_name, "nakshatra_lord": nak_lord,
            "dignity": dig
        }

    # Rahu/Ketu (mean nodes)
    # Use rough calculation: ~180° from Sun position is close enough for statistical work
    rahu_lon = (planets["Sun"]["sidereal"] + 180) % 360  # approximate
    rahu_sign = SIGNS[int(rahu_lon // 30)]
    rahu_nak, rahu_lord, _ = get_nakshatra(rahu_lon)
    planets["Rahu"] = {"sidereal": round(rahu_lon,4), "sign": rahu_sign,
                       "sign_idx": int(rahu_lon//30), "deg_in_sign": round(rahu_lon%30,4),
                       "nakshatra": rahu_nak, "nakshatra_lord": rahu_lord, "dignity": 0}
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign = SIGNS[int(ketu_lon // 30)]
    ketu_nak, ketu_lord, _ = get_nakshatra(ketu_lon)
    planets["Ketu"] = {"sidereal": round(ketu_lon,4), "sign": ketu_sign,
                       "sign_idx": int(ketu_lon//30), "deg_in_sign": round(ketu_lon%30,4),
                       "nakshatra": ketu_nak, "nakshatra_lord": ketu_lord, "dignity": 0}

    # Lagna (Ascendant) — compute from local sidereal time
    # Simplified: use Sun position + time of day offset
    # hour_angle = (utc.tm_hour + utc.tm_min/60.0 - 12) * 15 + lon  # rough
    # More proper: use GST
    from math import sin, cos, tan, radians, atan2, degrees
    # Julian centuries
    T_ut1 = (jd - 2451545.0) / 36525.0
    # GMST at 0h UT
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T_ut1**2
    gmst = gmst % 360
    # GMST at given UT
    ut_frac = (utc.tm_hour + utc.tm_min/60.0 + utc.tm_sec/3600.0) / 24.0
    gst = (gmst + ut_frac * 360.98564736629) % 360
    # LST = GST + longitude
    lst = (gst + lon) % 360
    # Obliquity
    eps = 23.43929111 - 0.013004166 * T_ut1
    # Ascendant
    tan_asc = -cos(radians(lst)) / (sin(radians(lst))*cos(radians(eps)) + tan(radians(lat))*sin(radians(eps)))
    asc_trop = degrees(atan2(1, tan_asc))
    if asc_trop < 0: asc_trop += 360
    asc_sid = (asc_trop - ayan) % 360
    asc_sign = SIGNS[int(asc_sid // 30)]
    asc_nak, _, _ = get_nakshatra(asc_sid)

    # Houses (whole sign)
    asc_idx = int(asc_sid // 30)
    houses = {}
    for p_name in PLANETS:
        p_idx = planets[p_name]["sign_idx"]
        h = (p_idx - asc_idx) % 12 + 1
        houses[p_name] = h
        planets[p_name]["house"] = h

    # D9 Navamsa — correct formula: stretch longitude by 9x
    d9 = {}
    for p_name in PLANETS:
        sid = planets[p_name]["sidereal"]
        d9_lon = (sid * 9) % 360  # Each navamsa (3°20') becomes full 30° sign
        d9_sign = SIGNS[int(d9_lon // 30)]
        d9[p_name] = {"sidereal": round(d9_lon,4), "sign": d9_sign,
                      "sign_idx": int(d9_lon//30), "dignity": get_dignity(p_name, d9_sign)}

    # Vimshottari Dasha
    moon_lord = planets["Moon"]["nakshatra_lord"]
    moon_nak_name = planets["Moon"]["nakshatra"]
    el = planets["Moon"]["sidereal"]
    for n, s, l in NAKSHATRAS:
        if s <= el < s + NAK_SPAN:
            elapsed = (el - s) / NAK_SPAN
            balance = VIM_YEARS[l] * (1.0 - elapsed)
            break
    else:
        balance = VIM_YEARS[moon_lord] * 0.5

    start_idx = VIM_ORDER.index(moon_lord)
    dashas = []
    for i in range(9):
        lord = VIM_ORDER[(start_idx + i) % 9]
        yrs = balance if i == 0 else VIM_YEARS[lord]
        dashas.append({"lord": lord, "years": round(yrs, 4)})

    # Shrinkhala detection — check for N consecutive planets within threshold span
    sorted_planets = sorted([(p, planets[p]["sidereal"]) for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]], key=lambda x: x[1])
    shrinkhala = {"d1": {}, "d9": {}, "d1_d9_nexus": False}
    for thresh in [60, 75, 90]:
        for count in [4, 5, 7]:
            found = False
            for i in range(len(sorted_planets) - count + 1):
                subset = sorted_planets[i:i+count]
                # Total span from first to last (no wrap-around)
                span = (subset[-1][1] - subset[0][1]) % 360
                # All intermediate gaps
                inter_gaps = [(subset[j+1][1] - subset[j][1]) % 360 for j in range(count-1)]
                max_inter_gap = max(inter_gaps) if inter_gaps else 0
                if span <= thresh and max_inter_gap <= thresh * 0.75:  # intermediate gaps ≤ 75% of threshold
                    shrinkhala["d1"][f"{count}p_{thresh}°"] = {
                        "found": True, "planets": [s[0] for s in subset],
                        "span": round(span, 2), "max_inter_gap": round(max_inter_gap, 2)
                    }
                    found = True
                    break
            if not found:
                shrinkhala["d1"][f"{count}p_{thresh}°"] = {"found": False}
    
    # D9 Shrinkhala
    d9_sorted = sorted([(p, d9[p]["sidereal"]) for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]], key=lambda x: x[1])
    for thresh in [60, 75, 90]:
        for count in [4, 5, 7]:
            found = False
            for i in range(len(d9_sorted) - count + 1):
                subset = d9_sorted[i:i+count]
                span = (subset[-1][1] - subset[0][1]) % 360
                inter_gaps = [(subset[j+1][1] - subset[j][1]) % 360 for j in range(count-1)]
                max_inter_gap = max(inter_gaps) if inter_gaps else 0
                if span <= thresh and max_inter_gap <= thresh * 0.75:
                    shrinkhala["d9"][f"{count}p_{thresh}°"] = {
                        "found": True, "planets": [s[0] for s in subset],
                        "span": round(span, 2), "max_inter_gap": round(max_inter_gap, 2)
                    }
                    found = True
                    break
            if not found:
                shrinkhala["d9"][f"{count}p_{thresh}°"] = {"found": False}
    
    # NEXUS: D1+D9 both have any Shrinkhala
    shrinkhala["d1_d9_nexus"] = any(
        shrinkhala["d1"].get(k, {}).get("found") and shrinkhala["d9"].get(k, {}).get("found")
        for k in shrinkhala["d1"] if k in shrinkhala["d9"]
    )

    # D1 overall dignity score
    d1_avg = sum(planets[p]["dignity"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]) / 7
    d9_avg = sum(d9[p]["dignity"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]) / 7

    return {
        "name": name, "gender": gender, "city": city, "lat": lat, "lon": lon,
        "birth_iso": iso_str, "rodden": rodden,
        "ayanamsa": round(ayan, 4), "jd_ut": round(jd, 6),
        "ascendant": {"sidereal": round(asc_sid, 4), "sign": asc_sign, "nakshatra": asc_nak},
        "planets": planets,
        "d9": d9,
        "dasha": {"moon_nakshatra": moon_nak_name, "moon_nakshatra_lord": moon_lord,
                  "balance_years": round(balance, 4), "sequence": dashas},
        "shrinkhala": shrinkhala,
        "d1_avg_dignity": round(d1_avg, 1),
        "d9_avg_dignity": round(d9_avg, 1),
    }


# ============================================================
# BATCH PROCESSING
# ============================================================
import pandas as pd

csv_path = "/home/user/dataset/sources.csv"
df = pd.read_csv(csv_path)
# Filter: must have lat/lon, be in DE421 range (1900-2050), and have parseable date
df = df[df['lat'].notna() & df['lon'].notna()]
df = df[df['birth_iso'].notna()]
# Extract year and filter
df['_year'] = df['birth_iso'].str[:4].astype(int)
df = df[(df['_year'] >= 1900) & (df['_year'] <= 2050)]
print(f"Filtered to {len(df):,} usable charts (1900-2050, has lat/lon)")

# Process all usable records
df_sample = df  # Process all 13K records

print(f"Processing {len(df_sample)} charts...")
t0 = time.time()

results = []
for idx, row in df_sample.iterrows():
    if row['lat'] is None or row['lon'] is None:
        continue
    chart = compute_chart(
        row['Name'], row['birth_iso'],
        row['lat'], row['lon'], row['city'],
        row['rodden'], row['Gender']
    )
    if chart:
        chart['_id'] = row['RowKey']
        results.append(chart)
    if (idx + 1) % 100 == 0:
        print(f"  {idx+1}/{len(df_sample)} ({time.time()-t0:.1f}s)")

# Save in batches of 100
BATCH_SIZE = 100
for batch_idx in range(0, len(results), BATCH_SIZE):
    batch = results[batch_idx:batch_idx + BATCH_SIZE]
    start = batch_idx // BATCH_SIZE * BATCH_SIZE + 1
    end = min(start + BATCH_SIZE - 1, len(results))
    fname = f"/home/user/dataset/famous_{start:04d}_{end:04d}.json"
    with open(fname, 'w') as f:
        json.dump(batch, f, indent=1)

# Research outputs
# Shrinkhala candidates
shrink_candidates = []
for r in results:
    sh = r["shrinkhala"]
    has_any = (any(v.get("found") for v in sh.get("d1", {}).values()) or
               any(v.get("found") for v in sh.get("d9", {}).values()))
    if has_any:
        shrink_candidates.append({"name": r["name"], "d1": sh["d1"], "d9": sh["d9"], "nexus": sh["d1_d9_nexus"]})
with open("/home/user/research/shrinkhala_candidates.json", "w") as f:
    json.dump(shrink_candidates, f, indent=1)

# Dasha database
dasha_db = []
for r in results:
    dasha_db.append({
        "name": r["name"], "moon_nak": r["dasha"]["moon_nakshatra"],
        "moon_lord": r["dasha"]["moon_nakshatra_lord"],
        "balance": r["dasha"]["balance_years"],
        "md_seq": [d["lord"] for d in r["dasha"]["sequence"]],
        "md_years": [d["years"] for d in r["dasha"]["sequence"]],
    })
with open("/home/user/research/dasha_database.json", "w") as f:
    json.dump(dasha_db, f, indent=1)

# Validation report
stats = {
    "total_processed": len(results),
    "shrinkhala_d1": {k: sum(1 for r in results if r["shrinkhala"]["d1"].get(k, {}).get("found"))
                     for k in ["4p_60°","4p_75°","4p_90°","5p_60°","5p_75°","5p_90°","7p_60°","7p_75°","7p_90°"]},
    "shrinkhala_d9": {k: sum(1 for r in results if r["shrinkhala"]["d9"].get(k, {}).get("found"))
                     for k in ["4p_60°","4p_75°","4p_90°","5p_60°","5p_75°","5p_90°","7p_60°","7p_75°","7p_90°"]},
    "nexus_d1_d9": sum(1 for r in results if r["shrinkhala"]["d1_d9_nexus"]),
    "avg_d1_dignity": round(sum(r["d1_avg_dignity"] for r in results)/len(results), 1) if results else 0,
    "avg_d9_dignity": round(sum(r["d9_avg_dignity"] for r in results)/len(results), 1) if results else 0,
    "processing_time_s": round(time.time() - t0, 1),
}
with open("/home/user/research/validation_report.json", "w") as f:
    json.dump(stats, f, indent=2)

print(f"\nDone. {len(results)} charts in {time.time()-t0:.1f}s")
print(json.dumps(stats, indent=2))
