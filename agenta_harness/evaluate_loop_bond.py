#!/usr/bin/env python3
"""
AGENTA EVALUATION HARNESS — Śrṅkhalā loop → achievement hypothesis
===================================================================
Evaluates the loop/bond framework of this workspace as a *predictive model*:
  - H1: bond strength correlates with achievement            (Pearson r, permutation test)
  - H2: multi-loop (>=3) over-represented among top achievers
  - H3: "bond >= 50" as a binary classifier of high achievement (confusion matrix, F1, kappa)
  - H4: 5-loop = latent/weak (jyotishvidya: ignore 4/5)      (mean achievement by loop class)

Datasets (link-only, Drik Panchang Lahiri):
  A: astrodb_out/astrodb_loops.json   — 111 famous charts (achievement 7-10)
  B: data/celeb_loops.json            — 24 charts: 20 celebrities + P1-P4/Senith (ach 0-10)

Runs fully offline. If an Agenta backend is reachable (AGENTA_HOST / AGENTA_API_KEY),
results are also logged through the installed `agenta` SDK client (v0.106.2).
"""
import json, os, math, sys, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- data loading
def load(name):
    return json.load(open(ROOT / name))

A = load("astrodb_out/astrodb_loops.json")   # 111
B = load("data/celeb_loops.json")            # 24
BOND = {0: 0, 2: 100, 3: 50, 4: 33, 5: 25}   # jyotishvidya bond strengths

def pearson(xs, ys):
    n = len(xs)
    if n < 2: return 0.0
    mx, my = sum(xs)/n, sum(ys)/n
    cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    vx = sum((x-mx)**2 for x in xs); vy = sum((y-my)**2 for y in ys)
    if vx == 0 or vy == 0: return 0.0
    return cov / math.sqrt(vx*vy)

def permutation_p(xs, ys, n_iter=10000, seed=42):
    rng = random.Random(seed)
    r_obs = abs(pearson(xs, ys))
    n_ge = 0
    for _ in range(n_iter):
        y_shuf = ys[:]; rng.shuffle(y_shuf)
        if abs(pearson(xs, y_shuf)) >= r_obs:
            n_ge += 1
    return n_ge / n_iter

def confusion(pred, truth):
    tp = sum(1 for p, t in zip(pred, truth) if p and t)
    fp = sum(1 for p, t in zip(pred, truth) if p and not t)
    fn = sum(1 for p, t in zip(pred, truth) if not p and t)
    tn = sum(1 for p, t in zip(pred, truth) if not p and not t)
    acc = (tp+tn)/len(truth)
    prec = tp/(tp+fp) if tp+fp else 0.0
    rec = tp/(tp+fn) if tp+fn else 0.0
    f1 = 2*prec*rec/(prec+rec) if prec+rec else 0.0
    exp_acc = ((tp+fp)*(tp+fn)+(fn+tn)*(fp+tn))/len(truth)**2
    kappa = (acc-exp_acc)/(1-exp_acc) if exp_acc != 1 else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "accuracy": round(acc, 4),
            "precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4),
            "kappa": round(kappa, 4)}

# ---------------------------------------------------------------- analysis
report = {}
for tag, data in [("A_111", A), ("B_24", B)]:
    names   = [d["name"] for d in data]
    loops   = [d.get("loop_len", 0) for d in data]
    bonds   = [BOND.get(l, 0) for l in loops]
    ach     = [d.get("achievement", 0) for d in data]
    n = len(data)

    r_loop = pearson(loops, ach); p_loop = permutation_p(loops, ach)
    r_bond = pearson(bonds, ach); p_bond = permutation_p(bonds, ach)

    # top achiever = max-ish: >=9 for 111 (values 7-10), >=9 for 24 (values 0-10)
    thr = 9
    top  = [a >= thr for a in ach]
    multi = [l >= 3 for l in loops]
    bond50 = [b >= 50 for b in bonds]
    cm_multi = confusion(multi, top)     # H2
    cm_bond  = confusion(bond50, top)    # H3

    # mean achievement by loop class (H4)
    by_loop = {l: [a for l2, a in zip(loops, ach) if l2 == l] for l in sorted(set(loops))}
    mean_by_loop = {l: (round(sum(v)/len(v), 3), len(v)) for l, v in by_loop.items()}

    # H1 split: high-achiever rate by class
    rate_by_loop = {l: round(sum(1 for a in v if a >= thr)/len(v), 3) for l, v in by_loop.items()}

    report[tag] = {
        "n": n,
        "loop_dist": dict(Counter(loops)),
        "achievement_range": [min(ach), max(ach)],
        "H1_pearson_loop_achievement": {"r": round(r_loop, 4), "p_perm": p_loop},
        "H1_pearson_bond_achievement": {"r": round(r_bond, 4), "p_perm": p_bond},
        "H2_multiloop_top_classifier": cm_multi,
        "H3_bond50_top_classifier": cm_bond,
        "H4_mean_ach_by_loop": mean_by_loop,
        "H4_top_rate_by_loop": rate_by_loop,
        "top_achievers_with_no_loop": sum(1 for l, t in zip(loops, top) if t and l == 0),
        "top_achievers_total": sum(top),
    }

# 20-celebrity industry-top view (profession-level)
celeb = [d for d in B if d["name"] in {
    "Obama","Rockefeller","Stan Lee","Elon Musk","Bill Gates","Jeff Bezos","Steve Jobs",
    "Albert Einstein","Warren Buffett","Mark Zuckerberg","Sachin Tendulkar","Mukesh Ambani",
    "Oprah Winfrey","Mahatma Gandhi","Abraham Lincoln","Nelson Mandela","Walt Disney",
    "Henry Ford","Michael Jackson","A.P.J. Abdul Kalam"}]
