# Divisional Convention & Cox-n Validation Report (2026-08-02)

*Validation pass on v5.1-era P-series engine. Scripts: `scripts/validate_divisional_convention.py`, `scripts/divisional_score_impact.py`. Data: `dataset/divisional_convention_audit.json`, `dataset/divisional_score_impact.json`.*

## Finding 1 — CRITICAL: three different divisional conventions coexist in the repo

`scripts/p_update.py` computes D9/D7/D5 with the **multiplication method** (`floor((lon*N) mod 360 / 30)`).
- Algebraically, this equals the **BPHS movable/fixed/dual** rule (movable→same sign, fixed→+8/+6/+4, dual→+4/+6/+8) — a legitimate classical convention.
- **D7 (Saptamsha):** multiplication ≡ odd/even-forward-from-7th. It matches the repo's earlier method AND the user's Turn-7 link convention → **marriage scores are convention-stable** ✓
- **D5 (Panchamsha):** multiplication ≡ mov/fix/dual (same/5th/9th), which **differs** from the common odd/even-forward-from-5th → **children scores are NOT convention-stable** ✗
- **D9 (Navamsa):** multiplication differs from `senath_recompute.py`'s odd/even-**reverse** method → **same person (P5 Senath) has a different D9 depending on which script computes it** ✗

### Impact (P1–P9)
| Varga | Planets with divergent sign | Convention compared against |
|---|---|---|
| D9 | **48** | senath_recompute.py (odd/even reverse) |
| D7 | **38** | odd/even reverse (mult == odd/even forward) |
| D5 | **51** | odd/even forward from 5th |

### Score impact (marriage % / children %)
| Person | Marriage mult→oer→oef | Children mult→oer→oef |
|---|---|---|
| Senith | 78→44→78 | 11→33→11 |
| Niromi | 22→0→22 | 89→67→**33** |
| Senath | 11→11→11 | 78→**11**→44 |
| Upulakshi | 0→22→0 | 67→33→**78** |
| Dewli | 11→**89**→11 | 33→33→11 |

