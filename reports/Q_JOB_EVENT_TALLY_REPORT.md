# Q-Series Job/Event Tally

## Bottom line

The current Q dataset allows an exploratory comparison of **occupation labels** with birth-date planetary signs. It does **not** allow a valid event/transit test because the 5,010 people do not have complete linked life-event timelines.

## Job analysis performed

Occupation strings were grouped by transparent keyword rules into broad groups such as Athlete, Actor/Media, Politics/Government, Academic/Science, Writer/Journalism, Law, Medicine, Business, Religion and Engineering/Tech. A chi-square association test compared each planet's birth-date midpoint sign with job group. Benjamini–Hochberg false-discovery-rate adjustment was applied across planets.

| Planet | p-value | FDR q-value | Cramer's V | FDR flag |
|---|---:|---:|---:|---|
| Sun | 0.354 | 0.473 | 0.048 | No |
| Moon | 0.543 | 0.652 | 0.046 | No |
| Mercury | 0.066 | 0.114 | 0.051 | No |
| Venus | 0.172 | 0.258 | 0.050 | No |
| Mars | 0.773 | 0.773 | 0.044 | No |
| Jupiter | 0.740 | 0.773 | 0.045 | No |
| Saturn | 0.013 | 0.027 | 0.054 | Yes, exploratory |
| Uranus | <0.001 | <0.001 | 0.092 | Yes, likely cohort-confounded |
| Neptune | <0.001 | <0.001 | 0.146 | Yes, likely cohort-confounded |
| Pluto | <0.001 | <0.001 | 0.178 | Yes, likely cohort-confounded |
| Rahu/Ketu | 0.004 | 0.010 | 0.055 | Yes, exploratory |

## Interpretation

This does **not** establish that planets cause or predict jobs.

The outer-planet results are especially vulnerable to confounding: Uranus, Neptune and Pluto occupy slow-moving generational signs. A historical dataset with different occupations recorded for different generations will naturally create sign–occupation associations even if astrology has no effect. The same problem can affect Rahu/Ketu and Saturn.

The effect sizes are small. For example, Saturn's Cramer's V is approximately 0.054. That indicates a weak association in this coding scheme, even though the p-value is below 0.05. Large samples can make small, non-practical differences appear statistically detectable.

The occupation categories are also source-derived labels, not standardized employment records. They may reflect survivorship, public-figure selection, country, sex, historical period and Wikipedia recording practices.

## Events

No valid Q-series event tally has been completed. The available repository event file contains only 10 dated events for two reference people, not 5,010 Q people. Therefore we cannot test whether promotions, marriages, awards, bankruptcies, illness or other events occur near planetary returns or transits for the Q cohort.

## Correct next test

For each Q person, add independently sourced event rows and calculate:

1. Planetary conditions on each event date.
2. Whether the event occurs within pre-registered windows around returns, sign ingresses, stations or natal degree contacts.
3. Matched control dates for the same person.
4. Person-clustered or mixed-effects models.
5. Historical-period and geography controls.
6. A locked validation set not used to discover the hypothesis.

Current conclusion:

> Jobs show weak exploratory associations with some birth-date planetary signs, but the analysis is not a transit test and is heavily vulnerable to cohort and data-collection confounding. There is currently insufficient evidence to say that planetary movements tally with Q-series life events.

Files:

- `outputs/q_job_planet_association/planet_job_tests.csv`
- `outputs/q_job_planet_association/job_group_counts.csv`
- `outputs/q_job_planet_association/report.json`
- `q_job_planet_association.py`
