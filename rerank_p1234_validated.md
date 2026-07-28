# Re-Rank of the 5 Charts (P1–P5) — P1234 / Vedic-Yoga Validation Update

**Context:** This re-rank updates `rerank_matrix_scored.md` (which ranked the 4 charts P1–P4
on the 23-dimension *worldly* research matrix) by adding the **Vedic-Yoga / P1234 validation
evidence** produced in this project (loops, bonds, Mahapurusha yogas, exchanges, P1234 status —
all from `p1234_validation/`, computed with the Drik-compatible Lahiri ayanamsa; Drik planet
data UNCHANGED). **P5 Senath** (Drik-link person, added as the 5th reference chart per user
instruction) is included on the Vedic/validation axis; his *worldly* score is **not in the
workspace** (he is not in `famous_people_birth_data.json`), so a full 50/50 integrated blend
for P5 is **blocked by missing data** (stated explicitly per the workspace rules — no guessing).

**No system changes.** Loop definition, bond logic, P1234 theory and chart method are untouched;
this only *ranks* using the new data.

---

## 1. Validation evidence per chart (from this project)

| Chart | Lagna (computed) | loop | bond | Mahapurusha | Exchange (Parivartana/loop) | ach. |
|---|---|---|---|---|---|---|
| **P1** Polgahawela Bappa (1962 ♂) | Aries | 2 | 100 | **2** (Rucaka/Mars, Sasa/Saturn) | PARI_001 (Ven–Mer) | 8 |
| **P2** Upulakshi (1997 ♀) | Taurus* | 2 | 100 | 0 | PARI_001 (Jup–Sat) | 5 |
| **P3** Senith (1995 ♂) | Pisces | **5** | 25 | 0 | LOOP_005 (only 5-loop) | 4 |
| **P4** Niromi (1967 ♀) | Taurus (Vargottama) | 0 | 0 | **1** (Malavya/Venus) | none | 9 |
| **P5** Senath (2001 ♂) | Virgo† | 2 | 100 | **1** (Malavya/Venus) | PARI_001 (Ven–Jup) | n/a‡ |

\*Upulakshi's registry time `12:00:00` is a placeholder → computed Lagna = Taurus, not the
"Aries Lagna" in the notes (data-quality flag).
†Senath's Lagna = Virgo 5°44′ from the Drik link (birthplace unknown → proxy; see data-quality).
‡Senath is a Drik-link person, NOT in `famous_people_birth_data.json`, so the workspace
contains **no achievement/profession score** for him.

---

## 2. Axis A — Worldly / realized status (prior research matrix, unchanged)

Composite (career+finance+money+fame+success+education+CEO+assets+where-wealth):

- **P4 · Niromi — 38.0**
- **P1 · Polgahawela Bappa — 34.5**
- **P2 · Upulakshi — 25.0**
- **P3 · Senith — 15.0**
- **P5 · Senath — UNKNOWN (not in workspace dataset; no guess made).**

**Rank A: P4 > P1 > P2 > P3** (P5 excluded — missing data).

---

## 3. Axis B — P1234 / Vedic-Yoga validation strength (NEW, from this validation)

Transparent 0–5 sub-scores (max 15), derived only from the validation outputs:

| Sub-score | P1 | P2 | P3 | P4 | P5 | basis |
|---|---|---|---|---|---|---|
| Exchange / loop structure | 4 | 4 | **5** | 0 | 4 | 5-loop rarest; 2-loop Parivartana strong; 0-loop = 0 |
| Bond strength | **5** | **5** | 1 | 0 | **5** | bond 100 / 20 |
| Mahapurusha (dignity yoga) | **5** | 0 | 0 | 2.5 | 2.5 | 2 Maha = 5; 1 (Malavya) = 2.5; none = 0 |
| **Vedic composite (sum)** | **14** | **9** | **6** | **2.5** | **11.5** | |

