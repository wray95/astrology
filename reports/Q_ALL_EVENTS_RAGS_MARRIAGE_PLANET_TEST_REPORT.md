# Q-Series Rags-to-Riches, Marriage and All-Available Event Test

## Scope

The full Q source contains 5,010 people. The current biography extraction provides 1,812 candidate event rows, but only 161 have enough date precision for a date-only planetary midpoint. There are no verified Q rags-to-riches, wealth-gain, poverty, major-success, major-failure, childbirth or financial-loss outcomes yet.

Candidate rows:

- Death: 141
- Career-period mentions: 1,416
- Marriage/spouse candidates: 220
- Debut/career-start candidates: 34
- Incarceration/conviction candidates: 1

## Event-date movement counts

For 161 usable dates, the table counts events where the transiting planet was in the same sign as that person's natal planet, within 3° of the natal degree, or retrograde.

| Planet | Same natal sign | Within 3° | Retrograde |
|---|---:|---:|---:|
| Saturn | 19 | 4 | 60 |
| Mars | 15 | 4 | 19 |
| Venus | 8 | 1 | 14 |
| Jupiter | 16 | 0 | 51 |
| Rahu | 13 | 3 | 161 |
| Ketu | 13 | 3 | 161 |

Rahu and Ketu are mean nodes and conventionally retrograde, so their retrograde column is not a discriminating feature.

## Preliminary control comparison

Three random age-window control dates were generated per usable event, giving 450 controls.

| Planet | Event same-sign rate | Control same-sign rate | Event retrograde rate | Control retrograde rate |
|---|---:|---:|---:|---:|
| Saturn | 11.8% | 9.3% | 37.3% | 40.0% |
| Mars | 9.3% | 6.2% | 11.8% | 7.8% |
| Venus | 5.0% | 8.9% | 8.7% | 8.7% |
| Jupiter | 9.9% | 8.0% | 31.7% | 32.2% |

These are descriptive ratios only. They are not adjusted p-values or causal estimates.

## Required conclusion

The current data cannot test “rags to riches” because no Q person has a verified wealth trajectory linking poverty/background, career breakthrough, wealth milestone and later net worth. It also cannot test marriage, childbirth or success reliably because the spouse/debut fields are candidate extractions and lack verified dates for most records.

The current output shows no strong universal retrograde signal. Saturn same-sign exposure is slightly higher in candidate dates than preliminary controls, but this is weak and dominated by unverified death/career records. The next stage is manual verification and objective outcome labels before inferential testing.

Files:

- `outputs/q_all_event_sequence_test/events.csv`
- `outputs/q_all_event_sequence_test/controls.csv`
- `outputs/q_all_event_sequence_test/summary.json`
- `q_all_event_sequence_test.py`
