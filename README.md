# Astrology Workspace — Four Sri Lankan Horoscopes + 20-Celebrity + 24-Chart + 5,000-Dataset Research

Link-only Vedic analysis (Drik Panchang Lahiri longitudes, astro-seek dashas, jyotishvidya Śrṅkhalā method).

## Quick start
- **CHAT_SUMMARY.md** — COMPRESSED log of all turns.
- **chat_log.md** — full detailed turn-by-turn log.
- **all_four_reanalysis.md** — main report (§1–16).
- **detailed_rerank.md** — recreated full matrix + detailed re-rank.
- **shrinkhala_industry_pattern.md** — "5-loop = industry-top" hypothesis test.
- **celeb_loop_database.md** — REAL 24-chart loop database (Drik, boundary-flagged).
- **astrodatabank_loop_methodology.md** — EXECUTABLE plan for Astro-Databank research + FINAL SUMMARY.
- **loop_research_500_framework.md** — user-pasted 500-framework (stats flagged UNVERIFIED).

## 5,000-chart famous-person dataset (Batch 1 = 111)
- `data/famous_seed.py` — Batch-1 seed (111 real/user-supplied records, all categories).
- `scripts/build_famous_dataset.py` — IDs + dedup + Groups 1/2/3 (NEW, no theory change).
- `scripts/astrodatabank_loop_batch.py` — EXISTING pipeline (Drik fetch→parse→loop→bond, unchanged).
- `scripts/generate_outputs.py` — writes the 10 required output CSVs (NEW).
- Outputs: `famous_people_birth_data.csv/json`, `exact_time_people.csv`, `date_only_people.csv`, `uncertain_people.csv`, `duplicate_people.csv`, `drikpanchang_fetch_results.csv`, `loop_results.csv`, `bond_results.csv`, `aggregate_statistics.csv`.
- Batch 1 result: 111 charts; 0-loop 36%, 2-loop 27%, 3-loop 24%, 4-loop 8%, 5-loop 2%; r(loop,ach)=−0.021.

## Standing rules
Link-only (no computed/Swiss-Ephemeris web data; positions from Drik/ephemeris links). Drik = longitudes; astro-seek = dashas; females → spouse karaka Jupiter. Every turn appends to chat_log.md and pushes to GitHub.