**Rank B: P1 > P5 > P2 > P3 > P4**
P1 leads on both loop/bond AND dignity (2 Mahapurusha + 2-loop + bond 100).
**P5 Senath is #2 on the Vedic axis** — he is the only chart that combines a strong
2-loop Parivartana (bond 100, like P1/P2) **WITH** a Mahapurusha (Malavya, like P4).
P4 is last on the Vedic axis (premium Malavya dignity but no loop and no bond at all).
P3 carries the rarest 5-loop but the weakest bond and no Mahapurusha.

---

## 4. Integrated re-rank (Axis A + Axis B, normalized 0–1, 50/50 default)

P1–P4 (full data):

| Chart | Worldly (norm) | Vedic (norm) | **Blend 50/50** |
|---|---|---|---|
| P1 | 0.908 | 1.000 | **0.954** |
| P4 | 1.000 | 0.179 | 0.590 |
| P2 | 0.658 | 0.643 | 0.650 |
| P3 | 0.395 | 0.429 | 0.412 |

**>>> INTEGRATED RE-RANK (P1–P4, default 50/50): P1 > P2 > P4 > P3**

**P5 Senath:** cannot be placed on the integrated 50/50 blend because Axis A (worldly) is
**missing from the workspace** (he is not a famous-person record). On the Vedic axis alone he
ranks **#2 (11.5)**, between P1 (14) and P2 (9). If/when his worldly data is supplied he can be
integrated; without it, the workspace rule is to **state the missing data, not guess**.

### Sensitivity (P1–P4, robustness of the top/bottom)
- 70% worldly / 30% vedic → **P1 > P4 > P2 > P3**
- 30% worldly / 70% vedic → **P1 > P2 > P4 > P3**
P1 is **#1 under every reasonable weighting** (strong on both axes). P3 is **#4 under every
weighting** (weak on both, despite the rare 5-loop). The only swap is **P2 ↔ P4**: P4 leads
when worldly status is weighted heavily (wealthiest); P2 leads when Vedic structure is weighted
heavily (strong 2-loop + bond 100).

---

## 5. Tiers (integrated, P1–P4; P5 flagged)

- **TIER 1 — P1 Polgahawela Bappa:** best all-round — 2nd on worldly, **1st on the Vedic
  validation axis** (2 Mahapurusha + Parivartana + bond 100).
- **TIER 2 — P2 Upulakshi / P4 Niromi (coin-flip by weight):** P4 = wealthiest, top worldly,
  but **no loop/bond/yoga structure** (Vedic-bottom); P2 = moderate wealth but solid Vedic
  structure (2-loop Parivartana + bond 100). P2 overtakes P4 once Vedic evidence is weighted ≥ ~40%.
- **TIER 2/3 — P5 Senath:** structurally the **strongest yoga combo after P1** (Parivartana +
  Malavya + Sun/Venus exaltations) → #2 on the Vedic axis; but early-career with **no workspace
  worldly score yet**, so his realized ranking is pending data.
- **TIER 3 — P3 Senith:** the rare 5-loop is his only Vedic bright spot; weakest on realized
  wealth, bond, Mahapurusha and education-adjusted status → **last among P1–P4**.

---

## 6. Key takeaway for the P1234 theory
The five reference charts are **not homogeneous**. On the user's own loop/bond system, **P1, P2
and P5 are the structurally strong charts** (2-loop Parivartana + bond 100), while **P4 — though
wealthiest — has no loop and no bond** and **P3 has the rarest 5-loop but the weakest bond (25)**.
A P1234 "positive reference" set that weights both realized outcome AND chart structure ranks
**P1 highest**, with **P5 (once his worldly data arrives) a strong #2 on pure yoga structure**.
This is consistent with the project's null finding that loop count does **not** predict achievement
(r ≈ −0.02): P4 (wealthiest, 0-loop) and P3 (weakest, 5-loop) sit at opposite ends of both wealth
and loop length.
