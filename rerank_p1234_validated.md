# Re-Rank of the 4 Charts — P1234 / Vedic-Yoga Validation Update

**Context:** This re-rank updates `rerank_matrix_scored.md` (which ranked the 4 charts
on the 23-dimension *worldly* research matrix) by adding the **Vedic-Yoga / P1234
validation evidence** produced in this project (loops, bonds, Mahapurusha yogas,
exchanges, P1234 status — all from `p1234_validation/`, computed with the
Drik-compatible Lahiri ayanamsa; Drik planet data UNCHANGED).

**No system changes.** Loop definition, bond logic, P1234 theory and chart method
are untouched; this only *ranks* using the new data.

---

## 1. Validation evidence per chart (from this project)

| Chart | Lagna (computed) | loop | bond | Mahapurusha | Exchange (Parivartana/loop) | ach. |
|---|---|---|---|---|---|---|
| **P1** Polgahawela Bappa (1962 ♂) | Aries | 2 | 100 | **2** (Rucaka/Mars, Sasa/Saturn) | PARI_001 (Ven–Mer) | 8 |
| **P2** Upulakshi (1997 ♀) | Taurus* | 2 | 100 | 0 | PARI_001 (Jup–Sat) | 5 |
| **P3** Senith (1995 ♂) | Pisces | **5** | 25 | 0 | LOOP_005 (only 5-loop) | 4 |
| **P4** Niromi (1967 ♀) | Taurus (Vargottama) | 0 | 0 | **1** (Malavya/Venus) | none | 9 |

\*Upulakshi's registry time `12:00:00` is a placeholder → computed Lagna = Taurus,
not the "Aries Lagna" in the notes (data-quality flag). Drik planet data is whole-degree.

---

## 2. Axis A — Worldly / realized status (prior research matrix, unchanged)

Composite (career+finance+money+fame+success+education+CEO+assets+where-wealth):

- **P4 · Niromi — 38.0**
- **P1 · Polgahawela Bappa — 34.5**
- **P2 · Upulakshi — 25.0**
- **P3 · Senith — 15.0**

**Rank A: P4 > P1 > P2 > P3**  (wealthiest self-made founder > wealthy businessman > MNC employee > limited/student)

---

## 3. Axis B — P1234 / Vedic-Yoga validation strength (NEW, from this validation)

Transparent 0–5 sub-scores (max 15), derived only from the validation outputs:

| Sub-score | P1 | P2 | P3 | P4 | basis |
|---|---|---|---|---|---|
| Exchange / loop structure | 4 | 4 | **5** | 0 | 5-loop rarest (3/111); 2-loop Parivartana strong; 0-loop = 0 |
| Bond strength | **5** | **5** | 1 | 0 | bond 100 / 20 (existing bond system: 100,100,25,0) |
| Mahapurusha (dignity yoga) | **5** | 0 | 0 | 2.5 | 2 Maha = 5; 1 (Malavya) = 2.5; none = 0 |
| **Vedic composite (sum)** | **14** | **9** | **6** | **2.5** | |

**Rank B: P1 > P2 > P3 > P4**
P1 leads on both loop/bond AND dignity (2 Mahapurusha + 2-loop + bond 100).
P4 is **last on the Vedic axis** — it has the premium Malavya dignity but **no loop
and no bond at all** (loop_len 0, bond 0), consistent with the jyotishvidya
Śrṅkhalā bond ranking (P2 > P1 > P3 > P4). P3 carries the rarest 5-loop but the
weakest bond and no Mahapurusha.

---

## 4. Integrated re-rank (Axis A + Axis B, normalized 0–1, 50/50 default)

| Chart | Worldly (norm) | Vedic (norm) | **Blend 50/50** |
|---|---|---|---|
| P1 | 0.908 | 1.000 | **0.954** |
| P4 | 1.000 | 0.179 | 0.590 |
| P2 | 0.658 | 0.643 | 0.650 |
| P3 | 0.395 | 0.429 | 0.412 |

**>>> INTEGRATED RE-RANK (default 50/50): P1 > P2 > P4 > P3**

### Sensitivity (robustness of the top/bottom)
- 70% worldly / 30% vedic → **P1 > P4 > P2 > P3**
- 30% worldly / 70% vedic → **P1 > P2 > P4 > P3**

P1 is **#1 under every reasonable weighting** (strong on both axes). P3 is **#4
under every weighting** (weak on both, despite the rare 5-loop). The only swap is
**P2 ↔ P4**: P4 leads when worldly status is weighted heavily (it is the wealthiest);
P2 leads when Vedic structure is weighted heavily (strong 2-loop + bond 100, vs P4's
absent loop/bond).

---

## 5. Tiers (integrated)

- **TIER 1 — P1 Polgahawela Bappa:** best all-round — 2nd on worldly, **1st on the
  Vedic validation axis** (2 Mahapurusha + Parivartana + bond 100). Rises to #1 once
  the new yoga/loop evidence is weighted alongside realized wealth.
- **TIER 2 — P2 Upulakshi / P4 Niromi (coin-flip by weight):** P4 = wealthiest,
  top worldly, but **no loop/bond/yoga structure** (Vedic-bottom); P2 = moderate
  wealth but solid Vedic structure (2-loop Parivartana + bond 100). P2 overtakes P4
  as soon as Vedic evidence is weighted ≥ ~40%.
- **TIER 3 — P3 Senith:** the rare 5-loop is his only Vedic bright spot; weakest on
  realized wealth, bond, Mahapurusha and education-adjusted status → **last**.

---

## 6. Key takeaway for the P1234 theory
The four reference charts are **not homogeneous**. On the user's own loop/bond
system, **P1 and P2 are the structurally strong charts** (2-loop Parivartana + bond
100) while **P4 — though the wealthiest — has no loop and no bond** and **P3 has the
rarest 5-loop but the weakest bond (25)**. A P1234 "positive reference" set that
weights both realized outcome AND chart structure would therefore rank **P1 highest**,
with P4 and P2 exchanging #2/#3 by emphasis, and P3 last. This is consistent with the
project's null finding that loop count does **not** predict achievement (r ≈ −0.02):
P4 (wealthiest, 0-loop) and P3 (weakest, 5-loop) sit at opposite ends of both wealth
and loop length.
