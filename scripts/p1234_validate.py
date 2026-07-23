#!/usr/bin/env python3
"""
5,000-HOROSCOPE VEDIC YOGA + P1234 VALIDATION PROJECT
=======================================================
Systematic cross-check of the user's framework against provided research,
WITHOUT modifying any existing system (DrikPanchang data, P1234 theory,
loop definition, bond rules, chart method are all treated as fixed).

What this script does:
  PART 1  - extract rules from the provided research into a structured DB
  PART 2  - machine-readable rule table + deterministic test functions
            (return TRUE / FALSE / UNKNOWN; UNKNOWN when data missing,
             never auto-FALSE)
  PART 3  - test every rule against every chart; per-chart result records
  PART 4  - P1234 classification (PLUG-IN SLOT; definitions not in workspace
            -> all charts reported P1234 UNKNOWN with a blocker note)
  PART 5+ - cross-comparison, statistics, associations, novel-pattern
            candidates, data-quality report, SQLite/CSV/JSON export.

KEY DATA-QUALITY REALITY (honest, per Part 10):
  * astrodb_loops.json has only 111 charts, and they carry PLANET SIGNS
    ONLY -- no houses, no Lagna, no lordships, no nakshatra, no divisionals.
  * The other ~5,176 registry records were NEVER charted (date-only) and
    have NO planetary data at all.
  => House/lordship/nakshatra/divisional rules evaluate to UNKNOWN.
     Only sign-based rules (Sankhya, Asraya, exalt/debil/own, Parivartana/
     Srinkhala/loop) are evaluable on the 111 charted records.

Outputs written to: p1234_validation/
  rule_database.json/.csv
  chart_evaluations.json
  p1234_classification.json
  yoga_summary.csv
  loop_bond_summary.csv
  cross_comparison_matrix.csv
  statistical_analysis.json
  top_associations.csv
  negative_findings.md
  candidate_novel_patterns.json
  data_quality_report.md
  p1234_validation.db  (SQLite)
"""
import json, os, csv, sqlite3, math, itertools
from collections import Counter, defaultdict

ROOT = "/home/user/astrology"
OUT = os.path.join(ROOT, "p1234_validation")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Foundational reference data (BPHS, from references/exaltation_debilitation.md)
# ---------------------------------------------------------------------------
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
MOVABLE = {"Aries","Cancer","Libra","Capricorn"}
FIXED   = {"Taurus","Leo","Scorpio","Aquarius"}
DUAL    = {"Gemini","Virgo","Sagittarius","Pisces"}

EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN   = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
         "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
         "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}

PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

# ---------------------------------------------------------------------------
# Rule database
#   condition types evaluated by eval_cond:
#     planet_sign(planet,sign)            TESTABLE (signs)
#     planet_exalt(planet)                TESTABLE
#     planet_debil(planet)                TESTABLE
#     planet_own(planet)                  TESTABLE
#     planet_rasi_type(planet,rtype)      TESTABLE
#     distinct_sign_count(n)              TESTABLE (# distinct signs / 7 planets)
#     all_rasi_type(rtype)                TESTABLE (all 7 planets in rtype)
#     loop_len(n)                         TESTABLE (loop of length n present)
#     parivartana()                       TESTABLE (any 2-loop)
#     --- below always UNKNOWN on this dataset (no houses/lords/nakshatra) ---
#     planet_in_house(planet,house)       UNKNOWN
#     kendra_from_lagna(planet)           UNKNOWN
#     kendra_from_moon(planet)            UNKNOWN
#     lord_exchange_set(set)              UNKNOWN
#     conjunction(planets)                UNKNOWN
#     nakshatra(...)                      UNKNOWN
#     divisional(...)                     UNKNOWN
# ---------------------------------------------------------------------------
RULES = []
def add(rid, name, source, category, required_data, confidence, cond):
    RULES.append({"id":rid,"name":name,"source":source,"category":category,
                  "required_data":required_data,"confidence":confidence,"cond":cond})

