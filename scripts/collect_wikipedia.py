#!/usr/bin/env python3
"""
Collect famous-person BIRTH DATA from Wikipedia (link-only, never fabricated).
Enumerates article titles via categorymembers across globally-diverse
occupational/national categories, fetches each article's wikitext infobox,
and extracts real birth_date (+ optional birth_time) and birth_place.

Output: data/wikipedia_people.json  (checkpoint, resumable)
Group classification:
  Group 1 (exact-time): infobox birth_date includes hour/minute
  Group 2 (date-only) : infobox has full Y/M/D but no time
  (records without a parseable full date are skipped)

This is DATASET-COLLECTION infra only. It does NOT touch the existing
loop/bond/aggregation/Drik fetch-parse logic. Times are only taken from the
source infobox; nothing is invented.
"""
import json, re, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://en.wikipedia.org/w/api.php"
UA = "famous-birthdata-collector/1.0 (research dataset; contact: agent@arena.ai)"
OUT = "/home/user/astrology/data/wikipedia_people.json"
CHECKPOINT_TITLES = "/home/user/astrology/data/_wp_titles_done.json"

MONTHS = {m: i+1 for i, m in enumerate(
    ["january","february","march","april","may","june","july","august",
     "september","october","november","december"])}
MONTHS_ABBR = {m: i+1 for i, m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"])}

# (Wikipedia category title, profession label) — globally diverse
CATEGORIES = [
    # Global occupation categories
    ("Category:Actors", "Actor"),
    ("Category:Film actors", "Actor"),
    ("Category:Television actors", "Actor"),
    ("Category:Stage actors", "Actor"),
    ("Category:Voice actors", "Actor"),
    ("Category:Singers", "Singer"),
    ("Category:Songwriters", "Singer"),
    ("Category:Musicians", "Musician"),
    ("Category:Composers", "Musician"),
    ("Category:Politicians", "Politician"),
    ("Category:Heads of state", "Politician"),
    ("Category:Prime ministers", "Politician"),
    ("Category:Presidents", "Politician"),
    ("Category:Monarchs", "Politician"),
    ("Category:Writers", "Author"),
    ("Category:Novelists", "Author"),
    ("Category:Poets", "Author"),
    ("Category:Playwrights", "Author"),
    ("Category:Journalists", "Journalist"),
    ("Category:Scientists", "Science"),
    ("Category:Physicists", "Science"),
    ("Category:Biologists", "Science"),
    ("Category:Mathematicians", "Science"),
    ("Category:Astronomers", "Science"),
    ("Category:Chemists", "Science"),
    ("Category:Economists", "Science"),
    ("Category:Philosophers", "Author"),
    ("Category:Historians", "Author"),
    ("Category:Artists", "Arts"),
    ("Category:Painters", "Arts"),
    ("Category:Sculptors", "Arts"),
    ("Category:Architects", "Arts"),
    ("Category:Businesspeople", "Business"),
    ("Category:Entrepreneurs", "Business"),
    ("Category:Financiers", "Business"),
    ("Category:Military personnel", "Military"),
    ("Category:Military leaders", "Military"),
    ("Category:Explorers", "Explorer"),
    ("Category:Athletes", "Athlete"),
    ("Category:Olympic competitors", "Athlete"),
    ("Category:Footballers", "Footballer"),
    ("Category:Basketball players", "Basketball"),
    ("Category:Tennis players", "Tennis"),
    ("Category:Cricketers", "Cricketer"),
    ("Category:Baseball players", "Baseball"),
    ("Category:Swimmers", "Swimmer"),
    ("Category:Boxers", "Boxer"),
    ("Category:Golfers", "Golfer"),
    ("Category:Models", "Model"),
    ("Category:Comedians", "Actor"),
    ("Category:Film directors", "Director"),
    ("Category:Activists", "Activist"),
    ("Category:Nobel laureates", "Science"),
    ("Category:Academy Award winners", "Actor"),
    ("Category:Grammy Award winners", "Singer"),
    # National / regional coverage (global spread required by spec)
    ("Category:American actors", "Actor"),
    ("Category:American politicians", "Politician"),
    ("Category:American singers", "Singer"),
    ("Category:American writers", "Author"),
    ("Category:American scientists", "Science"),
    ("Category:British actors", "Actor"),
    ("Category:English politicians", "Politician"),
    ("Category:Indian actors", "Actor"),
    ("Category:Indian politicians", "Politician"),
    ("Category:Indian cricketers", "Cricketer"),
    ("Category:Indian writers", "Author"),
    ("Category:Pakistani politicians", "Politician"),
    ("Category:Bangladeshi people", "Public"),
    ("Category:Nepalese people", "Public"),
    ("Category:Sri Lankan actors", "Actor"),
    ("Category:Sri Lankan cricketers", "Cricketer"),
    ("Category:Chinese actors", "Actor"),
    ("Category:Chinese politicians", "Politician"),
    ("Category:Japanese actors", "Actor"),
    ("Category:Japanese writers", "Author"),
    ("Category:South Korean actors", "Actor"),
    ("Category:South Korean singers", "Singer"),
    ("Category:Indonesian people", "Public"),
    ("Category:Filipino actors", "Actor"),
    ("Category:Thai actors", "Actor"),
    ("Category:Vietnamese people", "Public"),
    ("Category:Malaysian people", "Public"),
    ("Category:Arab musicians", "Singer"),
    ("Category:Egyptian actors", "Actor"),
    ("Category:Iranian actors", "Actor"),
    ("Category:Turkish politicians", "Politician"),
    ("Category:Israeli politicians", "Politician"),
    ("Category:Nigerian actors", "Actor"),
    ("Category:South African politicians", "Politician"),
    ("Category:Kenyan people", "Public"),
    ("Category:Ghanaian people", "Public"),
    ("Category:Ethiopian people", "Public"),
    ("Category:Brazilian actors", "Actor"),
    ("Category:Brazilian footballers", "Footballer"),
    ("Category:Mexican actors", "Actor"),
    ("Category:Argentine footballers", "Footballer"),
    ("Category:Colombian singers", "Singer"),
    ("Category:Cuban musicians", "Singer"),
    ("Category:Jamaican musicians", "Singer"),
    ("Category:Canadian actors", "Actor"),
    ("Category:Canadian politicians", "Politician"),
    ("Category:Australian actors", "Actor"),
    ("Category:Australian cricketers", "Cricketer"),
    ("Category:New Zealand cricketers", "Cricketer"),
    ("Category:Irish writers", "Author"),
    ("Category:French actors", "Actor"),
    ("Category:French politicians", "Politician"),
    ("Category:German politicians", "Politician"),
    ("Category:German physicists", "Science"),
    ("Category:Italian politicians", "Politician"),
    ("Category:Italian actors", "Actor"),
    ("Category:Spanish actors", "Actor"),
    ("Category:Russian politicians", "Politician"),
    ("Category:Russian writers", "Author"),
    ("Category:Polish politicians", "Politician"),
    ("Category:Ukrainian people", "Public"),
    ("Category:Swedish actors", "Actor"),
    ("Category:Dutch painters", "Arts"),
]

PER_CAT_CAP = 400          # max members taken from each category
TARGET = 5000              # stop after this many valid dated records
BATCH = 200                # progress-report batch size
MAX_WORKERS = 6

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower().replace(".", "").replace(",", "").replace("  ", " ")

def api_get(params, retries=4):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 429:
                    time.sleep(2 + attempt * 2); continue
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 + attempt * 2); continue
            if attempt == retries - 1:
                return None
            time.sleep(1 + attempt)
        except Exception:
            time.sleep(1 + attempt)
    return None

