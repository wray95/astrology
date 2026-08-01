# Unified Q-Series Date-Only Discovery

Applied all currently valid date-only Gochara features to the Q candidate event/control sample.

## Features tested

For Saturn, Mars, Venus, Jupiter, Rahu and Ketu:

- Transit in same sign as natal planet
- Transit within 3° of natal degree
- Retrograde/direct status

Also retained in the Q workspace:

- Saturn pre-ingress, natal-sign and exact-return windows
- Three-year lead/core/lag windows
- Annual sign ingresses and retrograde-day counts
- Jupiter/Venus/Rahu/Ketu baseline features

## Discovery sample

- Candidate events: 161
- Preliminary controls: 450
- Features tested: 18

## Largest exploratory ratios

| Feature | Event rate | Control rate | Continuity-corrected RR | Fisher p |
|---|---:|---:|---:|---:|
| Saturn within 3° | 2.5% | 0.9% | 2.78 | 0.217 |
| Mars retrograde | 11.8% | 7.8% | 1.53 | 0.145 |
| Mars same natal sign | 9.3% | 6.2% | 1.51 | 0.209 |
| Saturn same natal sign | 11.8% | 9.3% | 1.28 | 0.362 |
| Jupiter same natal sign | 9.9% | 8.0% | 1.26 | 0.510 |
| Venus retrograde | 8.7% | 8.7% | 1.02 | 1.000 |

No feature is statistically persuasive in this exploratory sample. The Saturn exact-degree result is based on only four candidate events, so its ratio is unstable.

Rahu and Ketu retrograde status is not useful as a discriminator because the mean nodes are conventionally retrograde throughout the sample.

## Interpretation

The discovery screen suggests three candidates for future testing:

1. Saturn within a narrow natal-degree orb
2. Mars retrograde
3. Mars in the natal Mars sign

These are hypotheses only. The current sample is dominated by death/career candidate extractions, lacks verified wealth and success outcomes, has preliminary controls, and contains repeated observations from the same people.

The correct next step is to add verified financial, career, marriage, childbirth and failure events, then repeat the discovery screen with person-level bootstrap, multiple-testing correction and a locked validation set.

Files:

- `outputs/q_unified_discovery/feature_rankings.csv`
- `outputs/q_unified_discovery/summary.json`
- `q_unified_discovery.py`
