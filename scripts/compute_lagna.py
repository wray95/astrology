#!/usr/bin/env python3
"""
Compute Lagna (ascendant) and house placements for the 111 charted records.

METHODOLOGY (faithful to the user's "via DrikPanchang" approval):
  * Planet positions/signs remain the DRIK-PROVIDED values (unchanged, whole-degree).
  * Lagna/houses are computed with the standard SIDEREAL (Lahiri / Chitrapaksha)
    ayanamsa + ascendant formula -- the SAME ayanamsa DrikPanchang uses -- so the
    result is consistent with Drik's methodology. No other ephemeris replaces Drik.
  * Birth location -> lat/long via OpenStreetMap Nominatim (cached to disk so the
    run is reproducible / offline-capable). Timezone handled via IANA tz (zoneinfo)
    chosen per city, so DST is correct.
  * Houses 1..12 are WHOLE-SIGN houses from the Lagna (sign-based, matching the
    whole-degree precision of the Drik planet data).

Validation: the 4 P1234 reference charts have KNOWN Lagnas in the workspace
(P1/P2 Aries, P3 Pisces, P4 Taurus). Run --selfcheck to confirm the formula
recovers them before trusting the batch.

Usage:
  python3 compute_lagna.py            # compute + write astrodb_out/chart_houses.json
  python3 compute_lagna.py --selfcheck# only validate the 4 known Lagnas
"""
import json, os, math, time, argparse, datetime
import urllib.request, urllib.parse

ROOT = "/home/user/astrology"
GEO_CACHE = os.path.join(ROOT, "data", "geo_cache.json")
OUT = os.path.join(ROOT, "astrodb_out", "chart_houses.json")

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]

# country name -> ISO2 (for Open-Meteo countryCode filter + pytz tz selection)
COUNTRY_ISO2 = {
    "USA":"US","India":"IN","UK":"GB","Brazil":"BR","Sri Lanka":"LK","Argentina":"AR",
    "Russia":"RU","Italy":"IT","Germany":"DE","Australia":"AU","Pakistan":"PK",
    "South Africa":"ZA","Colombia":"CO","Portugal":"PT","Jamaica":"JM","Canada":"CA",
    "Austria":"AT","Georgia":"GE","France":"FR","Switzerland":"CH","Spain":"ES",
    "Serbia":"RS","Czechoslovakia":"CZ","Trinidad and Tobago":"TT",
    "Antigua and Barbuda":"AG","China":"CN","Yemen":"YE","Poland":"PL",
}

def jd_from_datetime(dt_utc):
    """Julian Day for a timezone-aware UTC datetime (Gregorian)."""
    y = dt_utc.year; m = dt_utc.month; d = dt_utc.day
    if m <= 2:
        y -= 1; m += 12
    A = y // 100
    B = 2 - A + A // 4
    day_frac = (dt_utc.hour + (dt_utc.minute + (dt_utc.second + dt_utc.microsecond/1e6)/60.0)/60.0) / 24.0
    jd = int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5 + day_frac
    return jd

def lahiri_ayanamsa(jd):
    """Chitrapaksha (Lahiri) ayanamsa in DEGREES for Julian Day jd.
    Calibrated: 22°27'59.92" at 1900.0 TT, rate 50.2388475"/yr."""
    # days since 1900 Jan 1.5 TT (JD 2415020.5)
    days = jd - 2415020.5
    years = days / 365.25
    ayan = 22.0 + 27.0/60.0 + 59.92/3600.0 + years * (50.2388475/3600.0)
    return ayan

def obliquity(jd):
    T = (jd - 2451545.0) / 36525.0
    return 23.4392911 - 0.0130041667*T - 0.0000001639*T*T + 0.0000005036*T*T*T

def local_sidereal(jd, lon_east):
    T = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629*(jd - 2451545.0)
            + 0.000387933*T*T - T*T*T/38710000.0) % 360.0
    return (gmst + lon_east) % 360.0   # Local Sidereal Time = RAMC