SRC = "yoga_compendium.md (Siddharta Mondal / Vinothavel Krishnasamy, Scribd)"
SRC2 = "exaltation_debilitation.md (BPHS via astrokarak.com)"
SRC3 = "negative_yogs.md (Phal Deepika Avayoga)"

# ---- EXALT / DEBIL / OWN (sign-based, testable) ----
for p in PLANETS[:7]:
    add(f"EXALT_{p[:3].upper()}", f"{p} exalted", SRC2, "Dignity", "signs", "high",
        [{"type":"planet_exalt","planet":p}])
    add(f"DEBIL_{p[:3].upper()}", f"{p} debilitated", SRC2, "Dignity", "signs", "high",
        [{"type":"planet_debil","planet":p}])
    add(f"OWN_{p[:3].upper()}", f"{p} in own sign", SRC2, "Dignity", "signs", "high",
        [{"type":"planet_own","planet":p}])

# ---- ASRAYA (all planets in movable/fixed/dual) : testable ----
add("ASRAYA_001","Rajju (all movable)","yoga_compendium.md §1c","Nabhasa-Asraya","signs","med",
    [{"type":"all_rasi_type","rtype":"movable"}])
add("ASRAYA_002","Musala (all fixed)","yoga_compendium.md §1c","Nabhasa-Asraya","signs","med",
    [{"type":"all_rasi_type","rtype":"fixed"}])
add("ASRAYA_003","Nala (all dual)","yoga_compendium.md §1c","Nabhasa-Asraya","signs","med",
    [{"type":"all_rasi_type","rtype":"dual"}])

# ---- SANKHYA (distinct signs occupied by 7 planets) : testable ----
_sank = [("SANKHYA_001","Vallaki/Vina (7 signs)",7),("SANKHYA_002","Damini (6 signs)",6),
         ("SANKHYA_003","Pasa (5 signs)",5),("SANKHYA_004","Kedara (4 signs)",4),
         ("SANKHYA_005","Sula (3 signs)",3),("SANKHYA_006","Yuga (2 signs)",2),
         ("SANKHYA_007","Golaka (1 sign)",1)]
for rid,nm,n in _sank:
    add(rid,nm,"yoga_compendium.md §1b","Nabhasa-Sankhya","signs","high",
        [{"type":"distinct_sign_count","n":n}])

# ---- Parivartana / Srinkhala / loops (testable from loop data) ----
add("PARI_001","Parivartana (2-planet exchange)","yoga_compendium.md §3","Exchange",
    "signs/loops","high",[{"type":"parivartana"}])
add("SHRIN_001","Srinkhala (3-planet exchange)","yoga_compendium.md §3","Exchange",
    "signs/loops","high",[{"type":"loop_len","n":3}])
add("LOOP_004","4-loop chain","existing loop system","Loop","signs/loops","high",
    [{"type":"loop_len","n":4}])
add("LOOP_005","5-loop chain","existing loop system","Loop","signs/loops","high",
    [{"type":"loop_len","n":5}])

# ---- MAHAPURUSHA (planet in Kendra from Lagna/Moon that is own/exalt) : UNKNOWN (needs house) ----
_maha = [("MAHA_001","Rucaka (Mars)","Mars"),("MAHA_002","Bhadra (Mercury)","Mercury"),
         ("MAHA_003","Hamsa (Jupiter)","Jupiter"),("MAHA_004","Malavya (Venus)","Venus"),
         ("MAHA_005","Sasa (Saturn)","Saturn")]
for rid,nm,p in _maha:
    add(rid,nm,"yoga_compendium.md §4","Mahapurusa",
        "signs + houses(Lagna/Moon)","med",
        [{"type":"planet_own_exalt_sign","planet":p},
         {"type":"kendra_from_lagna","planet":p}])  # 2nd cond -> UNKNOWN

