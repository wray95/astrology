# Saturn Return Q-Series Research Run

**Run date:** 2026-07-29  
**Input:** `data/births_people.json`  
**Method:** Date-only Swiss Ephemeris, Lahiri sidereal, UTC-noon midpoint

## Research separation

The P1–P9 people remain a separate prediction/reference series. The source dataset did not contain exact matching records for the named P people, so no P record was silently mixed into Q. Every source record was therefore labelled Q1–Q5010. If P records are later added to the source roster, the exclusion list in `saturn_return_q_series.py` must be applied and the Q IDs regenerated deterministically.

## What was calculated

For each Q person:

1. Saturn's sidereal longitude, sign and degree on the birth date.
2. A first Saturn-return estimate by searching ages 25–35.
3. A second Saturn-return estimate by searching ages 54–65.
4. The nearest daily UTC-noon date to the natal Saturn longitude.
5. Angular error of the date-only estimate.

No birth time, Ascendant, houses, D1, D9, local angles or dasha calculations were used.

## Results

- **5,010 Q people processed**
- **0 P-name records found inside the input dataset**
- First return: mean age **29.406**, median **29.473** years
- Second return: mean age **58.892**, median **58.972** years
- First-return angular error: median **0.022°**, maximum **0.549°** on the daily reference grid
- Birth-date range represented: **33 CE–2025 CE**

The return ages are consistent with Saturn's approximately 29.5-year sidereal cycle. This is an astronomical timing result, not evidence that any particular life outcome occurs at the return.

## Natal Saturn sign counts

| Sign | Q people |
|---|---:|
| Capricorn | 528 |
| Sagittarius | 509 |
| Aquarius | 463 |
| Libra | 448 |
| Virgo | 438 |
| Cancer | 396 |
| Leo | 387 |
| Scorpio | 445 |
| Pisces | 361 |
| Aries | 347 |
| Taurus | 355 |
| Gemini | 333 |

These counts should not be interpreted as a biological or psychological effect. They are primarily a distribution of birth dates in this source dataset and may reflect collection bias.

## What happens at the returns?

The current Q dataset contains birth records, occupations and source metadata but **no complete person-linked life-event timeline** for these 5,010 records. Consequently, this run cannot honestly conclude what happened to Q people at their first or second Saturn returns.

To test that question, add a verified event table with at least:

- `q_id`
- exact or interval event date
- event type
- description
- source URL and reliability
- date precision
- whether the event was collected independently of the Saturn hypothesis

Then calculate event windows around each return, for example ±30, ±90 and ±365 days, and compare them with matched non-return control periods for the same person. Controls should be matched by age, calendar season, historical period and observation time. Use person-level bootstrap or clustered models because each person contributes multiple events.

## P-series prediction use

The Q series may be used for **hypothesis generation** only. A valid P-series prediction workflow would be:

1. Define event categories and return windows using Q data only.
2. Lock the definitions before looking at P outcomes.
3. Calculate each P person's date-only Saturn return dates separately.
4. Report predictions with uncertainty, not certainties.
5. Compare predictions with later verified P events.

Without event outcomes, the P output can identify return dates and possible windows, but it cannot claim that a promotion, marriage, loss or other event will occur.

## Files

- `outputs/saturn_returns_q_series/q_saturn_returns.csv`
- `outputs/saturn_returns_q_series/q_saturn_returns.json`
- `outputs/saturn_returns_q_series/run_summary.json`
- `saturn_return_q_series.py`

The data and script have been saved in the workspace. No GitHub push was performed because repository credentials and an explicit push authorization were not available in this step.