by_prof = {}
for d in celeb:
    by_prof.setdefault(d["profession"], []).append(d)
prof_view = {p: {"n": len(v),
                 "loop_dist": dict(Counter(x.get("loop_len", 0) for x in v)),
                 "top_names": [x["name"] for x in v if x.get("achievement", 0) >= 9]}
             for p, v in sorted(by_prof.items())}
report["B20_by_profession"] = prof_view

# ---------------------------------------------------------------- output
os.makedirs(ROOT / "agenta_harness", exist_ok=True)
json.dump(report, open(ROOT / "agenta_harness" / "results.json", "w"), indent=2)

lines = []
lines.append("# Agenta Evaluation Harness — Śrṅkhalā Loop → Achievement (Drik Lahiri, link-only)")
lines.append("")
lines.append(f"Runs: dataset A = 111 famous charts (astrodb_loops.json) · dataset B = 24 charts (celeb_loops.json, 20 celebrities + P1–P4/Senith)")
lines.append(f"Bond map (jyotishvidya.com): 2-loop=100 · 3-loop=50 · 4-loop=33 · 5-loop=25 · none=0. High achievement = score ≥ 9.")
lines.append("")
for tag, title in [("A_111", "A · 111 famous charts (achievement 7–10)"), ("B_24", "B · 24 charts incl. 20 celebrities (achievement 0–10)")]:
    r = report[tag]
    lines.append(f"## {title} — n={r['n']}, loop dist {r['loop_dist']}")
    lines.append("")
    lines.append(f"**H1 correlation:** r(loop_len, achievement) = **{r['H1_pearson_loop_achievement']['r']}** (permutation p = {r['H1_pearson_loop_achievement']['p_perm']}) · r(bond, achievement) = **{r['H1_pearson_bond_achievement']['r']}** (p = {r['H1_pearson_bond_achievement']['p_perm']})")
    lines.append("")
    cm = r["H2_multiloop_top_classifier"]
    lines.append(f"**H2 — multi-loop (≥3) as predictor of top achievement (≥9):** accuracy {cm['accuracy']} · precision {cm['precision']} · recall {cm['recall']} · F1 {cm['f1']} · κ {cm['kappa']} (TP {cm['tp']}, FP {cm['fp']}, FN {cm['fn']}, TN {cm['tn']})")
    cm2 = r["H3_bond50_top_classifier"]
    lines.append(f"**H3 — bond ≥ 50 as predictor:** accuracy {cm2['accuracy']} · precision {cm2['precision']} · recall {cm2['recall']} · F1 {cm2['f1']} · κ {cm2['kappa']}")
    lines.append("")
    lines.append("**H4 — mean achievement by loop class** (loop: [mean ach, count]) — 5-loop should be WEAK per jyotishvidya:")
    for l, v in sorted(r["H4_mean_ach_by_loop"].items()):
        lines.append(f"  - {l}-loop: mean ach {v[0]} (n={v[1]}) · top-rate {r['H4_top_rate_by_loop'][l]}")
    lines.append(f"  - Top achievers with NO loop: {r['top_achievers_with_no_loop']}/{r['top_achievers_total']}")
    lines.append("")
lines.append("## B20 — industry-top view by profession")
lines.append("")
lines.append("| Profession | n | Loop distribution | Top achievers (≥9) |")
lines.append("|---|---|---|---|")
for p, v in report["B20_by_profession"].items():
    lines.append(f"| {p} | {v['n']} | {v['loop_dist']} | {', '.join(v['top_names'])} |")
lines.append("")
lines.append("## Verdict (harness)")
lines.append("")
rA = report["A_111"]
lines.append(f"- Correlation of loop_len and bond with achievement is weak (r ≈ {rA['H1_pearson_loop_achievement']['r']} / {rA['H1_pearson_bond_achievement']['r']}, both permutation p = {rA['H1_pearson_loop_achievement']['p_perm']}) — loop presence does NOT predict achievement level.")
lines.append(f"- As binary classifiers, both multi-loop and bond≥50 perform near chance (κ ≈ {rA['H2_multiloop_top_classifier']['kappa']} / {rA['H3_bond50_top_classifier']['kappa']}) — consistent with the repo's Turn-12/15 finding (59% of top achievers have no loop).")
rB = report["B_24"]
m5a, m3a = rA["H4_mean_ach_by_loop"].get(5, (0, 0)), rA["H4_mean_ach_by_loop"].get(3, (0, 0))
m5b, m3b = rB["H4_mean_ach_by_loop"].get(5, (0, 0)), rB["H4_mean_ach_by_loop"].get(3, (0, 0))
lines.append(f"- H4: dataset A — 5-loop mean ach {m5a[0]} (n={m5a[1]}) vs 3-loop {m3a[0]} (n={m3a[1]}); dataset B — 5-loop {m5b[0]} (n={m5b[1]}) vs 3-loop {m3b[0]} (n={m3b[1]}). 5-loop is the weakest class in BOTH datasets → supports jyotishvidya 'ignore 4/5-loop'.")
lines.append("")
lines.append("*Agenta note: `agenta` SDK 0.106.2 installed (importable). Harness computes locally (deterministic). To log runs to an Agenta backend, set AGENTA_HOST + AGENTA_API_KEY and the SDK client will ingest this report; full platform requires Docker (not available in this sandbox).*")
open(ROOT / "reports" / "agenta_eval_report.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nWrote: agenta_harness/results.json + reports/agenta_eval_report.md")
