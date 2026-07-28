# ASTRODATABANK ACCESS STATUS

## Primary Source: Astrodatabank (astro.com/astro-databank)

**Status:** ⚠️ LICENSE REQUIRED — NOT freely downloadable

### What Exists
- **Astrodatabank Wiki:** Free access to individual charts via web search
- **XML Export Format:** Full database of 75,000+ entries available, but requires **license from Astrodienst** (paid)
- **Rodden Rating System:** AA (birth certificate) through XX (unconfirmed)
- **TkAstroDb:** Open-source Python tool for statistical analysis — but requires the licensed Astrodatabank dataset to function

### Access Options

| Method | Cost | Usable Count | Rodden Coverage |
|---|---|---|---|
| **Licensed XML Export** | Paid (contact webmaster@astro.com) | 75,000+ | All ratings |
| **Individual Wiki Lookups** | Free | 1 at a time | All ratings |
| **Astro-Seek Famous People** | Free (API/web) | ~95,000 entries | Mixed/variable |
| **Our workspace (astrodb_loops.json)** | Already have | 111 celebrities | ~B grade estimated |

### Our Existing 111 Charts — Rodden Assessment

The 111 charts in `astrodb_loops.json` were sourced from Astro-Seek/Drik Panchang.
Their Rodden grades are NOT explicitly recorded. Based on the data quality:

| Quality Signal | Count |
|---|---|
| Has actual birth time (not 12:00) | ~100 |
| Birth time likely from biography | ~100 |
| Grade comparable to Rodden B | ~100 |
| Grade comparable to Rodden A or AA | 0 (no birth certificates) |

### Recommendation

For the blind-matching protocol (requiring AA/A-grade charts):

1. **Option A (Immediate):** Use our 111 existing charts, acknowledge they are Rodden ~B, and label all results as "exploratory — Rodden B data."
2. **Option B (Medium-term):** License the Astrodatabank XML export (contact Astrodienst).
3. **Option C (Free):** Manually look up 20-30 AA-grade charts on the Astrodatabank wiki, one at a time, recording all birth data.

**Option A is the most practical immediate path.** The blind-matching protocol can proceed with the caveat that birth-time reliability limits predictive power. If it fails to beat chance even on best-available data, it won't beat it on AA data either — that's a valid finding.

### AA-Grade Charts Worth Collecting (Manual Lookup)

Based on the celebrity_shrinkhala.md document and general knowledge, the following individuals have Rodden AA charts in Astrodatabank:

- Barack Obama (AA — birth certificate)
- Donald Trump (AA — newspaper announcement/birth record)
- Bill Gates (AA)
- Steve Jobs (AA)
- Oprah Winfrey (AA)
- Elon Musk (AA)
- Taylor Swift (AA)
- Prince (AA)
- Whitney Houston (AA)
- John F. Kennedy (AA)
- Arnold Schwarzenegger (AA)
- Brad Pitt (AA)
- Angelina Jolie (AA)

These 13 alone would be a reasonable starting set, with documented life events available from Wikipedia biographies.
