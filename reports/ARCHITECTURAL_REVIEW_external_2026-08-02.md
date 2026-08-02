# EXTERNAL ARCHITECTURAL REVIEW — ASTROLOGY RESEARCH OS (2026-08-02)
*Saved verbatim per standing rule (every turn saved to git). Source: user-provided external review. Author: external reviewer. See `reports/review_response_grounded.md` for the repo's grounded assessment + new evidence.*

---

**BRUTAL ARCHITECTURAL REVIEW — ASTROLOGY RESEARCH OS**

**Overall Scores:**

- Architecture: **4/10** (fragmented, repair-driven)
- Scientific Methodology: **6/10** (honest about limits, but foundational flaws)
- Software Engineering: **3/10** (monolithic scripts, no dependency graph, no versioning)
- Machine Learning: **3/10** (misframed problems, wrong metrics)
- Database Design: **2/10** (JSON/CSV files, no schema, impossible to scale)
- Scalability: **1/10** (will break at ~5K charts)
- Research Reproducibility: **7/10** (commits matter, but no provenance tracking)

**BIGGEST PROBLEMS (in order of severity)**

1. **Label Bottleneck is Fatal**
   - 111 charted records with any usable data. 0 wealth labels. 0 marriage labels. 0 career transition labels.
   - 279:1 imbalance on children.
   - All ML models trained on synthetic classification or presence/absence of yoga, not life outcomes.
   - You can't validate "Shrinkhala predicts wealth" with no wealth labels.

2. **Confusing Yoga Detection with Outcome Prediction**
   - Features are mostly yoga presence/absence (binary); targets are industry classification (synthetic labels) or 5-loop presence.
   - This is NOT predictive modeling — it's pattern frequency analysis dressed up as ML.
   - Fix: reframe as hypothesis testing (Kaplan-Meier, Cox regression).

3. **Synthetic Charts Are Statistically Useless**
   - 3,649 AI-generated charts with industry labels, zero astrological signal.
   - Circular: invented labels → correlations are artifacts.
   - Fix: delete synthetic dataset; use real Rodden AA/A data.

4. **No Causal Framework**
   - No DAG, no collider detection, no adjustment sets. Confounded by selection/survivorship/publication bias.

5. **Dasha/Transit Engine is Computationally Orphaned**
   - Vimshottari computed but never linked to events. No Person → Events → Dasha alignment layer.

**TOP 20 IMPROVEMENTS (ranked by impact)**
1. Build event-outcome dataset: 100 people × 20+ dated events (3 mo)
2. Rodden AA/A filter (2 days)
3. Switch to DuckDB + Parquet with schema versioning (1 week)
4. Cox proportional hazards for all dasha/transit claims (3 days)
5. DAG + collider analysis (1 week)
6. Event timestamps ↔ dasha/transit linkage (2 weeks)
7. Pre-registration + blind rating (5 days)
8. Replace synthetic charts with real AA/A (3 days)
9. Held-out cross-validation (2 days)
10. Auto feature interaction detection (1 week)
11. Benjamini-Hochberg FDR across all tests (3 days)
12. Sensitivity analysis: birth-time ±10m/±30m (1 week)
13. Research registry + experiment tracker (1 week)
14. SHAP + counterfactuals (5 days)
15. Bayesian hierarchical model (2 weeks)
16. Knowledge graph Person↔Chart↔Event↔Dasha↔Source (3 weeks)
17. Publish negative findings prominently (1 day, ongoing)
18. Kaplan-Meier stratified by yoga (3 days)
19. Astro-Databank XML dump + versioned snapshots (2 days)
20. Validation framework: effect sizes, CIs, I² (1 week)

**WHAT TO REDESIGN ENTIRELY:** data model (relational + versioning), feature engineering (auto-generate ~10K), ML pipeline (survival analysis), hypothesis testing (pre-register, Bayesian CIs), reproducibility (experiment registry + commit hashes).

**WHAT TO REMOVE ENTIRELY:** synthetic 3,649-chart dataset; industry classification benchmarks; ML model comparisons on imbalanced yoga presence; "Shrinkhala predicts success" framing (own data refutes: P3 = 5-loop, achievement=4).

**MISSING MODULES:** event ontology; causal discovery engine (NOTEARS/PC); survival analysis (KM, Cox, Weibull/Gompertz); experiment registry; provenance tracking; sensitivity analysis; meta-analysis engine; publication pipeline.

**TECHNOLOGIES TO ADOPT:** DuckDB/PostgreSQL; featuretools; lifelines; pcalg/py-causal; W&B or DVC; scikit-learn CV + SHAP; Quarto.

**RESEARCH ROADMAP (v5 → v10):** v6 (3 mo: real events, AA/A only, DuckDB, Cox PH) → v7 (2 mo: causal discovery, sensitivity, registry) → v8 (2 mo: 10K features, Bayesian hierarchical, knowledge graph) → v9 (1 mo: meta-analysis, publication pipeline) → v10 (1 mo: held-out validation, preprint).

**PUBLISHABLE RESEARCH? Not yet.** No outcome labels; n=111 with 0 wealth labels; synthetic data; no causal inference. Example publishable claim format given (pre-registered, Cox HR + 95% CI, jitter-robust).

**BIGGEST RISKS:** label collection fails; birth-time error dominates signal; selection bias (famous ≠ typical); publication bias; p-hacking.

**One Final Note:** the willingness to report negative findings (P3 = 5-loop, achievement=4; loop↔achievement r≈−0.02) is rare and good. That honesty is the biggest asset.
