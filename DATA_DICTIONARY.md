# Lahiri Saturn Research Engine — Data Dictionary

## CSV Column Definitions

### Identification & Demographics
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Name` | String | "Steve Jobs" | Full name from Astro-Databank |
| `Birth Date` | Date (YYYY-MM-DD) | "1955-02-24" | Verified from multiple sources |
| `Birthplace` | String | "San Francisco, CA" | City, state/country |
| `Country` | String | "USA" | ISO 3166-1 alpha-2 or full name |
| `Birth Time (UTC)` | Time (HH:MM) | "19:15" | 24-hour UTC, required (no estimates) |
| `Rodden Rating` | Categorical | "A" or "AA" | AA=Excellent, A=Reliable, B=Reported, C=Questionable, DD=Invented |
| `Data Source` | String | "Astro-Databank" | Primary source of birth data |

### Professional & Achievement Data
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Profession` | String | "Technology Founder" | Career category (27 total) |
| `Major Achievement` | String | "Apple Computer co-founder" | Peak accomplishment or contribution |
| `Peak Year` | Integer | 2001 | Year of major success/recognition |
| `Peak Event Date` | Date (YYYY-MM-DD) | "2001-06-21" | Estimated from peak_year (using June 21 = midyear default) |

### Natal Saturn (Vedic/Lahiri)
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Natal Saturn Sign` | Categorical | "Leo" | Aries–Pisces (Vedic zodiac after Lahiri ayanamsa correction) |
| `Natal Saturn Degree` | Float (0–30) | 7.41 | Degrees within sign (0° = sign start, 30° = sign end) |
| `Natal Saturn House` | Integer (1–12) | 1 | Vedic house placement (Whole Sign houses) |
| `Natal Saturn Dignity` | Categorical | "Neutral" | Exalted, Own Sign, Friendly, Neutral, Enemy, Debilitated |

### Transit Saturn (At Event Date)
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Transit Saturn Sign` | Categorical | "Unknown" | Saturn position on peak event date |
| `Transit Saturn Degree` | Float (0–30) | "Unknown" | Degrees within sign (placeholder in seed data) |

### Pattern Classification
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Saturn Pattern` | String | "Unknown" | Aspect type (placeholder in seed data) |
| `Pattern Type` | Categorical | "Unknown" | Pre-Ingress, Return, Conjunction, Square, Trine, Sextile, Opposition, Other |

### Data Quality
| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `Calculation Status` | Categorical | "calculated" | pending, calculated, error |
| `Notes` | Text | "" | Additional context, data quality flags, sources |

---

## JSON Structure

### Top-Level Metadata
```json
{
  "metadata": {
    "title": "Lahiri Saturn Transit & Wealth Analysis - Seed Dataset",
    "methodology": "Swiss Ephemeris + Lahiri Ayanamsa (Vedic Astrology)",
    "record_count": 51,
    "rodden_ratings": "AA/A only (highest confidence)",
    "generated": "2024-08-01T14:23:15.123456"
  },
  "records": [...]
}
```

### Per-Record Structure
```json
{
  "name": "Steve Jobs",
  "birth": {
    "date": "1955-02-24",
    "place": "San Francisco, CA",
    "country": "USA",
    "time_utc": "19:15",
    "rodden_rating": "A",
    "source": "Astro-Databank"
  },
  "achievement": {
    "description": "Apple Computer co-founder",
    "peak_year": 2001,
    "peak_event_date": "2001-06-21",
    "profession": "Technology Founder"
  },
  "saturn": {
    "natal": {
      "sign": "Leo",
      "degree": 7.41,
      "house": 1,
      "retrograde": false,
      "dignity": "Neutral"
    },
    "transit": {
      "sign": "Unknown",
      "degree": null,
      "house": null,
      "aspect_to_natal": null,
      "orb": null
    },
    "pattern": null,
    "saturn_return": false
  },
  "other_transits": {
    "jupiter": null,
    "rahu_ketu": null,
    "dasha": null
  },
  "quality": {
    "calculation_status": "calculated",
    "notes": ""
  }
}
```

---

## Data Validation Rules

### Birth Date
- ✓ Must be YYYY-MM-DD format
- ✓ Must be a valid calendar date
- ✓ Must be before peak event date
- ✓ Must be documented (not estimated)

### Birth Time
- ✓ Must be HH:MM format (24-hour UTC)
- ✓ Cannot be "00:00" unless verified
- ✓ Cannot be estimated
- If unknown → Flag with "Unknown" and mark Rodden DD (exclude from seed)

### Birthplace
- ✓ Must include city
- ✓ Should include state/country
- ✓ Should have approximate coordinates (optional in seed)

### Rodden Rating
- ✓ Seed data: AA or A only
- ✓ Phase 2: A or B allowed
- ✓ Exclude: C, DD, or unknown ratings

### Achievement Date
- ✓ Must be specific year (not "sometime in 1990s")
- ✓ Must be verifiable in 2+ sources (Wikipedia, Britannica, etc.)
- ✓ For seed: Using midyear (June 21) as default when exact date unknown
- ✓ Future phases: Capture exact date when available

### Saturn Positions
- ✓ Degree must be 0–30 (within sign)
- ✓ House must be 1–12 (Vedic Whole Sign)
- ✓ Orb (if applicable) must be 0–8° for major aspects
- ✓ Must use Lahiri ayanamsa (not tropical)

---

## Rodden Rating Definitions

| Rating | Reliability | Inclusion | Description |
|--------|------------|-----------|---|
| **AA** | Excellent | ✓ Seed phase | Birth time from birth certificate or government record |
| **A** | Reliable | ✓ Seed phase | Birth time from biography, horoscope, or reliable source |
| **B** | Reported | ✗ Seed, ✓ Phase 2 | Birth time from less reliable source or biography |
| **C** | Questionable | ✗ | Birth time speculative or uncertain |
| **DD** | Invented | ✗ | Birth time invented/fabricated by astrologer |
| **X** | Unknown | ✗ | No birth time data |

---

## Profession Categories (27 Total)

| Category | Examples | Count |
|----------|----------|-------|
| Technology Founder | Jobs, Gates, Bezos, Musk, Wozniak | 8 |
| Investor | Buffett | 1 |
| Economist | Keynes, Smith | 2 |
| Physicist | Einstein, Newton, Hawking | 3 |
| Scientist | Curie, Darwin, Tesla | 4 |
| Psychologist | Freud, Jung | 2 |
| Medical | Florence Nightingale | 1 |
| Statesman | Churchill | 1 |
| President/PM | FDR, Thatcher, Gandhi, Lincoln | 4 |
| Activist | MLK, Mandela | 2 |
| Athlete | Pelé, Ali, Tiger Woods | 3 |
| Designer | Coco Chanel | 1 |
| Artist | Picasso, van Gogh | 2 |
| Composer | Beethoven | 1 |
| Writer | Doyle, Christie, Hemingway, Angelou | 4 |
| Entertainer | Disney, Winfrey | 2 |
| Industrialist | Ford, Edison | 2 |
| Inventor | Bell, Tesla (categorized separately) | — |
| Philosopher | Russell, Sagan, Bertrand Russell | 3 |
| Explorer | Jane Goodall | 1 |
| Researcher | Rachel Carson | 1 |
| Entrepreneur | Branson, various | 2 |
| **TOTAL** | | **51** |

---

## Missing Data Notation

| Convention | Meaning | Example |
|------------|---------|---------|
| `null` | Data not yet calculated | `"transit_saturn": null` |
| `"Unknown"` | Data cannot be obtained | `"Natal Saturn Sign": "Unknown"` |
| `""` (empty string) | Field not applicable or intentionally blank | `"Notes": ""` |
| `0` | Numeric zero (valid value) | `"Degree": 0` (0° Aries) |

**Key rule**: Never leave critical fields blank for seed data. Use "Unknown" only if documented as missing.

---

## Quality Flags & Notes

### Common Flags
| Flag | Meaning | Action |
|------|---------|--------|
| `Rodden A only` | High confidence | ✓ Include in seed |
| `Estimated birth time` | Less precise | ✗ Exclude from seed |
| `Conflicting birth data` | Multiple sources disagree | Verify with Astro-Databank |
| `Event date ±1 year` | Achievement year approximated | Document margin of error |
| `Cross-checked vs Wikipedia` | Verified | ✓ Include |

### In `Notes` Field
Examples of good documentation:
```
"Rodden AA per Astro-Databank, verified vs Wikipedia"
"Birth time from biography; event date is company IPO announcement"
"Profession updated to 'Media Executive' (was 'Broadcaster')"
"Saturn Return window: 1985–1987 (29.5-year cycle)"
```

---

## Export/Import Guidelines

### CSV Round-Trip
```python
import pandas as pd

