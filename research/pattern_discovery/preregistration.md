# BLIND-MATCHING PROTOCOL — v1.0
## Based on Shawn Carlson (1985) double-blind design, adapted for Vedic event-prediction

---

## 1. OBJECTIVE

Test whether the Vedic astrology framework (D1 + D9 + Vimshottari Dasha + yogas)
can match birth charts to correct event timelines **above the chance rate**,
without knowing which chart belongs to which person.

**Null hypothesis (H0):** The framework matches charts to event-timelines at 
the rate expected by random guessing (1/N per match, where N = number of pairs).

**Alternative (H1):** The framework matches at a rate significantly above chance.

---

## 2. DESIGN

### Participants (Charts)
- **N charts required:** 20–30 minimum (Carlson used 28)
- **Rodden grade:** AA or A only (birth certificate or birth record)
- **Excluded:** Rodden B, C, DD, or unknown
- **Balanced:** Mix of professions, eras, achievement levels
- **Source:** Astrodatabank (astro.com/astro-databank)

### Participants (Event Timelines)
- For each chart, create a timeline of 5–8 dated major life events
- Event types: career breakthrough, marriage, divorce, major award, 
  significant wealth event, publicly documented illness/accident, death
- Each event has: exact date (YYYY-MM-DD), category, source citation

### Blinding Mechanism
1. **Chart preparation:** Each birth chart is computed independently. 
   Identifiers (name, profession, birthplace) are stripped. Charts are 
   assigned random codes (C1, C2, ... CN).
2. **Timeline preparation:** Each event timeline is similarly stripped of 
   identifiers and assigned random codes (T1, T2, ... TN).
3. **Shuffling:** Charts and timelines are independently shuffled so that 
   C1 does NOT necessarily correspond to T1.
4. **The task:** The framework (or blinded analyst) must match each chart 
   to its correct timeline.

### Outcome Measure
```
Matches = number of correctly paired (chart, timeline) combinations
Total possible = N (exactly one correct timeline per chart)
Chance expectation = 1 correct match (for N pairs, random guessing
                     gives exactly 1 match on average: E[match] = N × 1/N = 1)
Significance threshold = p < 0.05 vs. the null distribution
```

**Null distribution:** For N pairs, the number of correct matches under 
random guessing follows approximately Poisson(1) for large N. For small N, 
use the exact permutation distribution. Need ≥5 correct matches out of 
20 to reach p < 0.05 (one-tailed).

---

## 3. MATCHING CRITERIA (Must Be Pre-Registered)

For each event type, define IN ADVANCE what constitutes a "prediction 
from the chart" that would lead to matching it with the correct timeline.

### Example Event Types and Pre-Registered Criteria:

| Event Type | Chart Promise (D1/D9) | Dasha Activation | Match Window |
|---|---|---|---|
| Career breakthrough | 10L strong + benefic aspect OR 10L in Kendra + Raja Yoga present | 10L MD/AD active OR Jupiter MD/AD + 10L in Kendra | ±12 months of event date |
| Marriage | 7L strong + Venus unafflicted OR 7H with benefic + UL clean | 7L MD/AD active OR Venus MD/AD + 7L strong | ±6 months of event date |
| Major award/recognition | AL strong + 10L dignified + Raja Yoga | Jupiter MD/AD OR 10L MD/AD + benefic transit | ±12 months |
| Wealth milestone | Dhana Yoga present + 2L strong + 11L well-placed | 2L MD/AD OR Venus MD/AD + 11L activated | ±12 months |
| Death | 8L active + Maraka involvement | 8L MD/AD OR Maraka dasha (2L/7L) active | ±3 months |

### Scoring Rules:
- A correct match = chart-timeline pair where ≥3 of the 5–8 events match 
  the pre-registered criteria
- All criteria are applied **identically** to all charts — no per-chart adjustment
- Any criterion applied must be stated in this file BEFORE testing begins

---

## 4. ANALYSIS

### Primary Analysis
```
Report:
- Number of correct matches out of N
- Expected matches under chance (1)
- p-value from exact permutation test
- Effect size: (correct_matches - 1) / N
```

### Secondary Analysis
```
Break down by event type:
- For each event type, report hit rate vs base rate
- "Career breakthrough during Jupiter MD": X/N events vs 13.3% base rate
- Apply Bonferroni correction for number of event types tested
```

### Negative Analysis
```
- False positive rate: how many charts were matched to WRONG timelines
- Which criteria produced the most false positives
- Were any criteria useless (below chance)?
```

---

## 5. REQUIRED MATERIALS BEFORE STARTING

| Item | Status |
|---|---|
| N ≥ 20 AA/A-grade charts from Astrodatabank | ❌ NOT ACQUIRED |
| Dated event timelines for all N charts | ❌ NOT ACQUIRED |
| Pre-registered match criteria (this file) | ⚠️ DRAFT ONLY |
| Blinded chart preparation protocol | ⚠️ DRAFT ONLY |
| Statistical analysis script | ❌ NOT WRITTEN |
| Independent analyst (not the hypothesis author) | ❌ NOT IDENTIFIED |

---

## 6. CARLSON STUDY REFERENCE

> Carlson, S. (1985). "A double-blind test of astrology." *Nature*, 318, 419-425.
> 
> Design: 28 astrologers matched birth charts to CPI personality profiles 
> among 3 decoys. Astrologers predicted they'd get >50% correct.
> Actual result: 34% (chance = 33%). Verdict: performed at chance level.

Key difference in our design: We test EVENT TIMING (dasha prediction), 
not personality. This is a harder test — dashas move, houses and planets 
are mathematically defined. If anything, this SHOULD be easier to beat 
than Carlson's personality-matching test. If we can't beat chance on 
event-timing, we can't beat it on anything.
