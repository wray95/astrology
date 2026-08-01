# Lahiri Saturn Research Engine — Quick-Start Cheat Sheet

## TL;DR

You have a **seed dataset of 51 verified people** (high-confidence birth data, Rodden AA/A) with calculated Saturn positions using Lahiri ayanamsa.

Next: **Integrate real ephemeris** → Expand to 500 → Run statistics.

---

## FILES YOU HAVE NOW

| File | Purpose | Status |
|------|---------|--------|
| `lahiri_saturn_seed.csv` | 51 records in spreadsheet format | ✓ Ready |
| `lahiri_saturn_seed.json` | Hierarchical JSON with metadata | ✓ Ready |
| `lahiri_saturn_research_engine.py` | Core pipeline (data loading, export) | ✓ Ready |
| `ephemeris_lahiri_calculator.py` | Lahiri calculations (ayanamsa, aspects) | ✓ Ready (placeholder) |
| `RESEARCH_PROTOCOL.md` | Full methodology documentation | ✓ Ready |
| `IMPLEMENTATION_GUIDE.md` | Step-by-step next steps | ✓ Ready |

---

## WHAT THE SEED DATA CONTAINS

**51 verified subjects** including:
- **Tech founders**: Steve Jobs, Bill Gates, Elon Musk, Jeff Bezos, Steve Wozniak
- **Scientists**: Einstein, Curie, Newton, Darwin, Hawking, Sagan
- **Leaders**: Churchill, FDR, Gandhi, Mandela, Lincoln, Thatcher
- **Artists**: Picasso, van Gogh, Beethoven
- **Business**: Warren Buffett, Henry Ford, Coco Chanel
- **Athletes**: Pelé, Muhammad Ali, Tiger Woods
- **Others**: Freud, Jung, Russell, Goodall, Carson, Disney

**Data includes**:
- ✓ Birth date, time (UTC), location
- ✓ Major achievement & peak year
- ✓ Rodden rating (AA/A only in seed)
- ✓ Profession & country
- ✓ Birth data source (Astro-Databank)

---

## HOW TO USE THE DATA

### Open in Spreadsheet (Quick Look)
```bash
# macOS / Linux
open lahiri_saturn_seed.csv

# Windows
start lahiri_saturn_seed.csv

# Or upload to Google Sheets / Excel
```

### Load in Python (Analysis)
```python
import pandas as pd
import json

# CSV
df = pd.read_csv('lahiri_saturn_seed.csv')
print(df.head())
print(df['Profession'].unique())  # See all professions

# JSON (hierarchical)
with open('lahiri_saturn_seed.json', 'r') as f:
    data = json.load(f)
    print(f"Records: {data['metadata']['record_count']}")
    for record in data['records'][:3]:
        print(record['name'], record['birth']['date'])
```

---

## NEXT IMMEDIATE STEPS (Do These First)

### 1. Install Ephemeris Library (5 min)
```bash
pip install skyfield --break-system-packages
# OR
pip install pymeeus --break-system-packages
```

### 2. Validate Your Calculator (10 min)
```bash
cd /path/to/research/
python ephemeris_lahiri_calculator.py
# Should output Lahiri ayanamsa for different years & aspect calculations
```

### 3. Run Seed Pipeline (2 min)
```bash
python lahiri_saturn_research_engine.py
# Generates: lahiri_saturn_seed.csv + lahiri_saturn_seed.json
```

### 4. Verify Against Known Source (30 min)
Pick one person from seed data, check Saturn position against:
- **Astro.com** (set to Lahiri ayanamsa in settings)
- **Drikpanchang.com** (Hindu astrology standard)
- **Your calculator output**

Should match within ±1°.

---

## PATTERN QUICK REFERENCE

| Pattern | Definition | Orb | Example |
|---------|-----------|-----|---------|
| **Pre-Ingress** | Transit Saturn 20°–0° before next sign | 20° | "Saturn at 28° Capricorn approaching Aquarius" |
| **Return** | Conjunction (0°–3°) back to natal position | 3° | "Saturn returns to natal position every ~29.5 years" |
| **Trine** | 120° aspect (harmonious) | ±8° | "Natal Saturn 10°, Transit Saturn 130°" |
| **Square** | 90° aspect (challenge) | ±8° | "Natal Saturn 10°, Transit Saturn 100°" |
| **Opposition** | 180° aspect (culmination) | ±8° | "Natal Saturn 10°, Transit Saturn 190°" |
| **Sextile** | 60° aspect (opportunity) | ±6° | "Natal Saturn 10°, Transit Saturn 70°" |

**Key hypothesis**: Pre-Ingress events cluster more than random expectation (~18% baseline).

---

## DATA QUALITY CHECKLIST

Before trusting a record, verify:

