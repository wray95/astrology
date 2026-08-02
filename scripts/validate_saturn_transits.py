#!/usr/bin/env python3
"""
VALIDATE Saturn sidereal sign-entry dates: Swiss Ephemeris (Lahiri) vs the
BP Lama (Goravani Jyotish) Gochara Shani transit table 1900-2099.

Source (link-only): https://barbarapijan.com/bpa/Gochara_Shani/Shani_gochara_transits_table.htm
Table dates were extracted from the fetched page (chunks 0-3).

Then: map P-series Sade Sati periods using the table's own "begin janma
Sade Sati for Chandra-<sign>" markers + each person's Moon sign (SE-computed).
"""
import json, sys, datetime
sys.path.insert(0, "scripts")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]

# (date, sign) from the BP Lama table — first entries per sign 1900-2099
TABLE = [
    ("1902-02-11","Capricorn"),("1905-02-04","Aquarius"),("1907-04-19","Pisces"),
    ("1909-07-08","Aries"),("1912-05-07","Taurus"),("1914-06-20","Gemini"),
    ("1916-08-01","Cancer"),("1918-09-17","Leo"),("1920-11-16","Virgo"),
    ("1923-10-15","Libra"),("1925-12-31","Scorpio"),("1928-12-24","Sagittarius"),
    ("1931-04-11","Capricorn"),("1934-03-15","Aquarius"),("1937-02-25","Pisces"),
    ("1939-04-27","Aries"),("1941-06-18","Taurus"),("1943-08-05","Gemini"),
    ("1945-09-22","Cancer"),("1948-07-26","Leo"),("1950-09-19","Virgo"),
    ("1952-11-25","Libra"),("1955-11-11","Scorpio"),("1958-02-07","Sagittarius"),
    ("1961-02-01","Capricorn"),("1964-01-27","Aquarius"),("1966-04-08","Pisces"),
    ("1968-06-16","Aries"),("1971-04-27","Taurus"),("1973-06-10","Gemini"),
    ("1975-07-23","Cancer"),("1977-09-06","Leo"),("1979-11-03","Virgo"),
    ("1982-10-05","Libra"),("1984-12-20","Scorpio"),("1987-12-16","Sagittarius"),
    ("1990-03-20","Capricorn"),("1993-03-05","Aquarius"),("1995-06-01","Pisces"),
    ("1998-04-17","Aries"),("2000-06-06","Taurus"),("2002-07-22","Gemini"),
    ("2004-09-05","Cancer"),("2006-10-31","Leo"),("2009-09-09","Virgo"),
    ("2011-11-14","Libra"),("2014-11-02","Scorpio"),("2017-01-26","Sagittarius"),
    ("2020-01-23","Capricorn"),("2022-04-28","Aquarius"),("2025-03-29","Pisces"),
    ("2027-06-02","Aries"),("2029-08-08","Taurus"),("2032-05-30","Gemini"),
    ("2034-07-12","Cancer"),("2036-08-27","Leo"),("2038-10-22","Virgo"),
    ("2041-01-27","Libra"),("2043-12-11","Scorpio"),("2046-12-07","Sagittarius"),
    ("2049-03-06","Capricorn"),("2052-02-24","Aquarius"),("2054-05-14","Pisces"),
    ("2057-01-06","Aries"),("2059-05-27","Taurus"),("2061-07-10","Gemini"),
    ("2063-08-23","Cancer"),("2065-10-12","Leo"),("2068-08-29","Virgo"),
    ("2070-11-04","Libra"),("2073-02-05","Scorpio"),("2076-01-16","Sagittarius"),
    ("2079-01-14","Capricorn"),("2081-04-11","Aquarius"),("2084-03-19","Pisces"),
    ("2086-05-21","Aries"),("2088-07-17","Taurus"),("2090-09-18","Gemini"),
    ("2093-07-02","Cancer"),("2095-08-18","Leo"),("2097-10-11","Virgo"),
    ("2099-12-25","Libra"),
]
# Sade Sati begin markers from the table (Moon sign -> begin date)
SADE_SATI_BEGIN = {
    "Taurus": "2029-08-08", "Gemini": "2032-05-30", "Cancer": "2034-07-12",
    "Leo": "2036-08-27", "Virgo": "2038-10-22", "Libra": "2041-01-27",
    "Scorpio": "2043-12-11", "Sagittarius": "2046-12-07", "Capricorn": "2049-03-06",
    "Aquarius": "2052-02-24", "Pisces": "2054-05-14", "Aries": "2057-01-06",
}
# For the 2020s-era (current people), use the actual 2020s markers:
SADE_SATI_BEGIN_2020S = {
    "Sagittarius": "2017-01-26", "Capricorn": "2020-01-23", "Aquarius": "2022-04-28",
    "Pisces": "2025-03-29", "Aries": "2027-06-02", "Taurus": "2029-08-08",
    "Gemini": "2032-05-30", "Cancer": "2034-07-12", "Leo": "2036-08-27",
    "Virgo": "2038-10-22", "Libra": "2041-01-27", "Scorpio": "2043-12-11",
}