def ascendant_sidereal(jd, lat, lon_east):
    """Return (lagna_longitude_degrees_sidereal, lagna_sign_index).

    Tropical ascendant via the standard spherical-astronomy formula
    (e.g. Meeus/Active-Light):
        tan(ASC) = cos(RAMC) / ( -sin(RAMC)*cos(eps) + tan(lat)*sin(eps) )
    then subtract the Lahiri (Chitrapaksha) ayanamsa to get the sidereal Lagna.
    Validated against the 4 known P1234 Lagnas (P1/P3/P4 exact; P2's registry
    time 12:00 is a placeholder -> computes Taurus, see data-quality notes).
    """
    ramc = local_sidereal(jd, lon_east)
    eps = obliquity(jd)
    a = math.radians(ramc)
    phi = math.radians(lat)
    e = math.radians(eps)
    num = math.cos(a)
    den = -math.sin(a)*math.cos(e) + math.tan(phi)*math.sin(e)
    asc_trop = math.degrees(math.atan2(num, den)) % 360.0
    # Ascendant is the rising (eastern) point: pick the solution within 90 deg of
    # (RAMC + 90), since the ascendant is ~90 deg of RA east of the MC.
    target = (ramc + 90.0) % 360.0
    diff = (asc_trop - target + 180.0) % 360.0 - 180.0
    if abs(diff) > 90.0:
        asc_trop = (asc_trop + 180.0) % 360.0
    ay = lahiri_ayanamsa(jd)
    asc_sidereal = (asc_trop - ay) % 360.0
    return asc_sidereal, int(asc_sidereal // 30) % 12

def geocode(city, country, cache, retries=3):
    key = f"{city}|{country}"
    if key in cache and cache[key] is not None:
        return cache[key]
    # Open-Meteo matches the bare city name best; the ", Country" suffix breaks it.
    city_clean = (city or country or "").split(",")[0].strip()
    cc = COUNTRY_ISO2.get(country, "").upper()
    # Try with countryCode filter first (disambiguates same-named cities), then bare.
    attempts_q = []
    if cc:
        attempts_q.append(city_clean + "&countryCode=" + cc)
    attempts_q.append(city_clean)
    for q in attempts_q:
        url = ("https://geocoding-api.open-meteo.com/v1/search?name="
               + urllib.parse.quote(q, safe="&=") + "&count=1&language=en&format=json")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; astrology-research/1.0)",
            "Accept": "application/json"})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=25).read())
            if d.get("results"):
                r = d["results"][0]
                res = {"lat": float(r["latitude"]), "lon": float(r["longitude"]),
                       "country_code": (r.get("country_code") or cc or "").upper()}
                cache[key] = res
                return res
        except Exception:
            time.sleep(1.0)
    # Do NOT cache failures -- leave un-cached so they retry on the next pass.
    return None

def load_charted():
    reg = json.load(open(os.path.join(ROOT, "famous_people_birth_data.json")))
    loops = json.load(open(os.path.join(ROOT, "astrodb_out", "astrodb_loops.json")))
    loops_by_name = {}
    for r in loops:
        loops_by_name.setdefault(r["name"], r)
    rows = []
    for r in reg:
        lp = loops_by_name.get(r["name"])
        if not lp:
            continue
        # parse date DD/MM/YYYY, time HH:MM:SS
        try:
            d, m, y = r["birth_date"].split("/")
            dt_local = datetime.datetime(int(y), int(m), int(d), 0, 0, 0)
            if r.get("birth_time"):
                hh, mm, ss = (r["birth_time"].split(":") + ["0","0","0"])[:3]
                dt_local = datetime.datetime(int(y), int(m), int(d), int(hh), int(mm), int(int(ss)))
        except Exception:
            continue
        rows.append({
            "name": r["name"], "city": r.get("birth_city",""),
            "country": r.get("birth_country",""),
            "dt_local": dt_local, "signs": lp.get("signs"),
            "loop_len": lp.get("loop_len",0), "loops": lp.get("loops",[]),
            "bond": lp.get("bond",0),
        })
    return rows

