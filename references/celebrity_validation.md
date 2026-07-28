# Framework Validation — Celebrity Charts & Data-Quality Audit

**Method:** Computed real **sidereal (Lahiri ayanamsa)** birth charts for a set of globally
successful celebrities (birth data from indastro.com) **plus our three persons**, using
Swiss Ephemeris (`pyswisseph`). For each chart we tallied the "high-potential" markers our
repo's references use: **exaltation (Ex)**, **own-sign (Own)**, **debilitation (Db)**,
**Gajakesari** (Moon in a Kendra from Jupiter), and **Mahapurisa** (Mars/Mercury/Jupiter/Venus/Saturn
in a Kendra in its own/exaltation sign). `strong = Ex + Own`. Script: `scripts/validate_framework.py`.

> Caveats: local birth times used as given (UTC via standard offsets); lagna/house-based items are
> approximate to ±1 sign from time/coordinate uncertainty; **aspects not computed**. Dignity is
> sign-based and robust to small time errors.

---

## 1. Celebrity results (the "findings" from the Indastro list)

| Celebrity | Lagna | Ex | Own | Db | Gajakesari | Mahapurisa | strong |
|-----------|-------|----|-----|----|-----------|------------|--------|
| Elon Musk | Cancer | 1 | 2 | 0 | ✅ | Mars | **3** |
| Beyoncé | Aries | 1 | 1 | 2 | — | — | 2 |
| A.R. Rahman | Gemini | 1 | 1 | 0 | ✅ | — | 2 |
| Lionel Messi | Aquarius | 1 | 2 | 0 | — | Venus | **3** |
| Sachin Tendulkar | Virgo | 2 | 0 | **3** | — | — | 2 |
| Aamir Khan | Pisces | 0 | 2 | 1 | ✅ | — | 2 |
| Billie Eilish | Pisces | 0 | 0 | 0 | — | — | **0** |
| Rihanna | Aries | 1 | 1 | 0 | — | — | 2 |
| Tom Brady | Libra | 0 | 0 | 0 | ✅ | — | **0** |

**Conclusion 1 — dignity markers are *supportive, not deterministic*.**
Successful people often (Musk, Messi, Rahman, Aamir, Rihanna, Beyoncé) but **not always**
show exaltation/own-sign strength: **Billie Eilish and Tom Brady have strong = 0** yet are at the
top of their fields. Conversely, **Sachin Tendulkar has THREE debilitations** and is a national icon.
This is exactly the Astrokarak lesson already in `exaltation_debilitation.md`: *debilitation is a
description of quality, not a verdict.* Accurate prediction therefore needs **dasha timing, house
lordship, aspects, and life context** on top of dignity — dignity counting alone is insufficient.

---

## 2. ⚠️ CRITICAL data-quality audit — our three persons

I cross-checked the **original three-person JSON** (the "Drik Panchang" data the whole earlier
analysis was built on) against the independent ephemeris. **Planet signs must match regardless of
ayanamsa** (those differ by only ~1–2°, never whole signs).

| Person | Original JSON vs independent computation | Verdict |
|--------|-------------------------------------------|---------|
| **Person 3 (1995)** | Sun Cancer, Moon Sagittarius, Mars Virgo, Mercury Leo, Jupiter Scorpio, Venus Cancer, Saturn Pisces — **all signs match** | ✅ **Reliable** (house numbers off by one in JSON, but signs correct; debility labels already corrected) |
| **Person 1 (1962)** | JSON narrative says Moon *Sagittarius*, Venus *Taurus*; computation gives Moon **Aquarius**, Venus **Gemini** (Mars-in-Aries "own" does match) | ⚠️ **Partially unreliable** |
| **Person 2 (1997)** | JSON claims Aries lagna + **Moon exalted**, **Mars exalted**, **Jupiter own**, **Saturn own**; computation gives Taurus lagna, Moon exalted ✅ but **Mars in Virgo (NOT Capricorn/exalted)**, **Jupiter in Capricorn DEBILITATED (NOT Sagittarius/own)**, **Saturn in Pisces (NOT Aquarius/own)** | ❌ **Substantially wrong** |

