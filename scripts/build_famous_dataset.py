#!/usr/bin/env python3
"""Build the famous-people birth-data dataset by MERGING all collection
sources, assigning unique IDs, deduplicating, splitting into Groups 1/2/3,
and writing the registry + group CSVs.

Sources merged (all link-only, never fabricated):
  - data/famous_seed.py  : 111 records with REAL birth times (Group 1)
  - data/births_people.json : ~5,000 Wikipedia "Births by date" records
                              (Group 2, date-only; no time on the source
                              pages, so they are NOT charted per the rule)
  - (optional) data/wikipedia_people.json : infobox-collected records

Dedup key: (normalized name, birth_date). On collision, the record that
carries a birth_time (more complete -> Group 1) is kept; the other is moved
to duplicate_people.csv. This correctly collapses e.g. "Leonardo DiCaprio"
which appears both in the seed (with time) and on a Births day-page.

Does NOT touch the existing loop/bond/aggregation/Drik fetch-parse logic.
"""
import sys, csv, json, os, re
sys.path.insert(0, os.path.dirname(__file__) + "/../data")
from famous_seed import SEED

OUT = "/home/user/astrology"
BIRTHS = os.path.join(OUT, "data/births_people.json")
WIKI = os.path.join(OUT, "data/wikipedia_people.json")

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower().replace(".", "").replace(",", "")

def canonical(r):
    """Normalize source records into the common schema."""
    return {
        "name": (r.get("name") or "").strip(),
        "profession": (r.get("profession") or "").strip(),
        "birth_date": (r.get("birth_date") or "").strip(),
        "birth_time": (r.get("birth_time") or "").strip(),
        "birth_city": (r.get("birth_city") or "").strip(),
        "birth_country": (r.get("birth_country") or "").strip(),
        "source_url": (r.get("source_url") or "").strip(),
        "source_name": (r.get("source_name") or "").strip(),
        "reliability": (r.get("reliability") or "UNKNOWN").strip() or "UNKNOWN",
        "achievement": r.get("achievement", ""),
    }

records = [canonical(r) for r in SEED]

def load_json(path):
    if os.path.exists(path):
        try:
            return [canonical(r) for r in json.load(open(path))]
        except Exception:
            return []
    return []

records += load_json(BIRTHS)
records += load_json(WIKI)

# Dedup by (norm(name), birth_date); keep the time-bearing copy.
best = {}
dups = []
order = []
for r in records:
    if not r["name"] or not r["birth_date"]:
        # no date -> cannot place reliably; treat as uncertain candidate
        r["_group_hint"] = 3
        key = (norm(r["name"]), r["birth_date"] or "NODATE")
    else:
        key = (norm(r["name"]), r["birth_date"])
    if key in best:
        existing = best[key]
        # prefer the one with a birth_time
        if r["birth_time"] and not existing["birth_time"]:
            dups.append(existing)
            best[key] = r
        else:
            dups.append(r)
    else:
        best[key] = r
        order.append(key)

merged = [best[k] for k in order]

# Assign unique IDs + classify groups
out = []
n = 0
g1 = g2 = g3 = 0
for r in merged:
    if r.get("_group_hint") == 3 or not r["birth_date"]:
        grp = 3
    elif r["birth_time"]:
        grp = 1
    else:
        grp = 2
    n += 1
    rid = f"FP{n:05d}"
    rec = {"id": rid, **r, "group": grp}
    out.append(rec)
    if grp == 1: g1 += 1
    elif grp == 2: g2 += 1
    else: g3 += 1

# Master registry
with open(f"{OUT}/famous_people_birth_data.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "name", "profession", "birth_date", "birth_time",
        "birth_city", "birth_country", "source_url", "source_name", "reliability", "achievement", "group"])
    w.writeheader()
    [w.writerow(r) for r in out]
json.dump(out, open(f"{OUT}/famous_people_birth_data.json", "w"), indent=2)

# Group files
def wgroup(path, grp):
    rows = [r for r in out if r["group"] == grp]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "profession", "birth_date", "birth_time",
            "birth_city", "birth_country", "source_url", "source_name", "reliability", "achievement"])
        w.writeheader()
        [w.writerow({k: r.get(k, "") for k in w.fieldnames}) for r in rows]
    return len(rows)

g1n = wgroup(f"{OUT}/exact_time_people.csv", 1)   # group-file columns (overwritten below)
g2n = wgroup(f"{OUT}/date_only_people.csv", 2)
g3n = wgroup(f"{OUT}/uncertain_people.csv", 3)

with open(f"{OUT}/duplicate_people.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "profession", "birth_date", "birth_time", "birth_city", "birth_country"])
    w.writeheader()
    [w.writerow({k: d.get(k, "") for k in w.fieldnames}) for d in dups]

# exact_time_people.csv ALSO carries the columns the EXISTING pipeline expects
with open(f"{OUT}/exact_time_people.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "name", "date", "time", "profession", "achievement", "rodden"])
    w.writeheader()
    for r in out:
        if r["group"] == 1:
            w.writerow({"id": r["id"], "name": r["name"], "date": r["birth_date"],
                "time": r["birth_time"], "profession": r["profession"],
                "achievement": r.get("achievement", ""), "rodden": r.get("reliability", "")})

print(f"Seed records: {len(SEED)}")
print(f"Total merged (pre-dedup): {len(records)}")
print(f"Unique after dedup: {len(out)}")
print(f"Duplicates removed: {len(dups)}")
print(f"GROUP 1 (exact-time): {g1n}")
print(f"GROUP 2 (date-only): {g2n}")
print(f"GROUP 3 (uncertain): {g3n}")
print(f"Wrote: famous_people_birth_data.csv/json, exact_time_people.csv, date_only_people.csv, uncertain_people.csv, duplicate_people.csv")
