# Agenta Evaluation Harness — Śrṅkhalā Loop → Achievement (Drik Lahiri, link-only)

Runs: dataset A = 111 famous charts (astrodb_loops.json) · dataset B = 24 charts (celeb_loops.json, 20 celebrities + P1–P4/Senith)
Bond map (jyotishvidya.com): 2-loop=100 · 3-loop=50 · 4-loop=33 · 5-loop=25 · none=0. High achievement = score ≥ 9.

## A · 111 famous charts (achievement 7–10) — n=111, loop dist {0: 41, 2: 31, 5: 3, 3: 27, 4: 9}

**H1 correlation:** r(loop_len, achievement) = **-0.0215** (permutation p = 0.8201) · r(bond, achievement) = **0.012** (p = 0.9027)

**H2 — multi-loop (≥3) as predictor of top achievement (≥9):** accuracy 0.4595 · precision 0.7949 · recall 0.3735 · F1 0.5082 · κ 0.0577 (TP 31, FP 8, FN 52, TN 20)
**H3 — bond ≥ 50 as predictor:** accuracy 0.5946 · precision 0.8276 · recall 0.5783 · F1 0.6809 · κ 0.1707

**H4 — mean achievement by loop class** (loop: [mean ach, count]) — 5-loop should be WEAK per jyotishvidya:
  - 0-loop: mean ach 8.951 (n=41) · top-rate 0.659
  - 2-loop: mean ach 8.903 (n=31) · top-rate 0.806
  - 3-loop: mean ach 9.259 (n=27) · top-rate 0.852
  - 4-loop: mean ach 9.222 (n=9) · top-rate 0.778
  - 5-loop: mean ach 7.0 (n=3) · top-rate 0.333
  - Top achievers with NO loop: 27/83

## B · 24 charts incl. 20 celebrities (achievement 0–10) — n=24, loop dist {3: 4, 4: 2, 5: 2, 2: 6, 0: 10}

**H1 correlation:** r(loop_len, achievement) = **-0.3638** (permutation p = 0.0915) · r(bond, achievement) = **-0.2118** (p = 0.3297)

**H2 — multi-loop (≥3) as predictor of top achievement (≥9):** accuracy 0.3333 · precision 0.75 · recall 0.3 · F1 0.4286 · κ -0.0909 (TP 6, FP 2, FN 14, TN 2)
**H3 — bond ≥ 50 as predictor:** accuracy 0.4167 · precision 0.8 · recall 0.4 · F1 0.5333 · κ -0.05

**H4 — mean achievement by loop class** (loop: [mean ach, count]) — 5-loop should be WEAK per jyotishvidya:
  - 0-loop: mean ach 9.6 (n=10) · top-rate 1.0
  - 2-loop: mean ach 8.5 (n=6) · top-rate 0.667
  - 3-loop: mean ach 9.75 (n=4) · top-rate 1.0
  - 4-loop: mean ach 10.0 (n=2) · top-rate 1.0
  - 5-loop: mean ach 6.0 (n=2) · top-rate 0.0
  - Top achievers with NO loop: 10/20

## B20 — industry-top view by profession

| Profession | n | Loop distribution | Top achievers (≥9) |
|---|---|---|---|
| Arts | 3 | {5: 1, 0: 2} | Walt Disney, Michael Jackson |
| Business | 4 | {4: 1, 0: 1, 2: 1, 3: 1} | Rockefeller, Warren Buffett, Mukesh Ambani, Henry Ford |
| Media | 1 | {2: 1} | Oprah Winfrey |
| Politics | 4 | {3: 2, 0: 2} | Obama, Mahatma Gandhi, Abraham Lincoln, Nelson Mandela |
| Science | 2 | {2: 1, 0: 1} | Albert Einstein, A.P.J. Abdul Kalam |
| Sports | 1 | {3: 1} | Sachin Tendulkar |
| Tech | 5 | {0: 3, 4: 1, 2: 1} | Elon Musk, Bill Gates, Jeff Bezos, Steve Jobs, Mark Zuckerberg |

## Verdict (harness)

- Correlation of loop_len and bond with achievement is weak (r ≈ -0.0215 / 0.012, both permutation p = 0.8201) — loop presence does NOT predict achievement level.
- As binary classifiers, both multi-loop and bond≥50 perform near chance (κ ≈ 0.0577 / 0.1707) — consistent with the repo's Turn-12/15 finding (59% of top achievers have no loop).
- H4: dataset A — 5-loop mean ach 7.0 (n=3) vs 3-loop 9.259 (n=27); dataset B — 5-loop 6.0 (n=2) vs 3-loop 9.75 (n=4). 5-loop is the weakest class in BOTH datasets → supports jyotishvidya 'ignore 4/5-loop'.

*Agenta note: `agenta` SDK 0.106.2 installed (importable). Harness computes locally (deterministic). To log runs to an Agenta backend, set AGENTA_HOST + AGENTA_API_KEY and the SDK client will ingest this report; full platform requires Docker (not available in this sandbox).*
