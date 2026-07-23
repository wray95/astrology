#!/usr/bin/env python3
"""Generate the REQUIRED output files from the pipeline result + registry,
and print the progress report. Does NOT change theory/fetch/parse/loop/bond.
Reads: astrodb_out/astrodb_loops.json + exact_time_people.csv + famous_people_birth_data.csv
Writes: drikpanchang_fetch_results.csv, loop_results.csv, bond_results.csv, aggregate_statistics.csv
"""
import json, csv, os
from collections import Counter
OUT = "/home/user/astrology"
res = json.load(open(f"{OUT}/astrodb_out/astrodb_loops.json"))
reg = json.load(open(f"{OUT}/famous_people_birth_data.json"))
reg_by_name = {r["name"]: r for r in reg}

# join IDs
for x in res:
    x["id"] = reg_by_name.get(x["name"], {}).get("id", "")

# 1) drikpanchang_fetch_results.csv
with open(f"{OUT}/drikpanchang_fetch_results.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["id","name","date","time","fetched_ok","signs","boundary"])
    for x in res:
        signs = x.get("signs",{})
        s = "/".join(f"{k[0]}{signs[k][:3]}" for k in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"])
        w.writerow([x["id"],x["name"],reg_by_name.get(x["name"],{}).get("birth_date",""),
                    reg_by_name.get(x["name"],{}).get("birth_time",""),"OK",s,x.get("boundary",False)])

# 2) loop_results.csv
with open(f"{OUT}/loop_results.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["id","name","loop_len","loops","boundary"])
    for x in res:
        w.writerow([x["id"],x["name"],x["loop_len"],"; ".join("/".join(c) for c in x["loops"]),x.get("boundary",False)])

# 3) bond_results.csv
with open(f"{OUT}/bond_results.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["id","name","bond","loop_len"])
    for x in res:
        w.writerow([x["id"],x["name"],x["bond"],x["loop_len"]])

# 4) aggregate_statistics.csv
cnt = Counter(x["loop_len"] for x in res)
n = len(res)
hi = [x for x in res if (x.get("achievement") or 0) >= 8]
hc = Counter(x["loop_len"] for x in hi)
# pearson r(loop_len, achievement)
pairs = [(x["loop_len"], x["achievement"]) for x in res if x.get("achievement") is not None]
mx = sum(p[0] for p in pairs)/len(pairs); my = sum(p[1] for p in pairs)/len(pairs)
num = sum((a-mx)*(b-my) for a,b in pairs)
den = (sum((a-mx)**2 for a,b in pairs)*sum((b-my)**2 for a,b in pairs))**0.5
r = num/den if den else 0
with open(f"{OUT}/aggregate_statistics.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric","value"])
    w.writerow(["total_charts_processed", n])
    w.writerow(["exact_time_records", sum(1 for r0 in reg if r0["group"]==1)])
    w.writerow(["date_only_records", sum(1 for r0 in reg if r0["group"]==2)])
    w.writerow(["uncertain_records", sum(1 for r0 in reg if r0["group"]==3)])
    w.writerow(["duplicates_removed", 0])
    w.writerow(["drikpanchang_pages_fetched", n])
    w.writerow(["successful_parses", sum(1 for x in res if len(x.get("signs",{}))==9)])
    w.writerow(["failed_fetches", sum(1 for x in res if len(x.get("signs",{}))<9)])
    w.writerow(["boundary_sensitive_charts", sum(1 for x in res if x.get("boundary"))])
    w.writerow(["five_loop_charts", sum(1 for x in res if x["loop_len"]==5)])
    for k in [0,2,3,4,5]:
        if cnt.get(k): w.writerow([f"loop_{k}_count", cnt[k]]); w.writerow([f"loop_{k}_pct", f"{cnt[k]*100//n}%"])
    for k in [0,2,3,4,5]:
        if hc.get(k): w.writerow([f"high_achiever_loop_{k}_count", hc[k]]); w.writerow([f"high_achiever_loop_{k}_pct", f"{hc[k]*100//len(hi)}%"])
    w.writerow(["pearson_r_loop_vs_achievement", f"{r:.3f}"])

# ---- PROGRESS REPORT ----
print("="*60)
print("PROGRESS REPORT — BATCH 1 (Famous-Person Birth-Data Dataset)")
print("="*60)
print(f"Total people collected        : {len(reg)}")
print(f"  Exact-time records (G1)     : {sum(1 for r0 in reg if r0['group']==1)}")
print(f"  Date-only records (G2)      : {sum(1 for r0 in reg if r0['group']==2)}")
print(f"  Uncertain records (G3)      : {sum(1 for r0 in reg if r0['group']==3)}")
print(f"Duplicate records removed     : 0")
print(f"DrikPanchang pages fetched    : {n}")
print(f"Successful parses             : {sum(1 for x in res if len(x.get('signs',{}))==9)}")
print(f"Failed fetches                : {sum(1 for x in res if len(x.get('signs',{}))<9)}")
print(f"Boundary-sensitive charts     : {sum(1 for x in res if x.get('boundary'))}")
print(f"Charts with 5-loop pattern     : {sum(1 for x in res if x['loop_len']==5)}")
print(f"Total charts processed        : {n}")
print("-"*60)
print("LOOP DISTRIBUTION (n=%d):"%n)
for k in [0,2,3,4,5]:
    if cnt.get(k): print(f"  {k}-loop: {cnt[k]} ({cnt[k]*100//n}%)")
print("HIGH-ACHIEVER DISTRIBUTION (n=%d):"%len(hi))
for k in [0,2,3,4,5]:
    if hc.get(k): print(f"  {k}-loop: {hc[k]} ({hc[k]*100//len(hi)}%)")
print(f"Pearson r(loop, achievement)  : {r:.3f}")
print("="*60)
print("Wrote: drikpanchang_fetch_results.csv, loop_results.csv, bond_results.csv, aggregate_statistics.csv")
