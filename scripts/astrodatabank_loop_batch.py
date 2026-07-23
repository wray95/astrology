#!/usr/bin/env python3
"""
ASTRO-DATABANK -> DRIK PANCHANG LOOP BATCH PIPELINE (executable)
=================================================================
Reads an Astro-Databank export (CSV or JSON, Rodden AA/A preferred),
fetches REAL sidereal (Lahiri) planet signs from Drik Panchang for each
record, detects closed-loop (Parivartana/Srinkhala) cycles, assigns the
jyotishvidya bond strength, and aggregates a real loop distribution.

WHY THIS IS VALID UNDER OUR RULES:
  - Astro-Databank = BIRTH DATA source (name/date/time/place + Rodden rating).
  - Drik Panchang  = PLANETARY POSITIONS (Lahiri/Chitra-Paksha ayanamsa).
  - No Swiss-Ephemeris / computed data. Link-only, both ends.

USAGE:
  python3 astrodatabank_loop_batch.py INPUT.csv [--out outdir]
  python3 astrodatabank_loop_batch.py INPUT.json

EXPECTED CSV COLUMNS (header row, case-insensitive):
  name, date, time, profession, achievement, rodden
    date  = DD/MM/YYYY   (Drik format)
    time  = HH:MM:SS     (24h; blank -> 12:00 noon, Moon flagged approx)
    profession = free text (e.g. Politician, Business, Actor, Scientist)
    achievement = 1-10 illustrative eminence tier (optional; for stats)
    rodden = AA/A/B/C/DD/X (optional; filter to AA/A for reliability)

Astro-Databank wiki export note: the live wiki (astro-databank.com) was
UNREACHABLE from the build sandbox (HTTP 000). Export the dataset on a
machine where it is reachable (or use the public SQL/XML dump / Wikidata
mirror), then point this script at the CSV. Caching avoids re-fetching.
"""
import re, json, csv, sys, os, time, argparse, urllib.request
from collections import Counter
from statistics import mean

SIGNS = {"Mesha":"Aries","Vrishabha":"Taurus","Mithuna":"Gemini","Karka":"Cancer",
    "Simha":"Leo","Kanya":"Virgo","Tula":"Libra","Vrischika":"Scorpio",
    "Dhanu":"Sagittarius","Makara":"Capricorn","Kumbha":"Aquarius","Meena":"Pisces"}
ABBREV = {"Mesh":"Aries","Vrish":"Taurus","Mitu":"Gemini","Kark":"Cancer","Simh":"Leo",
    "Kany":"Virgo","Tula":"Libra","Vrisch":"Scorpio","Dhan":"Sagittarius",
    "Maka":"Capricorn","Kumb":"Aquarius","Meen":"Pisces"}
RULER = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
    "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
    "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
BOND = {2:100, 3:50, 4:33, 5:25}
CACHE = "/home/user/astrology/cache"

def fetch_signs(date, t, cache_dir=CACHE):
    os.makedirs(cache_dir, exist_ok=True)
    key = f"{date.replace('/','')}_{t.replace(':','')}.html"
    path = os.path.join(cache_dir, key)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        html = open(path, encoding="utf-8", errors="ignore").read()
    else:
        url = f"https://www.drikpanchang.com/planet/position/planetary-positions-sidereal.html?date={date}&time={t}"
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8","ignore")
        open(path,"w",encoding="utf-8").write(html)
    pat = re.compile(
        r'alt="(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"\s+class="dpPlanetTitleImage">'
        r'.*?icon_([a-z]+)\.svg"\s+alt="([A-Za-z]+)"[^>]*>(\d+)\s*(?:&#176;|&deg;|°)\s*(\d+)?\s*(?:&#8242;|′|&#8242;)?\s*(\d+)?',
        re.S)
    signs, degs, seen = {}, {}, set()
    for m in pat.finditer(html):
        planet, sf, sfull, deg, minute, sec = m.groups()
        if planet in seen: continue
        seen.add(planet)
        sign = SIGNS.get(sfull) or ABBREV.get(minute) or SIGNS.get(sf.capitalize())
        signs[planet] = sign
        try:
            degs[planet] = float(deg) + (float(minute)/60 if minute else 0)
        except: degs[planet] = None
        if len(signs) == 9: break
    return signs, degs

