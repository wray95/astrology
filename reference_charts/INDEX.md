# P1234 Reference Charts Index (P1–P5)

Workspace organization of the **5 positive reference charts** of the 5,000-horoscope Vedic-Yoga
+ P1234 validation project. All planet data is DrikPanchang (Lahiri/Chitrapaksha ayanamsa); the
Lagna/houses are computed with the Drik-compatible Lahiri ayanamsa in `scripts/compute_lagna.py`
and the validation engine in `scripts/p1234_validate.py` (its `P1234_REFERENCE` dict now lists
**P1–P5**, with P5 = Senath added per user instruction). Re-run outputs live in `p1234_validation/`.

| Role | Name | Folder | Lagna | loop / bond | Hallmark | Ach. | Source |
|---|---|---|---|---|---|---|---|
| P1 | Polgahawela Bappa | `P1_Polgahawela_Bappa/` | Aries | 2 / 100 | PARI_001 (Ven–Mer) | 8 | famous_people + astrodb_loops + chart_houses |
| P2 | Upulakshi | `P2_Upulakshi/` | Taurus* | 2 / 100 | PARI_001 (Jup–Sat) | 5 | famous_people + astrodb_loops + chart_houses |
| P3 | Senith | `P3_Senith/` | Pisces | 5 / 25 | LOOP_005 | 4 | famous_people + astrodb_loops + chart_houses |
| P4 | Niromi | `P4_Niromi/` | Taurus (Vargottama) | 0 / 0 | MAHA_004 (Malavya) | 9 | famous_people + astrodb_loops + chart_houses |
| P5 | Senath | `P5_Senath/` | Virgo† | 2 / 100 | PARI_001 + MAHA_004 | n/a‡ | Drik link (14/05/2001 16:08:40, Lahiri) |

\*P2 registry time `12:00:00` is a **placeholder** → computed Lagna = Taurus, not the "Aries
Lagna" in the notes (data-quality flag).
†Senath Lagna = Virgo 5°44′ from the Drik link; birthplace unknown (proxy).
‡Senath is a Drik-link person, **NOT** in `famous_people_birth_data.json` → no workspace
achievement/profession score (Vedic axis only; see `rerank_p1234_validated.md`).

## `P5_Senath/` contents
- `horoscope_senath.md` — full horoscope (Drik link)
- `senath_matrix.md` — planet × sign × house × dignity matrix
- `senath_dasha_matrix.md` — CORRECTED job/money by dasha (Rahu MD 2014–2032, current)
- `senath_recompute.md` — master recompute (link data, Navamsa, P1234 battery)
- `senath_rahu_guru_vargottama.md` — (superseded) Houston-proxy vargottama note
- `senath_recomputed.json` — machine-readable recompute output
- `senath_reference.json` — P5 reference chart record (injected into the engine)
- `cache/` — raw Drik + astro-seek parses

## How P5 was integrated (no system changes)
1. `scripts/p1234_validate.py` `P1234_REFERENCE` gained `"Senath": {"role":"P5", ...,
   "hallmarks":["PARI_001","MAHA_004"]}`; docstrings/console updated P1–P4 → P1–P5.
2. `main()` injects reference charts not in the famous-people registry (reads
   `astrodb_out/p1234_reference_charts.json`), so Senath is evaluated and recorded as
   **COMPLETE / P5** in `p1234_validation/p1234_classification.json` and `chart_evaluations.json`.
3. Re-run regenerates all 15 `p1234_validation/` outputs with 5 reference charts
   (COMPLETE for P1–P5).
