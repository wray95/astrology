# SHRINKALA v1.0 — Repository Definition
## Source: Repository files (celebrity_shrinkhala.md + Scribd document #673088430)

**Status:** ✅ FOUND IN REPOSITORY

---

## Source Citation

**Primary source file:** `celebrity_shrinkhala.md` (lines 1-8)
**External reference:** https://www.jyotishvidya.com/srinkhala.htm
**Scribd document:** `Scribd #673088430 — Srinkhala` (2-page source)

---

## Definition (Quoted Verbatim)

> "Srinkhala is a **closed** chain of **3+ planets** linked by mutual dispositors 
> (A in B's sign, B in C's sign, C in A's sign…). It is the 'younger sister of 
> Parivartana' (2 planets)."

> "Strength rule (critical): Parivartana bond = 100; 3-planet Srinkhala = 50; 
> 4-planet = 33; 5-planet = 25. 'It is best to consider only a 3-planet Srinkhala… 
> ignore the same if there are more planets involved as the effect… is not considerable.'"

> "Interpretive rule: planets in a Srinkhala 'behave as if they are placed in their 
> own signs' (gain strength)."

---

## Algorithm

```
1. Build planet → dispositor graph from D1 signs
2. Find all directed cycles of length ≥ 3
3. Classify by cycle length:
   - 3 planets: bond = 50 (meaningful)
   - 4 planets: bond = 33 (weakened)
   - 5+ planets: bond = 25 (IGNORE — effect not considerable)
4. Check dusthana lord involvement (6L, 8L, 12L)
5. If dusthana lords present → Dainya/Khala Shrinkala
6. If only auspicious lords → Maha Shrinkala
```

---

## Test Hypothesis

- **H0:** 5-loop Shrinkala (bond=25) has NO predictive value beyond random
- **H1:** 3-loop Shrinkala (bond=50) correlates with higher achievement

---

## Unresolved Rules

| Rule | Status |
|---|---|
| Exact mechanism for "own-sign" behavior | UNRESOLVED |
| Ketu/Rahu participation | UNRESOLVED |
| Nak-level Shrinkala (Jiva) | UNRESOLVED |
| D9 Shrinkala confirmation rules | UNRESOLVED |