# Import
df = pd.read_csv('lahiri_saturn_seed.csv')

# Clean up types
df['Birth Date'] = pd.to_datetime(df['Birth Date'])
df['Peak Event Date'] = pd.to_datetime(df['Peak Event Date'])
df['Natal Saturn Degree'] = pd.to_numeric(df['Natal Saturn Degree'], errors='coerce')

# Export (preserves formatting)
df.to_csv('lahiri_saturn_output.csv', index=False)
```

### JSON Round-Trip
```python
import json

# Import
with open('lahiri_saturn_seed.json', 'r') as f:
    data = json.load(f)

# Access
for record in data['records']:
    name = record['name']
    saturn_sign = record['saturn']['natal']['sign']

# Export
with open('lahiri_saturn_output.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

## Ayanamsa Values Used

### Lahiri Ayanamsa by Year (for reference)

| Year | Ayanamsa (°) | Source |
|------|-------------|--------|
| 1900 | 20.88 | K.P. Gill tables |
| 1950 | 22.73 | — |
| 1980 | 23.84 | — |
| 2000 | 24.58 | — |
| 2020 | 25.32 | — |
| 2024 | 25.50 | Latest estimate |

**Formula for interpolation** (between table years):
```
Ayanamsa(Y) = A1 + (A2 - A1) × (Y - Y1) / (Y2 - Y1)
```

Example: Ayanamsa for 1955?
```
A(1955) = 22.73 + (23.84 - 22.73) × (1955 - 1950) / (1980 - 1950)
        = 22.73 + 1.11 × 5 / 30
        = 22.73 + 0.185
        = 22.92°
```

---

## References & Standards

### Vedic Astrology Standards
- **Lahiri Ayanamsa**: K.P. Gill, "Lahiri Ayanamsa" (standard in India)
- **House System**: Whole Sign (Vedic standard, not Placidus)
- **Dignity Assessment**: Parasara's 6-fold dignity scale

### Data Sources
- **Birth Data**: Astro-Databank (www.astro.com/astro-databank/)
- **Event Verification**: Wikipedia, Britannica, IMDb, Nobel Prize records
- **Saturn Positions**: Swiss Ephemeris (Skyfield library)

### Orb Standards (Vedic)
- **Conjunction**: 0°–3° (tight)
- **Square/Opposition/Trine**: 0°–8° (major aspects)
- **Sextile**: 0°–6° (minor aspect)
- **Pre-Ingress Window**: 20°–0° (sign boundary approach)

---

**Generated**: 2024-08-01
**Version**: 1.0 (Seed Phase)
**Next Update**: Phase 2 (100+ records with full ephemeris calculations)

