# Spouse Prediction — "Rich / Wealthy Spouse" Analysis

**Source:** Astrologylover — *"Rich and Wealthy Spouse in Astrology"* (Debraj Roy),
https://astrologylover.com/rich-wealthy-spouse-astrology/

Applied to the **three corrected charts** (Lahiri sidereal, whole-sign; from `celebrity_validation.md`).
Assumption: all three natives are **male** → **Venus = spouse significator** (for a female we would
use Jupiter instead). Full accuracy per the source also requires the **Navamsa (D9)** and
**Upapada Lagna (UL / Arudha of 12th)** — flagged as "next step" below; this analysis is D1-based.

---

## Indicators used (from the article)
1. **Lagna Lord in 7th** → ambitious, career-oriented, accomplished spouse.
2. **11th Lord in 7th / conjunct 7th Lord (strong)** → prosperous, wealthy partner.
3. **7th Lord conjunct a Yogakaraka, or Yogakaraka in 7th** → financial fortune after marriage; spouse from good family.
4. **Strong 7th Lord** (own/exaltation) → spouse from wealthy family.
5. **Sreenath Yoga:** 7th Lord exalted in 10th **with** 9th Lord → rise in fortune post-marriage.
6. **Venus in 9th** → positive changes / fortune after marriage.
7. **Venus conjunct Sun (Sun ahead degree-wise)** → **wealthy spouse & improved fortune after marriage**.
8. Navamsa: exalted/own 7th Lord, strong UL Lord → wealthy/prestigious spouse family.
9. *Key nuance:* "rich" often means the **spouse's condition is better than the native's** — not literally a millionaire.

---

## Corrected charts — spouse factors

### Person 1 (1962) — Aries lagna, male
- 7th house **Libra (empty)**; 7th Lord **Venus in Gemini (3rd)** — neutral sign, moderate (not own/exalted → not a "strong 7th Lord").
- Lagna Lord Mars in 1st (not 7th). 11th Lord Saturn in 10th (own, strong) but **not in 7th / not conjunct 7th Lord**.
- No Yogakaraka-in-7th, no Sreenath Yoga, Venus not in 9th, **Venus–Sun NOT conjunct** (Sun Taurus, Venus Gemini).
- Native's own 2nd & 11th houses are strong (Sun+Mercury in 2nd; Moon+Jupiter in 11th).
- **Reading:** spouse from a respectable/comfortable family, stable marriage; **no specific "rich-spouse" combination fires**. Since the native is already wealthy, a "spouse richer than native" is not indicated. → **Moderate / comfortable spouse.**

### Person 2 (1997) — Taurus lagna, male
- 7th house **Scorpio (empty)**; 7th Lord **Mars in Virgo (5th)** — Virgo is Mars's enemy sign → 7th Lord moderately weak.
- Lagna Lord Venus in 10th (not 7th). 11th Lord Saturn in 12th (not in 7th).
- ✅ **Venus conjunct Sun in Aquarius (10th), Sun ahead by 4.9°** → article's *wealthy spouse & fortune after marriage*. Venus in 10th (career/public house) → spouse in a professional / public-facing role, linked to the native's career.
- No Sreenath Yoga (7th Lord not exalted in 10th).
- **Reading:** spouse likely **career-oriented / professional, from a decent-to-good family**; financial fortune improves after marriage. The Venus–Sun-in-10th points to a spouse with public/professional standing. → **Moderate-to-strong positive** for a well-placed spouse (7th Lord in enemy sign is the tempering factor).

### Person 3 (1995) — Aries lagna, male
- 7th house **Libra (empty)**; 7th Lord **Venus in Cancer (4th)** — neutral sign, moderate.
- Lagna Lord Mars in 1st. 11th Lord Saturn in 12th (not in 7th).
- ✅ **Venus conjunct Sun in Cancer (4th), Sun ahead by 3.7°** → article's *wealthy spouse & fortune after marriage*. Venus in 4th (home/happiness) → spouse brings domestic stability & wealth.
- ⚠️ Venus is **combust** (3.7° from Sun) → some marital friction / delay alongside the promise.
- Native's 2nd & 11th houses are **empty/weak** → native is not wealthy. Per the article's definition ("rich = better than the native"), this makes the "rich spouse" promise **more meaningful** here than for Person 1.
- **Reading:** **strong indication of a spouse financially better-off than the native and a rise in fortune after marriage** — but with some marital adjustment (combust Venus). Possible spouse from a comfortable/prestigious family. → **Positive rich-spouse signal** (most "relative" wealth gain).

---

## Summary — "rich/wealthy spouse" outlook

| Person | Key signal | Outlook |
|--------|-----------|---------|
| **Person 3** | Venus–Sun conjunct (Sun ahead) in 4th; native less wealthy | **Strongest relative rich-spouse signal** + fortune after marriage (combust Venus = some friction) |
| **Person 2** | Venus–Sun conjunct (Sun ahead) in 10th | **Professional / well-placed spouse** + fortune after marriage |
| **Person 1** | No rich-spouse combination; comfortable own wealth | **Moderate / comfortable spouse**, not indicated as richer than native |

**Note the inversion vs the financial-ranking:** for *native* wealth Person 1 led; for a *rich spouse*,
Persons 2 & 3 (especially 3) lead, because the article's "rich" is often *relative to the native*.

---

## Next step for higher accuracy
The article stresses **Navamsa (D9)** and **Upapada Lagna (UL)**. I can compute:
- D9 placements (esp. 7th Lord in D9 own/exalted, Venus Vargottama, Sun in 7th of D9), and
- Upapada Lagna (Arudha of 12th) and its lord's strength in D9,
to firm up these spouse predictions. Say the word and I'll extend `scripts/validate_framework.py`
to emit D9 + UL and re-run.
