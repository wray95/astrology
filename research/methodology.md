# METHODOLOGY — Fixed Calculation Choices
## Research Project v2 | Established 25 Jul 2026

---

## 1. AYANAMSA

**Choice:** Lahiri (Chitra Paksha)

**Rationale:** Most widely used in Vedic astrology. Used by AppliedJyotish, 
Astro-seek, Drik Panchang. B.V. Raman, KP, and True Chitra Paksha produce 
slightly different results — mismatches with reference calculators can be 
**ayanamsa artifacts**, not calculation errors.

**Formula used:** J2000.0 baseline (23°51'25" at epoch) + linear precession 
(50.27 arcseconds/year).

**Known discrepancy:** Our linear formula differs from IAU 2006 precise formula 
used by Swiss Ephemeris by ~9 months in dasha dates. This root cause is documented.

---

## 2. HOUSE SYSTEM

**Choice:** Whole Sign Houses

**Rationale:** Standard for classical Vedic technique (Parashara). Houses = signs.
Placidus is used by AppliedJyotish for their Kundali display, but our
analysis uses Whole Sign for yoga classification, house lord placement,
and all classical framework application.

**When Placidus is used:** Noted explicitly in the specific analysis (rare).

---

## 3. EPHEMERIS

**Choice:** Skyfield + JPL DE421

**Alternative for reference comparison:** Swiss Ephemeris (used by AppliedJyotish, 
Astro-seek, Drik Panchang)

**Known discrepancy:** JPL DE421 vs Swiss Ephemeris produce Moon longitudes 
differing by ~0.05-0.15°, which can shift Nakshatra boundaries in edge cases.
This is a documented limitation — not an error.

---

## 4. TIMEZONE / DST RESOLUTION

**Choice:** Manual historical timezone assignment per known Sri Lanka rules:

| Period | SL Timezone |
|---|---|
| Pre-1996 | UTC+5:30 |
| 1996–2006 | UTC+6:00 |
| Post-2006 | UTC+5:30 |

**Source:** IANA tz database (Asia/Colombo).

**Limitation:** P2 Upulakshi (1997) uses placeholder TOB 12:00 — the timezone
is correct (+6:00) but the birth time itself is unreliable.

---

## 5. VIMSHOTTARI DASHA CALCULATION

**Method:** Moon's sidereal longitude → Nakshatra → Nakshatra lord → 
remaining arc balance → proportional balance in years → sequential MD/AD/PD.

**Year length:** 365.2425 days (Gregorian mean). Dates computed by fractional
year addition.

**Sequence:** Ketu(7) → Venus(20) → Sun(6) → Moon(10) → Mars(7) → 
Rahu(18) → Jupiter(16) → Saturn(19) → Mercury(17).

---

## 6. D9 (NAVAMSA) CALCULATION

**Method:** Standard Parashara navamsa. Each 30° sign divided into 9 parts 
of 3°20'. Navamsa sign = (base triplicity group + navamsa number) mod 12.

**Known limitation:** Degrees in astrodb_loops.json are ROUNDED to whole numbers.
D9 positions are approximate (±~1 navamsa). This is sufficient for vargottama
counting but not for pada-level analysis.

---

## 7. RODDEN GRADING

**Applied grading scale:**

| Grade | Definition | Included in hypothesis testing? |
|---|---|---|
| **AA** | Birth certificate / official record | ✅ Yes |
| **A** | Birth record quoted by family/memory | ✅ Yes |
| **B** | Biography / autobiography | ⚠️ Included with flag |
| **C** | No time given / rectified | ❌ Excluded |
| **DD** | Conflicting or dirty data | ❌ Excluded |
| **UNKNOWN** | No Rodden grade available | ⚠️ Treated as B for documentation, excluded from hypothesis testing |

---

## 8. REFERENCE CALCULATORS

- **AppliedJyotish.com**: Lahiri ayanamsa, Placidus houses, Swiss Ephemeris
- **Astro-seek.com**: Lahiri ayanamsa, Whole Sign/Placidus options
- **DrikPanchang.com**: Lahiri ayanamsa, Sidereal positions

**Validation rule:** Reference calculator results are NEVER copied into our
engine. They are used ONLY for comparison. Differences are root-caused and
documented as methodology artifacts.
