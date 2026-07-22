#!/usr/bin/env python3
import io
p = "/home/user/astrology/all_four_reanalysis.md"
s = open(p, encoding="utf-8").read()

# ---------- 1) Replace the trailing D9-status paragraph of Section 13 ----------
marker = "**D9 status:**"
tail_marker = "## 14. GAPS"
i = s.index(marker)
j = s.index(tail_marker)
assert i < j
new_d9 = '''**D9 (Navamsa) — derived from the link‑provided Drik Panchang longitudes via the standard navamsa division (METHOD per user‑supplied astrologylover.com "how to read navamsa chart" + Scribd "Understanding the D9 Navamsha Chart"):**
- Each 30° sign → 9 navamsas of 3°20′; **odd signs** (Aries/Gemini/Leo/Libra/Sagittarius/Aquarius) start the navamsa from the same sign; **even signs** (Taurus/Cancer/Virgo/Scorpio/Capricorn/Pisces) start from the 9th sign. D9 Lagna: **P1 Gemini** (Aries 9°26′), **P3 Sagittarius** (Pisces 6°), **P4 Taurus** (Vargottama — user), **P2 unknown** (no Lagna degree supplied). astro‑seek navamsa `typ=9` still 404s, so D9 signs are navamsa‑derived from Drik longitudes (link INPUT + link METHOD) — not Swiss‑Ephemeris/computed ephemeris.

**D9 planet signs (navamsa, from Drik longitudes) + dignity:**

| Planet | P1 D9 | P2 D9 | P3 D9 | P4 D9 |
|---|---|---|---|---|
| Sun | Aries (EX) | Libra (DEB) | Virgo | Cancer |
| Moon | Gemini | Pisces | Aquarius | Pisces |
| Mars | Taurus | Gemini | Virgo (VARG) | Capricorn (EX) |
| Mercury | Virgo (OWN) | Scorpio | Leo (VARG) | Gemini (OWN) |
| Jupiter | Cancer (EX) | Aquarius | Libra | Pisces (OWN) |
| Venus | Virgo (DEB) | Virgo (DEB) | Leo | Gemini |
| Saturn | Aquarius (OWN) | Pisces (VARG) | Scorpio | Aquarius (OWN) |
| Rahu | Leo | Gemini | Scorpio | Leo |
| Ketu | Aquarius | Sagittarius | Taurus | Aquarius |

*(VARG = Vargottama = same sign in D1 & D9; per astrologylover/Scribd a Vargottama planet is "very strong" — even a debilitated Vargottama gives wealth/fame with struggle.)*

**D9 dignity / strength** (own–exalt–debilitated; astrologylover: *"planet exalted in birth but debilitated in D9 gives debilitation result"*):
- **P4 — STRONGEST navamsa:** Mars EX + Mercury/Saturn/Jupiter OWN + Lagna Vargottama (Taurus) → 4 planets own/exalt, 0 debilitated. Her wealth is the most "certain" of the four in D9.
- **P1 — strong but Venus weak:** Sun EX + Jupiter EX + Mercury/Saturn OWN, but **Venus DEBILITATED in Virgo** (and not exchanging) → the D1 Venus–Mercury promise is diluted in D9.
- **P3 — clean, two Vargottamas:** Mars & Mercury VARGOTTAMA, rest neutral, 0 debilitated → the two key 5‑loop members are navamsa‑empowered.
- **P2 — weakest dignity:** Sun & Venus DEBILITATED, only Saturn Vargottama → but her exchange repeats (below).

**D9 closed‑loop (Parivartana/Shrinkala, lengths 2–5):**
- **P1:** **NONE** — Venus & Mercury both fall in Virgo in D9 → conjunction, not exchange; the D1 2‑loop BREAKS.
- **P2:** **2‑loop Jupiter ↔ Saturn (REPEATS from D1)** + **NEW 2‑loop Mars ↔ Mercury** (Mars Gemini / Mercury Scorpio). Jupiter–Saturn now confirmed in BOTH D1 and D9 = strengthened per Scribd/Reddit "repetition strengthens."
- **P3:** **NEW 2‑loop Mercury ↔ Sun** (Mercury Leo / Sun Virgo) → 9th & 10th houses from D9 Lagna Sagittarius = **Dharma‑Karma (9th/10th) exchange in navamsa**. The D1 5‑loop does not repeat as a 5‑loop.
- **P4:** **NONE.**

**D1 ↔ D9 — repeated (strengthened) / new / broken:**

| Person | D1 loop | D9 loop | Verdict |
|---|---|---|---|
| P1 | 2‑loop Venus↔Mercury | none | **BROKEN in D9** (Venus debil Virgo) → D1‑only, diluted |
| P2 | 2‑loop Jupiter↔Saturn | 2‑loop Jupiter↔Saturn (**repeat**) + 2‑loop Mars↔Mercury | **REPEATED/STRENGTHENED** + new |
| P3 | 5‑loop (Jup→Mar→Mer→Sun→Moon) | 2‑loop Mercury↔Sun (new) | loop members Mars/Mercury **Vargottama** → navamsa‑empowered |
| P4 | none | none | no exchange (wealth via dignity/yogas) |

**Combined D1 + D9 re‑ranking (Parivartana/Shrinkala axis):**
- **Exchange‑network rank (D1+D9):** **P2 (1)** — only exchange that REPEATS in both charts (Jupiter–Saturn) + new Mars–Mercury, so her NRY + 10th/12th foreign‑MNC signal is the most reinforced. **P3 (2)** — largest latent 5‑loop + two Vargottama members + new Dharma‑Karma D9 exchange. **P1 (3)** — D1 2‑loop only, Venus debilitated/diluted in D9. **P4 (4)** — no exchange (top on dignity instead).
- **D9 dignity/strength rank:** **P4 (1) > P1 (2) > P3 (3) > P2 (4).**
- **Final composite (all axes):** Financial/realized **P1 ≈ P4 > P2 > P3** (unchanged — D9 *confirms* P4 as most‑certain wealth via strongest navamsa; P1 strong but D9 Venus caveat). Exchange‑network **P2 > P3 > P1 > P4**. Astrology aptitude **P3 > P4 ≈ P1 > P2**. Foreign **P4 ≈ P2 > P1 > P3**.

*(Visual board: `shrinkala_dashboard.html` updated with D9 tables + combined re‑rank.)'''

