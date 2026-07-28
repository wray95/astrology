#!/usr/bin/env python3
p = "/home/user/astrology/all_four_reanalysis.md"
s = open(p, encoding="utf-8").read()

start = "## 8. NEECHABHANGA RAJA YOGA (bavishyavani 5 rules)"
end = "\n## 9. FAME / CAREER / EXPLOSIVE RAHU (Reddit)"
i = s.index(start); j = s.index(end)
assert i < j

new_sec8 = '''## 8. NEECHABHANGA RAJA YOGA (bavishyavani 5 rules + indastro + Reddit)

**Method (user-supplied links):**
- *bavishyavani.in (5 rules):* Rule 1 = debilitated planet's dispositor in a Kendra from Lagna; **Rule 3 = mutual exchange (Parivartana) involving the debilitated planet cancels debilitation**; Rules 2/4/5 (aspected by benefic, in Kendra, etc.).
- *indastro.com/neechbhang-raja-yoga (Moon-sign based):* NRY forms when (1) the debilitated planet's **dispositor is in a Kendra FROM THE MOON**, or (2) it is in its exaltation sign from Moon, or (3) the lord of its dispositor + lord of the exalted planet are in **mutual Kendra from the ascendant**, or (4) the planet exalted in that sign is in Kendra from Moon, or (5) it is debilitated in D1 but **exalted in D9**. **Caveat (indastro): a COMBUST or RETROGRADE debilitated planet does NOT form NRY.** (Navamsa NRY: each planet forms NRY in its debilitation sign — Sun Libra, Moon Scorpio, Mars Cancer, Mercury Pisces, Jupiter Capricorn, Venus Virgo, Saturn Aries.)
- *Reddit (prior turn):* "Parivartana is not neecha Bhanga yoga. So it does not cancel out the debilitation." → exchange helps but is not, per that view, strict Neecha-Bhanga.

**Moon signs (Drik):** P1 Aquarius · P2 Taurus · P3 Sagittarius · P4 Libra. (Kendra from Moon used for indastro Rules 1/2/4.)

**Per-person reconciliation (D1):**

| Person | Debilitated planet (D1) | bavishyavani | indastro | Reddit | Net NRY verdict |
|---|---|---|---|---|---|
| **P1** | none | n/a | n/a | n/a | **None needed** (born wealthy). D9 Venus debil Virgo but no cancellation → no NRY. |
| **P2** | Jupiter (Capricorn) | **YES** (Rule 3 Parivartana Jup↔Sat) | **NO** — dispositor Saturn in Pisces = 11th from Moon (Taurus), not Kendra; mutual-Kendra (Sat/Mars) from Aries unmet; D9 Jupiter Aquarius not exalted | exchange ≠ cancellation | **Framework-dependent / disputed:** confirmed only under bavishyavani (classical Parivartana); indastro & Reddit do NOT treat the exchange as strict Neecha-Bhanga. Jupiter's debility is at least *relieved/mitigated* by the exchange (which REPEATS in D1+D9, Turn 7) but strict NRY cancellation is not secure. |
| **P3** | Venus (Cancer, per link) | **Likely YES** (Rule 1: dispositor Moon in 10th Kendra from Pisces Lagna) | **YES by Rule 1** (dispositor Moon in Kendra from Moon = 1st) — **BUT BLOCKED**: Venus is COMBUST (3.7° from Sun in Cancer) → indastro says combust planet does not form NRY | exchange not the issue; combust blocks | **Pending/conditional:** hinges on (a) accepting the link's "Venus debilitated in Cancer" claim (standard debil is Virgo — if Venus is actually not debilitated, no NRY), and (b) indastro's combustion caveat. If debil accepted + combustion ignored → NRY forms (bavishyavani + indastro R1); if indastro combustion rule applied → blocked. |
| **P4** | none (no flagged debil; D9 also 0 debil) | n/a | n/a | n/a | **None needed** (born wealthy). |

**Updated NRY verdict:**
- **P1 / P4:** no NRY (no debilitated planet) — unchanged.
- **P2:** **downgraded from "CONFIRMED" to "framework-dependent."** The Jupiter–Saturn Parivartana is a genuine, D1+D9-repeating strong yoga (Turn 7) and a classical Neecha-Bhanga per bavishyavani/Parashara; however the user-supplied indastro method (Moon-sign, dispositor-in-Kendra-from-Moon) does **not** register it, and Reddit warns exchange ≠ cancellation. Read as: Jupiter's debility is *mitigated*, not definitively cancelled.
- **P3:** remains **conditional** — gains indastro Rule-1 support (dispositor Moon in Kendra from Moon) IF the "Venus debilitated in Cancer" link assertion is accepted, but is **blocked by indastro's combustion rule** (Venus combust). Still pending Venus-sign confirmation.
- **D9 NRY foot-note:** P1's D9 Venus is debilitated in Virgo with dispositor Mercury in Virgo (4th/Kendra from D9 Moon Gemini) → a navamsa NRY is *possible* per indastro, but P1 has no D1 debilitation so this does not create a D1 NRY; it only underscores the D9 Venus weakness noted in Turn 7.'''

s = s[:i] + new_sec8 + s[j:]

# Update Section 12 matrix NRY row
old_nry = "| NRY | none needed | CONFIRMED (Rule 3) | Pending (Venus) | none needed |"
new_nry = "| NRY | none needed | Framework-dependent (bavishyavani R3 vs indastro/Reddit: not strict) | Pending: link Venus-debil → bavishyavani+indastro R1, but Venus COMBUST blocks (indastro) | none needed |"
assert old_nry in s
s = s.replace(old_nry, new_nry, 1)

# Update Section 13 markdown table NRY cell for P2
old_13 = "NRY (bavishyavani R3); Reddit \u2260 neecha bhanga"
new_13 = "NRY: bavishyavani R3 YES; indastro NO (dispositor not Kendra from Moon); Reddit \u2260 neecha bhanga \u2192 framework-dependent"
assert old_13 in s
s = s.replace(old_13, new_13, 1)

open(p, "w", encoding="utf-8").write(s)
print("report Section 8 + NRY rows updated OK; length", len(s))
