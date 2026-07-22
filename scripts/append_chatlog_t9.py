#!/usr/bin/env python3
p = "/home/user/astrology/chat_log.md"
s = open(p, encoding="utf-8").read()

t9 = """
---

## Turn 9 \u2014 2026-07-23 \u2014 Re-read all horoscopes; re-rank by "own-sign + 2/3/4/5 loop yoga = exalted" strength rubric

**User (command):** "reread all horoscopes and rerank with details normally planets in ownsign,2,3,4,5 loop yoga = exalted"

**Assistant answer (summary):** Re-read all four from the link-provided Drik Panchang longitudes + user Lagnas (no new data; re-derived). Applied the user's rubric: a planet in its **own sign (Swakshetra)** and a planet in a **2/3/4/5-loop** (Parivartana/Shrinkala) both = top ("exalted") tier; score = distinct planets that are own-sign OR in a loop, across D1 and D9 (loops from the Turns 6\u20137 closed-loop search, navamsa method).
- **Scoring:** P3 = 5 (D1 5-loop Sun,Moon,Jupiter,Mars,Mercury; also D9 Mer\u2013Sun) \u2192 top. P1 = 4 (own D1 Mars+Saturn, own D9 Mercury+Saturn, D1 2-loop Venus+Mercury). P2 = 4 (0 own; D1 2-loop Jup\u2013Sat + D9 2-loops Jup\u2013Sat & Mars\u2013Mer = 4 loop planets). P4 = 4 (own D1 Venus, own D9 Jupiter+Mercury+Saturn; 0 loop).
- **Re-rank:** D1-only = **P3 (5) > P1 (4) > P2 (2) > P4 (1)**. D1+D9 combined = **P3 (5) > P1 (4) \u2248 P2 (4) \u2248 P4 (4)** (P3 alone on top; P1/P2/P4 tie at 4, broken by composition: P1 balanced 3-own+2-loop, P2 pure-loop 0-own+4-loop, P4 pure-dignity 4-own+0-loop).
- **Contrast:** this axis REVERSES the financial ranking (P1\u2248P4 > P2 > P3) \u2014 the financially-weakest P3 tops the loop/exchange-strength axis via its unique 5-planet Shrinkala loop, while the wealthiest P4 is weakest here (its power is exaltation/placement, not exchange). Also differs from Turn-7 D9-dignity rank (P4 > P1 > P3 > P2) and exchange-network rank (P2 > P3 > P1 > P4).
- Deliverables: added report **\u00a714 STRENGTH RE-RANK** (renumbered old GAPS \u2192 \u00a715), added matching row to `matrix_dashboard.html`; `scripts/rerank_strength.py`. Committed + pushed to GitHub.

*(PAT remains redacted in this log; recommend rotation.)*
"""

if not s.endswith("\n"):
    s += "\n"
s += t9
open(p, "w", encoding="utf-8").write(s)
print("chat_log.md Turn 9 appended; length", len(s))
