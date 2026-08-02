#!/usr/bin/env python3
"""
FOUR-HYPOTHESIS WINDOW TEST (advisor design, pre-registered 2026-08-02)
=======================================================================
H1: event during Saturn transit of natal Saturn sign (each visit window)
H2: event during Jupiter transit of natal Jupiter sign (each visit window)
H3: event within ±1y of an exact Saturn return (1st/2nd/3rd)
H4: random control windows (same total exposure, randomized)

FAIR-EXPOSURE DESIGN (handles age clustering):
  For each event at age A: exposure_h = fraction of [0, A] inside windows_h.
  Observed rate vs mean exposure -> binomial one-sided test.
  H4 = random windows of identical total duration -> must equal exposure.

Events: first career event (career_active start / debut), n=905.
Natal-sign pool: registry (5,276) + uploads (4,397) + scholars (200) -> used
for sign-distribution sanity (uploads have no event dates).
"""
import json, sys, math, re, gzip, csv, random
from collections import Counter
sys.path.insert(0, "scripts")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
DAYS = 365.25
PIDS = {"Saturn": 6, "Jupiter": 5}

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
    jd = jd_of(y0, 1, 1); end = jd_of(y1, 12, 31); step = 4.0
    prev = None
    while jd <= end:
        s = int(lon_at(jd, pid) // 30)
        if prev is not None and s != prev:
            lo, hi = jd - step, jd
            for _ in range(20):
                mid = (lo + hi) / 2
                if int(lon_at(mid, pid) // 30) == s: hi = mid
                else: lo = mid
            entries.append((hi, s))
        prev = s; jd += step
    _ENTRIES[pid] = entries
    return entries

def sign_visits(pid, natal_idx, birth_jd, age_max=85):
    """(start, end) JD for each visit of the planet through the natal sign."""
    entries = global_entries(pid)
    visits = []
    for i, (e, s) in enumerate(entries):
        if s != natal_idx or e < birth_jd: continue
        if e > birth_jd + age_max * DAYS: break
        nxt = entries[i+1][0] if i+1 < len(entries) else e + DAYS
        visits.append((e, nxt))
    return visits

def saturn_returns(birth_jd, age_max=85):
    """Exact Saturn return JDs (natal lon crossing), 1st/2nd/3rd."""
    natal = lon_at(birth_jd, 6)
    returns = []
    entries = global_entries(6)
    for i, (e, s) in enumerate(entries):
        if e < birth_jd or e > birth_jd + age_max * DAYS: continue
        # scan this sign visit for crossing natal lon
        nxt = entries[i+1][0] if i+1 < len(entries) else e + DAYS
        lo, hi = e, nxt
        for _ in range(24):
            mid = (lo + hi) / 2
            if lon_at(mid, 6) > natal: hi = mid
            else: lo = mid
        if abs((lon_at(lo, 6) - natal + 180) % 360 - 180) < 0.6:
            returns.append(lo)
    return returns

def exposure(visits_or_windows, birth_jd, event_jd):
    """Fraction of [birth, event] inside windows."""
    if not visits_or_windows: return 0.0
    total = 0.0
    for w in visits_or_windows:
        s, e = max(w[0], birth_jd), min(w[1], event_jd)
        if s < e: total += e - s
    return total / (event_jd - birth_jd) if event_jd > birth_jd else 0.0

def binom_p(k, n, p0):
    return sum(math.comb(n, i) * (p0**i) * ((1-p0)**(n-i)) for i in range(k, n+1))

# ---------- events ----------
reg = {}
with gzip.open("data/famous_people_birth_data.csv.gz", "rt", errors="ignore") as f:
    for row in csv.DictReader(f):
        nm = (row.get("name") or "").strip(); bd = (row.get("birth_date") or "").strip()
        if nm and bd: reg[nm] = bd
qa = {}
with gzip.open("outputs/q_biographical_wikipedia/q_biographical_details.csv.gz", "rt", errors="ignore") as f:
    for row in csv.DictReader(f):
        nm = (row.get("name") or "").strip()
        ca = (row.get("career_active") or "").strip(); db = (row.get("debut") or "").strip()
        if nm and (ca or db): qa[nm] = (ca, db)
events = []
for nm, (ca, db) in qa.items():
    if nm not in reg: continue
    m2 = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", reg[nm].strip())
    if not m2: continue
    y, mo, d = int(m2.group(3)), int(m2.group(1)), int(m2.group(2))
    cm = re.match(r"^(\d{4})", ca) or re.search(r"(\d{4})", ca)
    dm = re.match(r"^([A-Za-z]+)?\s*(\d{4})", db)
    if cm and 1850 <= y <= 2010 and y <= int(cm.group(1)) <= y+85:
        events.append((nm, (y, mo, d), int(cm.group(1)), "career_active"))
    if dm and 1850 <= y <= 2010 and y <= int(dm.group(2)) <= y+85:
        events.append((nm, (y, mo, d), int(dm.group(2)), "debut"))
seen = set(); evs = []
for e in events:
    k = (e[0], e[3])
    if k not in seen: seen.add(k); evs.append(e)

# ---------- run ----------
R = {"H1_saturn_sign": {"ins": 0, "expo": 0.0, "n": 0},
     "H2_jupiter_sign": {"ins": 0, "expo": 0.0, "n": 0},
     "H3_saturn_return": {"ins": 0, "expo": 0.0, "n": 0},
     "H4_random_control": {"ins": 0, "expo": 0.0, "n": 0}}
rng = random.Random(2026)
rows = []
# precompute per-event in-window booleans for each possible natal sign (12)
SAT_WIN = [None] * 12   # list per sign: list of (birth,event,idx)->bool via matrix below
def win_matrix(make_windows, birth_jd, event_jd):
    """For each natal sign 0..11, True if event in any window for that sign."""
    return [any(s <= event_jd <= e for s, e in make_windows(i, birth_jd)) for i in range(12)]

def sat_visits(i, bj):
    return sign_visits(6, i, bj)
def jup_visits(i, bj):
    return sign_visits(5, i, bj)
def ret_windows(i, bj):
    # ±1y around returns for natal Saturn in sign i (natal lon = sign midpoint)
    entries = global_entries(6)
    out = []
    for k, (e, s) in enumerate(entries):
        if s != i or e < bj: continue
        nxt = entries[k+1][0] if k+1 < len(entries) else e + DAYS
        # approximate return = entry + 2.5y*2/3? no — use actual crossing of midpoint
        lo, hi = e, min(nxt, bj + 90*DAYS)
        natal = i*30 + 15.0
        for _ in range(20):
            mid = (lo + hi) / 2
            if lon_at(mid, 6) > natal: hi = mid
            else: lo = mid
        if abs((lon_at(lo, 6) - natal + 180) % 360 - 180) < 0.7:
            out.append((lo - DAYS, lo + DAYS))
    return out

data = []
for nm, (y, mo, d), ev_y, src in evs:
    bj = jd_of(y, mo, d); ej = jd_of(ev_y, 7, 1)
    if ej <= bj: continue
    ns = natal_sign(y, mo, d, 6); nj = natal_sign(y, mo, d, 5)
    mS = win_matrix(sat_visits, bj, ej)
    mJ = win_matrix(jup_visits, bj, ej)
    mR = win_matrix(ret_windows, bj, ej)
    # H4 random control — FIXED: sample windows over full [0, span] (may extend past ej)
    span = (ej - bj) / DAYS
    rand_wins = []
    for _ in range(5):
        a0 = rng.uniform(0, span)
        rand_wins.append((bj + a0*DAYS, bj + (a0+2.5)*DAYS))
    in_rand = any(s <= ej <= e for s, e in rand_wins)
    ex_rand = exposure(rand_wins, bj, ej)
    R["H1_saturn_sign"]["ins"] += mS[ns]; R["H1_saturn_sign"]["n"] += 1
    R["H1_saturn_sign"]["expo"] += sum(mS)/12.0
    R["H2_jupiter_sign"]["ins"] += mJ[nj]; R["H2_jupiter_sign"]["n"] += 1
    R["H2_jupiter_sign"]["expo"] += sum(mJ)/12.0
    R["H3_saturn_return"]["ins"] += mR[ns]; R["H3_saturn_return"]["n"] += 1
    R["H3_saturn_return"]["expo"] += sum(mR)/12.0
    R["H4_random_control"]["ins"] += in_rand; R["H4_random_control"]["n"] += 1
    R["H4_random_control"]["expo"] += ex_rand
    data.append({"name": nm, "birth": f"{y}-{mo:02d}-{d:02d}", "event_year": ev_y,
                 "saturn_sign": ns, "jupiter_sign": nj, "mS": mS, "mJ": mJ, "mR": mR,
                 "in_random": in_rand, "exp_random": ex_rand, "src": src})

n = R["H1_saturn_sign"]["n"]
obs = {k: R[k]["ins"] for k in R}
print(f"n events = {n}\n")
print(f"{'Hypothesis':<22}{'in':>5}{'rate':>8}{'mean_expo':>10}")

# permutation tests (age-preserving: shuffle natal signs across events)
def perm_p(matrix_key, obs_count, iters=5000):
    rng2 = random.Random(7)
    m = [d[matrix_key] for d in data]
    cnt = 0
    for _ in range(iters):
        perm = [rng2.randrange(12) for _ in range(n)]
        c = sum(1 for i in range(n) if m[i][perm[i]])
        if c >= obs_count: cnt += 1
    return cnt / iters

out = {}
for key, label, matkey in [("H1_saturn_sign","H1 Saturn in natal sign","mS"),
                            ("H2_jupiter_sign","H2 Jupiter in natal sign","mJ"),
                            ("H3_saturn_return","H3 Saturn return ±1y","mR")]:
    r = R[key]; k = r["ins"]; ex = r["expo"]/n; rate = k/n
    pp = perm_p(matkey, k)
    out[key] = {"n": n, "in": k, "rate": round(rate,4), "mean_exposure": round(ex,4),
                "permutation_p": pp}
    print(f"{label:<22}{k:>5}{rate:>8.3f}{ex:>10.3f}   permutation p = {pp:.4f}")
r4 = R["H4_random_control"]
out["H4_random_control"] = {"n": r4["n"], "in": r4["ins"], "rate": round(r4["ins"]/r4["n"],4),
                            "mean_exposure": round(r4["expo"]/r4["n"],4)}
print(f"{'H4 random control':<22}{r4['ins']:>5}{r4['ins']/r4['n']:>8.3f}{r4['expo']/r4['n']:>10.3f}   (sanity: rate ≈ exposure)")
print("\n-> hypothesis supported iff permutation p < 0.05 AND rate > mean_exposure AND beats H4.")

# ---------- natal-sign distribution: ALL birthdays (registry + uploads + scholars) ----------
pool = Counter()
def add_reg(dt, src):
    for nm, bd in dt.items():
        m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", bd.strip())
        if m:
            y = int(m.group(3))
            if 1850 <= y <= 2010:
                pool[(SIGNS[natal_sign(y, int(m.group(1)), int(m.group(2)), 6)],
                      SIGNS[natal_sign(y, int(m.group(1)), int(m.group(2)), 5)])] += 1
add_reg(reg, "registry")
import glob
for f in glob.glob("/home/user/uploads/*.csv"):
    with open(f, errors="ignore") as fh:
        rd = csv.DictReader(fh)
        col = "Full Name" if "Full Name" in (rd.fieldnames or []) else "Name"
        bcol = "Birth Date (YYYY-MM-DD)" if "Birth Date (YYYY-MM-DD)" in (rd.fieldnames or []) else ("BirthDate" if "BirthDate" in (rd.fieldnames or []) else None)
        if not bcol: continue
        for row in rd:
            bd = (row.get(bcol) or "").strip()
            m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", bd)
            if m:
                y = int(m.group(1))
                if 1850 <= y <= 2010:
                    pool[(SIGNS[natal_sign(y, int(m.group(2)), int(m.group(3)), 6)],
                          SIGNS[natal_sign(y, int(m.group(2)), int(m.group(3)), 5)])] += 1
for f in ["data/eminent_scholars_1900_onward.csv"]:
    try:
        with open(f, errors="ignore") as fh:
            rd = csv.DictReader(fh)
            for row in rd:
                bd = (row.get("BirthDate") or "").strip()
                m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", bd)
                if m:
                    y = int(m.group(1))
                    if 1850 <= y <= 2010:
                        pool[(SIGNS[natal_sign(y, int(m.group(2)), int(m.group(3)), 6)],
                              SIGNS[natal_sign(y, int(m.group(2)), int(m.group(3)), 5)])] += 1
    except Exception: pass
sat_dist = Counter(); jup_dist = Counter()
for (s, j), c in pool.items():
    sat_dist[s] += c; jup_dist[j] += c
print(f"\nNatal-sign pool (registry+uploads+scholars): {sum(pool.values())} people")
print("Saturn sign dist:", dict(sat_dist))
print("Jupiter sign dist:", dict(jup_dist))
import statistics
sv = list(sat_dist.values()); jv = list(jup_dist.values())
print(f"Saturn uniformity: max/min = {max(sv)/min(sv):.2f} | Jupiter max/min = {max(jv)/min(jv):.2f}")

json.dump({"hypotheses": out, "n_events": n,
           "rows": [{k: v for k, v in r.items() if k not in ("mS","mJ","mR")} for r in data],
           "natal_pool": {"n": sum(pool.values()), "saturn": dict(sat_dist), "jupiter": dict(jup_dist)}},
          open("dataset/four_hypothesis_window_test.json", "w"), indent=1)
print("\nWrote dataset/four_hypothesis_window_test.json")
