# H2 TEST REPORT — "First breakthrough during Saturn transit of natal Saturn sign"
*Pre-registered: PRE_REGISTRATION_H2_saturn_window_v2.md (2026-08-02). Data: registry birth dates (5,276) joined with Wikipedia infobox career-active/debut (q_biographical_wikipedia) → n=905 events. Script: scripts/h2_saturn_window_test.py → dataset/h2_saturn_window_test.json.*

## Protocol (pre-registered)
- **Window A** = Saturn in natal Saturn sign (Lahiri), ~2.5 y (entry→next entry), INCLUDES months before exact return (per hypothesis).
- **Window B** = exact return ±1 y (subset of A).
- **Window C** = control: 2.5 y before A and 2.5 y after A.
- Event = FIRST dated career event (career-active start year; debut where present). Birth-date-only (Saturn sign needs no birth time). Event JD = mid-year approximation.

## Results
| Test | n | in Window A | Expected | Result |
|---|---|---|---|---|
| All events, naive (life-uniform) | 905 | 3.9% | 8.5% | below chance (age-bias artifact — see note) |
| **Age-adjusted 25–35** (first-return era) | 132 | **25.8%** | **25%** | **exactly chance (p=0.45)** |
| **Age-adjusted 27–33** (tight) | 79 | **43.0%** | **~42%** | **exactly chance (p=0.44)** |
| Control C (all ages) | 905 | 10.9% | 17% | below chance (same age-bias) |

- Window B (±1y exact return): 3.1% all-ages (below chance — same artifact); not separately significant.
- Natal Saturn sign distribution: roughly uniform (sanity OK).

## Verdict
**H2 NOT SUPPORTED.** When the age-at-event distribution is accounted for, first-career events fall inside the natal-Saturn-sign window at **exactly chance rate** (25.8% vs 25%; 43.0% vs 42%). The naive "below chance" numbers are an age-clustering artifact: career starts cluster at ages 22–28, mostly BEFORE the first window begins (~27) — matching the observed "things happen just before Saturn return" intuition, but the effect disappears entirely once you compare like-for-like ages.

**Methodological notes (why this is a credible null):**
1. Window definitions fixed before analysis (pre-registered).
2. A-vs-C comparison cancels age/cohort bias (adjacent age bands).
3. Saturn sign from birth DATE only (no birth-time sensitivity; sign flips only near boundary, <2% of dates).
4. n=905 gives power: an 8.5%-vs-15% true effect would be detected with ~90% power.
5. Caveats: career-active start year is a first-activity proxy, not "first major breakthrough"; raw infobox extraction (its own summary.json warns "no dates inferred; verify before statistical use"); year-granularity (mid-year JD).

## What would change the answer (registered)
1. Exact event dates (month/day) rather than years — removes mid-year noise.
2. "First major breakthrough" labels (first hit single, first unicorn, first major award) — career-active ≠ breakthrough.
3. All events per person (multi-event power), per advisor's improvement.
4. Same test for JUPITER (12-y cycle → 3× more windows in a lifetime → more power for the analogous "Jupiter in natal Jupiter sign" hypothesis).

## Data-provenance flags
- Uploaded 8×600 CSVs: names partially synthetic ("Tennessee Vonnegut 1") → usable for birth-date distribution only; NOT used in the event test (no event dates); natal-sign distribution sanity only.
- 151,200-career file referenced in the gochara plan no longer exists in repo (removed in cleanup).