**Implication:** the earlier financial ranking (Person 2 ranked #1 as a "clean chart with two
exaltations + four yogas") was built on **erroneous source data**. The "four yogas" (Chandra Mangal,
Ruchaka, Hamsa, Shubha Kartari) and "two exaltations" claims for Person 2 do **not** survive an
independent computation. (The ephemeris itself is verified — it reproduces Elon Musk's published
sidereal chart exactly, and Person 3's signs exactly.)

---

## 3. Corrected charts for our three persons (Lahiri, whole-sign)

**Person 1 (1962-05-27, Dehiwatta) — Aries lagna**
- Mars (1st/8th lord) **own in lagna** ✅; Saturn (10th/11th lord) **own in 10th** → strong Raja-yoga (Sasa Mahapurisa); Moon (11th lord) in 11th (gains); Jupiter (9th lord) in 11th (fortune); Venus (2nd/7th lord) in 2nd (wealth/partnership); **Gajakesari** ✅; Mahapurisa: Mars + Saturn.
- Reading: a **solid, prosperous, self-made business chart** — own lagna + own 10th + gains lords placed. Far stronger than the sparse original narrative suggested.

**Person 2 (1997-03-14, Colombo) — Taurus lagna**
- Moon **exalted in 1st** ✅ (emotional/financial strength, good earnings drive).
- BUT 9th lord **Jupiter debilitated in 9th**, 11th lord **Mercury debilitated in 11th**, Saturn (10th/11th lord) in 12th → **weak luck (9th) and weak gains (11th)**.
- Reading: **mixed/moderate** — one strong exaltation undermined by debilitated 9th & 11th lords. Not the "clean powerhouse" the original data implied.

**Person 3 (1995-08-07, Colombo) — Aries lagna** (signs match JSON; debility labels corrected earlier)
- 9th lord **Moon in 9th** (good dharma/fortune), 5th lord **Mercury in 5th** (intellect/children), 2nd/7th lord **Venus in 4th** (wealth/family) — genuine Raja/Putra-type placements.
- BUT 11th lord **Saturn in 12th** (weak gains), **combust Sun** (4th lord) in 4th, Mars (1st/8th lord) in 6th.
- Reading: **moderate, service-oriented** — decent dharma/intellect houses, but gains weak and some afflictions.

---

## 4. REVISED financial ranking (based on corrected charts)

| Rank | Person | Why (corrected) |
|------|--------|-----------------|
| 🥇 1 | **Person 1** | Own lagna (Mars) + own 10th (Saturn) = Raja yoga; gains/fortuna lords in 11th; Gajakesari. Structurally the strongest, prosperous, self-made. |
| 🥈 2 | **Person 3** | 9th & 5th lords well-placed (dharma/intellect); but 11th lord in 12th + combust Sun → moderate, service-bound. |
| 🥉 3 | **Person 2** | Moon exalted (drive/earnings) but **9th & 11th lords debilitated** → weak luck & gains. Previously over-rated due to bad source data. |

**This reverses the earlier ranking** (which put Person 2 first on false "exaltations").

---

## 5. How to predict more accurately (synthesis)
1. **Verify raw positions first.** Dignity/yoga analysis is only as good as the input chart — audit it against an independent ephemeris (as done here) before trusting any ranking.
2. **Use dignity as a supporting lens, not a verdict** (Brady/Billie = 0 yet legendary; Sachin = 3 debils yet iconic).
3. **Prioritize house lordship & placement** (e.g., 9th/11th lords for luck/gains; 10th lord for career) over isolated exaltation counts.
4. **Add dasha timing & aspects** — the missing layers for true predictive accuracy.