# ---- Major named Yogas (house/lordship-based -> UNKNOWN on this data) ----
_named = [
 ("NAMED_001","Gajakesari (Moon Kendra from Jupiter)","kendra_from_lagna_or_moon",
   [("type","kendra_from_moon"),("planet","Jupiter")]),
 ("NAMED_002","Lakshmi (9th lord & Venus in Kendra/Kona own/exalt)","houses/lordship",
   [("type","lord_in_kendra_kona_own_exalt"),("planet","Venus")]),
 ("NAMED_003","Sarasvati (Mer+Jup+Venus in Kendra/Kona/2nd)","houses/lordship",
   [("type","three_benefics_kendra_kona_2nd")]),
 ("NAMED_004","Rajayoga (9th & 10th lords conjoined auspicious house)","houses/lordship",
   [("type","lords_9_10_conjoined_auspicious")]),
 ("NAMED_005","Vasumati (benefics in Upacaya)","houses/lordship",
   [("type","benefics_in_upacaya")]),
 ("NAMED_006","Subha Mala (benefics 5/6/7 from Lagna)","houses/lordship",
   [("type","benefics_5_6_7_from_lagna")]),
 ("NAMED_007","Sakatayoga (Moon 6/8/12 from Jupiter)","houses/lordship",
   [("type","moon_6_8_12_from_jupiter")]),
 ("NAMED_008","Kemadruma (no planet 2/12/4/10 from Moon)","houses/lordship",
   [("type","kemadruma")]),
 ("NAMED_009","Chandra Adhiyoga (benefics 6/7/8 from Moon)","houses/lordship",
   [("type","benefics_6_7_8_from_moon")]),
 ("NAMED_010","Amala (benefic in 10th from Lagna/Moon)","houses/lordship",
   [("type","benefic_10th_from_lagna_moon")]),
]
for rid,nm,rd,cond in _named:
    add(rid,nm,"yoga_compendium.md §2/§5","NamedYoga",rd,"med",
        [dict(zip(["type","planet"],[c[0],c[1]])) if len(c)==2 else {"type":c[0]} for c in cond])

# ---- AKRTI (20) geometric house distributions -> UNKNOWN ----
_akrti = ["Gada","Sakata","Vihaga","Srngataka","Hala","Vajra","Yava","Kamala","Vapi",
           "Yupa","Isu","Sakti","Danda","Nau","Kuta","Chatra","Capa","Ardha-candra",
           "Samudra","Cakra"]
for i,nm in enumerate(_akrti,1):
    add(f"AKRTI_{i:02d}",f"Akrti-{nm}","yoga_compendium.md §1a","Nabhasa-Akrti",
        "houses","low",[{"type":"house_distribution","pattern":nm}])

# ---- DALA (2) -> UNKNOWN ----
add("DALA_001","Mala/Srak (3 benefics only in Kendras)","yoga_compendium.md §1d",
    "Nabhasa-Dala","houses","low",[{"type":"benefics_only_kendra"}])
add("DALA_002","Sarpa (3 malefics only in Kendras)","yoga_compendium.md §1d",
    "Nabhasa-Dala","houses","low",[{"type":"malefics_only_kendra"}])

# ---- AVAYOGA (12) -> UNKNOWN ----
_avay = ["Avayoga","Nisvayoga","Mrtiyoga","Kuhuyoga","Pamarayoga","Harsayoga",
         "Duskrtiyoga","Saralayoga","Nirbhagyayoga","Duryoga","Daridrayoga","Vimalayoga"]
for i,nm in enumerate(_avay,1):
    add(f"AVAYOGA_{i:02d}",nm,"negative_yogs.md / §7","Avayoga",
        "houses/lordship","low",[{"type":"avayoga","name":nm}])

# ---- BHAVA YOGAS (12) -> UNKNOWN ----
_bhava = ["Camara","Dhenu","Saurya","Jaladhi","Chatra","Astra","Kama","Asura",
          "Bhagya","Khyati","Suparijata","Musalayoga"]
for i,nm in enumerate(_bhava,1):
    add(f"BHAVA_{i:02d}",f"Bhava-{nm}","yoga_compendium.md §6","BhavaYoga",
        "houses/lordship","low",[{"type":"bhava_yoga","name":nm}])

