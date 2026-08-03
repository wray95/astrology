#!/usr/bin/env python3
"""
EVENT DATABASE MINER — Wikipedia milestone mining (link-only, standing rule)
============================================================================
Builds the advisor's public-milestone event database:
  person | event_type | event_date | source | category

Mining strategy (no scraping of every page):
  1. SEED events: milestone patterns with years (e.g. "founded in 1975",
     "released in 1984", "won the Nobel Prize in 1972") from the
     q_biographical_wikipedia already-downloaded extracts (infobox fields).
  2. For a TARGETED list (e.g., P-series, advisor examples), fetch the
     Wikipedia summary paragraph (REST API, link-only) and extract the
     same patterns.

Event categories (per advisor): company founded, IPO, sold, Nobel, Oscar,
Grammy, election, appointment, Olympic gold, marriage, death, first
bestseller, major discovery. Plus generic milestone years.

Output: dataset/event_database.json
Schema: {"events":[{person, birth_date, event_type, event_date, source, category}]}
"""
import json, re, gzip, csv, time, urllib.request
from collections import Counter

OUT = "dataset/event_database.json"

# ---- year-extraction patterns (ordered; first match wins) ----
PATTERNS = [
    ("company_founded", r"(?:founded|established|started|co-founded)\s+(?:the\s+)?(?:company|firm|business|startup|corporation)?\s*(?:in\s+|on\s+)?(1[89]\d\d|20\d\d)"),
    ("first_bestseller", r"(?:first|debut)\s+(?:novel|book|album|single|film|movie)\s+(?:was\s+)?(?:published|released|launched|debuted)\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("nobel", r"(?:won|received|awarded)\s+the\s+Nobel\s+Prize\s*(?:in|for)?\s*(?:Physics|Chemistry|Medicine|Literature|Peace|Economics)?\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("oscar", r"(?:won|received|awarded)\s+(?:an\s+|the\s+)?Academy\s+Award\s*(?:for)?\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("grammy", r"(?:won|received|awarded)\s+(?:a\s+|the\s+)?Grammy\s+Award\s*(?:for)?\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("election", r"(?:elected|won)\s+(?:the\s+)?(?:presidential\s+)?election\s*(?:in|of)?\s*(?:the\s+)?(1[89]\d\d|20\d\d)"),
    ("appointment", r"(?:appointed|named)\s+(?:as\s+)?(?:CEO|president|chairman|director|professor|ambassador)\s*(?:of|at)?\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("olympic_gold", r"(?:won|took)\s+(?:the\s+)?gold\s+medal\s*(?:at|in)?\s*(?:the\s+)?(?:Olympics|Olympic|Games)?\s*(?:in\s+)?(1[89]\d\d|20\d\d)"),
    ("death", r"(?:died|passed\s+away)\s*(?:on|in)?\s*(?:the\s+)?(?:1[89]\d\d|20\d\d)"),
    ("milestone_year", r"(?:in|since|during|by)\s+(1[89]\d\d|20\d\d)"),
]

def extract_events(text, name, birth_date):
    """Return list of {event_type, event_date, source} found in text."""
    found = []
    for ev_type, pat in PATTERNS:
        for m in re.finditer(pat, text, re.I):
            y = int(m.group(1))
            if 1800 <= y <= 2026:
                found.append({"person": name, "birth_date": birth_date,
                              "event_type": ev_type, "event_date": str(y),
                              "source": "wikipedia_infobox" if birth_date else "wikipedia_summary",
                              "category": "milestone"})
    # dedupe within person
    uniq = {}
    for e in found:
        k = (e["person"], e["event_type"], e["event_date"])
        uniq[k] = e
    return list(uniq.values())

# ---- 1) seed from q_biographical infobox fields (career_active/debut already there) ----
events = []
with gzip.open("outputs/q_biographical_wikipedia/q_biographical_details.csv.gz", "rt", errors="ignore") as f:
    for row in csv.DictReader(f):
        nm = (row.get("name") or "").strip()
        bd = (row.get("birth_date") or "").strip()
        ca = (row.get("career_active") or "").strip()
        db = (row.get("debut") or "").strip()
        m = re.match(r"^(\d{4})", ca)
        if m: events.append({"person": nm, "birth_date": bd, "event_type": "career_start",
                             "event_date": m.group(1), "source": "q_bio_infobox", "category": "milestone"})
        m = re.match(r"^([A-Za-z]+)?\s*(\d{4})", db)
        if m: events.append({"person": nm, "birth_date": bd, "event_type": "debut",
                             "event_date": m.group(2), "source": "q_bio_infobox", "category": "milestone"})

# ---- 2) targeted summary mining: P-series + advisor examples + a 100-person sample ----
TARGETS = ["Elon Musk", "Bill Gates", "J. K. Rowling", "Michael Jordan",
           "Anura Kumara Dissanayake"] + [
    "Albert Einstein", "Marie Curie", "Isaac Newton", "Nelson Mandela", "Winston Churchill",
    "Martin Luther King Jr.", "Mahatma Gandhi", "Abraham Lincoln", "Franklin D. Roosevelt",
    "John F. Kennedy", "Ronald Reagan", "Barack Obama", "Donald Trump", "Vladimir Putin",
    "Narendra Modi", "Angela Merkel", "Margaret Thatcher", "Indira Gandhi", "Aung San Suu Kyi",
    "Steve Jobs", "Jeff Bezos", "Mark Zuckerberg", "Larry Page", "Sergey Brin",
    "Jack Ma", "Warren Buffett", "Charlie Munger", "George Soros", "Carlos Slim",
    "Mukesh Ambani", "Gautam Adani", "Ratan Tata", "Jamsetji Tata", "Azim Premji",
    "Sundar Pichai", "Satya Nadella", "Tim Cook", "Elon Musk", "Bill Gates",
    "Michael Jackson", "Madonna", "Elvis Presley", "The Beatles", "Bob Dylan",
    "Paul McCartney", "Freddie Mercury", "Kurt Cobain", "Taylor Swift", "Beyonce",
    "Rihanna", "Drake", "Ed Sheeran", "Adele", "Shakira",
    "Leonardo DiCaprio", "Tom Hanks", "Robert De Niro", "Meryl Streep", "Al Pacino",
    "Brad Pitt", "Angelina Jolie", "Johnny Depp", "Will Smith", "Denzel Washington",
    "Steven Spielberg", "Martin Scorsese", "Quentin Tarantino", "Christopher Nolan",
    "Stan Lee", "J. R. R. Tolkien", "George R. R. Martin", "Stephen King", "Agatha Christie",
    "Charles Dickens", "Jane Austen", "William Shakespeare", "Leo Tolstoy", "Mark Twain",
    "Ernest Hemingway", "F. Scott Fitzgerald", "Gabriel Garcia Marquez", "Haruki Murakami",
    "Salman Rushdie", "Arundhati Roy", "Chetan Bhagat", "Aravind Adiga", "Kiran Desai",
    "Usain Bolt", "Michael Phelps", "Serena Williams", "Roger Federer", "Rafael Nadal",
    "Lionel Messi", "Cristiano Ronaldo", "Pele", "Diego Maradona", "Sachin Tendulkar",
    "Muhammad Ali", "Mike Tyson", "Floyd Mayweather", "Conor McGregor", "Ayrton Senna",
    "Michael Schumacher", "Lewis Hamilton", "Max Verstappen", "Tiger Woods", "Babe Ruth",
    "Kobe Bryant", "LeBron James", "Stephen Curry", "Kevin Durant", "Magic Johnson",
]

def fetch_summary(name):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(name.replace(" ", "_"))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research; astrology-event-miner)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode())
    return d.get("extract", "")

seen_targets = set()
n_fetch = 0
for t in TARGETS:
    if t in seen_targets: continue
    seen_targets.add(t)
    try:
        txt = fetch_summary(t)
        n_fetch += 1
        for e in extract_events(txt, t, ""):
            e["source"] = "wikipedia_summary"
            events.append(e)
        time.sleep(0.4)
    except Exception as ex:
        print(f"  fetch fail {t}: {ex}")
print(f"fetched {n_fetch} summaries")

# ---- dedupe all ----
uniq = {}
for e in events:
    k = (e["person"], e["event_type"], e["event_date"])
    if k not in uniq:
        uniq[k] = e
events = list(uniq.values())

# stats
by_type = Counter(e["event_type"] for e in events)
print(f"\ntotal events: {len(events)}")
print("by type:", dict(by_type))
print("people covered:", len(set(e["person"] for e in events)))

json.dump({"events": events, "n": len(events), "by_type": dict(by_type),
           "schema": "person|event_type|event_date|source|category",
           "note": "Event dates are YEARS (mid-year approximation in tests); exact dates pending Wikidata/IMDb/Nobel/Olympic sources."},
          open(OUT, "w"), indent=1)
print(f"\nWrote {OUT}")