def enumerate_titles():
    seen = set()
    titles = []
    for cat, prof in CATEGORIES:
        cmcontinue = None
        taken = 0
        while taken < PER_CAT_CAP:
            params = {"action": "query", "list": "categorymembers",
                      "cmtitle": cat, "cmtype": "page", "cmlimit": "100",
                      "format": "json", "formatversion": "2"}
            if cmcontinue:
                params["cmcontinue"] = cmcontinue
            d = api_get(params)
            if not d:
                break
            for m in d.get("query", {}).get("categorymembers", []):
                t = m["title"]
                # skip obvious non-person pages
                if any(t.startswith(p) for p in ("List of", "Category:", "Template:", "Wikipedia:", "File:", "Portal:", "Outline of")):
                    continue
                if t in seen:
                    continue
                seen.add(t)
                titles.append((t, prof))
                taken += 1
                if taken >= PER_CAT_CAP:
                    break
            cm = d.get("continue", {}).get("cmcontinue")
            if not cm:
                break
            cmcontinue = cm
        # tiny politeness between categories
        time.sleep(0.1)
    return titles

def clean_wiki(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&#160;", " ")
    return re.sub(r"\s+", " ", s).strip()

def parse_birth_date(val):
    """Return (dd, mm, yyyy, hh, mm) or None. hh/mm None if absent."""
    val = val.strip()
    # template forms
    m = re.search(r"\{\{(?:Birth[ _-]?date(?: and age)?|Birth[ _-]?date)[^}]*\}\}", val, re.I)
    if m:
        tmpl = m.group(0)
        # collect integer tokens in order
        ints = [int(x) for x in re.findall(r"\b(\d{1,4})\b", tmpl)]
        # filter plausible (drop 2-digit that are df/mf flags handled by being non-int? they are ints)
        if len(ints) >= 3:
            y, mo, d = ints[0], ints[1], ints[2]
            hh = ints[3] if len(ints) > 3 else None
            mi = ints[4] if len(ints) > 4 else None
            if 1 <= mo <= 12 and 1 <= d <= 31:
                return (d, mo, y, hh, mi)
    # ISO date
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", val)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return (d, mo, y, None, None)
    # "D Month YYYY" or "Month D, YYYY"
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", val)
    if m:
        d, mon, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        mo = MONTHS.get(mon) or MONTHS_ABBR.get(mon[:3])
        if mo and 1 <= d <= 31:
            return (d, mo, y, None, None)
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", val)
    if m:
        mon, d, y = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        mo = MONTHS.get(mon) or MONTHS_ABBR.get(mon[:3])
        if mo and 1 <= d <= 31:
            return (d, mo, y, None, None)
    return None

def extract_infobox(wikitext):
    """Robustly extract the first {{Infobox ...}} block via brace matching
    (fast, no catastrophic backtracking)."""
    idx = wikitext.find("{{Infobox")
    if idx == -1:
        idx = wikitext.find("{{infobox")
        if idx == -1:
            return None
    depth = 0
    i = idx
    n = len(wikitext)
    while i < n:
        if wikitext[i:i+2] == "{{":
            depth += 1
            i += 2
            continue
        if wikitext[i:i+2] == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return wikitext[idx:i]
            continue
        i += 1
    return None

def parse_infobox(wikitext):
    block = extract_infobox(wikitext)
    if not block:
        return None, None
    def field(name):
        fm = re.search(r"\|\s*" + name + r"\s*=\s*(.*?)(?=\n\s*\|[\w ]+\s*=|\n\}\})", block, re.S)
        return fm.group(1).strip() if fm else None
    bd = field("birth_date") or field("born")
    bp = field("birth_place")
    if not bd:
        return None, bp
    parsed = parse_birth_date(bd)
    return parsed, bp

def fetch_infobox(title):
    params = {"action": "query", "prop": "revisions", "rvprop": "content",
              "rvslots": "main", "titles": title, "format": "json", "formatversion": "2"}
    d = api_get(params)
    try:
        page = d["query"]["pages"][0]
        rev = page.get("revisions", [{}])[0]
        content = rev.get("slots", {}).get("main", {}).get("content", "")
        return content
    except Exception:
        return ""

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # load existing checkpoint
    records = []
    done = set()
    if os.path.exists(OUT):
        try:
            records = json.load(open(OUT))
        except Exception:
            records = []
    if os.path.exists(CHECKPOINT_TITLES):
        try:
            done = set(json.load(open(CHECKPOINT_TITLES)))
        except Exception:
            done = set()
    done |= {norm(r.get("name", "")) for r in records}

    print(f"Loaded checkpoint: {len(records)} records, {len(done)} titles done", flush=True)
    TITLES_CACHE = "/home/user/astrology/data/_wp_titles.json"
    if os.path.exists(TITLES_CACHE):
        try:
            titles = json.load(open(TITLES_CACHE))
            print(f"Reused enumerated titles from cache: {len(titles)}", flush=True)
        except Exception:
            titles = enumerate_titles()
            json.dump(titles, open(TITLES_CACHE, "w"))
    else:
        titles = enumerate_titles()
        json.dump(titles, open(TITLES_CACHE, "w"))
    print(f"Enumerated {len(titles)} candidate titles", flush=True)

    # filter out already-done
    todo = [(t, p) for (t, p) in titles if norm(t) not in done]
    print(f"Todo after dedup: {len(todo)}", flush=True)

    batch_count = 0
    g1 = g2 = 0
    lock = __import__("threading").Lock()

    def worker(item):
        try:
            title, prof = item
            wt = fetch_infobox(title)
            if not wt:
                return None
            parsed, bp = parse_infobox(wt)
            if not parsed:
                return None
            d, mo, y, hh, mi = parsed
            date = f"{d:02d}/{mo:02d}/{y}"
            if hh is not None and mi is not None:
                t = f"{hh:02d}:{mi:02d}:00"
            else:
                t = ""
            place_clean = clean_wiki(bp) if bp else ""
            city = place_clean.split(",")[0].strip() if place_clean else ""
            country = place_clean.split(",")[-1].strip() if (place_clean and "," in place_clean) else ""
            rec = {
                "name": title.replace("_", " "),
                "profession": prof,
                "birth_date": date,
                "birth_time": t,
                "birth_city": city,
                "birth_country": country,
                "birth_place_raw": place_clean,
                "source_url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title),
                "source_name": "Wikipedia",
                "reliability": "UNKNOWN",
            }
            return rec
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(worker, it): it for it in todo}
        for fut in as_completed(futs):
            res = fut.result()
            with lock:
                if res:
                    records.append(res)
                    done.add(norm(res["name"]))
                    if res["birth_time"]:
                        g1 += 1
                    else:
                        g2 += 1
                    batch_count += 1
                    if batch_count % BATCH == 0:
                        json.dump(records, open(OUT, "w"), indent=0)
                        json.dump(list(done), open(CHECKPOINT_TITLES, "w"))
                        print(f"PROGRESS BATCH ({batch_count}): total={len(records)} G1(time)={g1} G2(date)={g2}", flush=True)
                if len(records) >= TARGET:
                    # cancel remaining
                    for f in futs:
                        f.cancel()
                    break

    json.dump(records, open(OUT, "w"), indent=0)
    json.dump(list(done), open(CHECKPOINT_TITLES, "w"))
    print(f"\nDONE. Collected {len(records)} records (G1 exact-time={g1}, G2 date-only={g2}). Wrote {OUT}", flush=True)

if __name__ == "__main__":
    main()
