# DATA VERIFICATION REPORT
## 5,287-Entry Dataset (famous_people_birth_data.json)

**Date:** 25 Jul 2026 | **Methodology:** See `methodology.md`

---

## 1. DATASET OVERVIEW

| Metric | Count | % |
|---|---|---|
| **Total entries** | 5,287 | 100% |
| **Entries with REAL birth times** (not 12:00/00:00) | **101** | **1.9%** |
| **Entries with default/unknown birth times** | 5,186 | 98.1% |
| **Entries with Rodden-grade reliability** | 4 (all "B") | 0.08% |
| **Entries with unknown reliability** | 5,283 | 99.92% |

---

## 2. SOURCE ANALYSIS

| Source | Count | Notes |
|---|---|---|
| Wikipedia (Births by date) | 5,005 | **DATE-ONLY** records — no birth times. Useless for Vedic calculations. |
| Wikipedia | 171 | Date + possible time, sourced from Wikipedia biographies |
| Wikipedia (framework cross-ref) | 107 | Cross-referenced for the loop study |
| Prior 4-family analysis | 4 | Our 6 reference people: Bappa, Upulakshi, Senith, Niromi |

---

## 3. RODDEN GRADING

| Grade | Count | Included in hypothesis testing? |
|---|---|---|
| **AA** (birth certificate) | **0** | N/A |
| **A** (family/memory) | **0** | N/A |
| **B** (biography) | **4** | ⚠️ Included with flag |
| **C** (no time/rectified) | **0** | ❌ |
| **DD** (conflicting) | **0** | ❌ |
| **UNKNOWN** | **5,283** | ❌ **EXCLUDED** from hypothesis testing |

---

## 4. OUR 6 REFERENCE CHARTS — VERIFICATION STATUS

| Chart | Birth Time | Reliability | Rodden | Status |
|---|---|---|---|---|
| **P1 Bappa** | 03:38:54 | B | B | ⚠️ PARTIALLY VERIFIED — source=Prior analysis, no independent birth record |
| **P2 Upulakshi** | 12:00:00 | B | B | ❌ **UNRELIABLE** — placeholder noon time. Real TOB unknown. **EXCLUDED from testing.** |
| **P3 Senith** | 21:18:00 | B | B | ⚠️ PARTIALLY VERIFIED — Corrected Moon from engine (Mula/Ketu), time from astro-seek link |
| **P4 Niromi** | 08:17:37 | B | B | ⚠️ PARTIALLY VERIFIED — source=Prior analysis, no independent birth record |
| **P5 Senath** | 16:08:40 | NOT IN FILE | B | ⚠️ PARTIALLY VERIFIED — Added from Drik Panchang / Astro-seek link |
| **P6 Dewli** | 08:22:03 | NOT IN FILE | — | ⚠️ PARTIALLY VERIFIED — From AppliedJyotish PDF, time differs from Drik link (07:52) |

---

## 5. CRITICAL FINDINGS

### The 5,287 dataset is NOT suitable for Vedic astrology research

1. **98.1% have no birth time.** Vedic chart computation requires exact birth time for Lagna and houses.
2. **Zero AA-grade charts.** No birth certificate verification for any entry.
3. **Wikipedia "Births by date" (5,005 entries)** provides only dates — these are completely useless for Dasha/Lagna/house calculations.

### The 111-entry astrodb_loops.json is the only usable dataset

This file contains:
- 111 celebrity charts with actual birth times
- Computed loop data and achievement scores
- Approximate degree data (rounded, not precise)
- Planet signs and houses

**Limitation:** Degrees are rounded, not precise enough for pada-level or transit analysis.

### Recommendation

The project's hypothesis-testing phase (Priorities 4-7) can only use:
1. The 111 astrodb_loops.json celebrities (Rodden ~B)
2. Any newly acquired AA/A-grade charts from Astrodatabank or similar sources

The 5,287-entry file should remain for reference but is **excluded** from all statistical testing.
