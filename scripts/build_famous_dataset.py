#!/usr/bin/env python3
"""Build the famous-people birth-data dataset from a seed (Batch 1).
Assigns unique IDs, deduplicates, splits into Groups 1/2/3, and writes the
registry + group CSVs. Does NOT touch the existing loop/bond/fetch logic.
Run the EXISTING astrodatabank_loop_batch.py on exact_time_people.csv after.
"""
import sys, csv, json, os
sys.path.insert(0, os.path.dirname(__file__)+"/../data")
from famous_seed import SEED

OUT = "/home/user/astrology"
def norm(s): return (s or "").strip().lower().replace(".","").replace(",","").replace("  "," ")

records = []
seen = {}
dups = []
n = 0
for r in SEED:
    key = (norm(r["name"]), r.get("birth_date",""), norm(r.get("birth_city","")))
    if key in seen:
        dups.append(r); continue
    seen[key] = True
    n += 1
    rid = f"FP{n:05d}"
    rec = {"id":rid, **r}
    # group classification
    if r.get("birth_time","").strip():
        rec["group"] = 1   # exact-time
    elif r.get("birth_date","").strip():
        rec["group"] = 2   # date-only
    else:
        rec["group"] = 3   # uncertain
    records.append(rec)

# master registry
with open(f"{OUT}/famous_people_birth_data.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id","name","profession","birth_date","birth_time",
        "birth_city","birth_country","source_url","source_name","reliability","achievement","group"])
    w.writeheader(); [w.writerow(r) for r in records]
json.dump(records, open(f"{OUT}/famous_people_birth_data.json","w"), indent=2)

# group files
def wgroup(path, grp):
    rows = [r for r in records if r["group"]==grp]
    with open(path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","name","profession","birth_date","birth_time",
            "birth_city","birth_country","source_url","source_name","reliability","achievement"])
        w.writeheader(); [w.writerow({k:r.get(k,"") for k in w.fieldnames}) for r in rows]
    return len(rows)

g1 = wgroup(f"{OUT}/exact_time_people.csv", 1)
g2 = wgroup(f"{OUT}/date_only_people.csv", 2)
g3 = wgroup(f"{OUT}/uncertain_people.csv", 3)
with open(f"{OUT}/duplicate_people.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name","profession","birth_date","birth_time","birth_city"])
    w.writeheader(); [w.writerow({k:d.get(k,"") for k in w.fieldnames}) for d in dups]

# exact_time_people.csv also carries the columns the EXISTING pipeline expects
with open(f"{OUT}/exact_time_people.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id","name","date","time","profession","achievement","rodden"])
    w.writeheader()
    for r in records:
        if r["group"]==1:
            w.writerow({"id":r["id"],"name":r["name"],"date":r["birth_date"],
                "time":r["birth_time"],"profession":r["profession"],
                "achievement":r.get("achievement",""),"rodden":r.get("reliability","")})

print(f"SEED records: {len(SEED)}")
print(f"Unique after dedup: {len(records)}")
print(f"Duplicates removed: {len(dups)}")
print(f"GROUP 1 (exact-time): {g1}")
print(f"GROUP 2 (date-only): {g2}")
print(f"GROUP 3 (uncertain): {g3}")
print(f"Wrote: famous_people_birth_data.csv/json, exact_time_people.csv, date_only_people.csv, uncertain_people.csv, duplicate_people.csv")
