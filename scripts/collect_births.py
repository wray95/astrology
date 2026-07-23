#!/usr/bin/env python3
"""
Collect famous-person BIRTH DATA from Wikipedia "Births by date" day-pages
(link-only, never fabricated). Each day-page (e.g. "January 1") lists real,
notable people born that day with the exact year inline -- no per-article
fetch required, so this scales to thousands of dated records cheaply.

Output: data/births_people.json  (checkpoint, resumable)
All records are GROUP 2 (date-only): the source pages carry name + full
birth date + a short description (profession hint) but NOT a birth time, so
per the standing rule they are NOT sent to the DrikPanchang pipeline.
Birth place/time are left blank (not fabricated).

This is DATASET-COLLECTION infra only; it does not touch the existing
loop/bond/aggregation/Drik fetch-parse logic.
"""
import json, re, os, sys, time, urllib.parse, urllib.request
from threading import Lock

RAW = "https://en.wikipedia.org/w/index.php"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
OUT = "/home/user/astrology/data/births_people.json"
DONE_DAYS = "/home/user/astrology/data/_births_done.json"

MONTHS = ["January","February","March","April","May","June","July","August",
          "September","October","November","December"]
MON_NUM = {m: i+1 for i, m in enumerate(MONTHS)}

PER_DAY_CAP = 15          # max people taken per day (keeps global diversity)
TARGET = 5000            # stop after this many valid records
BATCH = 200              # progress-report batch size
MIN_GAP = 1.2            # seconds between fetches (polite)
BACKOFF = 30             # seconds on HTTP 429

_rate_lock = Lock()
_last_call = [0.0]

