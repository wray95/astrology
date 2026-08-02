# PRE-REGISTRATION — Gochara Timing in Q-Series (2026-08-02)

*Registered BEFORE outcome analysis per Phase 4.1 of the gochara plan.
Commit hash of this file: see git log (registered 2026-08-02).*

## Hypothesis 1 — D10 strength → career achievement
- Sample: n=111 timed Q-series charts (all exact-time in dataset; note: **0 of 111 are Rodden AA/A** — 107 UNKNOWN, 4 B; the plan's "AA/A only → 80-100" expectation does not hold in this dataset).
- Predictor: D10 strength score (pre-specified weights, scripts/d10_strength_test.py).
- Outcome: achievement 0-10 (as recorded in dataset).
- Test: Spearman ρ. Threshold: ρ > 0.35, p < 0.05.
- Honest caveat registered: outcome range is 4-10 with most at 8-10 (famous-only) → ρ attenuated.

## Hypothesis 2 — Jupiter transit to 10th overrepresents high achievers
- Sample: n=111, split by Jupiter-10th transit (any visit ages 20-35).
- Test: chi-square (Haldane-Anscombe corrected), OR > 1.5, p < 0.05.
- Post-hoc finding to be registered: feature near-universal in 15-yr window (low variance) — power will be minimal.

## Hypothesis 3 — D7 strength → marriage timing (Cox PH)
- Sample: n≥200 married people with marriage dates (Wikidata, pending availability).
- Test: Cox PH, time = marriage_age, event = married, covariates [D7_strength, Venus_MD_active, Jupiter_7th_transit].
- Threshold: HR > 1.5, p < 0.05. Robustness: ±30 min birth-time jitter.
- Status: **BLOCKED on marriage-date collection** (Wikidata rate-limited from this sandbox; see gochara_phase1_report.md).

## Data-management commitments
- 70/15/15 train/validation/test split before modeling; test set never touched during development.
- Effect sizes + 95% CI reported; confounders (era, gender, profession, culture) acknowledged.
- Negative findings published (repo precedent: null loop-achievement, FDR-corrected nulls).
