# BLIND VALIDATION — P1–P9 Predictions (2026-08-02)

**Protocol:** birth data only (`data/blind_validation_people.json`, no outcomes) → generic classical engine (`scripts/blind_validation_engine.py`, Swiss Ephemeris Lahiri, locked divisional convention, Vimshottari from Moon nakshatra) → predictions below. **The engine contains zero knowledge of any person's actual life.** Scoring is done by the user (who holds the outcomes) — results file `dataset/blind_validation_predictions.json`.

## Predictions (engine output — nothing hidden)

| ID | Name | MarScore | p(married by 30) | Marriage window* | ChildScore | p(children by 30) | Children window* |
|---|---|---|---|---|---|---|---|
| P1 | Polgahawela Bappa | 25 | 0.28 | 2030-03 → 2050-03 | 35 | 0.37 | (far) 2091-03 → 2107-03 |
| P2 | Upulakshi | 0 | 0.05 | 2033-02 → 2049-02 | 30 | 0.32 | 2033-02 → 2049-02 |
| P3 | Senith | 65 | 0.64 | (far) 2118-05 → 2138-05 | 15 | 0.19 | 2059-05 → 2075-05 |
| P4 | Niromi | 0 | 0.05 | (far) 2088-01 → 2104-01 | 50 | 0.50 | (far) 2088-01 → 2104-01 |
| P5 | Senath | 15 | 0.19 | (far) 2088-07 → 2108-07 | 45 | 0.46 | 2032-04 → 2045-07 |
| P6 | Dewli | 5 | 0.10 | (far) 2090-07 → 2106-07 | 20 | 0.23 | (far) 2090-07 → 2106-07 |
| P7 | Sineth | 0 | 0.05 | (far) 2081-07 → 2101-08 | 35 | 0.37 | 2031-03 → 2038-08 |
| P8 | Lakshi Amma | 30 | 0.32 | (far) 2074-01 → 2090-01 | 15 | 0.19 | (far) 2074-01 → 2090-01 |
| P9 | Lalith Uncle | 30 | 0.32 | (far) 2091-06 → 2111-06 | 35 | 0.37 | 2032-06 → 2048-06 |

\* Windows are karaka-MD ∩ Jupiter-transit. **Far-future windows (>2050) are the next recurrence of the karaka MD — score these as "no near-term window", not as real predictions.** Near-term-relevant windows: P1 marriage 2030–2050, P2 marriage+children 2033–2049, P5 children 2032–2045, P7 children 2031–2038, P9 children 2032–2048.

## Diagnostic components (per person, from JSON)
Each person's record lists: marriage reasons (D7 7L kendra/dignity, karaka D7 dignity/kendra, Saturn penalties), children reasons (D5 5L trikona/dignity, Jupiter D5 house/dignity, Saturn penalties), karaka MD windows, Jupiter transit entry months, confidence (0.5–0.65 range — low by design: birth times unverified, transits ±1–2 months).

## SCORING TEMPLATE — fill in Actual/Hit yourself (do not share outcomes into the repo)
```
BLIND VALIDATION RESULTS
Person | Domain | Prediction (score/p30/window)        | Actual | Hit? | Notes
P1     | Marriage | 25 / 0.28 / 2030-03→2050-03      | [you]  | [Y/N] |
P2     | Marriage | 0 / 0.05 / 2033-02→2049-02        | [you]  | [Y/N] |
P3     | Marriage | 65 / 0.64 / (none near-term)      | [you]  | [Y/N] |
P4     | Marriage | 0 / 0.05 / (none near-term)       | [you]  | [Y/N] |
P5     | Marriage | 15 / 0.19 / (none near-term)      | [you]  | [Y/N] |
P6     | Marriage | 5 / 0.10 / (none near-term)       | [you]  | [Y/N] |
P7     | Marriage | 0 / 0.05 / (none near-term)       | [you]  | [Y/N] |
P8     | Marriage | 30 / 0.32 / (none near-term)      | [you]  | [Y/N] |
P9     | Marriage | 30 / 0.32 / (none near-term)      | [you]  | [Y/N] |
P1     | Children | 35 / 0.37 / (none near-term)      | [you]  | [Y/N] |
P2     | Children | 30 / 0.32 / 2033-02→2049-02       | [you]  | [Y/N] |
P3     | Children | 15 / 0.19 / 2059-05→2075-05       | [you]  | [Y/N] |
P4     | Children | 50 / 0.50 / (none near-term)      | [you]  | [Y/N] |
P5     | Children | 45 / 0.46 / 2032-04→2045-07       | [you]  | [Y/N] |
P6     | Children | 20 / 0.23 / (none near-term)      | [you]  | [Y/N] |
P7     | Children | 35 / 0.37 / 2031-03→2038-08       | [you]  | [Y/N] |
P8     | Children | 15 / 0.19 / (none near-term)      | [you]  | [Y/N] |
P9     | Children | 35 / 0.37 / 2032-06→2048-06       | [you]  | [Y/N] |

SUMMARY (fill in): Marriages correct: __/9 · Children correct: __/9 · Strongest signal: __ · Weakest signal: __
```

## Engine transparency
- Weights: D7 7L kendra +20, D7 7L dignified +15, karaka D7 dignified +15, karaka D7 kendra +15, Saturn 7H/1H −10 each; children analogous (5L trikona +20, 5L dignified +15, Jupiter D5 dignified +15, Jupiter D5 in 4/5 +15, Saturn 5H −10).
- p(by30) = clamp(score/100 × 0.9 + 0.05). Heuristic, not calibrated — do NOT treat as a true probability.
- Confidence 0.5–0.65 = LOW: birth times are user-supplied/unverified; Vimshottari sensitive to Moon degree; transits ±1–2 months.
- Gender used for karaka (Venus M / Jupiter F, repo standing rule). Verify P6/P7 gender.
- Divisional convention: locked multiplication (= BPHS), via `scripts/varga_conventions.py`.
- Known caveat: P5 birth coordinates = Colombo (engine PD); the Drik-link Houston proxy differs (see divisional_convention_validation.md) — D9-based reasoning for P5 may shift under the other coordinates.
