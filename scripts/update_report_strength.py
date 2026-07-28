#!/usr/bin/env python3
p = "/home/user/astrology/all_four_reanalysis.md"
s = open(p, encoding="utf-8").read()

marker = "## 14. GAPS & NEXT STEPS"
assert marker in s, "gaps header not found"

new_sec14 = '''## 14. STRENGTH RE-RANK — own-sign + loop-yoga = "exalted" (user rubric)

**Rubric (user, this turn):** *"normally planets in ownsign, 2/3/4/5 loop yoga = exalted."* Applied link-only: planet signs from Drik Panchang (§2); loops from the D1+D9 closed-loop search (Turns 6–7, navamsa method). A planet in its **own sign (Swakshetra)** and a planet in a **2/3/4/5-loop** (Parivartana/Shrinkala) are both counted as the top ("exalted") tier. **Score = distinct planets that are own-sign OR in a loop, across D1 and D9** (re-read from the longitudes + user Lagna).

**Per-person scoring:**

| Person | Own-sign D1 | Own-sign D9 | D1 loop (members) | D9 loop (members) | Top-tier (own∪loop) | Count |
|---|---|---|---|---|---|---|
| **P3 Senith** | none | none | 5-loop: Sun,Moon,Jupiter,Mars,Mercury | 2-loop: Mercury,Sun | Sun,Moon,Jupiter,Mars,Mercury | **5** |
| **P1 Bappa** | Mars, Saturn | Mercury, Saturn | 2-loop: Mercury,Venus | none | Mars,Mercury,Saturn,Venus | **4** |
| **P2 Upulakshi** | none | none | 2-loop: Jupiter,Saturn | 2-loop: Jupiter,Saturn + Mars,Mercury | Jupiter,Mars,Mercury,Saturn | **4** |
| **P4 Niromi** | Venus | Jupiter,Mercury,Saturn | none | none | Venus,Jupiter,Mercury,Saturn | **4** |

**Re-rank:**
- **D1-only** (own-sign D1 ∪ loop D1): **P3 (5) > P1 (4) > P2 (2) > P4 (1).**
- **D1 + D9 combined:** **P3 (5) > P1 (4) ≈ P2 (4) ≈ P4 (4)** — P3 alone on top (its 5-loop maxes the score); P1/P2/P4 tie at 4, broken by composition:
  - **P1** = balanced (3 own-sign + 2 loop) — has BOTH strengths.
  - **P2** = pure exchange (0 own-sign + 4 loop) — loop-driven; its Jupiter–Saturn exchange REPEATS D1+D9 (Turn 7).
  - **P4** = pure dignity (4 own-sign + 0 loop) — Swakshetra strength, but NO exchange yoga.

**Key contrast with prior rankings (this axis is NEW — it measures exchange-network + Swakshetra, NOT realized wealth):**
- Financial/realized (§10): **P1 ≈ P4 > P2 > P3** — REVERSED here.
- D9 dignity (Turn 7): **P4 > P1 > P3 > P2** — P4 #1 on dignity (Mars exalt + 3 own in D9); those exaltations are NOT "loop/own-sign" so they don't count under this rubric.
- Exchange-network (Turn 7, repetition-weighted): **P2 > P3 > P1 > P4** — differs again (P2's repeated exchange weighted highest there).
- **Strength (this §14):** **P3 > P1 > P2 ≈ P4** — the financially-weakest (P3) tops the loop/exchange-strength axis via its unique 5-planet Shrinkala loop; the wealthiest (P4) is weakest here because its power is exaltation/placement (Malavya, Gaja Kesari), not exchange networks.

**Read:** P3's chart is strongest on *yoga-connectivity* (a 5-loop ties 5 planets across Kendra+Trikona) → highest "exalted-via-loop" credit, but the loop is largely latent (Sun debilitated in it; activates only across Moon→Mars→Jupiter dashas) so it does not translate to realized wealth. P4's wealth is real and certain (Turn 7 D9 dignity #1) but structurally different — built on exaltation/placement, not on the own-sign/loop axis measured here.

## 15. GAPS & NEXT STEPS'''

s = s.replace(marker, new_sec14, 1)
open(p, "w", encoding="utf-8").write(s)
print("report §14 (strength re-rank) added, GAPS -> §15; length", len(s))

# ---- matrix_dashboard.html: add a Strength re-rank row after Combined exchange rank ----
m = "/home/user/astrology/matrix_dashboard.html"
ms = open(m, encoding="utf-8").read()
anchor = '<tr><td class="dim">Combined exchange rank</td><td class="a">3</td><td class="g">1 (repeats)</td><td class="a">2 (empowered)</td><td class="r">4 (none)</td></tr>'
assert anchor in ms
newrow = anchor + '\n      <tr><td class="dim">Strength re-rank (own-sign+loop=exalted)</td><td class="a">4 (#2)</td><td class="a">4 (tie)</td><td class="g">5 (#1)</td><td class="a">4 (tie)</td></tr>'
ms = ms.replace(anchor, newrow, 1)
open(m, "w", encoding="utf-8").write(ms)
print("matrix_dashboard.html strength row added")
