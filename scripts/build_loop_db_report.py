#!/usr/bin/env python3
"""Build the real (link-only, Drik Panchang Lahiri) 24-chart loop database report."""
import json
from collections import Counter

r = json.load(open("/home/user/astrology/celeb_loops.json"))

# order: built (3 celeb + 4 family) then 17 fetched
order = ["Obama","Rockefeller","Stan Lee","P1 Bappa","P2 Upulakshi","P3 Senith","P4 Niromi",
 "Elon Musk","Bill Gates","Jeff Bezos","Steve Jobs","Albert Einstein","Warren Buffett",
 "Mark Zuckerberg","Sachin Tendulkar","Mukesh Ambani","Oprah Winfrey","Mahatma Gandhi",
 "Abraham Lincoln","Nelson Mandela","Walt Disney","Henry Ford","Michael Jackson","A.P.J. Abdul Kalam"]
by = {x["name"]:x for x in r}
rows = [by[n] for n in order if n in by]

def looptxt(x):
    if not x["loops"]:
        return "0-loop (none)"
    return f'{x["loop_len"]}-loop (bond {x["bond"]}): ' + "; ".join("/".join(c) for c in x["loops"])

# distribution
cnt = Counter(x["loop_len"] for x in rows)
dist_lines = "\n".join(f"| {k}-loop | {cnt.get(k,0)} | {cnt.get(k,0)*100//len(rows)}% |" for k in [0,2,3,4,5])

# high achievers (ach >= 8)
hi = [x for x in rows if (x["achievement"] or 0) >= 8]
hicnt = Counter(x["loop_len"] for x in hi)
hi_lines = "\n".join(f"| {k}-loop | {hicnt.get(k,0)} | {hicnt.get(k,0)*100//len(hi)}% |" for k in [0,2,3,4,5])

# table rows
tab = ""
for x in rows:
    s = x["signs"]
    signstr = f'Su {s.get("Sun","?")[:3]}, Mo {s.get("Moon","?")[:3]}, Ma {s.get("Mars","?")[:3]}, Me {s.get("Mercury","?")[:3]}, Ju {s.get("Jupiter","?")[:3]}, Ve {s.get("Venus","?")[:3]}, Sa {s.get("Saturn","?")[:3]}'
    ma = " (Moon≈noon)" if x["moon_approx"] else ""
    tab += f"| {x['name']} | {x['field']} | {x['achievement']} | {signstr} | {looptxt(x)}{ma} |\n"

md = f"""# REAL 24-Chart Loop Database (Link-Only · Drik Panchang Lahiri)

**Built:** Turn 14. **Sources:** planet signs fetched live from Drik Panchang (`planetary-positions-sidereal`, Lahiri/Chitra-Paksha ayanamsa) for the 17 remaining celebrities; the 3 named celebrities + 4 family + Senith reused from prior turns (also Drik-derived). **No Swiss-Ephemeris / computed data.** Loop detection = closed-cycle search in the planet→dispositor functional graph (Parivartana = 2-cycle; Śrṅkhalā = 3+/4/5-cycle). Bond strength per jyotishvidya.com: 2=100, 3=50, 4=33, 5=25.

**Birth times:** from the user-pasted framework where supplied; **7 charts with no verified time (Gandhi, Lincoln, Mandela, Disney, Ford, Jackson, Kalam) use 12:00 noon → Moon sign approximate** (flagged). All other times are as pasted (also unverified — see integrity note in `loop_research_500_framework.md`).

## Full table (24 charts)

| Person | Field | Achieve* | Planet signs (Su/Mo/Ma/Me/Ju/Ve/Sa) | Loop (jyotishvidya bond) |
|---|---|---|---|---|
{tab}

\\*Achievement tier (1–10) is an illustrative label from general knowledge of each person's eminence, **not** derived from links — used only to group "high achievers" for the distribution test.

## Real distribution (n=24)

| Loop | Count | % |
|---|---|---|
{dist_lines}

## Distribution among HIGH ACHIEVERS only (n={len(hi)}, achievement ≥ 8)

| Loop | Count | % |
|---|---|---|
{hi_lines}

## What the REAL data shows (vs the pasted 500-framework)

1. **Loops are NOT over-represented among top achievers — the opposite.** In real data, **{hicnt.get(0,0)}/{len(hi)} ({hicnt.get(0,0)*100//len(hi)}%) of high achievers have NO multi-planet loop at all** (Musk, Gates, Bezos, Buffett, Gandhi, Lincoln, Mandela, Disney, Jackson, Kalam, Tendulkar). The pasted framework claimed "3-loop = 47% of high achievers, chi-square p<0.001" — **not reproducible; refuted** by real Drik data.
2. **The only 5-loop in the entire sample is Senith (P3) — the LOWEST achiever** (loop=5, bond=25). This confirms jyotishvidya ("ignore 4/5, effect not considerable") and our Turn-12 finding: a 5-loop is a *latent* network, not an "industry-top" marker.
3. **3-loop and 4-loop appear in a minority of tops, not a majority.** 3-loop: Obama (politics), Ford (business, *Moon≈noon — uncertain*). 4-loop: Rockefeller (business), Jobs (tech). So multi-loop correlates with SOME empire-builders (Rockefeller/Jobs 4-loop; business/tech), but is absent in most others.
4. **2-loop (Parivartana, bond 100) is the most common real loop** (6 charts: P1, P2, Einstein, Zuckerberg, Ambani, Oprah) — consistent with jyotishvidya's "Parivartana (100) > Śrṅkhalā" strength order. It appears in both tops (Einstein, Ambani, Oprah, Zuckerberg) and the family (P1, P2).
5. **0-loop tops are real and common** (Stan Lee, Musk, Gates, Bezos, Buffett, Gandhi, Lincoln, Mandela, Disney, Jackson, Kalam, Tendulkar, P4) — success comes from other yogas (Malavya, Gaja Kesari, Raja, Dhana, etc.), NOT from Śrṅkhalā. This matches our family finding (P4 = wealthiest with no loop; Stan Lee = top comics with no loop).

## Reconciliation
- **Agrees with jyotishvidya + Turn 12:** 3-loop = meaningful leadership marker (Obama); 4-loop can top (Rockefeller, Jobs) if it ties wealth/intellect/authority; 5-loop = latent/weak (Senith); bond strength > loop count; 0-loop ≠ failure.
- **Disagrees with the pasted 500-framework's statistics:** its specific frequencies (3-loop 33% pop / 47% tops, chi-square p<0.001, r=0.68) are illustrative, not measured. Real n=24 shows 0-loop dominance and only 1 five-loop (the weakest). The framework's *qualitative* conclusions (3-loop sweet spot, 5-loop latent) survive; its *quantitative* claims do not.

## Caveats
- 7 charts use noon Moon (approximate) — Ford's 3-loop is Moon-dependent and uncertain; the 11 other noon charts are 0-loop and robust to Moon sign.
- Sample is 24, not 500 — directional, not statistically definitive. But it is **real link-derived data**, unlike the pasted placeholder statistics.
- Achievement tiers are illustrative, not from links.

*(Raw data: `celeb_loops.json`. Parser: `scripts/fetch_celeb_loops.py`.)*
"""
open("/home/user/astrology/celeb_loop_database.md","w").write(md)
print("written celeb_loop_database.md")
print("distribution:", dict(cnt))
print("high-achiever 0-loop:", hicnt.get(0,0), "/", len(hi))
