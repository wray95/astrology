# Birth Degrees, Dignity, Sign-Candidates and Event Research

## Research question

Do people with particular date-only planetary degrees/signs, traditional sign dignities or sign-based configurations show different occupation distributions, and do those birth features recur on major event dates?

## Q-series run

- 5,010 Q people
- Lahiri sidereal UTC-noon midpoint
- No birth time, Ascendant, houses, D1 or D9

Traditional exaltation signs used as **sign-only features**:

- Sun Aries
- Moon Taurus
- Mars Capricorn
- Mercury Virgo
- Jupiter Cancer
- Venus Pisces
- Saturn Libra

Results:

- 2,368/5,010 have at least one sign-based exaltation feature
- 3,919 have at least one close sign/degree conjunction candidate using an 8° orb
- 1,887 have a sign-exchange candidate using sign-lord reciprocity

These are feature counts, not validated yogas. Many classical yogas require houses, Ascendant, lordship and aspects that cannot be established without birth time.

## Occupation comparison

An exploratory occupation-group chi-square test found:

- Individual exalted-planet features were not statistically compelling after considering the number of tests.
- Exalted-count versus occupation group: p=0.180, Cramer's V=0.051.
- Close-conjunction count versus occupation group: p=0.0019, Cramer's V=0.056.
- Sign-exchange candidate count versus occupation group: p=0.0376, Cramer's V=0.057.

The effects are small. The conjunction result is especially vulnerable to occupation, generation, geography, source-selection and date-distribution confounding. It is a discovery signal only, not evidence that a yoga causes an industry.

## Big-day event analysis status

There are **zero Q-linked event rows** in the repository. Thus the key test—whether a person's birth planetary degrees are contacted or activated by planetary movement on their major event date—cannot yet be run for Q.

The existing reference event sample contains only 10 events for 2 people and is not a Q validation sample. It cannot establish a general pattern.

## Correct event test

For each Q event, calculate on the event date:

1. Transiting planetary longitude and degree.
2. Distance from each natal planet degree.
3. Whether the transit is within pre-registered orbs, e.g. 1°, 3° or 5°.
4. Sign ingress, retrograde/direct station and speed.
5. Sign-based conjunctions and opposition/square/trine candidates.
6. Whether the event occurs near the person's first or second planetary return.
7. Whether the same contact appears in matched non-event control dates.

Then group the events into:

- employment, promotion and job change
- marriage and divorce
- childbirth and child loss
- wealth gain and bankruptcy/financial loss
- achievement and recognition
- illness, accident and death

The analysis must compare positive and negative outcomes separately and must use person-level clustering because each person can contribute multiple events.

## Degree-first principle, with a caution

Degrees are useful because they permit continuous contact measurements, but they are not automatically “the key of everything.” A degree pattern can arise by chance, and the result depends on:

- the orb selected
- the time precision of the event
- the uncertainty of the birth date reference
- multiple testing
- historical and seasonal confounding
- incomplete event reporting

The strongest design is a pre-registered, out-of-sample test where the degree/orb rule is chosen in Q discovery data and then tested once on held-out Q people or on the separate P series.

## Files

- `outputs/birth_degree_pattern_pipeline/q_birth_features.csv`
- `outputs/birth_degree_pattern_pipeline/feature_job_tests.csv`
- `outputs/birth_degree_pattern_pipeline/summary.json`
- `birth_degree_pattern_pipeline.py`
