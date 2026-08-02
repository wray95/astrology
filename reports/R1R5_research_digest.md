# R1–R5 / v3.0 Research Digest (2026-08-02)

*Digest of commits a3ac2bf (R1+R2) · 9e03321 (R1–R5 RETRY) · 65459a4 (v3.0 Batch OS). Compiled from commit messages + committed artifacts; numbers below are as reported by those runs.*

## Pipeline & data
- **v3.0 engine:** pyswisseph (Lahiri sidereal) + scikit-survival + lifelines + XGBoost + CatBoost; jyotishganit installed (Skyfield/JPL) — pyswisseph used for speed. Note: v3 moved off Drik-web positions to a **stable Swiss-Ephemeris Lahiri** source — consistent with the Turn-15 boundary-instability caveat (Drik day-to-day wobble for near-boundary planets).
- **Matrix growth:** 2,871 Q-series + 3,049 synthetic (7 industry CSVs) = **5,920 × 159** (v3.0) → +600 Famous Consumer Researchers (0 errors) = **6,520 × 159** (R1+R2/R1–R5).
- Ingest: `scripts/ingest_industry_csv.py` (159 features, geocoding, noon-birth fallback). Shadbala: `scripts/extract_shadbala_p_series.py` → `dataset/p_series_shadbala_av.json`.

## Survival analysis (Cox PH, n=2,871) — headline
| Feature | HR | p | Read |
|---|---|---|---|
| **Shrinkhala** | **3.88** | **<0.005** | **STRONG — 3.88× hazard of Saturn-return events; validates NEXUS** |
| Gaj-Kesari | 1.15 | 0.69 | not significant |
| Concordance | — | — | 0.63 (modest) |

Top industry-separating features: Shrinkhala_max, D10_Kendra, GajKesari.

## Industry classification (6 classes, n=5,920)
- **16.8% accuracy ≈ chance (16.7%)** — synthetic charts are astrologically well-mixed across industries; planetary features do NOT separate industries on synthetic data.

## R1–R5 RETRY additions
- +600 Consumer charts → 6,520 total.
- **Industry chi² p = 0.0005** (reported in commit message; contingency table not saved as a standalone artifact) — significant industry association with the expanded real+Consumer sample.
- **Shadbala/AV for P1–P9** computed (jyotishganit) — see below.
- **P7 Lagna = Leo confirmed** ✓ (P7 = Sineth).
- **Children-label bottleneck documented:** `children_classifier_results.json` — n_labeled=280, **n_positive=279** (one negative!) → ROC AUC = NaN; classifier not trainable until balanced labels exist. Top feature importances on the degenerate sample: Mars_varg, Saturn_H10, Saturn_deb_D1, Moon_deb_D1, Jupiter_MD, Shrinkhala_max, Shrinkhala.

## Shadbala strongest-planet summary (D1, rupas)
| Chart | Lagna | Strongest (rupas) | Total rupas |
|---|---|---|---|
| P1 Bappa | Aries | Sun 11.2 | 53.0 |
| P2 Upulakshi | Aries | Sun 10.0 | 49.3 |
| P3 Senith | Pisces | Moon 7.8 | 45.8 |
| P4 Niromi | Taurus | Sun 9.6 | 49.3 |
| P5 Senath | Virgo | Sun 9.1 | 48.3 |
| P6 Dewli | Libra | Mars 8.3 | 45.3 |
| P7 Sineth | **Leo ✓** | Sun 7.6 | 44.8 |
| P8 | Sagittarius | Jupiter 7.9 | 43.6 |
| P9 | Aries | Sun 8.8 | 47.0 |

Observations: Sun is the strongest shadbala planet in 6/9 charts (P1, P2, P4, P5, P7, P9); Jupiter strongest only in P8, Moon in P3, Mars in P6. (Day-birth cohort effect likely; not corrected for.)

## Cross-check vs earlier framework findings
- Shrinkhala survival HR=3.88 **reinforces** the bond-strength framework (jyotishvidya: 3-loop meaningful) as an *event-timing* factor — while the 111/24-chart correlation work (Turn 16) showed loop presence is NOT a level-of-achievement predictor. Together: **loops predict events, not rank**.
- Children label (279/280 positive) must be fixed before any children conclusions — current importances are on a degenerate sample.
