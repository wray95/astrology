#!/usr/bin/env python3
"""Compute the 1967-04-25 08:17:37 Dearborn, MI FEMALE chart (NEW 4th person).
Validate planetary longitudes against the Drik Panchang sidereal positions, then
derive Lagna, planet placements, yogas, and Vimshottari dasha (current + next peaks).
"""
import swisseph as swe
from datetime import datetime

swe.set_sid_mode(swe.SIDM_LAHIRI)

# ---- Birth data (from Drik Panchang link: 25/04/1967 08:17:37, Dearborn, MI) ----
Y, M, D, H, MI, SEC = 1967, 4, 25, 8, 17, 37
# Dearborn, Michigan. US DST in 1967 began Sun Apr 30, 1967 -> Apr 25 was EST (UTC-5)
TZ = -5.0
LAT, LON = 42.3226, -83.1763  # Dearborn, MI

# Julian Day from local time
jd = swe.julday(Y, M, D, 0) + (H - TZ + MI/60.0 + SEC/3600.0)/24.0
print("Julian Day (UT):", jd)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
# Nakshatra list starting at 0 Aries
NAK = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
       "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
       "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
       "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
       "Uttara Bhadrapada","Revati"]

def sign_of(lon):
    return SIGNS[int(lon//30)], lon%30.0

def nakshatra_of(lon):
    idx = int(lon//(360.0/27.0))
    deg = lon % (360.0/27.0)
    return NAK[idx], deg, idx

# ---- Planets (mean node for Rahu/Ketu) ----
planets = {
    "Sun":  swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
}
print("\n=== SIDEREAL (Lahiri) PLANETARY LONGITUDES ===")
res = {}
for name, ipl in planets.items():
    lon = swe.calc_ut(jd, ipl, swe.FLG_SIDEREAL)[0][0]
    res[name] = lon
    s, d = sign_of(lon); nk, nd, ni = nakshatra_of(lon)
    print(f"{name:8} {lon:8.2f}  {s:11} {d:6.2f}  {nk} {nd:5.2f}")

# Rahu (mean node) & Ketu
rahu = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)[0][0]
ketu = (rahu + 180.0) % 360.0
res["Rahu"] = rahu; res["Ketu"] = ketu
s, d = sign_of(rahu); nk, nd, ni = nakshatra_of(rahu)
print(f"{'Rahu':8} {rahu:8.2f}  {s:11} {d:6.2f}  {nk} {nd:5.2f}")
s, d = sign_of(ketu); nk, nd, ni = nakshatra_of(ketu)
print(f"{'Ketu':8} {ketu:8.2f}  {s:11} {d:6.2f}  {nk} {nd:5.2f}")

# ---- Ascendant / Lagna (Whole-sign houses, Vedic) ----
h = swe.houses(jd, LAT, LON, b'W')
asc = h[1][0] % 360.0
asc_sign = SIGNS[int(asc//30)]
print("\n=== ASCENDANT / LAGNA ===")
print(f"Lagna longitude: {asc:.2f}  -> {asc_sign} ({(asc%30):.2f} deg)")
nk, nd, ni = nakshatra_of(asc)
print(f"Lagna nakshatra: {nk} {nd:.2f}")

# ---- Drik Panchang cross-check (from link) ----
print("\n=== CROSS-CHECK vs DRIK PANCHANG (sidereal) ===")
dp = {  # Drik Panchang given values
    "Mars": 27.0+0,   # 27 Virgo
    "Mercury": 24.0,  # 24 Pisces
    "Jupiter": 2.0,   # 2 Cancer
    "Saturn": 13.0,   # 13 Pisces
    "Ketu": 1.0,      # 1 Libra
}
for name, dp_deg_in_sign in dp.items():
    # Drik Panchang gives deg-within-sign; convert to absolute
    # Need the sign from their notation: Kany=Virgo(5), Meen=Pisces(11), Kark=Cancer(3), Lib=Libra(6)
    signidx = {"Mars":5,"Mercury":11,"Jupiter":3,"Saturn":11,"Ketu":6}[name]
    dp_abs = signidx*30.0 + dp_deg_in_sign
    calc_abs = res[name]
    diff = (calc_abs - dp_abs + 540)%360 - 180
    print(f"{name:8} calc {calc_abs:7.2f}  DrikP {dp_abs:7.2f}  diff {diff:6.2f}")

# ---- Vimshottari Dasha ----
# Dasha sequence order starting from a given planet
SEQ = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,
         "Jupiter":16,"Saturn":19,"Mercury":17}

moon_lon = res["Moon"]
mk, md, mi = nakshatra_of(moon_lon)
# nakshatra -> starting lord
NAK_LORD = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn",
            "Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter",
            "Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu",
            "Jupiter","Saturn","Mercury"]
start_lord = NAK_LORD[mi]
# fraction elapsed in nakshatra -> REMAINING of first dasha
# (native is BORN into the running dasha; it starts at birth_year)
frac = md / (360.0/27.0)
rem_first = YEARS[start_lord] * (1.0 - frac)
print("\n=== VIMSHOTTARI DASHA ===")
print(f"Moon nakshatra: {mk} ({mi}) -> starting lord: {start_lord}, elapsed frac {frac:.3f}")
print(f"Remaining of first ({start_lord}) dasha at birth: {rem_first:.2f}y")

# Build the dasha timeline from birth (first dasha starts AT birth)
birth_year = Y
timeline = []
si = SEQ.index(start_lord)
cur = float(birth_year)
for k in range(9):
    lord = SEQ[(si + k) % 9]
    dur = rem_first if k == 0 else YEARS[lord]
    start = cur
    end = cur + dur
    timeline.append((lord, start, end, dur))
    cur = end

# Current age & date
today = datetime(2026, 7, 22)
cur_age = 2026 - birth_year
print(f"Birth: {Y}-{M:02d}-{D:02d}  | Current year 2026 -> age ~{cur_age}")
print("\nFull dasha sequence (year ranges):")
for lord, start, end, dur in timeline:
    mark = " <== NOW" if (start <= 2026.0 < end) else ""
    print(f"  {lord:8} {start:7.1f} - {end:7.1f}  ({dur}y){mark}")

# Current dasha
cur_dasha = [t for t in timeline if t[1] <= 2026.0 < t[2]][0]
print(f"\n>>> CURRENT DASHA: {cur_dasha[0]}  ({cur_dasha[1]:.1f}-{cur_dasha[2]:.1f})")
# Next dasha
idx = timeline.index(cur_dasha)
nxt = timeline[(idx+1)%9]
print(f">>> NEXT DASHA: {nxt[0]}  ({nxt[1]:.1f}-{nxt[2]:.1f})")

# Favorable planets for a female (Jupiter=spouse/karaka, Venus, Moon, Mercury, well-placed)
# Identify "peak/favorable" dashas among remaining
favorable = ["Venus","Jupiter","Mercury","Moon"]  # general benefic strong dashas
print("\nUpcoming FAVORABLE dashas for this chart:")
for lord, start, end, dur in timeline:
    if start >= 2026.0 and lord in favorable:
        print(f"  {lord:8} {start:.1f}-{end:.1f}  ({dur}y)")

# ---- House placements (whole-sign) ----
print("\n=== PLANETARY HOUSE PLACEMENTS (whole-sign, Lagna = house 1) ===")
asc_idx = int(asc//30)
for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
    lon = res[name]
    hnum = (int(lon//30) - asc_idx) % 12 + 1
    s, d = sign_of(lon)
    print(f"  {name:8} -> House {hnum}  ({s} {d:.1f})")
