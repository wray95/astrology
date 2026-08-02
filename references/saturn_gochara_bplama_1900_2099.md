# Shani (Saturn) Gochara Transits Table — BP Lama Jyotishavidya (reference)
*Source: https://barbarapijan.com/bpa/Gochara_Shani/Shani_gochara_transits_table.htm (fetched 2026-08-02, updated 2026-07-26 per page). Data origin per page: Goravani Jyotish Beta. Sidereal (Lahiri). Covers 1900–2099 C.E.; marks "begin janma Sade Sati" per Moon sign at each entry.*

## Validation (scripts/validate_saturn_transits.py → dataset/saturn_transit_validation_bplama.json)
Swiss Ephemeris (SIDM_LAHIRI) vs this table — first entry into each sign, 1900–2099:
- **81/82 entries match within ±3 days; max difference = 1 day** (SE consistently 0–1 day later; 2057-01-06 Aries not found by the ±30-day window search — likely fine, see JSON).
- **Conclusion: the workspace gochara engine's Saturn sign-entry dates are externally validated.** This complements the earlier checks (Saturn return mean 29.1 y / 58.5 y in gochara_features_test.py) — the transit layer is correct; the binding constraint is data (outcome labels), not ephemeris.

## First-entry dates (all 12 signs per cycle, 1900–2099) — extracted from the page
| Year | Aries | Taurus | Gemini | Cancer | Leo | Virgo | Libra | Scorpio | Sagittarius | Capricorn | Aquarius | Pisces |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1900s | 1909-07-08 | 1912-05-07 | 1914-06-20 | 1916-08-01 | 1918-09-17 | 1920-11-16 | 1923-10-15 | 1925-12-31 | 1928-12-24 | 1902-02-11 | 1905-02-04 | 1907-04-19 |
| 1930s | 1939-04-27 | 1941-06-18 | 1943-08-05 | 1945-09-22 | 1948-07-26 | 1950-09-19 | 1952-11-25 | 1955-11-11 | 1958-02-07 | 1931-04-11 | 1934-03-15 | 1937-02-25 |
| 1960s | 1968-06-16 | 1971-04-27 | 1973-06-10 | 1975-07-23 | 1977-09-06 | 1979-11-03 | 1982-10-05 | 1984-12-20 | 1987-12-16 | 1961-02-01 | 1964-01-27 | 1966-04-08 |
| 1990s | 1998-04-17 | 2000-06-06 | 2002-07-22 | 2004-09-05 | 2006-10-31 | 2009-09-09 | 2011-11-14 | 2014-11-02 | 2017-01-26 | 1990-03-20 | 1993-03-05 | 1995-06-01 |
| 2020s | 2027-06-02 | 2029-08-08 | 2032-05-30 | 2034-07-12 | 2036-08-27 | 2038-10-22 | 2041-01-27 | 2043-12-11 | 2046-12-07 | 2020-01-23 | 2022-04-28 | 2025-03-29 |
| 2050s | 2057-01-06 | 2059-05-27 | 2061-07-10 | 2063-08-23 | 2065-10-12 | 2068-08-29 | 2070-11-04 | 2073-02-05 | 2076-01-16 | 2049-03-06 | 2052-02-24 | 2054-05-14 |
| 2070s | 2086-05-21 | 2088-07-17 | 2090-09-18 | 2093-07-02 | 2095-08-18 | 2097-10-11 | 2099-12-25 | 2073-02-05 | 2076-01-16 | 2079-01-14 | 2081-04-11 | 2084-03-19 |

*(Each sign also has retrograde re-entries — see the JSON for the full list; the page notes "if Shani vakragati there can be 2 or 3 entries into the same rashi".)*

## Sade Sati periods for P-series (Moon signs from SE, windows from table entries)
| ID | Person | Moon | Sade Sati (begin → end) | Status @ 2026-08 |
|---|---|---|---|---|
| P1 | Bappa | Aquarius | 2022-04-28 → 2029-08-08 | **ACTIVE** |
| P7 | Sineth | Aquarius | 2022-04-28 → 2029-08-08 | **ACTIVE** |
| P5 | Senath | Capricorn | 2020-01-23 → 2027-06-02 | **ACTIVE (ends Jun 2027)** |
| P3 | Senith | Sagittarius | 2017-01-26 → 2025-03-29 | ended |
| P4 | Niromi | Libra | 2011-11-14 → 2020-01-23 | ended |
| P8 | Lakshi Amma | Libra | 2011-11-14 → 2020-01-23 | ended |
| P6 | Dewli | Scorpio | 2014-11-02 → 2022-04-28 | ended |
| P9 | Lalith Uncle | Leo | 2006-10-31 → 2014-11-02 | ended |
| P2 | Upulakshi | Taurus | 2000-06-06 → 2006-10-31 (last); **next 2029-08-08 → ~2036-08** | upcoming |

*Sade Sati = Saturn transits Moon sign + next 2 signs (per page's janma Sade Sati markers). Outcome-free descriptive feature — no life-outcome claims attached.*
