# Astro-Databank XML Goldmine — 5,409 Labeled Records
Source: github.com/anusfoil/astro_prediction (c_sample.xml, 16.5MB)
Date: 28 Jul 2026

## Dataset Structure
- 5,409 ADB entries with Astrodatabank export format
- All have: name, birth date, birth time (with JD_UT), place with coordinates, Rodden rating
- Planet positions: sun_sign+degmin, moon_sign+degmin, asc_sign+degmin
- 688/1000 have dated life events (extrapolated: ~3,700+ total)
- 544 unique category tags

## Wealth Classification Labels (per 1000 sample)
| Label | Count | Extrapolated |
|---|---|---|
| Wealthy | 28 | 151 |
| Rags to riches | 10 | 54 |
| Gain - Financial success in field | 45 | 243 |
| Gain - Money Through Marriage | 9 | 49 |
| Entrepreneur | 17 | 92 |
| Business owner | 24 | 130 |
| Top executive | 31 | 168 |
| Loss - Financial crisis | 6 | 32 |
| Loss - Bankruptcy | 2 | 11 |
| Philanthropist | 11 | 59 |

## Use for NEXUS Calibration
1. Parse all 5,409 records → extract birth data
2. Run through Swiss Ephemeris → compute D1, D9, yogas
3. Label: wealthy=1, bankruptcy/success failure=0
4. Train: which yoga rules actually predict wealth?
5. Calibrate: adjust NEXUS weights based on precision/recall

## Also from this repo
- RoxyAPI benchmark: 210 verified planet positions (DE441) for engine accuracy
- JyotishGanit: D1-D60 computation library
