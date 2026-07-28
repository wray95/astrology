# D1–D9 CONNECTION MODEL
## Validated against 111 Celebrity Charts (25 Jul 2026)

---

## MATHEMATICAL TRANSFORMATION

For every planet, the D1 → D9 transform is:

```
D1 Sign + D1 Degree → Sidereal Longitude → Navamsa Division → D9 Sign
```

**Procedure:**
1. Convert D1 sign + degree to sidereal longitude (0–360°)
2. Get position within sign: `pos = longitude % 30`
3. Determine navamsa number: `nav_num = floor(pos / (30/9))` — values 0–8
4. Determine D9 sign: `sign_index = (base * 3 + nav_num) % 12`
   where `base = floor(sign_index / 3)`
5. Vargottama: `D1 sign == D9 sign`

---

## EMPIRICAL RESULTS (111 Charts)

| Group | n | Mean Vargottama | Notes |
|---|---|---|---|
| 5-loop (bond=25) | 3 | 0.7 | Lowest vargottama |
| 4-loop (bond=33) | 9 | 0.9 | |
| No loop | 41 | 1.0 | |
| 2-loop (bond=100) | 31 | 1.2 | |
| 3-loop (bond=50) | 27 | 1.4 | Highest vargottama |

---

## WHAT D9 ADDS BEYOND D1

| Layer | D1 Shows | D9 Shows |
|---|---|---|
| Planet strength | Sign-based dignity | Inner strength/vargottama |
| Exchange validation | Rasi Parivartana | Navamsa Parivartana |
| Marriage | 7H condition | Spouse quality, marital strength |
| Career depth | 10H karma | Hidden career potential |
| Dasha effects | MD/AD lords | Whether dasha lord has inner support |

**Key finding:** The 3-loop (bond=50) group shows the highest vargottama (1.4) AND highest achievement (9.3). This suggests D9 confirmation amplifies the Shrinkala's effects — but n=27 is sufficient only for directional observation, not proof.

---

## LIMITATIONS

1. Planet degrees in astrodb_loops.json are ROUNDED — not precise enough for D9 pada-level analysis
2. Only 111 charts — insufficient for fine-grained statistical significance
3. D9 Parivartana requires full sign-rulership mapping — not yet automated
4. No documented life events beyond achievement scores in the dataset

---

## FUTURE WORK

- Acquire precise sidereal longitudes for all 111 charts
- Compute full D9 Parivartana (sign-rulership exchange in Navamsa)
- Correlate D9 vargottama with specific life events (marriage, career, wealth)
- Test D9 + Dasha prediction against documented events with dates