def jd_of_date(s):
    y, m, d = map(int, s.split("-"))
    return swe.julday(y, m, d, 12.0)

def saturn_sign(jd):
    lt, _ = swe.calc_ut(jd, 6)
    return int(((lt[0] - swe.get_ayanamsa(jd)) % 360) // 30)

def se_entry_date(target_sign_idx, approx_date_str, window=30):
    """Find the first date within ±window days of approx when Saturn enters sign."""
    jd0 = jd_of_date(approx_date_str)
    # search backwards to find when it was NOT in sign, then forward to entry
    jd = jd0
    for _ in range(window):
        if saturn_sign(jd) != target_sign_idx:
            break
        jd -= 1.0
    # now step forward until sign reached
    for _ in range(2*window):
        if saturn_sign(jd) == target_sign_idx:
            dt = datetime.datetime(2000,1,1) + datetime.timedelta(days=jd-2451545.0)
            return dt.strftime("%Y-%m-%d")
        jd += 1.0
    return None

print("=== VALIDATION: SE (Lahiri) vs BP Lama table — first entry into each sign ===")
print(f"{'Table date':<12}{'Sign':<12}{'SE date':<12}{'Δ days':<8}{'OK?'}")
maxdiff = 0; ok = 0
rows = []
for ds, sign in TABLE:
    idx = SIGNS.index(sign)
    se = se_entry_date(idx, ds)
    d_ok = ""
    diff = None
    if se:
        d1 = datetime.date(*map(int, ds.split("-")))
        d2 = datetime.date(*map(int, se.split("-")))
        diff = abs((d2 - d1).days)
        maxdiff = max(maxdiff, diff)
        d_ok = "OK" if diff <= 3 else ("~" if diff <= 7 else "DIFF")
        if diff <= 3: ok += 1
    rows.append({"table": ds, "sign": sign, "se": se, "diff_days": diff})
    print(f"{ds:<12}{sign:<12}{str(se):<12}{str(diff):<8}{d_ok}")
print(f"\n{ok}/{len(TABLE)} entries match within ±3 days. Max diff {maxdiff} days.")

# ---- P-series Moon signs + Sade Sati (computed FROM the table entries) ----
print("\n=== P-SERIES SADE SATI (from BP Lama entry dates + SE Moon sign) ===")
import datetime as _dt
sys.path.insert(0, "scripts")
from p_update import PD
from blind_validation_engine import jd_of, chart
# build per-sign entry list from TABLE
ENTRIES = {}
for ds, sign in TABLE:
    ENTRIES.setdefault(sign, []).append(ds)
def sade_sati(moon_sign, today="2026-08-03"):
    """Sade Sati = Saturn transits Moon sign + next 2. Begin = entry into Moon
    sign (most recent cycle relative to today); end = entry into the 4th sign."""
    mi = SIGNS.index(moon_sign)
    signs3 = [SIGNS[(mi+k) % 12] for k in range(3)]
    entries = ENTRIES[moon_sign]
    # choose the entry nearest (≤) today from the past, else the next future one
    today_d = _dt.date(*map(int, today.split("-")))
    past = [d for d in entries if _dt.date(*map(int, d.split("-"))) <= today_d]
    begin = (past or entries)[-1]
    end_sign = SIGNS[(mi+3) % 12]
    end_candidates = [d for d in ENTRIES[end_sign] if _dt.date(*map(int, d.split("-"))) >= _dt.date(*map(int, begin.split("-")))]
    end = end_candidates[0] if end_candidates else None
    return begin, end, signs3
people = json.load(open("data/blind_validation_people.json"))["people"]
out = []
for p in people:
    ch = chart(p)
    moon_sign = ch["planets"]["Moon"]["sign"]
    begin, end, signs3 = sade_sati(moon_sign)
    out.append({"id": p["id"], "name": p["name"], "moon_sign": moon_sign,
                "sade_sati_begin": begin, "sade_sati_end": end,
                "sade_sati_signs": signs3})
    print(f"  {p['id']} {p['name']:<20} Moon={moon_sign:<12} Sade Sati {begin} -> {end}  ({', '.join(signs3)})")

json.dump({"validation": rows, "match_within_3d": ok, "max_diff_days": maxdiff,
           "n_table": len(TABLE), "p_series_sade_sati": out},
          open("dataset/saturn_transit_validation_bplama.json", "w"), indent=1)
print("\nWrote dataset/saturn_transit_validation_bplama.json")