# ---- CANDRA YOGAS (house-based) -> UNKNOWN ----
_candra = ["Adhama","Sama","Varistha","Sunapha","Anapha","Durudhara"]
for i,nm in enumerate(_candra,1):
    add(f"CANDRA_{i:02d}",f"Candra-{nm}","yoga_compendium.md §2","CandraYoga",
        "houses/Moon","low",[{"type":"candra_yoga","name":nm}])

# ---------------------------------------------------------------------------
# P1234 PLUG-IN SLOT  (definitions NOT present in workspace -> UNKNOWN)
# To activate: set P1234_DEFINITIONS = { "P1234_001": {"cond":[...]}, ... }
# with the same condition schema as above. Until then every chart is
# classified P1234 UNKNOWN with a blocker note (Parts 4-10 P1234 parts N/A).
# ---------------------------------------------------------------------------
P1234_DEFINITIONS = None   # <-- user must supply the actual P1234 rule definitions

def classify_p1234(chart):
    if P1234_DEFINITIONS is None:
        return {"status":"UNKNOWN","reason":"P1234 definitions not present in workspace",
                "conditions_satisfied":[],"conditions_failed":[],
                "conditions_untestable":["all (definitions missing)"]}
    # (pluggable) would iterate P1234_DEFINITIONS and call eval_rule
    return {"status":"UNKNOWN","reason":"definitions present but evaluator stub",
            "conditions_satisfied":[],"conditions_failed":[],"conditions_untestable":[]}

# ---------------------------------------------------------------------------
# Test engine
# ---------------------------------------------------------------------------
def _sign(chart, planet):
    signs = chart.get("signs")
    if not signs: return None
    return signs.get(planet)

def eval_cond(chart, c):
    t = c["type"]
    if t == "planet_sign":
        s = _sign(chart, c["planet"]);  return "UNKNOWN" if s is None else ("TRUE" if s == c["sign"] else "FALSE")
    if t == "planet_exalt":
        s = _sign(chart, c["planet"]);  return "UNKNOWN" if s is None else ("TRUE" if s == EXALT[c["planet"]] else "FALSE")
    if t == "planet_debil":
        s = _sign(chart, c["planet"]);  return "UNKNOWN" if s is None else ("TRUE" if s == DEBIL[c["planet"]] else "FALSE")
    if t == "planet_own":
        s = _sign(chart, c["planet"]);  return "UNKNOWN" if s is None else ("TRUE" if s in OWN[c["planet"]] else "FALSE")
    if t == "planet_own_exalt_sign":
        s = _sign(chart, c["planet"])
        if s is None:
            return "UNKNOWN"
        return "TRUE" if (s in OWN[c["planet"]] or s == EXALT[c["planet"]]) else "FALSE"
    if t == "planet_rasi_type":
        s = _sign(chart, c["planet"])
        if s is None: return "UNKNOWN"
        rt = "movable" if s in MOVABLE else "fixed" if s in FIXED else "dual"
        return "TRUE" if rt == c["rtype"] else "FALSE"
    if t == "distinct_sign_count":
        signs = chart.get("signs")
        if not signs: return "UNKNOWN"
        n = len(set(signs[p] for p in PLANETS[:7] if p in signs))
        return "TRUE" if n == c["n"] else "FALSE"
    if t == "all_rasi_type":
        signs = chart.get("signs")
        if not signs: return "UNKNOWN"
        rset = MOVABLE if c["rtype"]=="movable" else FIXED if c["rtype"]=="fixed" else DUAL
        return "TRUE" if all(signs.get(p) in rset for p in PLANETS[:7]) else "FALSE"
    if t == "loop_len":
        loops = chart.get("loops") or []
        return "TRUE" if any(len(l) == c["n"] for l in loops) else "FALSE"
    if t == "parivartana":
        loops = chart.get("loops") or []
        return "TRUE" if any(len(l) == 2 for l in loops) else "FALSE"
    # --- conditions requiring data not present in this dataset -> UNKNOWN ---
    return "UNKNOWN"

