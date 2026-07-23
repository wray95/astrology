#!/usr/bin/env python3
"""
RERANK THE 4 charts using the RESEARCH DATA MATRIX TABLE
(detailed_rerank.md / all_four_reanalysis.md §12 — link-only, jyotishvidya
Srinkhala bond method; does NOT alter the 5-loop theory, loop detection,
bond logic, or Drik fetch/parse).

The matrix is qualitative (HIGH / MOD / STRONG / WEAK / ...). This script maps
each cell to a transparent 0-5 score, sums the user-requested dimensions, and
emits a ranked table + the alternate-axis ranks that live inside the same
matrix (Srinkhala bond, education, foreign, astrology aptitude, D9 dignity).

Output: rerank_matrix_scored.md
"""
OUT = "/home/user/astrology/rerank_matrix_scored.md"

# ---- numeric map for "magnitude" dimensions (0-5, higher = better) ----
MAG = {
    "STRONGEST": 5.0, "WEALTHIEST": 5.0, "HIGH": 4.0, "STRONG": 4.0,
    "MOD-HIGH": 3.5, "MODERATE": 3.0, "MOD": 3.0, "LOW-MOD": 2.0,
    "LIMITED": 1.5, "LOW": 1.5, "WEAK": 1.0, "MINIMAL": 1.0, "WEAKEST": 0.5,
}
def mag(s):
    s = (s or "").strip().upper()
    if s in MAG: return MAG[s]
    # fallback: take the strongest token present
    for k, v in MAG.items():
        if k in s: return v
    return 3.0

PERSONS = ["P1", "P2", "P3", "P4"]
PNAME = {
    "P1": "P1 · Polgahawela Bappa (1962 ♂ Aries)",
    "P2": "P2 · Upulakshi (1997 ♀ Aries)",
    "P3": "P3 · Senith (1995 ♂ Pisces)",
    "P4": "P4 · Niromi (1967 ♀ Taurus☆)",
}

# ---- the RESEARCH DATA MATRIX TABLE (qualitative cells, from detailed_rerank.md) ----
# user-requested composite dimensions:
MATRIX = {
    "Career":                         {"P1":"HIGH",      "P2":"MOD",        "P3":"LOW-MOD",   "P4":"HIGH"},
    "Finance (net worth)":           {"P1":"Wealthy",   "P2":"Moderate",   "P3":"Limited",   "P4":"Wealthiest"},
    "Money (liquid income)":         {"P1":"Strong",    "P2":"Moderate",   "P3":"Weak",      "P4":"Strong"},
    "Fame (public recognition)":     {"P1":"MOD-HIGH",  "P2":"LOW-MOD",    "P3":"LOW",       "P4":"MOD-HIGH"},
    "Success (overall)":             {"P1":"HIGH",      "P2":"Moderate",   "P3":"LOW-MOD",   "P4":"HIGH"},
    "Education":                     {"P1":"MOD",       "P2":"MOD",        "P3":"HIGH",      "P4":"MOD-HIGH"},
    "Highest position (CEO/Founder)":{"P1":"CEO",       "P2":"MNC employee","P3":"Researcher","P4":"CEO"},
    "Assets (every kind)":          {"P1":"STRONG",    "P2":"Moderate",   "P3":"Minimal",   "P4":"STRONGEST"},
    "Where wealth comes from":       {"P1":"Strong",    "P2":"Moderate",   "P3":"Weak",      "P4":"Strong (diversified)"},
}

# alternate axes that also live in the matrix
FOREIGN =    {"P1":"MOD (assets)","P2":"STRONG (job/MNC)","P3":"WEAK job/MOD study","P4":"STRONG (settlement)"}
SUDDEN  =    {"P1":"STRONG","P2":"Moderate","P3":"Weak","P4":"STRONG"}
MARRIAGE=    {"P1":"STRONG","P2":"Moderate","P3":"Weak","P4":"STRONGEST"}
ASTRO   =    {"P1":"Weak-MOD","P2":"Weak","P3":"STRONGEST","P4":"Moderate"}
# Srinkhala bond rank (jyotishvidya): 1=best .. 4=none
BOND_RANK = {"P2":1,"P1":2,"P3":3,"P4":4}     # P2 tripled/D9-confirmed, P4 none
D9_RANK   = {"P4":1,"P1":2,"P3":3,"P2":4}     # D9 dignity: P4 strongest

# position scoring
POS = {"CEO":5.0,"MNC employee":2.0,"Researcher":1.0}

def score_dim(dim):
    return {p: (POS[MATRIX[dim][p]] if dim.startswith("Highest") else mag(MATRIX[dim][p])) for p in PERSONS}

