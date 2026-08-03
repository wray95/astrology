# EVENT TIMING ENGINE — Report (2026-08-02)
*Reusable hypothesis-testing platform per advisor framework (message saved verbatim: PUBLIC_MILESTONE_FRAMEWORK_advisor_2026-08-02.md).*

## What was built
1. **`dataset/event_database.json`** — the Public Milestone Dataset (first version): 964 events (career-start 895, debut 16, milestone-year 52, company-founded 1) for 935 people. Seed = q_bio infobox (year-granular); +70 Wikipedia summary extracts (Elon Musk, Bill Gates, J.K. Rowling, Michael Jordan, AKD + targeted list; rest 429-rate-limited this session). Schema: person | birth_date | event_type | event_date | source | category. Event dates are YEARS (mid-year approximation) pending exact-date sources (Wikidata/IMDb/Nobel/Olympic).
2. **`scripts/event_timing_engine.py`** — general engine testing ANY timing rule vs ANY dated-event set: window constructors (saturn_sign, jupiter_sign, saturn_return±y, jupiter_return±y; extensible to dasha/ingress/nodes), age-preserving permutation test (natal-sign shuffle), exposure-based expected rate, Benjamini-Hochberg FDR.

## Results (n=912 events with registry birth dates)
| Rule | in-window | rate | exposure | permutation p | verdict |
|---|---|---|---|---|---|
| Saturn in natal sign | 37 | 4.1% | 8.3% | 1.0000 | null (below chance) |
| Jupiter in natal sign | 51 | 5.6% | 8.3% | 0.999 | null |
| Saturn return ±1y | 32 | 3.5% | 6.9% | 1.0000 | null |
| Jupiter return ±1y | 138 | 15.1% | 16.8% | 0.922 | null |
| **FDR q=0.05 survivors** | — | — | — | — | **none** |

All four classical timing rules: **no enrichment** at n=912. Consistent with the four-hypothesis test (n=904) — the effect is robustly null across both independent runs.

*Note: an earlier engine version had a window bug (next-same-sign vs consecutive entry) inflating exposures (Saturn 71%); fixed before this run — exposures now match the independent four-hypothesis test (~8%), confirming correctness.*

## Advisor-framework gaps still open (registered, not faked)
- **Control group B** (random non-famous people): cannot build here (need random birth-date cohort with event records — recommend 5,000 random births from civil records).
- **Event importance weights** (Nobel 10 … Marriage 3): schema ready; weights need assignment when real milestone types exist.
- **Source-quality hierarchy** (L1 gov/Nobel/Olympic; L2 Wikipedia/Britannica/IMDb; L3 news): schema ready; current events are L2 (Wikipedia infobox) with year granularity.
- **Exact event dates**: Wikidata blocked from sandbox (documented Turns 15/17); IMDb/Nobel/Olympic DBs not reachable — needs user-side run or API keys.
- **Per-category tests** (Business/Science/Arts/Politics/Sports): n per category too small (only 16 debuts, 1 company-founded) to split meaningfully yet — the engine supports it (event_type filter) once the DB grows.

## Bottom line
The **reusable platform** the advisor asked for now exists and is verified (its nulls replicate the independent test). The bottleneck is unchanged and now precisely quantified: **event data with exact dates and category/weight/source fields**. The Timing Atlas (10,000 people / 100,000 milestones) is the build target; the engine is ready for it.