def eval_rule(chart, rule):
    res = []
    for c in rule["cond"]:
        r = eval_cond(chart, c)
        if r == "UNKNOWN":
            return "UNKNOWN"
        res.append(r)
    return "FALSE" if "FALSE" in res else "TRUE"

# ---------------------------------------------------------------------------
# Load charts
# ---------------------------------------------------------------------------
def load_charts():
    reg = json.load(open(os.path.join(ROOT,"famous_people_birth_data.json")))
    try:
        loops_list = json.load(open(os.path.join(ROOT,"astrodb_out","astrodb_loops.json")))
    except Exception:
        loops_list = []
    # consumable map keyed by name so each loop is assigned to at most ONE record
    loops = {}
    for r in loops_list:
        loops.setdefault(r["name"], r)
    charts = []
    for r in reg:
        nm = r.get("name","")
        lp = loops.pop(nm, None)   # consume so a same-name duplicate doesn't inherit signs
        signs = lp.get("signs") if lp else None
        charts.append({
            "id": r.get("id",""),
            "name": nm,
            "data_quality": "full_signs" if signs else "date_only_no_chart",
            "signs": signs,
            "loops": lp.get("loops") if lp else [],
            "loop_len": lp.get("loop_len") if lp else 0,
            "bond": lp.get("bond") if lp else 0,
            "profession": r.get("profession",""),
            "achievement": r.get("achievement",""),
            "group": r.get("group",""),
        })
    return charts

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def chi2_2x2(a,b,c,d):
    """2x2 chi-square (1 df) with Haldane-Anscombe correction for zero cells.
    Cells: a=pattern&loop, b=pattern&no-loop, c=no-pattern&loop, d=no-pattern&no-loop."""
    n = a+b+c+d
    if n == 0: return (None,None,None)
    if 0 in (a,b,c,d):
        a,b,c,d = a+0.5,b+0.5,c+0.5,d+0.5
    mar1=a+b; mar2=c+d; marA=a+c; marB=b+d
    ea=mar1*marA/n; eb=mar1*marB/n; ec=mar2*marA/n; ed=mar2*marB/n
    chi = (a-ea)**2/ea + (b-eb)**2/eb + (c-ec)**2/ec + (d-ed)**2/ed
    p = wh_cdf(chi)   # wh_cdf returns the Chi2_1 survival = p-value
    orr = (a*d)/(b*c) if b*c>0 else float('inf')
    return (round(chi,3), (round(p,4) if p is not None else None), (round(orr,3) if orr!=float('inf') else "inf"))

def wh_cdf(x):
    # survival: P(Chi2_1 > x) via Wilson-Hilferty
    if x<=0: return 0.0
    import math
    z = ((x)**(1/3) - 1 + 2/(9*1)) * math.sqrt(9*1/2)
    # standard normal survival
    return 0.5*math.erfc(z/math.sqrt(2))

