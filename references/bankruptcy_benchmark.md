# Bankruptcy Benchmark — Negative Control Dataset
Source: CBS News "Celebrities Who Filed for Bankruptcy" + Astro-Databank
Date: 28 Jul 2026

## Confirmed Bankruptcy Cases (with DOB)

| Name | DOB | Known TOB | Place | Debt | Year |
|---|---|---|---|---|---|
| Alex Jones | 11 Feb 1974 | ? | Dallas, TX | $1.5B | 2022 |
| Todd Chrisley | 6 Apr 1969 | ? | Georgia | $49.4M | 2012 |
| Teresa Giudice | 18 May 1972 | ? | Patterson, NJ | $11M | 2009 |
| Sonja Morgan | 25 Nov 1963 | ? | Albany, NY | $19.8M | 2010 |
| Aaron Carter | 7 Dec 1987 | ? | Tampa, FL | $2M | 2013 |
| Francis Ford Coppola | 7 Apr 1939 | ? | Detroit, MI | Multiple | 3 bankruptcies |
| Abby Lee Miller | 21 Sep 1965 | ? | Pittsburgh, PA | $775K | 2010/2017 |
| Mike Tyson | 30 Jun 1966 | 08:45 | Brooklyn, NY | $23M | 2003 |
| 50 Cent | 6 Jul 1975 | ? | Queens, NY | $32M | 2015 |
| MC Hammer | 30 Mar 1962 | ? | Oakland, CA | $13M | 1996 |
| Walt Disney | 5 Dec 1901 | 00:30 | Chicago, IL | Multiple | 1923 |
| Donald Trump | 14 Jun 1946 | 10:54 | Queens, NY | Multiple | 6 bankruptcies |

## Astro-Databank Category Reference
- Category: Lifestyle: Financial: Loss - Bankruptcy
- URL: astro.com/astro-databank/Category:Lifestyle_:_Financial_:_Loss_-_Bankruptcy
- Status: Cloudflare-blocked (requires browser)

## How to Use for Engine Validation

1. Find these names in VedAstro 15K dataset → extract birth data
2. Run through Swiss Ephemeris pipeline → compute D1, D9, yogas
3. Check for Daridra Yoga indicators:
   - 6L/8L/12L in 2H or 11H
   - 2L/11L in 6/8/12
   - Kemadruma Yoga (no planets in 2nd/12th from Moon)
   - Debilitated 2L/11L without NBRY
   - Venus + Saturn conjunction in dusthana
4. Compare Dhana Yoga scores vs known bankruptcy outcomes
5. If engine gives high wealth scores to bankruptcy cases → false positive → recalibrate

## Priority: Those WITH Known Birth Times
- Mike Tyson (30 Jun 1966, 08:45, Brooklyn) — Rodden A
- Walt Disney (5 Dec 1901, 00:30, Chicago) — Rodden A
- Donald Trump (14 Jun 1946, 10:54, Queens) — Rodden A
