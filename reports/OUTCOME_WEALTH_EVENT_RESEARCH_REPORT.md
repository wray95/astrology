# Outcome and Major-Event Research Update

## Required outcome fields

Every Q person now has explicit fields for wealth, poverty, success and failure. They are set to `unknown_not_documented` when the source data does not support a classification. This is compulsory data completeness, not a fabricated rich/poor label.

It would be methodologically invalid to call someone rich or poor from occupation, fame, planetary position or an unverified web statement.

## Candidate event extraction

From source-attributed Wikipedia infobox fields, the pipeline extracted 1,812 candidate date mentions:

- career-period candidates: 1,416
- marriage/spouse date candidates: 220
- death dates: 141
- debut/career-start candidates: 34
- incarceration/conviction candidates: 1

Only **161** had a usable day/month-level date for a date-only planetary midpoint calculation. Year-only dates were retained but not assigned an exact transit chart.

These are **candidate extractions**, not verified life events. For example, a spouse field may contain a name without a marriage date, and a career-period field may contain a range rather than a debut or success date.

## Preliminary movement screen

The date-only movement file includes Saturn, Jupiter, Venus and Mars sign/status fields for usable dates:

`outputs/outcome_event_movement/q_candidate_events_with_movements.csv`

This is not yet a valid success-versus-failure test because:

- Wealth, poverty, success and failure are not documented for the Q people.
- Candidate extraction errors have not been manually verified.
- The event sample is selected by which infobox fields happen to exist.
- Many records are month/year or year-only rather than exact dates.
- Repeated rows from one person are not independent.

## Proper next stage

For each candidate event, verify against at least one independent source and assign:

- exact date or date interval
- event type
- positive/negative/neutral outcome
- source reliability
- whether the event was known before the hypothesis was defined

For wealth, use measurable definitions such as a documented net-worth threshold, company sale, bankruptcy filing or public financial record. Do not infer poverty from lack of wealth data.

Only after verification should the analysis compare planetary movement windows against matched control dates and report odds ratios, confidence intervals, effect sizes and person-clustered uncertainty.