s = s[:i] + new_d9 + "\n\n" + s[j:]

# ---------- 2) Add D9 rows to the Section 12 matrix ----------
lines = s.split("\n")
out = []
for ln in lines:
    out.append(ln)
    if ln.startswith("| Key yogas |"):
        out.append("| D9 exchange (D1+D9) | none (Venus\u2011Mer BREAKS in D9) | Jupiter\u2011Sat REPEATS + new Mars\u2011Mer | new Mer\u2011Sun (Dharma\u2011Karma) | none |")
        out.append("| D9 dignity/strength | Strong (2 EX+2 OWN; Venus DEB) | Weakest (Sun/Venus DEB; Sat VARG) | Clean (Mars/Mer VARG; 0 DEB) | **Strongest** (Mars EX+Mer/Jup/Sat OWN; Lagna VARG) |")
        out.append("| Combined exchange rank | 3 | 1 (repeats) | 2 (empowered) | 4 (none) |")
s = "\n".join(out)

# ---------- 3) Update Section 14 gap #4 ----------
s = s.replace(
    "4. **D9/D10/D11** \u2014 still open; astro-seek navamsa/dashamsha/ekadashamsha calculators can confirm yogas. Not yet fetched.",
    "4. **D9** \u2014 CLOSED via navamsa method (derived from Drik Panchang longitudes + astrologylover.com/Scribd D9 references; astro-seek `typ=9` still 404). **D10/D11** \u2014 still open; astro-seek dashamsha/ekadashamsha calculators can confirm career/yoga. Not yet fetched.")

open(p, "w", encoding="utf-8").write(s)
print("report updated OK; length", len(s))