# composite over the 9 user dimensions
composite = {p: 0.0 for p in PERSONS}
lines = []
lines.append("| Dimension | P1 | P2 | P3 | P4 |")
lines.append("|---|---|---|---|---|")
scores_by_dim = {}
for dim in MATRIX:
    sc = score_dim(dim)
    scores_by_dim[dim] = sc
    for p in PERSONS: composite[p] += sc[p]
    cells = " | ".join(f"{MATRIX[dim][p]} ({sc[p]:.1f})" for p in PERSONS)
    lines.append(f"| {dim} | {cells} |")

ranked = sorted(PERSONS, key=lambda p: -composite[p])
order = " > ".join(f"{p} ({composite[p]:.1f})" for p in ranked)

# alternate-axis ranks
def axis_rank(table):
    # magnitude: higher score = better
    sc = {p: mag(table[p]) for p in PERSONS}
    return [p for p in sorted(PERSONS, key=lambda p: -sc[p])], sc

forx, fx = axis_rank(FOREIGN)
sudx, sx = axis_rank(SUDDEN)
marx, mx = axis_rank(MARRIAGE)
astx, ax = axis_rank(ASTRO)
edux, ex = axis_rank(MATRIX["Education"])
# bond & d9 are inverted (1=best)
bond_ordered = [p for p in sorted(PERSONS, key=lambda p: BOND_RANK[p])]
d9_ordered   = [p for p in sorted(PERSONS, key=lambda p: D9_RANK[p])]

md = []
md.append("# Re-Rank of the 4 Charts — using the Research Data Matrix Table\n")
md.append("**Method:** the qualitative 23-dimension research matrix (detailed_rerank.md / "
          "all_four_reanalysis.md §12) is scored on a transparent 0–5 scale (HIGH/STRONG=4, "
          "MOD=3, LOW-MOD=2, WEAK=1, STRONGEST/WEALTHIEST=5). The 9 user-requested dimensions "
          "are summed into a **composite**; the other matrix dimensions are reported as separate "
          "axes. Link-only; jyotishvidya Śrṅkhalā bond ranking applied (P2 > P1 > P3 > P4). "
          "No change to the 5-loop theory, loop detection, or bond logic.\n")
md.append("\n## 1. Scored research-data matrix (composite dimensions)\n")
md.append("\n".join(lines))
md.append(f"\n\n**Composite (sum of 9 dimensions):**\n")
for p in ranked:
    md.append(f"- **{PNAME[p]}** — {composite[p]:.1f}")
md.append(f"\n**>>> COMPOSITE RE-RANK: {order}**\n")
md.append("\n## 2. Tiers (composite)\n")
md.append("- **TIER 1 — P4 Niromi ≈ P1 Polgahawela Bappa:** wealthy/wealthiest self-made founders; "
          "strong career, sudden gains, marriage-wealth. P4 edges on foreign *settlement* + "
          "inheritance + most diversified assets; P1 edges on business scale + property windfalls.\n"
          "- **TIER 2 — P2 Upulakshi:** moderate wealth, strongest foreign *job/MNC* (10th–12th "
          "Parivartana) and NRY comeback in Jupiter MD 2032.9+.\n"
          "- **TIER 3 — P3 Senith:** limited wealth; weakest on career/foreign-job/marriage/sudden "
          "gains; lone bright spots = strongest education + astrology aptitude + foreign-study window "
          "(Moon/Jupiter 2027–28). His 5-loop is negligible per jyotishvidya (score 25, ignored).\n")
md.append("\n## 3. Alternate axes from the same matrix\n")
md.append("| Axis | Rank (best → worst) |")
md.append("|---|---|")
md.append(f"| Composite (career+finance+money+fame+success+education+CEO+assets+where-wealth) | {' > '.join(ranked)} |")
md.append(f"| Śrṅkhalā bond-strength (jyotishvidya) | {' > '.join(bond_ordered)} |")
md.append(f"| D9 dignity / strength | {' > '.join(d9_ordered)} |")
md.append(f"| Education | {' > '.join(edux)} |")
md.append(f"| Foreign (job/settlement) | {' > '.join(forx)} |")
md.append(f"| Astrology aptitude | {' > '.join(astx)} |")
md.append(f"| Sudden gains | {' > '.join(sudx)} |")
md.append(f"| Marriage-wealth | {' > '.join(marx)} |")
md.append("\n*Note:* the axes measure different things — e.g. P3 tops the **education/astrology** "
          "and (via its latent 5-loop) the **exchange-network** axis, yet ranks last on realized "
          "wealth; P4 tops **D9 dignity** and **composite**, but has no exchange yoga. The composite "
          "above reflects *realized* status (the user's requested dimensions).\n")

open(OUT, "w").write("\n".join(md))
print("Wrote", OUT)
print("COMPOSITE RE-RANK:", order)
print("Bond:", " > ".join(bond_ordered), "| D9:", " > ".join(d9_ordered),
      "| Edu:", " > ".join(astx), "| Foreign:", " > ".join(forx))