def raw_get(title, retries=8):
    url = RAW + "?" + urllib.parse.urlencode({"title": title, "action": "raw"})
    for attempt in range(retries):
        with _rate_lock:
            wait = MIN_GAP - (time.time() - _last_call[0])
            if wait > 0:
                time.sleep(wait)
            _last_call[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                if r.status == 429:
                    time.sleep(BACKOFF); continue
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(BACKOFF); continue
            if attempt == retries - 1:
                return None
            time.sleep(2 + attempt)
        except Exception:
            time.sleep(2 + attempt)
    return None

def clean(t):
    t = re.sub(r"\{\{[^}]*\}\}", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", t)
    t = t.replace("[[", "").replace("]]", "").replace("[", "").replace("]", "")
    t = t.replace("&ndash;", " ").replace("&mdash;", " ").replace("&#160;", " ")
    t = t.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", t).strip()

def parse_line(line):
    """Return (name, year, desc) or None for a '* ...' birth entry."""
    s = line.lstrip()
    if not s.startswith("*"):
        return None
    s = s[1:].lstrip()
    links = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", s)
    if not links:
        return None
    # candidate years in parentheses: ([[1942]]) or (1942)
    ym = re.search(r"\(\s*\[?\[?(\d{1,4}(?:\s*(?:BC|BCE))?)\]?\]?\s*\)", s)
    year = ym.group(1).strip() if ym else None
    # name
    name = None
    first_target = links[0][0].strip()
    if re.fullmatch(r"\d{1,4}", first_target):
        # ancient format: [[766]] &ndash; [[Name]] -> year=766, name=2nd link
        if not year:
            year = first_target
        if len(links) > 1:
            name = (links[1][1] or links[1][0]).strip()
    else:
        name = (links[0][1] or links[0][0]).strip()
        if not year:
            for tgt, _ in links[1:]:
                if re.fullmatch(r"\d{1,4}", tgt.strip()):
                    year = tgt.strip(); break
    if not name or not year:
        return None
    if "BC" in year.upper() or "BCE" in year.upper():   # schema has no BC support; skip
        return None
    yint = int(re.sub(r"\D", "", year))
    if yint <= 0 or yint > 2026:
        return None
    if re.fullmatch(r"\d{1,4}", name):   # name is just a year -> bad
        return None
    if len(name) > 60 or len(name) < 2:
        return None
    # description (profession hint):
    #  - modern  : "* [[Name]] ([[year]]) - description"
    #  - ancient : "* [[year]] &ndash; [[Name]], description"
    # Names never contain a SPACED dash, so the first spaced dash is the
    # name|description separator in the modern form. In the ancient form the
    # description follows the name link (after its closing ']]' / comma).
    desc = ""
    sn = s.replace("&ndash;", " – ").replace("&mdash;", " — ")
    if re.fullmatch(r"\d{1,4}", first_target):   # ancient form
        idxs = [m.start() for m in re.finditer(r"\]\]", sn)]
        if len(idxs) >= 2:
            after = sn[idxs[1] + 2:]
            after = after.lstrip().lstrip(",").lstrip()
            after = re.sub(r"^[–—-]\s*", "", after)
            desc = clean(after).split("(")[0].strip()
    else:                                       # modern form
        for pat in (" – ", " — ", " - "):
            i = sn.find(pat)
            if i != -1:
                desc = clean(sn[i + len(pat):]).split("(")[0].strip()
                break
    return name, yint, desc

def parse_day(title):
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2})", title)
    if not m or m.group(1) not in MON_NUM:
        return None
    month = MON_NUM[m.group(1)]; day = int(m.group(2))
    wt = raw_get(title)
    if not wt:
        return month, day, []
    # bound the Births section (level-2 heading only; skip === subheads)
    lines = wt.splitlines()
    in_b = False; sec = []
    for ln in lines:
        if re.match(r"^==\s*Births\s*==", ln):
            in_b = True; continue
        if in_b and re.match(r"^==[^=]", ln):   # next level-2 heading (not ===)
            break
        if in_b:
            sec.append(ln)
    people = []
    for ln in sec:
        if not ln.lstrip().startswith("*"):
            continue
        if ln.lstrip().startswith("**"):
            continue
        r = parse_line(ln)
        if not r:
            continue
        name, yint, desc = r
        art = name.replace(" ", "_")
        people.append({
            "name": name,
            "birth_date": f"{day:02d}/{month:02d}/{yint}",
            "profession": desc,
            "birth_time": "",
            "birth_city": "",
            "birth_country": "",
            "source_url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(art),
            "source_name": "Wikipedia (Births by date)",
            "reliability": "UNKNOWN",
        })
    return month, day, people

def spread(items, n):
    """Pick up to n entries spread evenly across the full list (includes the
    first and last), so a day-page's chronological order does not bias the
    sample toward only ancient or only modern births."""
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    records, done = [], set()
    if os.path.exists(OUT):
        try: records = json.load(open(OUT))
        except Exception: records = []
    if os.path.exists(DONE_DAYS):
        try: done = set(json.load(open(DONE_DAYS)))
        except Exception: done = set()

    days = [f"{m} {d}" for m in MONTHS for d in range(1, 28 if m == "February" else 32)]
    days.append("February 29")
    days = [d for d in days if d not in done]

    print(f"Loaded {len(records)} records; {len(done)} days done; {len(days)} days to process", flush=True)
    batch = 0
    for day in days:
        res = parse_day(day)
        if not res or len(res) < 3:
            done.add(day); continue
        _, _, people = res
        for p in spread(people, PER_DAY_CAP):
            records.append(p)
        done.add(day)
        batch += 1
        if batch % 10 == 0:
            json.dump(records, open(OUT, "w"), indent=0)
            json.dump(list(done), open(DONE_DAYS, "w"))
            print(f"PROGRESS: days={len(done)} total={len(records)}", flush=True)
        if len(records) >= TARGET:
            break

    json.dump(records, open(OUT, "w"), indent=0)
    json.dump(list(done), open(DONE_DAYS, "w"))
    print(f"\nDONE. Collected {len(records)} date-only records from {len(done)} day-pages. Wrote {OUT}", flush=True)

if __name__ == "__main__":
    main()
