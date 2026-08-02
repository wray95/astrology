# GOCHARA ENGINE — Phase 1/2 Execution Report (2026-08-02)

*Executed per the external action plan (saved verbatim: GOCHARA_ENGINE_PLAN_external_2026-08-02.md). Pre-registration: PRE_REGISTRATION_gochara.md (commit 2026-08-02).*

## Reality checks on the plan's assumptions (before results)
| Plan assumption | Repo reality |
|---|---|
| "Rodden AA/A only → ~80-100 timed people" | **0 AA/A** among the 111 timed (107 UNKNOWN, 4 B). The AA/A core of the whole workspace = 14 charts (celebs). All tests below therefore use the 111 exact-time charts with rodden=UNKNOWN — stated honestly, not hidden. |
| "5,287 Q-series with achievement" | 5,287 collected (5,176 date-only, no time → NOT chartable under standing rules); 111 exact-time are the testable core. |
| Wikidata P26+P577 for marriage dates | **Blocked** (query timeout from sandbox; consistent with Turn 15/17). Also plan's SPARQL used P577 (publication date); marriage date is pq:P580 qualifier on P26 statements. Phase 3 blocked until run outside sandbox. |

## Phase 1 — D10 strength vs achievement (H1)
- `scripts/d10_strength_test.py` → `dataset/d10_strength.json` (n=111, pre-specified weights).
- **Spearman ρ = 0.287 (permutation p = 0.023)** — statistically nonzero, **below the plan's 0.35 bar → NOT MET**.
- Sanity: top scores FDR/ Buffet/Angelina (75-85), bottom Messi/Ali/Pele/Serena/Dwayne Johnson (0) — the score dislikes sports/charismatic fields, same failure mode as Layer-1 strength (arts/sports under-rated).
- Outcome range 4-10, most 8-10 → attenuated ρ; honest ceiling on what n=111 famous can show.

## Phase 2 — Gochara timing features (H2)
- `scripts/gochara_features_test.py` → `dataset/gochara_features.json`.
- **Saturn returns verify classically:** 1st return mean 29.1 y (range 28.3-29.8, n=111) ✓ · 2nd return mean 58.5 y ✓ — the transit engine is correct.
- **Jupiter-10th (ages 20-35) is near-universal** (107/111 high-achievers had ≥1 visit; Jupiter transits every sign ~2.5y every 12y) → feature has almost no variance → chi² p=1.0, OR meaningless (23.9 with corrected near-zero cells). **The plan's example OR=2.36 is not reproducible with this feature definition.** A tighter feature (e.g., Jupiter-10th *within 2 years before career milestone*) might discriminate, but needs event dates we don't have.
- Median-split version: same degeneracy (p=1.0).

## Phase 3 — blocked (environment)
- Wikidata timeouts → no marriage-date collection possible from this sandbox. Query corrected to pq:P580 qualifier form; needs to run from user's machine.

## Phase 4 — done
- `PRE_REGISTRATION_gochara.md` registered (3 hypotheses, thresholds, data-management commitments) before full analysis.

## Bottom line (honest)
- D10 strength shows a **weak, significant, direction-correct correlation** (ρ=0.29) — consistent with the Layer-1 result (ρ=0.31 famous-only / 0.61 with non-famous). Below the plan's bar; not a publishable claim alone.
- Gochara Jupiter-10th as defined has **no discriminative power** (near-universal) — needs event-timed features (the plan's own Phase-3 event data), not age proxies.
- The engine (transits, Saturn returns) is verified correct; the data (outcome variance, labels, rodden) remains the binding constraint — exactly the review's #1 finding.
- Next feasible step from here: combine D10 + Layer-1 + loop features into one pre-registered multi-feature test once outcome-labeled data (P-series hidden set or new labels) exists.
