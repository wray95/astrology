#!/usr/bin/env python3
"""
Pre-populate the DrikPanchang HTML cache for every GROUP-1 (exact-time)
record, using a full browser User-Agent (the EXISTING pipeline's minimal
'Mozilla/5.0' UA is now bot-blocked with HTTP 403). The pipeline's
fetch_signs() reads cache/<datewithoutslash>_<timewithoutcolon>.html when
present, so warming the cache lets the UNMODIFIED pipeline run offline.

This is collection-infra only: it does NOT change the pipeline's URL
construction, HTML parsing, loop detection, bond logic, or aggregation.
It only fills the cache with real Drik sidereal (Lahiri) planet-position
pages, fetched ONCE and kept stable (boundary flag is set by the pipeline).
"""
import csv, os, sys, time, urllib.request
OUT = "/home/user/astrology"
CACHE = os.path.join(OUT, "cache")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

def key_for(date, t):
    return f"{date.replace('/','')}_{t.replace(':','')}.html"

def warm(date, t):
    path = os.path.join(CACHE, key_for(date, t))
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return "cached"
    url = (f"https://www.drikpanchang.com/planet/position/planetary-positions-sidereal.html"
           f"?date={date}&time={t}")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"})
    try:
        html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    except Exception as e:
        return f"ERR {e}"
    if "dpPlanetTitleImage" not in html:
        return "ERR no-planet-data"
    os.makedirs(CACHE, exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)
    return "fetched"

def main():
    os.makedirs(CACHE, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(OUT, "exact_time_people.csv"))))
    present = warmed = err = 0
    for r in rows:
        date = r.get("date") or ""
        t = (r.get("time") or "").strip()
        if not date or "/" not in date:
            continue
        if not t:
            t = "12:00:00"
        res = warm(date, t)
        if res == "cached": present += 1
        elif res == "fetched": warmed += 1
        else:
            err += 1
            print(f"  {r.get('name')}: {res}", file=sys.stderr)
        time.sleep(0.3)
    print(f"Group-1 cache: already-present={present} newly-fetched={warmed} errors={err} (total={present+warmed+err})")

if __name__ == "__main__":
    main()
