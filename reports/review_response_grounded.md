# Grounded Response to External Architectural Review (2026-08-02)
*This file records: (1) which review claims are CONFIRMED by repo evidence, (2) nuances, (3) new evidence produced this turn, (4) the do-now vs do-later plan.*

## A. Review claims CONFIRMED by repo data

| Review claim | Repo evidence |
|---|---|
| Label bottleneck fatal | 111 charted exact-time; **rodden: 107 UNKNOWN + 4 B → 0 AA/A**. Children classifier: 279/280 positive (AUC NaN). 13 marriage labels = 12 unique (1 duplicate). No dated wealth/career outcome labels. |
| Yoga-presence ≠ outcome prediction | 193 features mostly binary yoga flags; industry classification ≈ chance (16.8% vs 16.7% baseline on 6 classes). ML comparisons (RF/XGB/CatBoost) on ~31% accuracy vs ~30% baseline = no signal. |
| Synthetic charts useless for inference | 3,049 synthetic industry charts (procedurally generated random births — not literally "AI-generated"; count differs slightly from review's 3,649) → chance-level industry accuracy confirms zero signal. |
| No causal framework | Confirmed: no DAG/adjustment anywhere; all observational. |
| Dasha under-linked to events | Partially confirmed: ONE survival analysis exists (Cox PH Shrinkhala→Saturn return HR=3.88, p<0.005, n=2,871) — right statistical family, but on date-only charts (noon-Moon) and Saturn-return events, not life-outcome events. No Person→Events→Dasha layer. |
| Rodden filter needed | Confirmed: filtering to AA/A leaves exactly **14 charts** (the celebrity set). |
| p-hacking risk real | **NEW this turn:** of 15 hypotheses, 4 raw p<0.05 → **0 survive Benjamini-Hochberg at q=0.05**; 3 survive at q=0.10 (Gaj-Kesari→wealth, Shrinkhala→wealth, Shrinkhala-len→wealth). All "MODERATE/STRONG" evidence labels in astro_research_os_hypotheses.json must be downgraded to "suggestive (q=0.10)". |
| Birth-time error risk | **NEW this turn — LOWER than feared:** jitter test on all 112 charted (SE Lahiri, ±10/±30 min): **±10m → 4% of charts flip ≥1 planet sign; ±30m → 5%**. Only Moon (3-4) and Mercury (1) ever flip; never >1 planet per chart; Sun/Mars/Jup/Ven/Sat never flip. Loop-class instability from realistic birth-time error ≈ 4-5%, not dominant. (The bigger positional risk remains Drik-web day-to-day wobble for near-boundary planets: 62% of celeb charts flagged, Turn 15.) |

## B. Nuances / corrections to the review

1. **"Dasha engine orphaned" is ~70% true.** The Saturn-return Cox analysis (HR=3.88) is real and uses the review's recommended family; P-series dasha matrices exist (senath_dasha_matrix.md). What's missing is exactly what the review says: dated life-event timestamps aligned to dasha periods.
2. **"111 charted with any usable data" understates the matrices:** 6,520 charts × 193 features exist (v4 .npz, Git LFS), but they are date-only real + synthetic — the review's deeper point (few verified, time-bearing, outcome-labeled) stands.
3. **The review's fix #19 (Astro-Databank XML) is blocked from this sandbox** (HTTP 000 since Turn 15) — needs the user's machine or another network.
4. **Missing from the review:** the Drik boundary-instability finding is the repo's *actual* top data risk (source wobble), and it is already mitigated by (a) single-session caches, (b) boundary flags, (c) the v3+ move to Swiss Ephemeris (stable). Birth-time jitter is a secondary risk, now quantified as small.
5. **Ayanamsa choice is NOT a risk:** verified vs Drik to <25″ (Turn 16). The review's sensitivity item #12 should focus on birth-time + source, not ayanamsa.

## C. New evidence produced this turn (committed)

- `scripts/birthtime_jitter_sensitivity.py` + `dataset/birthtime_jitter_sensitivity.json` — jitter test results above.
- FDR computation (in-line; reproducible) — 0/15 survive q=0.05.
- Rodden audit — 0 AA/A among 111; AA/A core = 14 charts.
- Review saved verbatim: `reports/ARCHITECTURAL_REVIEW_external_2026-08-02.md`.

## D. Do-now vs do-later

**Can be done in this workspace (next turns):**
1. Downgrade the 15-hypothesis evidence labels per FDR (edit astro_research_os_hypotheses.json + regenerate).
2. Kaplan-Meier curves stratified by yoga on the Saturn-return data (lifelines) — the repo already has the Cox scaffold.
3. Experiment-registry skeleton (JSON/markdown: hypothesis, pre-registration date, status) — cheap, satisfies review fix #7/#13 partially.
4. DuckDB scaffold: convert key CSV/JSON (famous registry, loops, hypotheses) to Parquet + DuckDB with schema — review fix #3, 1 session.
5. Provenance table: chart_id → source → computation date → hash (audit what exists).

**Needs user / external action (cannot be done here):**
1. Real outcome labels: 100 people × 20+ dated events (birth, education, first job, promotion, marriage, wealth event...). THIS is the #1 blocker — everything else is infrastructure.
2. Astro-Databank access (AA/A source) — blocked from sandbox.
3. Birth-time verification for the 107 UNKNOWN-rodden charted people (many are user-supplied times).
4. Decision: delete or quarantine the synthetic charts (recommend: keep file, stop using for inference; flag in registry).
5. Confirm Senath's true birth place (Colombo vs Houston proxy) — open from Turn 19/20.