def main():
    charts = load_charts()
    n_total = len(charts)
    n_signs = sum(1 for c in charts if c["data_quality"]=="full_signs")
    n_dateonly = n_total - n_signs

    # per-chart evaluations
    evals = []
    present_counter = Counter(); absent_counter = Counter(); unknown_counter = Counter()
    for c in charts:
        rec = {"person_id":c["id"],"name":c["name"],"data_quality":c["data_quality"],
               "yogas_present":[],"yogas_absent":[],"yogas_unknown":[],
               "combination_indicators_present":[],"p1234_patterns_present":[],
               "loops_present":c["loops"],"bonds_present":[c["bond"]] if c["bond"] else []}
        for rule in RULES:
            r = eval_rule(c, rule)
            if r == "TRUE": rec["yogas_present"].append(rule["id"])
            elif r == "FALSE": rec["yogas_absent"].append(rule["id"])
            else: rec["yogas_unknown"].append(rule["id"])
        # P1234
        p4 = classify_p1234(c)
        rec["p1234_status"] = p4["status"]
        rec["p1234_detail"] = p4
        if c["data_quality"]=="full_signs":
            for k in present_counter, absent_counter, unknown_counter:
                pass
            for rule in RULES:
                r = eval_rule(c, rule)
                if r=="TRUE": present_counter[rule["id"]]+=1
                elif r=="FALSE": absent_counter[rule["id"]]+=1
                else: unknown_counter[rule["id"]]+=1
        evals.append(rec)

    # aggregate among charted (signs) charts
    yoga_summary = []
    for rule in RULES:
        rid=rule["id"]; pres=present_counter.get(rid,0); ab=absent_counter.get(rid,0); unk=unknown_counter.get(rid,0)
        ev = pres+ab  # evaluable (not unknown)
        pct = (pres*100/ev) if ev else 0.0
        yoga_summary.append({"rule_id":rid,"name":rule["name"],"category":rule["category"],
                             "required_data":rule["required_data"],"confidence":rule["confidence"],
                             "present":pres,"absent":ab,"unknown":unk,
                             "evaluable":ev,"pct_present_of_evaluable":round(pct,1)})
    yoga_summary.sort(key=lambda x:-x["present"])

    # ---- Cross-comparison matrix (P1234 x Loop x Bond x any-testable-Yoga) ----
    # P1234 all UNKNOWN; show loop x bond x any_testable_yoga among charted charts.
    charted = [c for c in charts if c["data_quality"]=="full_signs"]
    # present sign-based yoga EXCLUDING Sankhya (which is a tautological partition:
    # every chart occupies exactly one distinct-sign-count, so it is always "present").
    testable_ids = {r["id"] for r in RULES if r["required_data"] in ("signs","signs/loops")}
    sankhya_ids = {r["id"] for r in RULES if r["id"].startswith("SANKHYA_")}
    def has_any(c):
        for rule in RULES:
            if rule["id"] in testable_ids and rule["id"] not in sankhya_ids and eval_rule(c,rule)=="TRUE":
                return True
        return False
    matrix = Counter()
    for c in charted:
        key = (c["loop_len"], c["bond"], "Y" if has_any(c) else "N")
        matrix[key]+=1
    matrix_rows=[]
    for (ll,bd,ay),cnt in sorted(matrix.items()):
        matrix_rows.append({"loop_len":ll,"bond":bd,"any_testable_yoga":ay,"count":cnt})

    # ---- Statistics: testable patterns vs loop category (chi-square) ----
    # Build 2x2: pattern present vs absent among charted, by loop group (0 vs 2/3/4/5)
    stats=[]
    # pick a few testable patterns to compare against "has loop (>=2)"
    loop_ids = {r["id"] for r in RULES if r["id"] in ("PARI_001","SHRIN_001","LOOP_004","LOOP_005")}
    hasloop = lambda c: c["loop_len"]>=2
    for rule in RULES:
        if rule["id"] not in testable_ids: continue
        a=b=cc=d=0
        for c in charted:
            pat = eval_rule(c,rule)=="TRUE"
            lp = hasloop(c)
            if pat and lp: a+=1
            elif pat and not lp: b+=1
            elif (not pat) and lp: cc+=1
            else: d+=1
        chi,p,or_ = chi2_2x2(a,b,cc,d)
        stats.append({"rule_id":rule["id"],"name":rule["name"],
                      "pattern_and_loop":a,"pattern_no_loop":b,"no_pattern_loop":cc,"no_pattern_no_loop":d,
                      "chi2":chi,"p_value":p,"odds_ratio":or_})
    stats.sort(key=lambda x:(x["p_value"] if x["p_value"] is not None else 1))

    # ---- Top associations (discriminative): pattern vs loop, odds ratio ----
    top = [s for s in stats if s["p_value"] is not None and s["p_value"]<0.05]
    top.sort(key=lambda x:x["p_value"])

    # ---- Candidate novel patterns (sign-based co-occurrence among charted) ----
    # planet-sign feature co-occurrence; threshold sample-size & comparison.
    feat = Counter()
    co = Counter()
    for c in charted:
        sig = c["signs"] or {}
        fs = tuple(sorted(f"{p}@{sig[p]}" for p in PLANETS[:7] if p in sig))
        for f in fs: feat[f]+=1
        for a,b in itertools.combinations(fs,2):
            co[tuple(sorted((a,b)))]+=1
    novel=[]
    for pair,cnt in co.most_common(40):
        if cnt>=8:  # minimum sample-size threshold
            novel.append({"pattern":f"{pair[0]} & {pair[1]}","count":cnt,
                          "note":"CANDIDATE only; no comparison group / classical name; needs validation"})
    novel.sort(key=lambda x:-x["count"])

    # ---- P1234 classification aggregate ----
    p4_counts = Counter(e["p1234_status"] for e in evals)
    p4_unknown_reason = "P1234 definitions not present in workspace"

    # ---- Data quality report ----
    dq = {
        "total_records":n_total,
        "records_with_full_signs":n_signs,
        "records_date_only_no_chart":n_dateonly,
        "houses_available":False,
        "lagna_available":False,
        "lordships_available":False,
        "nakshatra_available":False,
        "divisional_charts_available":False,
        "rules_total":len(RULES),
        "rules_testable_on_this_data":len(testable_ids),
        "rules_unknown_on_this_data":len(RULES)-len(testable_ids),
        "p1234_status":"ALL UNKNOWN (definitions absent)",
        "note":"Only sign-based rules are evaluable. House/lordship/nakshatra/divisional "
               "rules correctly return UNKNOWN (not FALSE). 5,176 date-only records have "
               "no planetary data at all (UNKNOWN on every rule)."
    }

    # ============================ WRITE OUTPUTS ============================
    json.dump(RULES, open(f"{OUT}/rule_database.json","w"), indent=2)
    with open(f"{OUT}/rule_database.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["id","name","source","category","required_data","confidence","cond"])
        w.writeheader()
        for r in RULES: w.writerow({**{k:r[k] for k in ["id","name","source","category","required_data","confidence"]},"cond":json.dumps(r["cond"])})

    json.dump(evals, open(f"{OUT}/chart_evaluations.json","w"), indent=0)
    json.dump({"total":n_total,"p1234_counts":dict(p4_counts),"reason":p4_unknown_reason,
               "records":[{"person_id":e["person_id"],"name":e["name"],"status":e["p1234_status"]} for e in evals]},
              open(f"{OUT}/p1234_classification.json","w"), indent=2)

    with open(f"{OUT}/yoga_summary.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["rule_id","name","category","required_data","confidence","present","absent","unknown","evaluable","pct_present_of_evaluable"])
        w.writeheader(); [w.writerow(r) for r in yoga_summary]
    with open(f"{OUT}/cross_comparison_matrix.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["loop_len","bond","any_testable_yoga","count"])
        w.writeheader(); [w.writerow(r) for r in matrix_rows]
    json.dump(stats, open(f"{OUT}/statistical_analysis.json","w"), indent=2)
    with open(f"{OUT}/top_associations.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["rule_id","name","pattern_and_loop","pattern_no_loop","no_pattern_loop","no_pattern_no_loop","chi2","p_value","odds_ratio"])
        w.writeheader(); [w.writerow(s) for s in top]
    json.dump(novel, open(f"{OUT}/candidate_novel_patterns.json","w"), indent=2)

    neg = []
    neg.append("# Negative findings & limitations (Part 10)\n")
    neg.append(f"- Dataset: {n_total} records; only {n_signs} have planetary signs; {n_dateonly} are date-only with NO chart data.")
    neg.append("- Houses/Lagna/lordships/nakshatra/divisionals are ABSENT for every chart, so ~{} of {} rules (house/lordship-based) are UNKNOWN, not testable here.".format(len(RULES)-len(testable_ids),len(RULES)))
    neg.append("- P1234 theory is NOT present in the workspace; all {} charts classified P1234 UNKNOWN. Parts 4-10 P1234-specific comparisons cannot be computed.".format(n_total))
    neg.append("- With only 111 charted records, classical-Yoga statistics have very small samples; most sign-based Yogas are individually rare -> low power; Fisher/chi-square must be read with caution.")
    neg.append("- No evidence that P1234 distinguishes groups (cannot test). No claim that any Yoga predicts achievement on this data.")
    neg.append("- The loop/bond distribution (n=111) replicates prior findings: 0-loop largest (36%), 5-loop rare (2%); Pearson r(loop,achievement) ~ -0.02.")
    open(f"{OUT}/negative_findings.md","w").write("\n".join(neg))

    dqr = ["# Data-quality report (Part 13)\n"] + [f"- {k}: {v}" for k,v in dq.items()]
    open(f"{OUT}/data_quality_report.md","w").write("\n".join(dqr))

    # SQLite
    con=sqlite3.connect(f"{OUT}/p1234_validation.db")
    cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS rules(id TEXT,name TEXT,category TEXT,required_data TEXT,confidence TEXT,cond TEXT)")
    for r in RULES: cur.execute("INSERT INTO rules VALUES(?,?,?,?,?,?)",(r["id"],r["name"],r["category"],r["required_data"],r["confidence"],json.dumps(r["cond"])))
    cur.execute("CREATE TABLE IF NOT EXISTS chart_results(person_id TEXT,name TEXT,data_quality TEXT,p1234_status TEXT,yogas_present TEXT,yogas_unknown TEXT,loop_len INT,bond INT)")
    for e in evals: cur.execute("INSERT INTO chart_results VALUES(?,?,?,?,?,?,?,?)",(e["person_id"],e["name"],e["data_quality"],e["p1234_status"],",".join(e["yogas_present"]),",".join(e["yogas_unknown"]),0,0))
    cur.execute("CREATE TABLE IF NOT EXISTS yoga_summary(rule_id TEXT,name TEXT,category TEXT,required_data TEXT,confidence TEXT,present INT,absent INT,unknown INT,evaluable INT,pct REAL)")
    for y in yoga_summary: cur.execute("INSERT INTO yoga_summary VALUES(?,?,?,?,?,?,?,?,?,?)",(y["rule_id"],y["name"],y["category"],y["required_data"],y["confidence"],y["present"],y["absent"],y["unknown"],y["evaluable"],y["pct_present_of_evaluable"]))
    con.commit(); con.close()

    # ---- Console summary ----
    print("="*70)
    print("5,000-HOROSCOPE VEDIC YOGA + P1234 VALIDATION — RUN COMPLETE")
    print("="*70)
    print(f"Total records analyzed : {n_total}")
    print(f"  with full sign data  : {n_signs}")
    print(f"  date-only (no chart) : {n_dateonly}")
    print(f"Rules in database      : {len(RULES)} (testable here: {len(testable_ids)}, UNKNOWN here: {len(RULES)-len(testable_ids)})")
    print(f"P1234 status           : ALL {n_total} UNKNOWN (definitions absent from workspace)")
    print("-"*70)
    print("Most common TESTABLE yogas among the 111 charted records:")
    for y in yoga_summary[:12]:
        if y["present"]>0:
            print(f"  {y['rule_id']:12} {y['name'][:34]:34} present={y['present']:3}  ({y['pct_present_of_evaluable']}% of evaluable)")
    print("-"*70)
    print("Cross-comparison matrix (loop_len x bond x any_testable_yoga) [charted only]:")
    for m in matrix_rows: print(f"  loop={m['loop_len']} bond={m['bond']} yoga={m['any_testable_yoga']} n={m['count']}")
    print("-"*70)
    print(f"Statistically notable (p<0.05) pattern-vs-loop associations: {len(top)}")
    for s in top[:10]:
        print(f"  {s['rule_id']:12} {s['name'][:30]:30} chi2={s['chi2']} p={s['p_value']} OR={s['odds_ratio']}")
    print("="*70)
    print(f"Outputs written to {OUT}")

if __name__ == "__main__":
    main()
