# Date-only NEXUS: Transit/Reference-Chart Research Methodology

## Purpose

This project investigates whether date-based astronomical conditions are statistically associated with documented real-world events. It does **not** assume astrology is valid and does not attempt to prove or disprove it by rhetoric. Every result must be treated as an observation, an association, a pre-registered hypothesis, or an unsupported claim.

## Strict scope rule

The pipeline uses a person's **civil date of birth only**. It does not use or infer:

- birth time
- Ascendant/Lagna
- houses or D1 house positions
- D9 or any divisional chart
- Vimshottari dasha
- local angles or time-sensitive birth-chart claims

`UTC noon` is used only as a reproducible midpoint for daily reference values. It is explicitly **not** an assumed birth time. Every chart also includes a 00:00–24:00 UTC interval so investigators can identify fields that are stable or uncertain across the day.

## What was run

Command:

```bash
python3 date_only_nexus.py \
  --input data/births_people.json \
  --out outputs/date_only_nexus_5010
```

Result on 2026-07-29:

- 5,010 people processed
- 5,010 unique birth dates
- 5,010 date-level reference charts
- 0 birth times used
- 0 Ascendants, houses, D1 or D9 charts generated

Outputs:

- `people_date_only.csv`: one row per person with provenance and selected date-only features
- `reference_charts_by_date.json`: full reference chart for each date
- `run_summary.json`: reproducibility and scope metadata

The source file has dates for 5,010 people, but its city/country/latitude/longitude fields are largely empty. Therefore location is retained when present but was not silently fabricated. Geocoding is a separate data-acquisition step and must preserve source, coordinates, uncertainty and date of retrieval.

## Reference-chart features

The Swiss Ephemeris calculation uses Lahiri sidereal positions for the Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, mean Rahu and derived Ketu. For each body the output records longitude, sign, degree within sign, daily speed, retrograde/direct status and nakshatra.

Additional fields:

- midpoint conjunctions and major aspects, with explicit orb
- combustion proxy at the midpoint using an 8.5° threshold
- lunar phase and phase angle
- midpoint tithi, yoga and karana, marked time-sensitive
- midpoint lunar nakshatra, marked time-sensitive
- eclipse-proximity **proxy** based on proximity to New/Full Moon; this is not an eclipse catalogue, an eclipse visibility calculation, or proof of an eclipse
- daily 00:00/24:00 positions and stability flags

### Important precision limitation

Without a time of day, no single exact Moon longitude, combustion state, stationary state, tithi, karana or local eclipse condition can be claimed for a birth date. The correct research treatment is an interval, a midpoint plus sensitivity flag, or exclusion from analyses requiring exact timing.

## Required data model for the next stage

### Person table

`person_id`, name, date of birth, location text, latitude, longitude, country, occupation, education, wealth/outcome category, achievement measures, failure measures, source URL, source reliability, verification date, and missingness flags.

Do not replace unknown values with noon, a guessed location, a famous person's coordinates, or a default reliability grade.

### Event table

`event_id`, `person_id`, event type, event date, date precision (`day`, `month`, `year`), event description, outcome coding, source URL, source reliability, independent-source count, and whether the event was available before analysis.

Events should be coded with objective definitions: award, first employment, promotion, business founded, bankruptcy, marriage, divorce, child birth, illness, accident, retirement, death, etc. A timeline is more informative than a birth-only table because it supplies repeated within-person observations and permits time-aligned exposure/control comparisons.

### Event astronomy table

For every event date, calculate the same date-only reference features and add:

- event-date uncertainty and time-zone policy
- feature stability across the date
- sign changes, speed changes and station proximity
- aspect/conjunction distances
- lunar and eclipse-proxy fields
- a link to the exact software version and ephemeris settings

## Analysis design

### 1. Descriptive observation

Report counts, percentages, distributions and missingness first. Example: the proportion of promotions within seven days of a defined station window, versus the proportion of matched control dates.

### 2. Exposure definitions must be fixed before testing

Examples:

- `station_7d`: planet speed is within a pre-registered threshold of zero
- `sign_ingress_1d`: a planet changes sign within the event-date window
- `conjunction_3deg`: angular separation ≤3° at the midpoint, with interval sensitivity
- `eclipse_proxy_18deg`: only the documented phase proxy
- `cycle_window`: a pre-defined fraction of a known synodic period

Do not search dozens of orbs and windows and report only the most favorable one without correction for multiple testing.

### 3. Controls

Use matched control dates for the same person where possible, such as dates sampled from the person's eligible lifespan and matched on age, season, country or historical period. Also compare unrelated people and negative-control event types. This helps distinguish a planetary signal from seasonality, publicity, calendar artifacts, survivorship, age and historical clustering.

### 4. Statistical tests

- **Frequency/percentage:** describes how common an exposure or outcome is.
- **Risk ratio:** event probability in exposed periods divided by unexposed periods.
- **Odds ratio:** odds in exposed versus control observations; useful in case-control designs.
- **Confidence interval:** uncertainty range around an estimate; do not interpret it as the probability the hypothesis is true.
- **Effect size:** practical magnitude, not only p-value.
- **Chi-square:** compares categorical counts when expected counts are adequate.
- **Fisher exact:** safer for small cell counts.
- **Poisson/negative-binomial models:** useful for event counts and differing observation time.
- **Logistic or survival models:** useful for binary outcomes or time-to-event outcomes.
- **Bootstrap:** resamples people, not just rows, to preserve within-person dependence.
- **False-positive/false-negative rates:** evaluate classification thresholds; report precision, recall and calibration when making predictions.

Because many event rows belong to the same person, ordinary row-wise tests can overstate certainty. Cluster standard errors by person, use mixed-effects models, or bootstrap at the person level.

### 5. Discovery versus confirmation

Split the data by person, not by event row:

- discovery/training set: generate candidate hypotheses
- locked validation set: test the pre-specified candidates once
- independent replication set: strongest confirmation

A pattern discovered and tested on the same people is exploratory, not predictive evidence.

## Machine learning: permitted role

Unsupervised clustering, association-rule mining, anomaly detection and feature importance can generate hypotheses. Classification can estimate out-of-sample predictive performance. ML must not be treated as causal evidence. Use nested cross-validation, a simple baseline model, class-balance controls, permutation tests, feature-selection inside each training fold, and a held-out person-level test set. Human review is required before turning a model pattern into an astrological hypothesis.

## Generation and geography analyses

Compare historical periods only after controlling or stratifying for geography, occupation, sex where available, population composition, data-source composition, age and event recording practices. Planetary generations may be strongly confounded with calendar time, so period comparisons are descriptive unless a design separates astronomical exposure from secular history.

## Evidence language

- **Observation:** “18 of 200 events occurred during the pre-defined window.”
- **Statistical relationship:** “The adjusted risk ratio was 1.18, 95% CI 0.96–1.45.”
- **Experimental hypothesis:** “A station window may be associated with promotion dates; this is tested on held-out people.”
- **Unsupported claim:** “This planet causes promotion” or any claim made without an appropriate design.

## Next implementation milestones

1. Replace/augment the source roster with verified locations and source reliability.
2. Build a documented event-ingestion pipeline with source snapshots and event-date precision.
3. Generate event-date charts using the same feature code.
4. Pre-register a small number of event/exposure hypotheses and control windows.
5. Run person-clustered descriptive and inferential analyses.
6. Lock a validation set and report null results, missingness, multiple-testing corrections and sensitivity analyses.
7. Replicate on an external dataset.