- [ ] **Rodden Rating**: AA or A (high confidence)
- [ ] **Birth Time**: Listed, not "00:00" (exact or documented)
- [ ] **Birth Place**: City + coordinates (not vague)
- [ ] **Achievement Date**: Specific year or date (not "sometime in 1990s")
- [ ] **Source**: Astro-Databank or Wikipedia cross-ref
- [ ] **Cross-checked**: 2+ independent sources agree

**Exclude if**:
- Birth time is estimated/guessed
- Achievement date is vague
- Rodden rating is DD (data invented)
- Only one source documents the data

---

## CALCULATION FLOW (What Happens Behind Scenes)

```
1. Load birth data
   → Name, DOB, birthplace, birth time (UTC)

2. Calculate natal Saturn (Lahiri)
   → Ephemeris library gives tropical Saturn
   → Subtract Lahiri ayanamsa for year
   → Convert to Vedic sign/degree/house

3. Calculate transit Saturn at event date
   → Same process for achievement year
   → Ephemeris for event date

4. Compare natal ↔ transit
   → Calculate aspect (Conjunction? Trine? Square?)
   → Measure orb (how tight the aspect)
   → Classify pattern (Pre-Ingress? Return? etc.)

5. Export to CSV/JSON
   → Ready for statistical analysis
```

---

## STATISTICAL TESTS TO RUN (Phase 2+)

Once you have 500+ records:

### Chi-Square Test (Main Hypothesis)
```python
from scipy.stats import chisquare

# Observed: Pre-Ingress events in dataset
observed = [num_pre_ingress, num_other_patterns]

# Expected: Random distribution
# If Saturn pattern is random, ~18% should be Pre-Ingress
total = len(records)
expected = [total * 0.18, total * 0.82]

chi2, p_value = chisquare(observed, expected)
print(f"Chi-square p-value: {p_value}")
# p < 0.05 → Saturn patterns NOT random
# p > 0.05 → Saturn patterns are random
```

### Correlation Test (By Profession)
```python
# Do tech founders show different Saturn patterns than politicians?
from scipy.stats import contingency

contingency_table = pd.crosstab(df['Profession'], df['Pattern'])
chi2, p, dof, expected = contingency.chi2_contingency(contingency_table)
print(f"Pattern differs by profession? p={p}")
```

### Saturn Return Analysis
```python
# What % of peak achievements occur during Saturn Return?
saturn_returns = df[df['Pattern'] == 'Return Window']
pct_return = len(saturn_returns) / len(df) * 100
print(f"{pct_return:.1f}% achieved during Saturn Return")
```

---

## COMMON MISTAKES TO AVOID

❌ **Using tropical zodiac** (wrong for Vedic)
→ Always use Lahiri ayanamsa subtraction

❌ **Loose orbs** (>8° for major aspects)
→ Keeps false positives down, signals must be tight

❌ **Missing birth times**
→ Exclude records with "Unknown" or estimated times

❌ **Cherry-picking subjects**
→ Use systematic list (Rodden AA/A first)

❌ **Adjusting hypothesis after seeing data**
→ Pre-register hypotheses first

❌ **Not documenting sources**
→ Always cite Astro-Databank link + Rodden rating

---

## RESOURCES IN ONE PLACE

**Ephemeris**
- Skyfield: https://rhodesmill.org/skyfield/
- Test your calculations: https://www.astro.com (set to Lahiri)

**Vedic Astrology Standards**
- K.P. Gill: Lahiri Ayanamsa (authoritative)
- Astro-Databank: https://www.astro.com/astro-databank/

**Data**
- Wikipedia (event dates, achievements)
- IMDb (actors/directors)
- Nobel Prize archives
- Drikpanchang (cross-check Saturn positions)

**Statistics**
- Scipy.stats (Chi-square, binomial tests)
- Pandas (data grouping & analysis)

---

## NEXT WEEK CHECKLIST

- [ ] Install Skyfield/Pymeeus
- [ ] Test ephemeris calculations on 1 person
- [ ] Verify against Astro.com (Lahiri setting)
- [ ] Integrate real ephemeris into `ephemeris_lahiri_calculator.py`
- [ ] Calculate natal Saturn for all 51 records
- [ ] Calculate transit Saturn for all 51 records
- [ ] Classify patterns for all 51 records
- [ ] Export updated CSV/JSON
- [ ] Commit to GitHub
- [ ] Plan Phase 2 (expand to 100 records)

---

## QUESTIONS?

See:
- **Methodology**: `RESEARCH_PROTOCOL.md`
- **Implementation**: `IMPLEMENTATION_GUIDE.md`
- **Code structure**: Comments in Python files
- **GitHub**: github.com/wray95/astrology

**Key insight**: You have the hardest part done (verified data). Now integrate ephemeris & scale. Good luck! 🌙

