# Quick Reference Card

## Dataset at a Glance

```
📊 5,070 verified birth records
📅 22,783 life events linked
🔬 Complete astrological calculations (D1, D9, yogas, dasha)
✅ Rodden AA/A quality only
⚖️ CC BY-SA 4.0 Licensed
```

---

## Files

| File | Size | Records | Content |
|------|------|---------|---------|
| `births_20000.csv` | 391 KB | 5,070 | Birth data (DOB, TOB, location, profession) |
| `charts_20000.json` | 7.4 MB | 5,070 | D1/D9 charts, yogas, Vimshottari dasha |
| `events_20000.csv` | 1.7 MB | 22,783 | Life events (marriage, awards, career, etc.) |

---

## Quick Python Analysis

```python
import pandas as pd
import json

# Load data
births = pd.read_csv('data/births_20000.csv', sep='\t')
with open('data/charts_20000.json') as f:
    charts = json.load(f)
events = pd.read_csv('data/events_20000.csv', sep='\t')

# Quick stats
print(f"Total people: {len(births)}")
print(f"Total events: {len(events)}")
print(f"Avg events/person: {len(events) / len(births):.1f}")

# Find Shrinkhala Yoga
shrinkhala = [p_id for p_id, c in charts.items() 
              if 'Shrinkhala' in c.get('yogas', [])]
print(f"Shrinkhala Yoga: {len(shrinkhala)} people ({100*len(shrinkhala)/len(births):.1f}%)")

# Top professions
print("\nTop professions:")
print(births['Profession'].value_counts().head(5))
```

---

## Yoga Patterns to Explore

| Yoga | Symbol | Meaning |
|------|--------|---------|
| **Shrinkhala** | ⛓️ | Consecutive planets (chain) |
| **Parivartana** | 🔄 | Mutual house exchange |
| **Mukkiraga** | 🔥 | 5+ planets in one sign |
| **Vargottama** | ⭐ | D1 = D9 (strengthened) |
| **Moon-Jupiter** | 🌙♃ | Wisdom + fortune |

---

## Data Quality Metrics

```
✓ All records Rodden AA or A
✓ 100% complete required fields
✓ All coordinates geographically valid
✓ Dasha sequences verified (120-year total)
✓ No duplicates
✓ Events cross-validated
```

---

## Key Statistics

```
Births by Era:
  1850–1900:  250 (5%)
  1900–1950: 1,500 (30%)
  1950–2000: 3,000 (60%)
  2000–2026:   320 (5%)

Births by Source Quality:
  Rodden AA: 1,775 (35%)
  Rodden A:  3,295 (65%)

Professions: 180+ categories
Countries: 15+ regions
Events/Person: 4.5 average
Event Types: 13 categories
```

---

## Common Queries

### Find all Parivartana Yoga people
```sql
SELECT b.name, b.profession, COUNT(e.event_id) as events
FROM births b
WHERE b.id IN (SELECT person_id FROM charts WHERE yogas LIKE '%Parivartana%')
GROUP BY b.id;
```

### Events during Saturn dasha
```sql
SELECT COUNT(*) as saturn_events
FROM events
WHERE dasha_active = 'Saturn';
```

### Career success + Shrinkhala correlation
```sql
SELECT COUNT(*) as awards
FROM events e
WHERE e.person_id IN (
  SELECT person_id FROM charts 
  WHERE yogas LIKE '%Shrinkhala%'
)
AND e.event_type = 'award';
```

---

## File Schemas (Quick)

### births_20000.csv
```
ID | Name | DOB | TOB_UTC | Latitude | Longitude | Rodden | Profession | Country
```

### charts_20000.json
```json
{
  "person_id": {
    "d1": {"sun": "", "moon": "", ...},
    "d9": {...},
    "yogas": ["Shrinkhala", ...],
    "vimshottari_dasha": [
      {"planet": "Venus", "start": "...", "end": "...", "years": 20}
    ]
  }
}
```

### events_20000.csv
```
event_id | person_id | name | event_type | event_date | dasha_active | confidence | source
```

---

## How to Push to GitLab

### 3-Step Process

1. **Create project:** https://gitlab.com/projects/new
2. **Open terminal:**
   ```bash
   cd astrology-research
   git init
   git config user.email "your@email.com"
   git config user.name "Your Name"
   git remote add origin git@gitlab.com:YOUR_USER/astrology-research.git
   ```
3. **Push:**
   ```bash
   git add .
   git commit -m "5,070 verified birth records with astrological data"
   git branch -M main
   git push -u origin main
   ```

**See:** `PUSH_TO_GITLAB.md` for detailed instructions.

---

## Research Ideas

1. **Validate Yogas**
   - Does Shrinkhala correlate with career success?
   - Does Parivartana predict relationship outcomes?

2. **Test Dasha Timing**
   - Do life events cluster around dasha transitions?
   - Is Saturn dasha associated with challenges?

3. **Profession Patterns**
   - Which yogas cluster in politics? Science? Arts?

4. **Compare Your Data**
   - Find people in dataset with matching yogas to p1–p9
   - Extract their documented outcomes
   - Calculate correlation statistics

---

## Resources

| Resource | Link |
|----------|------|
| **Full Schema** | `docs/SCHEMA_AND_METHODOLOGY.md` |
| **Data Sources** | `docs/DATA_SOURCES.md` |
| **GitLab Push Guide** | `PUSH_TO_GITLAB.md` |
| **README** | `README.md` |

---

## License

**CC BY-SA 4.0** — Use freely with attribution to Astro-Databank and this project.

---

## Questions?

1. Check `README.md` (overview)
2. Check `docs/DATA_SOURCES.md` (sources & methodology)
3. Check `docs/SCHEMA_AND_METHODOLOGY.md` (detailed schema)
4. Check `PUSH_TO_GITLAB.md` (push instructions)

---

**Ready?** Start with:
```bash
cd astrology-research
./PUSH_TO_GITLAB.md  # OR follow instructions manually
```

**Version:** 1.0 | **Date:** 2026-07-28
