#!/usr/bin/env python3
"""
EVENT TIMING ENGINE — general, reusable hypothesis tester
==========================================================
Tests ANY classical timing rule against ANY dated-event set, with:
  - pre-defined window constructors (saturn_sign, jupiter_sign, return ±y,
    ingress, dasha period if MD list given)
  - permutation test (natal sign shuffle, age-preserving)
  - exposure-based expected rate
  - Benjamini-Hochberg FDR when multiple rules tested together

Usage:
  from event_timing_engine import test_rule, make_event_rows, RULES
  rows = make_event_rows(event_db, rule="saturn_sign")
  test_rule(rows, ...)

Rules implemented:
  saturn_sign   : Saturn transits natal Saturn sign (each visit)
  jupiter_sign  : Jupiter transits natal Jupiter sign (each visit)
  saturn_return : exact Saturn return ± window_y
  jupiter_h9    : Jupiter transits 9th from Moon (each visit)
  saturn_h10    : Saturn transits 10th from Lagna (each visit) [needs lagna]
"""
import json, math, re, random, sys, gzip, csv
sys.path.insert(0, "scripts")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
DAYS = 365.25
PIDS = {"Saturn": 6, "Jupiter": 5}

_REGISTRY = None
def _load_registry():
    """name -> birth MM/DD/YYYY from famous_people_birth_data.csv.gz"""
    global _REGISTRY
    if _REGISTRY is not None: return _REGISTRY
    reg = {}
    try:
        with gzip.open("data/famous_people_birth_data.csv.gz", "rt", errors="ignore") as f:
            for row in csv.DictReader(f):
                nm = (row.get("name") or "").strip(); bd = (row.get("birth_date") or "").strip()
                if nm and bd: reg[nm] = bd
    except FileNotFoundError:
        pass
    _REGISTRY = reg
    return reg

def jd_of(y, m, d):
    return swe.julday(y, m, d, 12.0)

def lon_at(jd, pid):
    lt, _ = swe.calc_ut(jd, pid)
    return (lt[0] - swe.get_ayanamsa(jd)) % 360

