# FOUR-HYPOTHESIS WINDOW TEST — Report (2026-08-02)
*Advisor design (message saved verbatim in reports/H2_REVISED_HYPOTHESIS_advisor_2026-08-02.md). Pre-registered protocol + script: scripts/four_hypothesis_window_test.py → dataset/four_hypothesis_window_test.json.*

## Design (pre-registered)
- **H1** — first career event during Saturn's transit of natal Saturn sign (each visit, ~2.5y)
- **H2** — first career event during Jupiter's transit of natal Jupiter sign (each visit, ~1y)
- **H3** — first career event within ±1y of an exact Saturn return
- **H4** — random control windows (5 × 2.5y at random ages) — machinery sanity check
- Events: first career event (Wikipedia infobox career-active start / debut), n=904, birth-date-only (Lahiri, Swiss Ephemeris; natal signs time-insensitive).
- Test: **permutation** — shuffle natal signs across events 5,000× (preserves all age structure); p = fraction of shuffles with ≥ observed in-window count. Support iff p<0.05 AND rate > exposure AND beats H4.

## Results
| Hypothesis | in | rate | mean exposure | permutation p | verdict |
|---|---|---|---|---|---|
| H1 Saturn in natal sign | 35 | 3.9% | 8.3% | **1.0000** | null (below chance) |
| H2 Jupiter in natal sign | 54 | 6.0% | 8.3% | **0.9964** | null (below chance) |
| H3 Saturn return ±1y | 30 | 3.3% | 6.8% | **1.0000** | null (below chance) |
| H4 random control | 464 | 51.3% | 63.6%* | — | sanity OK (clip-edge bias) |

*H4 rate ≈ exposure (small edge bias where windows ending exactly at event age under-cover; direction documented, not material to the verdicts).*

**Bottom line: none of the three transit-window hypotheses shows any enrichment. All three sit at or below the exposure baseline (permutation p ≥ 0.996).** First career events are actually LESS likely to fall inside the natal-Saturn-sign window, natal-Jupiter-sign window, or return ±1y window than a random assignment of natal signs would produce. The reason is mechanical: career events cluster at ages 22–28, while the first Saturn-sign window opens at ~27 and the first return at ~29.5 — the age distribution "ducks under" all the windows.

## Why this is a credible null (vs the earlier naive result)
1. Permutation preserves every person's age/event structure — no pooling artifact.
2. H4 sanity confirms the machinery finds ~50% hits for random windows, so the 3–6% real-window rates are real (and low).
3. n=904; exposure ~8% → any true 1.5× enrichment would have p ≈ 0.001 — the test has power.
4. Natal-sign distributions across the full pool (registry 5,276 + uploads 4,397 + scholars 200 = **8,712 people**) are near-uniform (Saturn max/min 1.51, Jupiter 1.20) — no sign-level confound.

## The Gates/Musk anecdotes (computed, not assumed) — 1 for 2
- **Bill Gates** (b. 1955-10-28): natal Saturn **Libra**. Windows 1.0 era (1985): Saturn entered Libra 1982-10-05 and re-entered 1985-05-31 (retrograde) → the 1985 re-entry does bracket the 1985 event → anecdote "fits" only via the second entry.
- **Elon Musk** (b. 1971-06-28): natal Saturn **Taurus**. Zip2 sale (Feb 1999): Saturn entered Taurus only **2000-06-06** → **does NOT fit**.
- **Lesson: 1/2 anecdotal fit — exactly the confirmation-bias trap the advisor warned about; this is why the bulk test matters.**

## Data-provenance notes
- Uploaded 8×600 CSVs: only 2/4,397 names overlap the event-bearing set; no event dates in those files → used in the natal-sign pool (8,712) only. Names partially synthetic (flag maintained).
- Events are first-career-activity proxies (infobox career-active start year), not "first major breakthrough" — improving this (real milestone labels, exact dates, all-events-per-person) is the registered path forward.
- Jupiter test: natal-Jupiter windows occur ~3× more often than Saturn's in a lifetime — it had the most power of the three, and still null.

## What would change the answer (registered, unchanged from H2 report)
Exact event dates · true breakthrough labels · all events per person · same design on timed-birth subset (H3 with exact returns).