def cycles(signs):
    disp = {p: RULER[signs[p]] for p in PLANETS if p in signs}
    found, visited = [], {}
    for start in PLANETS:
        if start not in disp: continue
        path, cur = [], start
        while cur in disp:
            if cur in visited:
                if cur in path:
                    cyc = path[path.index(cur):]
                    if len(cyc) >= 2: found.append(tuple(cyc))
                break
            visited[cur] = len(path); path.append(cur); cur = disp[cur]
    uniq = []
    for c in found:
        if not any(set(u)==set(c) for u in uniq): uniq.append(c)
    return uniq

def classify(cycs):
    lens = [len(c) for c in cycs]
    if not lens: return 0, [], 0
    longest = max(lens)
    return longest, [list(c) for c in cycs], BOND.get(longest,0)

def load_rows(path):
    rows = []
    if path.endswith(".json"):
        data = json.load(open(path))
        for d in data:
            rows.append(d)
        return rows
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for d in r:
            rows.append({k.strip().lower(): v for k,v in d.items()})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", default="/home/user/astrology/astrodb_out")
    ap.add_argument("--min-rodden", default=None, help="filter to AA/A (case-insensitive)")
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = load_rows(args.input)
    results = []
    for d in rows:
        name = d.get("name") or d.get("born") or "?"
        date = d.get("date") or ""
        t = (d.get("time") or "12:00:00").strip() or "12:00:00"
        if not date or "/" not in date:
            print(f"SKIP {name}: bad date '{date}'", file=sys.stderr); continue
        prof = d.get("profession") or d.get("category") or ""
        ach = d.get("achievement")
        ach = int(ach) if str(ach).isdigit() else None
        rodden = (d.get("rodden") or "").upper()
        if args.min_rodden and rodden and rodden not in args.min_rodden.split(","):
            continue
        moon_approx = (not (d.get("time") or "").strip())
        try:
            signs, degs = fetch_signs(date, t)
            if len(signs) < 9:
                print(f"WARN {name}: {len(signs)} planets", file=sys.stderr)
            L, loops, bond = classify(cycles(signs))
            boundary = any((d is not None and (d <= 1.0 or d >= 29.0)) for d in degs.values())
            results.append({"name":name,"profession":prof,"achievement":ach,
                "rodden":rodden,"moon_approx":moon_approx,"signs":signs,"degrees":degs,
                "boundary":boundary,"loop_len":L,"loops":loops,"bond":bond})
            print(f"OK {name}: loop={L} bond={bond}", file=sys.stderr)
        except Exception as e:
            print(f"ERR {name}: {e}", file=sys.stderr)
        time.sleep(args.delay)
    json.dump(results, open(os.path.join(args.out,"astrodb_loops.json"),"w"), indent=2)
    # CSV
    with open(os.path.join(args.out,"astrodb_loops.csv"),"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["name","profession","achievement","rodden","loop_len","bond","loops","moon_approx"])
        for r in results:
            w.writerow([r["name"],r["profession"],r["achievement"],r["rodden"],
                r["loop_len"],r["bond"],"; ".join("/".join(c) for c in r["loops"]),r["moon_approx"]])
    # stats
    n=len(results); cnt=Counter(r["loop_len"] for r in results)
    print(f"\n=== DISTRIBUTION (n={n}) ===")
    for k in [0,2,3,4,5]:
        if cnt.get(k): print(f"  {k}-loop: {cnt[k]} ({cnt[k]*100//n}%)")
    hi=[r for r in results if (r["achievement"] or 0)>=8]
    if hi:
        hc=Counter(r["loop_len"] for r in hi)
        print(f"\n=== HIGH ACHIEVERS (ach>=8, n={len(hi)}) ===")
        for k in [0,2,3,4,5]:
            if hc.get(k): print(f"  {k}-loop: {hc[k]} ({hc[k]*100//len(hi)}%)")
        # correlation loop_len vs achievement
        pairs=[(r["loop_len"],r["achievement"]) for r in results if r["achievement"] is not None]
        if len(pairs)>2:
            xs=[p[0] for p in pairs]; ys=[p[1] for p in pairs]
            mx,my=mean(xs),mean(ys)
            num=sum((x-mx)*(y-my) for x,y in pairs)
            den=(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))**0.5
            r=num/den if den else 0
            print(f"\n  Pearson r (loop_len vs achievement) = {r:.3f}")
    print(f"\nSaved: {args.out}/astrodb_loops.json + .csv")

if __name__ == "__main__":
    main()
