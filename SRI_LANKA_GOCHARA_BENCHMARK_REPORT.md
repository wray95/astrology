# Sri Lankan Moon-Anchored Gochara Benchmark

## Method

This is a date-only, Moon-anchored research benchmark. It uses a UTC-noon midpoint and Lahiri sidereal planetary positions. It does not calculate Lagna, houses, D1, D9 or time-dependent natal claims.

Because no birth time is available, the Moon sign and nakshatra are sensitivity outputs. Nakshatra is especially time-sensitive.

## Structured results

| Figure | Date-only natal Moon | Nakshatra midpoint | Election date | Saturn sign/degree | Saturn motion | Saturn from natal Moon |
|---|---|---|---|---|---|---:|
| Mahinda Rajapaksa | Aries 16.54° | Bharani | 17 Nov 2005 | Cancer 17.35° | Direct, near station | 4th |
| Gotabaya Rajapaksa | Pisces 27.17° | Revati* | 16 Nov 2019 | Sagittarius 22.50° | Direct | 10th |
| Anura Kumara Dissanayake | Capricorn 7.16° | Uttara Ashadha* | 21 Sep 2024 | Aquarius 20.82° | Retrograde | 2nd |

`*` Moon sign/nakshatra was not stable across the UTC date in the date-only sensitivity calculation, so it must not be treated as exact without birth time.

## Election-date planetary context

| Figure | Mars | Venus | Jupiter | Rahu | Ketu |
|---|---|---|---|---|---|
| Mahinda | Aries 17.74°, retrograde | Sagittarius 17.53°, direct | Libra 10.88°, direct | Pisces 17.41°, retrograde | Virgo 17.41°, retrograde |
| Gotabaya | Libra 4.02°, direct | Scorpio 24.06°, direct | Sagittarius 2.34°, direct | Gemini 16.52°, retrograde | Sagittarius 16.52°, retrograde |
| Anura | Gemini 15.50°, direct | Libra 3.84°, direct | Taurus 26.61°, direct | Pisces 12.67°, retrograde | Virgo 12.67°, retrograde |

## Descriptive observations

- Mahinda's election date had Saturn in Cancer and moving very slowly, meeting the pre-defined near-station rule of absolute speed below 0.01°/day. This is a station-like condition, not retrograde motion.
- Gotabaya's election date had Saturn direct in Sagittarius, approximately 10 signs from the date-only Pisces Moon midpoint.
- Anura's election date had Saturn retrograde in Aquarius, approximately 2 signs from the date-only Capricorn Moon midpoint.
- The three cases do not share the same Saturn sign, retrograde state or Moon-anchored distance. A three-case comparison therefore does not establish a universal election signature.

## Historical context and source correction

- Mahinda's presidential election was held on 17 November 2005; he was inaugurated on 19 November 2005. Source: the election record listed in the JSON.
- Gotabaya's election was held on 16 November 2019 and he was sworn in on 18 November 2019. Source: United Nations in Sri Lanka.
- Anura's election was held on 21 September 2024 and he was sworn in on 23 September 2024. Therefore “late 2024” is acceptable as a broad description, but the election date should be 21 September and the inauguration date 23 September.

## Research conclusion

This benchmark demonstrates how to encode the proposed Gochara framework, but it does not demonstrate that Saturn transits caused the political changes. The sample has N=3, no control leaders, no country-level control dates and uncertain Moon anchors. A valid test would compare many election winners, losers, cabinet changes and crisis dates against matched non-election dates while controlling for historical period and Saturn's ordinary cycle frequency.
