# YOGA DEFINITIONS — Mathematical (Fixed for Testing)

---

## PARIVARTANA YOGA (House Exchange)

**Algorithm:**
```
For each pair of planets (P1, P2):
  sign_of_P1 = birth_chart.signs[P1]
  sign_of_P2 = birth_chart.signs[P2]
  ruler_of_sign1 = rulers[sign_of_P1]
  ruler_of_sign2 = rulers[sign_of_P2]
  IF ruler_of_sign1 == P2 AND ruler_of_sign2 == P1:
    → PARIVARTANA YOGA PRESENT
```

**Strength scoring:**
- D1 only → strength = 1
- D1 + D9 confirmed → strength = 2
- D1 + D9 + both lords in Vimshottari sequence → strength = 3

---

## SHRINKHALA YOGA (Planetary Chain)

**Algorithm:**
```
Build directed graph: planet → sign it occupies → ruler of that sign
Find all directed cycles where:
  - Cycle length ≥ 3
  - Each planet in cycle occurs exactly once
  - Cycle closes (last planet's sign ruler = first planet)
```

**Bond strength** (from jyotishvidya.com/srinkhala.htm):
| Chain Length | Bond | Classification |
|---|---|---|
| 2 (Parivartana) | 100 | Strong |
| 3 | 50 | Meaningful |
| 4 | 33 | Weakened |
| 5+ | 25 | IGNORE |

---

## MUKKIRAGA PARIVARTHANA (3-Planet)

Identical to 3-planet Shrinkhala (bond=50).
Separate name, same algorithm as Shrinkhala with cycle_length==3.

---

## MOON-JUPITER EXCHANGE

**Algorithm:**
```
moon_sign = birth_chart.signs["Moon"]
jupiter_sign = birth_chart.signs["Jupiter"]
IF moon_sign in ["Sagittarius","Pisces"] AND jupiter_sign == "Cancer":
  → MOON-JUPITER EXCHANGE PRESENT
ELSE:
  → NOT PRESENT
```

**Sign rulers (fixed for all calculations):**
| Sign | Ruler |
|---|---|
| Aries | Mars |
| Taurus | Venus |
| Gemini | Mercury |
| Cancer | Moon |
| Leo | Sun |
| Virgo | Mercury |
| Libra | Venus |
| Scorpio | Mars |
| Sagittarius | Jupiter |
| Capricorn | Saturn |
| Aquarius | Saturn |
| Pisces | Jupiter |
