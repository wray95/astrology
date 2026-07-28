#!/usr/bin/env python3
"""Fetch real Drik Panchang (Lahiri sidereal) planet signs for the 17 remaining
celebrities, detect closed-loop (Parivartana/Srinkhala) cycles, and merge with
the 7 already-built charts (3 celebrities + 4 family + Senith) for a true
link-only loop distribution. No Swiss-Ephemeris / computed data used.
"""
import re, json, urllib.request, time, sys

SIGNS = {
    "Mesha":"Aries","Vrishabha":"Taurus","Mithuna":"Gemini","Karka":"Cancer",
    "Simha":"Leo","Kanya":"Virgo","Tula":"Libra","Vrischika":"Scorpio",
    "Dhanu":"Sagittarius","Makara":"Capricorn","Kumbha":"Aquarius","Meena":"Pisces",
}
# Sanskrit -> English sign (abbrev fallback)
ABBREV = {
    "Mesh":"Aries","Vrish":"Taurus","Mitu":"Gemini","Kark":"Cancer","Simh":"Leo",
    "Kany":"Virgo","Tula":"Libra","Vrisch":"Scorpio","Dhan":"Sagittarius",
    "Maka":"Capricorn","Kumb":"Aquarius","Meen":"Pisces",
}
# sign -> dispositor (ruler)
RULER = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
    "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
    "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter",
}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
BOND = {2:100, 3:50, 4:33, 5:25}  # jyotishvidya.com bond strength

def fetch_signs(date, t):
    url = f"https://www.drikpanchang.com/planet/position/planetary-positions-sidereal.html?date={date}&time={t}"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    pat = re.compile(
        r'alt="(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"\s+class="dpPlanetTitleImage">'
        r'.*?icon_([a-z]+)\.svg"\s+alt="([A-Za-z]+)"[^>]*>(\d+)\s*(?:&#176;|&deg;|°)\s*<strong>([A-Za-z]+)</strong>',
        re.S)
    signs = {}
    seen = set()
    for m in pat.finditer(html):
        planet, signfile, signfull, deg, abb = m.groups()
        if planet in seen:
            continue
        seen.add(planet)
        sign = SIGNS.get(signfull) or ABBREV.get(abb) or SIGNS.get(signfile.capitalize())
        signs[planet] = sign
        if len(signs) == 9:
            break
    return signs

def cycles(signs):
    disp = {p: RULER[signs[p]] for p in PLANETS if p in signs}
    # functional graph planet -> dispositor; find cycles length>=2
    cycles_found = []
    visited = {}
    for start in PLANETS:
        if start not in disp:
            continue
        path = []
        cur = start
        while cur in disp:
            if cur in visited:
                if cur in path:
                    idx = path.index(cur)
                    cyc = path[idx:]
                    if len(cyc) >= 2:
                        cycles_found.append(tuple(cyc))
                break
            visited[cur] = len(path)
            path.append(cur)
            cur = disp[cur]
    # dedupe cycles (same set, rotated)
    uniq = []
    for c in cycles_found:
        s = set(c)
        if not any(set(u) == s for u in uniq):
            uniq.append(c)
    return uniq

def classify(cycs):
    lens = [len(c) for c in cycs]
    if not lens:
        return 0, [], 0
    longest = max(lens)
    best = max(cycs, key=len)
    bond = BOND.get(longest, 0)
    return longest, [list(c) for c in cycs], bond

# ---- 17 remaining celebrities (date DD/MM/YYYY, time HH:MM:SS) ----
# Times: from user-pasted framework where given; MISSING -> noon (Moon flagged approx)
CELEBS = [
    ("Elon Musk",        "28/06/1971","14:30:00","Pretoria", False),
    ("Bill Gates",       "28/10/1955","14:25:00","Seattle",  False),
    ("Jeff Bezos",       "12/01/1964","14:15:00","Albuquerque", False),
    ("Steve Jobs",       "24/02/1955","19:15:00","San Francisco", False),
    ("Albert Einstein",  "14/03/1879","11:30:00","Ulm",      False),
    ("Warren Buffett",   "30/08/1930","15:00:00","Omaha",    False),
    ("Mark Zuckerberg",  "14/05/1984","15:00:00","White Plains", False),
    ("Sachin Tendulkar", "24/12/1973","10:00:00","Mumbai",   False),
    ("Mukesh Ambani",    "19/04/1957","14:30:00","Aden",     False),
    ("Oprah Winfrey",    "29/01/1954","14:30:00","Kosciusko",False),
    ("Mahatma Gandhi",   "02/10/1869","12:00:00","Porbandar",True),
    ("Abraham Lincoln",  "12/02/1809","12:00:00","Hodgenville",True),
    ("Nelson Mandela",   "18/07/1918","12:00:00","Mvezo",    True),
    ("Walt Disney",      "05/12/1901","12:00:00","Chicago",  True),
    ("Henry Ford",       "30/07/1863","12:00:00","Dearborn", True),
    ("Michael Jackson",  "29/08/1958","12:00:00","Gary",     True),
    ("A.P.J. Abdul Kalam","15/10/1931","12:00:00","Rameswaram",True),
]

