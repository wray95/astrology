#!/usr/bin/env python3
p = "/home/user/astrology/chat_log.md"
s = open(p, encoding="utf-8").read()

t8 = """
---

## Turn 8 \u2014 2026-07-23 \u2014 Neechbhang Raja Yoga re-check via indastro method + reconciliation

**User (data fed / command):** Supplied the NRY method link (plus the navamsa link from Turn 7):
- https://www.indastro.com/learn-astrology/yoga-dasa/neechbhang-raja-yoga.html (method: NRY is **Moon-sign based**; forms when the debilitated planet's **dispositor is in a Kendra FROM THE MOON**, OR it is in its exaltation sign from Moon, OR the lord of its dispositor + lord of the exalted planet are in **mutual Kendra from the ascendant**, OR the planet exalted in that sign is in Kendra from Moon, OR it is debilitated in D1 but **exalted in D9**. **Caveat: a COMBUST or RETROGRADE debilitated planet does NOT form NRY.** Navamsa NRY: each planet forms NRY in its debilitation sign.)
- (navamsa link already used Turn 7: astrologylover.com/how-to-read-navamsa-chart/)
Implicit command: re-check the NRY analysis for all four using the indastro framework and reconcile with the bavishyavani (Rule 3 Parivartana) and Reddit ("Parivartana \u2260 Neecha-Bhanga") positions already recorded.

**Assistant answer (summary):** Applied indastro's Moon-sign rules (Moon signs from Drik: P1 Aquarius, P2 Taurus, P3 Sagittarius, P4 Libra) to the four charts:
- **P1 / P4:** no debilitated planet in D1 (or D9) \u2192 NRY not applicable; unchanged.
- **P2 (Jupiter debil in Capricorn, Aries Lagna, Moon Taurus):** bavishyavani Rule 3 (Jupiter\u2194Saturn Parivartana) says NRY = YES, but **indastro says NO** \u2014 dispositor Saturn sits in Pisces = 11th from Moon (Taurus), NOT a Kendra; mutual-Kendra (Saturn/Mars from Aries) also unmet; D9 Jupiter (Aquarius) not exalted. Reddit agrees exchange \u2260 cancellation. \u2192 **NRY downgraded from "CONFIRMED" to "framework-dependent / disputed."** The Jupiter\u2013Saturn exchange remains a genuine, D1+D9-repeating strong yoga (Turn 7) that *mitigates* the debility, but strict Neecha-Bhanga cancellation is not secure under indastro.
- **P3 (Venus asserted debilitated in Cancer per link, Pisces Lagna, Moon Sagittarius):** indastro Rule 1 gives NRY (dispositor Moon = 1st/Kendra from Moon) \u2014 BUT Venus is **COMBUST** (3.7\u00b0 from Sun in Cancer) \u2192 indastro's combustion caveat **blocks** NRY. Also hinges on accepting the (non-standard) "Venus debilitated in Cancer" link claim (standard debil is Virgo). \u2192 **still Pending/conditional.**
- Updated report Section 8 (full bavishyavani + indastro + Reddit reconciliation table), Section 12 matrix NRY row, Section 13 NRY cell; updated both dashboards' NRY references.
- Deliverables: report \u00a78/\u00a712/\u00a713 NRY reconciliation; `matrix_dashboard.html` + `shrinkala_dashboard.html` NRY notes; `scripts/update_report_nry.py`, `scripts/patch_dashboards_nry.py`. Committed + pushed to GitHub.

*(PAT remains redacted in this log; recommend rotation.)*
"""

if not s.endswith("\n"):
    s += "\n"
s += t8
open(p, "w", encoding="utf-8").write(s)
print("chat_log.md Turn 8 appended; length", len(s))