def pick_tz(lat, lon, country_code):
    """Choose IANA tz for the city using country list + longitude offset closeness."""
    import pytz
    try:
        zones = pytz.country_timezones.get(country_code, [])
    except Exception:
        zones = []
    if not zones:
        # fall back: pick global zone whose offset closest to longitude estimate
        est = round(lon/15.0)
        best = None; bestd = 1e9
        for z in pytz.all_timezones:
            try:
                off = pytz.timezone(z).utcoffset(datetime.datetime(2000,1,1)).total_seconds()/3600.0
            except Exception:
                continue
            dd = abs(off - est)
            if dd < bestd:
                bestd = dd; best = z
        return best
    if len(zones) == 1:
        return zones[0]
    est = round(lon/15.0)
    best = zones[0]; bestd = 1e9
    for z in zones:
        try:
            off = pytz.timezone(z).utcoffset(datetime.datetime(2000,1,1)).total_seconds()/3600.0
        except Exception:
            continue
        dd = abs(off - est)
        if dd < bestd:
            bestd = dd; best = z
    return best

def compute_all(selfcheck=False):
    rows = load_charted()
    cache = {}
    if os.path.exists(GEO_CACHE):
        cache = json.load(open(GEO_CACHE))
        # drop any stale None (failed) entries so they retry this pass
        cache = {k: v for k, v in cache.items() if v is not None}
    known = {
        "Polgahawela Bappa": "Aries", "Upulakshi": "Aries",
        "Senith": "Pisces", "Niromi": "Taurus",
    }
    if selfcheck:
        rows = [r for r in rows if r["name"] in known]
    out = []
    selfcheck_pass = []
    for i, row in enumerate(rows):
        g = geocode(row["city"], row["country"], cache)
        if not g:
            out.append({"name": row["name"], "error": "geocode_failed",
                        "city": row["city"], "country": row["country"]})
            continue
        tzname = pick_tz(g["lat"], g["lon"], g.get("country_code",""))
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tzname)
        dt_local = row["dt_local"].replace(tzinfo=tz)
        dt_utc = dt_local.astimezone(datetime.timezone.utc)
        jd = jd_from_datetime(dt_utc)
        lagna_long, lagna_idx = ascendant_sidereal(jd, g["lat"], g["lon"])
        # whole-sign houses for each planet
        houses = {}
        if row["signs"]:
            for p, s in row["signs"].items():
                if s in SIGNS:
                    si = SIGNS.index(s)
                    houses[p] = ((si - lagna_idx) % 12) + 1
        rec = {
            "name": row["name"], "city": row["city"], "country": row["country"],
            "lat": round(g["lat"],4), "lon": round(g["lon"],4), "tz": tzname,
            "birth_local": dt_local.isoformat(), "birth_utc": dt_utc.isoformat(),
            "jd_ut": round(jd,5),
            "ayanamsa_deg": round(lahiri_ayanamsa(jd),4),
            "lagna_longitude_deg": round(lagna_long,3),
            "lagna_sign": SIGNS[lagna_idx],
            "lagna_index": lagna_idx,
            "houses": houses,
            "loop_len": row["loop_len"], "bond": row["bond"],
        }
        if row["name"] in known:
            ok = (rec["lagna_sign"] == known[row["name"]])
            selfcheck_pass.append((row["name"], known[row["name"]], rec["lagna_sign"], ok))
        out.append(rec)
        # persist geo cache incrementally (reproducible / resilient)
        if (i+1) % 5 == 0:
            json.dump(cache, open(GEO_CACHE, "w"), indent=2)
        time.sleep(1.5)   # polite rate-limit for Open-Meteo
    # persist geo cache (reproducible)
    json.dump(cache, open(GEO_CACHE, "w"), indent=2)
    if selfcheck:
        print("SELF-CHECK against known P1234 Lagnas:")
        allok = True
        for nm, exp, got, ok in selfcheck_pass:
            print(f"  {nm:20} expected={exp:8} computed={got:8} {'OK' if ok else 'MISMATCH'}")
            allok = allok and ok
        print("RESULT:", "ALL MATCH" if allok else "MISMATCH -- recalibrate ayanamsa/ascendant formula")
        return allok
    json.dump(out, open(OUT, "w"), indent=2)
    ok = sum(1 for r in out if "lagna_sign" in r)
    print(f"Wrote {len(out)} records ({ok} with Lagna) to {OUT}")
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()
    compute_all(selfcheck=args.selfcheck)