# ---- already-built charts (from prior turns, Drik-derived) ----
BUILT = {
    "Obama":        {"Sun":"Cancer","Moon":"Taurus","Mars":"Leo","Mercury":"Cancer","Jupiter":"Capricorn","Venus":"Gemini","Saturn":"Capricorn","Rahu":"Leo","Ketu":"Aquarius"},
    "Rockefeller":  {"Sun":"Gemini","Moon":"Taurus","Mars":"Virgo","Mercury":"Cancer","Jupiter":"Virgo","Venus":"Leo","Saturn":"Taurus","Rahu":"Aquarius","Ketu":"Leo"},
    "Stan Lee":     {"Sun":"Sagittarius","Moon":"Aries","Mars":"Aquarius","Mercury":"Sagittarius","Jupiter":"Libra","Venus":"Taurus","Saturn":"Virgo","Rahu":"Virgo","Ketu":"Pisces"},
    "P1 Bappa":     {"Sun":"Taurus","Moon":"Aquarius","Mars":"Aries","Mercury":"Taurus","Venus":"Gemini","Saturn":"Capricorn","Jupiter":"Aquarius","Rahu":"Cancer","Ketu":"Capricorn"},
    "P2 Upulakshi": {"Venus":"Aquarius","Jupiter":"Capricorn","Moon":"Taurus","Saturn":"Pisces","Sun":"Aquarius","Mars":"Virgo","Mercury":"Pisces","Rahu":"Virgo","Ketu":"Pisces"},
    "P3 Senith":    {"Jupiter":"Scorpio","Saturn":"Pisces","Rahu":"Libra","Ketu":"Aries","Sun":"Cancer","Moon":"Sagittarius","Mars":"Virgo","Mercury":"Leo","Venus":"Cancer"},
    "P4 Niromi":    {"Venus":"Taurus","Jupiter":"Cancer","Saturn":"Pisces","Mars":"Virgo","Mercury":"Pisces","Sun":"Aries","Moon":"Libra","Rahu":"Aries","Ketu":"Libra"},
}

def process(name, signs, moon_approx=False, achievement=None, field=None):
    cycs = cycles(signs)
    length, clist, bond = classify(cycs)
    return {"name":name,"signs":signs,"loops":clist,"loop_len":length,
            "bond":bond,"moon_approx":moon_approx,"achievement":achievement,"field":field}

results = []
# built charts with achievement/field labels
BUILT_META = {
    "Obama":{"ach":10,"field":"Politics"},"Rockefeller":{"ach":10,"field":"Business"},
    "Stan Lee":{"ach":8,"field":"Arts"},"P1 Bappa":{"ach":8,"field":"Business"},
    "P2 Upulakshi":{"ach":5,"field":"Job"},"P3 Senith":{"ach":4,"field":"Job"},
    "P4 Niromi":{"ach":9,"field":"Business"},
}
for n,s in BUILT.items():
    m = BUILT_META[n]
    results.append(process(n, s, False, m["ach"], m["field"]))

# fetch 17
for name, date, t, place, approx in CELEBS:
    try:
        signs = fetch_signs(date, t)
        if len(signs) < 9:
            print(f"WARN {name}: only {len(signs)} planets parsed", file=sys.stderr)
        # rough achievement/field by person (for distribution context)
        ach = {"Elon Musk":10,"Bill Gates":10,"Jeff Bezos":10,"Steve Jobs":10,
               "Albert Einstein":10,"Warren Buffett":10,"Mark Zuckerberg":9,
               "Sachin Tendulkar":9,"Mukesh Ambani":10,"Oprah Winfrey":9,
               "Mahatma Gandhi":10,"Abraham Lincoln":10,"Nelson Mandela":10,
               "Walt Disney":9,"Henry Ford":10,"Michael Jackson":9,
               "A.P.J. Abdul Kalam":9}.get(name,7)
        field = {"Elon Musk":"Tech","Bill Gates":"Tech","Jeff Bezos":"Tech","Steve Jobs":"Tech",
                 "Albert Einstein":"Science","Warren Buffett":"Business","Mark Zuckerberg":"Tech",
                 "Sachin Tendulkar":"Sports","Mukesh Ambani":"Business","Oprah Winfrey":"Media",
                 "Mahatma Gandhi":"Politics","Abraham Lincoln":"Politics","Nelson Mandela":"Politics",
                 "Walt Disney":"Arts","Henry Ford":"Business","Michael Jackson":"Arts",
                 "A.P.J. Abdul Kalam":"Science"}.get(name,"Other")
        results.append(process(name, signs, approx, ach, field))
        print(f"OK {name}: signs={signs}", file=sys.stderr)
    except Exception as e:
        print(f"ERR {name}: {e}", file=sys.stderr)
    time.sleep(1.0)

with open("/home/user/astrology/celeb_loops.json","w") as f:
    json.dump(results, f, indent=2)

# summary
print("\n=== LOOP DISTRIBUTION (24 charts, real Drik data) ===")
from collections import Counter
cnt = Counter(r["loop_len"] for r in results)
for k in sorted(cnt):
    print(f"  {k}-loop: {cnt[k]}")
print("\n=== PER PERSON ===")
for r in results:
    loops = "; ".join("/".join(c) for c in r["loops"]) or "none"
    print(f"  {r['name']:20s} loop={r['loop_len']} bond={r['bond']:3d} | {loops}")
