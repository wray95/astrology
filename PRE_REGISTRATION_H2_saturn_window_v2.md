# PRE-REGISTRATION (v2) — H2: First breakthrough during Saturn transit of natal Saturn sign
*Registered 2026-08-02 BEFORE analysis. Replaces the looser "exact Saturn return" framing.*

## Hypothesis (as revised by user/advisor, accepted)
**H2:** *The first major breakthrough tends to occur during the approximately 2.5-year period when transiting Saturn is in the person's natal Saturn sign (Lahiri), including the months before the exact return.*

## Windows (defined BEFORE looking at any chart/event)
- **Window A** = [Saturn enters natal Saturn sign → Saturn enters the NEXT sign] (~2.5 y). Includes the exact return moment. 
- **Window B** = exact Saturn return date ±1 year (subset of A; tested separately).
- **Window C (control)** = the 2.5-y window immediately BEFORE A (Saturn in previous sign) and the 2.5-y window AFTER A (Saturn in sign after next). Event rates in C must equal chance.
- **Chance expectation:** Saturn spends ~2.5 y of its 29.46-y cycle in each sign → P(event in A by chance) ≈ 2.5/29.46 ≈ **8.5%**. Binomial test vs 8.5%.

## Events (first stage — no birth time needed)
- Primary proxy: **career-active start year** (Wikipedia infobox `career_active` "YYYY–present" → start YYYY), n≈910.
- Secondary: **debut** dates (n≈34).
- Event definition: FIRST dated career/breakthrough event only (per advisor: stage 2+ can add all events when more labels exist).
- Birth dates: registry (5,287) + uploaded CSVs (8×600) + scholars (200). No birth time required (Saturn sign is time-insensitive).

## Test
- For each person: natal Saturn sign (Lahiri, Swiss Ephemeris) → all Saturn transits of that sign from birth to age 80 → windows A/B/C.
- Count: events inside A vs expected 8.5% (binomial, one-sided). Report also B and C rates.
- Thresholds: p < 0.05 (pre-registered; FDR across the 3 window tests). Effect must also show rate_in_A > rate_in_C.
- Robustness: Saturn sign needs only birth DATE; jitter ±1 day on date cannot flip a sign except near boundary (<2% of dates); report boundary count.

## Data-provenance flags (registered)
- Uploaded 8×600 CSVs: several names appear synthetic ("Tennessee Vonnegut 1", "Grace Lovelace 1") — treat as AI-generated/synthetic-provenance; usable for birth-date distribution and natal-sign sanity, NOT for outcome claims without verification.
- q_biographical_wikipedia CSV: raw infobox extraction, "no dates inferred" warning in its own summary.json — career_active years parsed as integers; spot-check format coverage before use.
- The 151,200-career file referenced by the plan no longer exists in the repo (removed in a cleanup commit) — noted.
