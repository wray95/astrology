# GOCHARA PREDICTION ENGINE — ACTION PLAN (external, 2026-08-02)
*Saved verbatim per standing rule. Author: user (external advisor). Execution status + results tracked in reports/gochara_phase1_report.md.*

---

**SITUATION**
- Q-series: 5,287 famous people with achievement scores (0-10)
- Birth times: Only 111 people (2.1%) — most are noon births (unreliable)
- Career datasets: 151,200 records (profession, birth date)
- Goal: Predict career/wealth outcomes using gochara (transit) timing

**PHASE 1: TIMED PEOPLE ANALYSIS (This Week)**
1.1 Extract Tier-A Data (Rodden AA/A Only): filter birth_time NOT null, NOT "12:00:00", birth_city available. Expected ~80-100 timed people.
1.2 Compute D10 Strength Scores: D10_score = (10L_dignity × w) + (10L_house_quality × w) + (Sun_D10_strength × w) − (Saturn_10H_blockage × w). Create d10_strength.json.
1.3 Test Correlation: Spearman ρ between D10_score and achievement. Target ρ > 0.35, n=80-100.

**PHASE 2: GOCHARA TIMING FEATURES (Weeks 2-3)**
2.1 Transit indicators (age-based): Saturn return 1st (27-31), 2nd (56-60), Jupiter to 10th (age_mod_12 9-11), Saturn to 10th. Create gochara_features.json.
2.2 Contingency table: Jupiter 10th vs high(8-10)/low(0-3) achievement; chi-square, OR. Example OR=2.36 shown.

**PHASE 3: MARRIAGE/CHILDREN PREDICTION (Weeks 4-5)**
3.1 Wikidata P26 (spouse) + P569 (birth) + P577 (marriage) → 200-300 marriage dates. (NOTE: P577 is publication date; marriage date is a qualifier on P26 — plan's SPARQL needs correction.)
3.2 D7 strength scoring: (7L_dignity×20) + (7L_Kendra×25) + (Venus_dignity×20) − (Saturn_7H×15) − (Mars_7H×10).
3.3 Cox PH: time = marriage_date − birth_date, event = married, covariates [D7_strength, Venus_MD_active, Jupiter_7th_transit]; HR > 1.5, p < 0.05; ±30min robustness.

**PHASE 4: PUBLISHABLE RESULTS (Week 6)**
4.1 Pre-register 3 hypotheses (GitHub commit): H1 D10→achievement ρ>0.35 p<0.05 n=80; H2 Jupiter-10th OR>1.5 p<0.05; H3 D7→marriage HR>1.5 p<0.05 n=200. Pre-reg date 2026-08-02.
4.2 Test set: 70/15/15 split, test never touched during development.
4.3 Report template (abstract/methods/results/conclusion) with honest-negative framing.

**EXPECTED OUTCOMES:** signal → ρ≈0.30-0.45, OR≈1.3-2.0, HR≈1.4-2.5; no signal → ρ≈0.00-0.15, OR≈1.0-1.1, HR≈1.0-1.1 → publish negative findings.

**TOOLS:** pyswisseph, scipy numpy pandas scikit-learn lifelines, pywikibot sparqlwrapper, matplotlib seaborn.

**TIMELINE:** Now (extract timed) → +3d (D10 ρ) → +7d (gochara) → +10d (Wikidata marriages) → +14d (D7+Cox+pre-reg) → +21d (analysis) → +30d (preprint).

**REALISTIC SUCCESS METRICS:** publication-ready iff pre-registered, effect size + 95% CI, sensitivity (±30m), held-out test, confounders acknowledged, negative findings reported.

**COMPETITIVE ADVANTAGE:** 5,287 Q-series with achievement, 151,200 career records, P1-P9 hidden test set, GitHub history. "Enough to publish honest research. Not 'proving' astrology, but rigorously testing claims."