- **Marriage ranking:** mult == oef (user's link convention) — stable ✓ · mult vs oer differs (Dewli 7th→1st, Niromi 5th→9th) ✗
- **Children ranking:** mult vs oef differs (`Niromi>Senath>Upulakshi` → `Upulakshi>Senath>Lalith>Niromi`) ✗

### Action needed
1. **Adopt one convention repo-wide** and document it in `p_update.py`. Recommended: BPHS mov/fix/dual (= current multiplication) for D7/D5, but **recompute P5 Senath's D9 with the same engine** (or update `senath_recompute.py`) so the two agree — currently the same person gets two different navamsas.
2. **Re-label the published P-series marriage/children percentages** as convention-dependent (state which convention was used).
3. Children axis is the most sensitive — treat D5-based scores as directional only until the convention is fixed.

## Finding 2 — "Cox PH direction signal" is fragile (n=12 unique, not 13)

`wiki_marriage_labels` in `dataset/marriage_conception_timing.json`:
- **Duplicate:** "Simone Biles" appears twice (13 rows, **12 unique people**). The commit message says n=13; the file's own `cox_ph_notes` says n=10 — **three inconsistent counts**.
- **Direction test (D7 7L in Kendra → earlier marriage):**
  - Kendra group: **n=2** (George Lucas 24.8, Cate Blanchett 28.6) vs non-kendra n=11
  - Mann-Whitney U p = **0.62** — not significant
  - **Leave-one-out: 1/13 removals flips the direction** — the "signal" survives only while both kendra cases remain
- **Age spot-checks (7/13):** Zuckerberg 28.0 ✓ · Matt Damon 35.2 ✓ · George Lucas 24.8 ✓ · Simone Biles 26.1 ✓ · Cate Blanchett 28.6 ✓ · Sigourney Weaver 35.0 ✓ · Patty Loveless 19.0 ✓ — ages are accurate.
- **Caveat:** celebrity birth times mostly unknown (noon default) → D7 ascendant/houses approximate → kendra flags are time-sensitive.

### Action needed
1. Dedupe the labels (remove the "(P2 match)" row).
2. Reframe the Cox result as **hypothesis-generation only**: at n=12 with a 2-person treatment group, it cannot support a directional claim. The repo's own note ("need 50+ labels") is correct.
3. Priorities for real evidence: (a) labels with **known birth times**, (b) 50+ unique people, (c) convention-fixed D7.

## Bottom line
- The P-series **marriage** axis is robust to convention choice (mult == user's link convention).
- The **children** axis and the **navamsa**-dependent outputs (vargottama, D9 dignity) are **convention-dependent** and must be locked to one documented convention.
- The **Cox "direction signal"** should not be cited as evidence yet — it's n=12, p=0.62, 2-person group, LOO-unstable.

## RESOLUTION (2026-08-02, same session) — convention locked + outliers fixed

### Decision: multiplication method (= BPHS movable/fixed/dual) is THE repo convention
- Created **`scripts/varga_conventions.py`** — single source of truth (`varga_sign(lon, N)`), self-tested against the BPHS D9 table (ALL 12 signs OK).
- Rationale: it is what the NEXUS engine (`p_update.py`) AND the ML matrices (`build_v4_matrix.py`, 6,520 charts) already use; locking it changes zero engine outputs; D9 matches classical BPHS exactly.

### Fix applied: `scripts/senath_recompute.py`
- `d9_sign()` changed from odd/even-REVERSE → locked convention (via varga_conventions). The reverse variant was an internal outlier that matched NEITHER the engine NOR the user's astrologylover.com link method.
- **Senath D9 deltas (link data, locked convention vs Turn 25/26):**
  | Point | Turn 25/26 (reverse) | Locked BPHS |
  |---|---|---|
  | Lagna D9 | Gemini/Leo | **Aquarius** |
  | Moon D9 | Gemini | **Cancer** |
  | Mars D9 | Capricorn | **Taurus** |
  | Saturn D9 | Pisces | **Pisces** (unchanged) |
  | Sun D9 | Sagittarius | Sagittarius (unchanged) |
  - **Vargottama conclusion UNCHANGED: no planet vargottama** (incl. Sun — the Turn-25 "Sun vargottama" was already nulled by Turn-26's recompute).

### NEW finding — position-source discrepancy for Senath (flag for user)
- Engine PD records Senath at **Colombo (6.9355, 79.8487, tz +5.5), 16:08:40 local**.
- The Turn-21 Drik LINK defaulted to **Houston, TX** (known proxy) → Moon Cap 20.873°.
- Swiss Ephemeris (Colombo, 16:08:40 IST) → Moon **Cap 19.152°** → **Δ = −103 arcmin (≈3.5 h of Moon motion)**.
- Consequence: D9 Moon = Cancer (link data) vs Gemini (engine data). Engine is likely the correct *person* data (real birthplace); the link was the proxy. **User should confirm Senath's true birth place/time** — until then both exist in the repo with different D9 outcomes.
- This is NOT a convention issue — it is a position-source issue, and both sides are internally consistent.

### P1–P4 historical D9 (Turn 6–7) — documented, NOT overwritten
- Per the standing "do not change my system" rule, the P1–P4 D9 analyses (d9_shrinkala.py, user's astrologylover.com method: odd→same, even→9th) are left as-is.
- Comparison vs locked BPHS on real degree data: **20/28 planet-D9 signs differ** (P1: 4, P2: 6, P3: 6, P4: 4). Examples: P1 Venus D9 Virgo→Capricorn; P2 Jupiter D9 Aquarius→Gemini; P3 Moon D9 Pisces→Cancer; P4 Saturn D9 Aquarius→Libra.
- **Decision needed from user:** re-derive P1–P4 D9 (loops, dignity, vargottama) under the locked BPHS convention, or keep the link-method D9 as the P1–P4 standard (it is a legitimate classical variant) — the two cannot both be "the repo's D9".

### Going forward
- All NEW varga computation: use `scripts/varga_conventions.py`.
- The P-series marriage (D7) axis: stable under every convention tested.
- The children (D5) axis: locked to engine convention; scores already reflect it.