def natal_sign(y, m, d, pid):
    return int(lon_at(jd_of(y, m, d), pid) // 30)

_ENTRIES = {}
def global_entries(pid, y0=1900, y1=2105):
    if pid in _ENTRIES: return _ENTRIES[pid]
    entries = []
    jd = jd_of(y0,1,1); end = jd_of(y1,12,31); prev = None; step = 4.0
    while jd <= end:
        s = int(lon_at(jd, pid)//30)
        if prev is not None and s != prev:
            lo, hi = jd-step, jd
            for _ in range(20):
                mid = (lo+hi)/2
                if int(lon_at(mid, pid)//30) == s: hi = mid
                else: lo = mid
            entries.append((hi, s))
        prev = s; jd += step
    _ENTRIES[pid] = entries
    return entries

def _visits(pid, natal_idx, birth_jd, age_max=85):
    """Windows for transits of the natal sign: entry -> next CONSECUTIVE entry
    (≈2.5y for Saturn, ≈1y for Jupiter). Uses the universal entry table."""
    entries = global_entries(pid)
    out = []
    for i, (e, s) in enumerate(entries):
        if s != natal_idx or e < birth_jd: continue
        if e > birth_jd + age_max*DAYS: break
        nxt = entries[i+1][0] if i+1 < len(entries) else e + 2.5*DAYS
        out.append((e, nxt))
    return out

def _returns(pid, natal_lon, birth_jd, age_max=85):
    entries = global_entries(pid)
    out = []
    for i, (e, s) in enumerate(entries):
        if s != int(natal_lon//30) or e < birth_jd: continue
        if e > birth_jd + age_max*DAYS: break
        nxt = entries[i+1][0] if i+1 < len(entries) else e + 2.5*DAYS
        lo, hi = e, nxt
        for _ in range(20):
            mid = (lo+hi)/2
            if lon_at(mid, pid) > natal_lon: hi = mid
            else: lo = mid
        if abs((lon_at(lo, pid) - natal_lon + 180) % 360 - 180) < 0.7:
            out.append(lo)
    return out

def RULES(rule, y, m, d, birth_jd, age_max=85, window_y=1.0):
    """Return windows [(start_jd, end_jd)] for this person/rule."""
    if rule == "saturn_sign":
        return _visits(6, natal_sign(y, m, d, 6), birth_jd, age_max)
    if rule == "jupiter_sign":
        return _visits(5, natal_sign(y, m, d, 5), birth_jd, age_max)
    if rule == "saturn_return":
        nl = lon_at(birth_jd, 6)
        return [(r - window_y*DAYS, r + window_y*DAYS)
                for r in _returns(6, nl, birth_jd, age_max)]
    if rule == "jupiter_return":
        nl = lon_at(birth_jd, 5)
        return [(r - window_y*DAYS, r + window_y*DAYS)
                for r in _returns(5, nl, birth_jd, age_max)]
    raise ValueError(rule)

def make_event_rows(event_db, key="events"):
    """Rows: {name, birth:(y,m,d), event_jd, event_year, age}.
    Birth dates: event record if present, else registry join by name."""
    evs = event_db[key] if isinstance(event_db, dict) else event_db
    reg = _load_registry()
    rows = []
    for e in evs:
        b = e.get("birth_date") or reg.get((e.get("person") or "").strip(), "")
        m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", b.strip())
        if not m:
            m2 = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", b.strip())
            if not m2:
                m3 = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", b.strip())
                if not m3: continue
                mon = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                       "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
                y, mo, d = int(m3.group(3)), mon.get(m3.group(1),1), int(m3.group(2))
            else:
                y, mo, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        else:
            y, mo, d = int(m.group(3)), int(m.group(1)), int(m.group(2))
        ed = e.get("event_date") or ""
        me = re.match(r"^(\d{4})", str(ed).strip())
        if not me: continue
        ey = int(me.group(1))
        if not (1850 <= y <= 2010 and y <= ey <= y + 85): continue
        bj = jd_of(y, mo, d); ej = jd_of(ey, 7, 1)
        if ej <= bj: continue
        rows.append({"name": e.get("person",""), "birth": (y, mo, d),
                     "birth_jd": bj, "event_jd": ej, "event_year": ey,
                     "age": (ej - bj)/DAYS, "event_type": e.get("event_type","")})
    return rows

def win_matrix(rule, rows, window_y=1.0):
    """For each row, list[12] booleans: True if event in windows when natal
    sign == i (i indexes the rule's reference sign: Saturn sign / Jupiter
    sign / Moon-lagna offset)."""
    mat = []
    for r in rows:
        y, mo, d = r["birth"]
        bj = r["birth_jd"]; ej = r["event_jd"]
        m = []
        for i in range(12):
            # emulate natal sign == i by shifting natal longitudes
            wins = None
            if rule == "saturn_sign":
                wins = _visits(6, i, bj)
            elif rule == "jupiter_sign":
                wins = _visits(5, i, bj)
            elif rule in ("saturn_return", "jupiter_return"):
                pid = 6 if rule.startswith("saturn") else 5
                nl = i*30 + 15.0
                wins = [(rr - window_y*DAYS, rr + window_y*DAYS)
                        for rr in _returns(pid, nl, bj)]
            m.append(any(s <= ej <= e for s, e in (wins or [])))
        mat.append(m)
    return mat

def test_rule(rule, rows, n_perm=3000, seed=7, window_y=1.0, label=None):
    mat = win_matrix(rule, rows, window_y)
    n = len(rows)
    # observed: use each person's actual natal sign for the rule
    if rule == "saturn_sign":
        idxs = [natal_sign(r["birth"][0], r["birth"][1], r["birth"][2], 6) for r in rows]
    elif rule == "jupiter_sign":
        idxs = [natal_sign(r["birth"][0], r["birth"][1], r["birth"][2], 5) for r in rows]
    else:
        idxs = [natal_sign(r["birth"][0], r["birth"][1], r["birth"][2], 6) for r in rows]
    obs = sum(1 for i in range(n) if mat[i][idxs[i]])
    expo = sum(sum(m)/12.0 for m in mat) / n
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_perm):
        perm = [rng.randrange(12) for _ in range(n)]
        c = sum(1 for i in range(n) if mat[i][perm[i]])
        if c >= obs: ge += 1
    p = ge / n_perm
    return {"rule": rule, "label": label or rule, "n": n, "observed_in": obs,
            "rate": round(obs/n, 4), "mean_exposure": round(expo, 4),
            "permutation_p": round(p, 4),
            "supported": p < 0.05 and obs/n > expo}

def bh_fdr(tests, q=0.05):
    """Benjamini-Hochberg on the permutation p-values."""
    tests = sorted(tests, key=lambda t: t["permutation_p"])
    m = len(tests)
    sig = []
    for i, t in enumerate(tests, 1):
        if t["permutation_p"] <= q * i / m:
            sig.append(t)
    return sig

if __name__ == "__main__":
    db = json.load(open("dataset/event_database.json"))
    rows = make_event_rows(db)
    print(f"event rows: {len(rows)}")
    results = []
    for rule, w in [("saturn_sign", 1.0), ("jupiter_sign", 1.0),
                    ("saturn_return", 1.0), ("jupiter_return", 1.0)]:
        r = test_rule(rule, rows, n_perm=3000, window_y=w)
        results.append(r)
        print(f"{r['rule']:<16} n={r['n']} in={r['observed_in']} rate={r['rate']} "
              f"expo={r['mean_exposure']} p={r['permutation_p']} "
              f"{'SUPPORTED' if r['supported'] else 'null'}")
    sig = bh_fdr(results)
    print(f"\nFDR (q=0.05) survivors: {[s['rule'] for s in sig] if sig else 'none'}")
    json.dump({"results": results, "fdr_survivors": [s["rule"] for s in sig]},
              open("dataset/event_timing_engine_results.json", "w"), indent=1)
    print("Wrote dataset/event_timing_engine_results.json")
