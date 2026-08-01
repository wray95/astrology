# Celebrity Dataset Sources

## Primary Source
- **Astro-Seek Famous People Database**: https://famouspeople.astro-seek.com/
- **Total database size**: ~95,000 celebrities
- **Curated subset**: 111 celebrities with computed loop data

## Data Quality
- **Rodden Rating**: B (most entries)
- **Birth time reliability**: Varies — most have documented birth times
- **Achievement scoring**: 0-10 scale from repo analysis

## Balanced Groups
| Group | n | Mean Ach | Mean Vargottama |
|---|---|---|---|
| 2-loop (bond=100) | 31 | 8.90 | 1.2 |
| 3-loop (bond=50) | 27 | 9.26 | 1.4 |
| 4-loop (bond=33) | 9 | 9.22 | 0.9 |
| 5-loop (bond=25) | 3 | 7.00 | 0.7 |
| No loop (bond=0) | 41 | 8.95 | 1.0 |

## Limitation
- Planet degrees are ROUNDED in astrodb_loops.json
- Exact sidereal longitudes needed for precise D9 computation
- Only 3 five-loop cases found — insufficient for statistical significance
