# LAYER 1 TEST — Chart Strength Score vs Real-World Outcome (2026-08-02)
*Per external advisor's test: "Build Layer 1 (chart strength scoring). Show me Spearman ρ > 0.35 between chart scores and real-world outcomes."*

## Method (pre-specified, transparent)
Score defined BEFORE looking at outcomes (pre-registration style), from classical dignity/yoga data only:
```
strength = 0.30*bond_norm + 0.20*(exalted+own)/7 + 0.15*mahapurusha/2
         + 0.15*benefic_kendra/4 + 0.10*kendra_lords_in_dignity/4 + 0.10*(1-debilitated/7)
```
- Data: 111 charted (astrodb_loops.json + chart_houses.json) + 24-chart celeb/P-series set.
- Outcome: achievement rating (1–10) — the only outcome-like variable in the repo (proxy for prominence).
- Script: `scripts/layer1_strength_test.py` · data: `dataset/layer1_strength_test.json`.

## Results
| Dataset | n | Spearman ρ | permutation p | Bar 0.35 | Verdict |
|---|---|---|---|---|---|
| 111 famous-only charts | 111 | **0.308** | 0.028 | NOT MET | significant but below bar |
| 24 celeb + P-series | 24 | **0.608** | (see json) | PASSED | above bar, but n=24 |

## Interpretation — honest
1. **The 111-set result is range-restricted:** achievement there is compressed to 7–10 (everyone is famous). A score can't discriminate among people who are ALL at the top — ρ is attenuated. This set structurally cannot test the hypothesis.
2. **The 24-set includes non-famous people** (P-series: Senith=4, Upulakshi=5) → outcome variance exists → ρ=0.61, above the advisor's bar.
3. **Neither is decisive:**
   - n=24 is small; the outcome is a *subjective 1–10 rating*, not a dated life event.
   - The advisor's own gold-standard test remains: **predict 20 NEW people blind, before seeing their lives**. That has not been done.
   - No causality claim is possible (all observational, no adjustment set).
4. **Most informative from both runs:** the score's worst failures are high-achievers with low chart scores — Buffett (ρ-set ach=10, score 12.9), Ali (10, 11.4), DiCaprio (9, 11.4), Gandhi (10, 12.9), Disney (9, 16.6), Jackson (9, 15.7). The score systematically under-rates *creative/charismatic* fields (arts, sports) and over-rates *parivartana-heavy* business charts. A single "strength" scalar is too blunt — consistent with the advisor's point that outcome-specific modeling (survival/Cox on dated events) is the path, not a universal score.

## Verdict vs the advisor's framing
- "If it works, Layer 2–3 follow. If not, astrology signal is weaker than you think."
- **Mixed: not a clean pass, not a clean fail.** There is a small, significant, direction-correct signal (ρ≈0.31–0.61 depending on outcome variance) — the first nonzero positive association in this workspace — but it does not clear the 0.35 bar on the only adequately-varied small set (0.61 on n=24 is suggestive, not convincing).
- **The 70% claim remains unsubstantiated** — no such claim exists in this workspace's measurements (see response doc). Nothing here supports 70% accuracy; ρ=0.6 (n=24) is a weak effect by any standard.

## Next step (agreed path)
The real test needs REAL outcome variance and REAL dates: the 100-people × 20-events label dataset. Layer 1's score + the 24-chart signal can be the seed features for the survival-analysis Layer 2 once labels exist.
