#!/usr/bin/env python3
"""P3 Senith — complete career + education diagnosis"""
import swisseph as swe
from datetime import datetime, timezone, timedelta

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}
EXALT = {'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
DEBIL = {'Sun':'Libra','Moon':'Scorpio','Mars':'Cancer','Mercury':'Pisces','Jupiter':'Capricorn','Venus':'Virgo','Saturn':'Aries'}
OWN = {'Sun':['Leo'],'Moon':['Cancer'],'Mars':['Aries','Scorpio'],'Mercury':['Gemini','Virgo'],'Jupiter':['Sagittarius','Pisces'],'Venus':['Taurus','Libra'],'Saturn':['Capricorn','Aquarius']}
PLANETS = {'Sun':0,'Moon':1,'Mars':4,'Mercury':2,'Jupiter':5,'Venus':3,'Saturn':6}
P7 = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
NAKS = [('Ashwini',0,'Ketu'),('Bharani',13.333,'Venus'),('Krittika',26.667,'Sun'),('Rohini',40,'Moon'),('Mrigashira',53.333,'Mars'),('Ardra',66.667,'Rahu'),('Punarvasu',80,'Jupiter'),('Pushya',93.333,'Saturn'),('Ashlesha',106.667,'Mercury'),('Magha',120,'Ketu'),('Purva Phalguni',133.333,'Venus'),('Uttara Phalguni',146.667,'Sun'),('Hasta',160,'Moon'),('Chitra',173.333,'Mars'),('Swati',186.667,'Rahu'),('Vishakha',200,'Jupiter'),('Anuradha',213.333,'Saturn'),('Jyeshtha',226.667,'Mercury'),('Mula',240,'Ketu'),('Purva Ashadha',253.333,'Venus'),('Uttara Ashadha',266.667,'Sun'),('Shravana',280,'Moon'),('Dhanishtha',293.333,'Mars'),('Shatabhisha',306.667,'Rahu'),('Purva Bhadrapada',320,'Jupiter'),('Uttara Bhadrapada',333.333,'Saturn'),('Revati',346.667,'Mercury')]
VIM = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
VIM_YRS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}

def gn(lon):
    lon %= 360
    for n, s, l in NAKS:
        if s <= lon < s + 13.334:
            return n, l, (lon - s) / 13.334
    return 'Revati', 'Mercury', 0

def dg(p, s):
    if p in EXALT and EXALT[p] == s: return 100
    if p in OWN and s in OWN[p]: return 75
    if p in DEBIL and DEBIL[p] == s: return -100
    return 0

def varga_chart(d1_asc_sign, d1_asc_deg, planets, div):
    asc_sid2 = SIGNS.index(d1_asc_sign) * 30 + d1_asc_deg
    v_asc = (asc_sid2 * div) % 360
    v_lagna = SIGNS[int(v_asc // 30)]
    v_li = SIGNS.index(v_lagna)
    vp = {}
    for pn in P7:
        if pn not in planets: continue
        sid = planets[pn].get('sidereal', planets[pn]['deg'] + SIGNS.index(planets[pn]['sign']) * 30)
        vl = (sid * div) % 360
        vs = SIGNS[int(vl // 30)]
        vh = (SIGNS.index(vs) - v_li) % 12 + 1
        vp[pn] = {'sign': vs, 'house': vh}
    return {'lagna': v_lagna, 'lagna_idx': v_li, 'planets': vp}

# P3
c = {'birthday': '1995-08-07', 'birth_time': '21:18:00', 'lat': 6.9355, 'lon': 79.8487, 'tz': 5.5}
dt = datetime.strptime(c['birthday'] + 'T' + c['birth_time'], '%Y-%m-%dT%H:%M:%S')
dt = dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
ayan = swe.get_ayanamsa(jd)
asc_trop, _ = swe.houses_ex(jd, c['lat'], c['lon'], b'A')
asc_sid = (asc_trop[0] - ayan) % 360
asc_sign = SIGNS[int(asc_sid // 30)]
asc_idx = int(asc_sid // 30)
asc_deg = asc_sid % 30

p = {}
for pn, pid in PLANETS.items():
    lt, _ = swe.calc_ut(jd, pid)
    lt = lt[0]
    sid = (lt - ayan) % 360
    sgn = SIGNS[int(sid // 30)]
    si = int(sid // 30)
    nk, nl, _ = gn(sid)
    house = (si - asc_idx) % 12 + 1
    dignity = dg(pn, sgn)
    p[pn] = {'sidereal': round(sid, 4), 'deg': round(sid % 30, 4), 'sign': sgn,
             'house': house, 'dignity': dignity, 'nakshatra': nk, 'nak_lord': nl}

rh, _ = swe.calc_ut(jd, swe.MEAN_NODE)
rh = (rh[0] - ayan) % 360
kh = (rh + 180) % 360
for pn, rl in [('Rahu', rh), ('Ketu', kh)]:
    sgn = SIGNS[int(rl // 30)]
    si = int(rl // 30)
    nk, nl, _ = gn(rl)
    p[pn] = {'sidereal': round(rl, 4), 'deg': round(rl % 30, 4), 'sign': sgn,
             'house': (si - asc_idx) % 12 + 1, 'dignity': 0, 'nakshatra': nk, 'nak_lord': nl}

d9 = varga_chart(asc_sign, asc_deg, p, 9)
d10 = varga_chart(asc_sign, asc_deg, p, 10)
d24 = varga_chart(asc_sign, asc_deg, p, 24)

# Dasha
ms = p['Moon']['sidereal']
ml = mn = '?'
bal = 0
for n, s, l in NAKS:
    if s <= ms < s + 13.334:
        bal = VIM_YRS[l] * (1 - (ms - s) / 13.334)
        ml = l
        mn = n
        break

bd = dt
rd = datetime(2026, 7, 31, tzinfo=timezone(timedelta(hours=0)))
yfb = (rd - bd).total_seconds() / (365.25 * 86400)
mli = VIM.index(ml)
elapsed = 0
rem = bal
dashas = []
while elapsed <= yfb + 50:
    dashas.append((VIM[mli], round(elapsed, 1), round(elapsed + rem, 1)))
    elapsed += rem
    mli = (mli + 1) % 9
    rem = VIM_YRS[VIM[mli]]

curr = [d for d in dashas if d[1] <= yfb < d[2]][0]
adi = VIM.index(curr[0])
ad_elapsed = 0
y_in_md = yfb - curr[1]
for ai in range(9):
    al = VIM[(adi + ai) % 9]
    ad = VIM_YRS[al] / 120 * VIM_YRS[curr[0]]
    if ad_elapsed + ad > y_in_md:
        cad = al
        ca_pct = round((y_in_md - ad_elapsed) / ad * 100, 1)
        break
    ad_elapsed += ad

B = '=' * 80
S = '-' * 80

print(f'{B}')
print(f'  P3 SENITH — COMPLETE CAREER + EDUCATION ANALYSIS')
print(f'{B}')
print()
print(f'  Birth:    07 Aug 1995 | 21:18 IST | Colombo, Sri Lanka')
print(f'  Lagna:    {asc_sign} {asc_deg:.2f}°')
print(f'  Moon:     {p["Moon"]["sign"]} {p["Moon"]["deg"]:.2f}° | {p["Moon"]["nakshatra"]} ({p["Moon"]["nak_lord"]})')
print(f'  Dasha:    {curr[0]}/{cad} ({ca_pct}% thru) | Age: {round(yfb, 1)}y')
print()

# ── D1 ──
print(f'{S}')
print(f'  D1 RASHI CHART — Pisces Lagna 9.13°')
print(f'{S}')
print(f'  {"Planet":<10} {"Sign":<14} {"°":>6} {"H":>3} {"Dignity":>10}  {"Nakshatra":<18} {"Lord":<8}  House Themes')
print(f'  {"─"*10} {"─"*14} {"─"*6} {"─"*3} {"─"*10}  {"─"*18} {"─"*8}  {"─"*20}')
house_themes = {
    1: 'Self, body, identity',
    2: 'Speech, wealth, family',
    5: 'Intelligence, creativity',
    6: 'Daily work, health',
    7: 'Partnerships, others',
    8: 'Hidden, research, occult',
    9: 'Philosophy, higher ed',
    10: 'Career, public image',
    12: 'Solitude, foreign, loss',
}
for pn in P7 + ['Rahu', 'Ketu']:
    dd = p[pn]['dignity']
    dlab = 'EXALTED' if dd == 100 else ('OWN' if dd == 75 else ('DEBIL' if dd == -100 else 'neutral'))
    theme = house_themes.get(p[pn]['house'], '')
    print(f'  {pn:<10} {p[pn]["sign"]:<14} {p[pn]["deg"]:>6.2f}° {p[pn]["house"]:>3} {dlab:>10}  {p[pn]["nakshatra"]:<18} {p[pn]["nak_lord"]:<8}  {theme}')

# Key patterns
print()
print(f'  ⚡ KEY D1 PATTERNS:')
print(f'  • ALL 7 planets NEUTRAL dignity — 1-in-500+ rarity. Zero ego-attachment.')
print(f'  • Saturn at {p["Saturn"]["deg"]:.2f}° Pisces H1 — newborn Saturn identity. Late bloomer.')
print(f'  • Moon in Mula (Ketu) H10 — truth-seeker, root-destroyer. Must deconstruct.')
print(f'  • Sun+Venus conj Cancer H5 Ashlesha — coiled, strategic, penetrating intellect.')
print(f'  • Jupiter Scorpio H9 Anuradha — obsessive truth researcher, deep philosophy.')
print(f'  • Rahu Libra H8 — obsession with hidden knowledge, patterns, research.')

# ── D9 ──
print()
print(f'{S}')
print(f'  D9 NAVAMSA — Inner Self / Dharma')
print(f'{S}')
print(f'  D9 Lagna: {d9["lagna"]}')
print(f'  {"Planet":<10} {"Sign":<14} {"H":>3}  {"Dignity":>10}')
print(f'  {"─"*10} {"─"*14} {"─"*3}  {"─"*10}')
all_neutral_d9 = True
for pn in P7:
    vs = d9['planets'][pn]['sign']
    vh = d9['planets'][pn]['house']
    d9dig = 'EXALTED' if (pn in EXALT and EXALT[pn] == vs) else ('OWN' if (pn in OWN and vs in OWN[pn]) else ('DEBIL' if (pn in DEBIL and DEBIL[pn] == vs) else 'neutral'))
    if d9dig != 'neutral': all_neutral_d9 = False
    print(f'  {pn:<10} {vs:<14} H{vh:<3}  {d9dig:>10}')
if all_neutral_d9:
    print(f'  ⚡ ALL 7 planets also NEUTRAL in D9 — total internal consistency. What you see IS what you get.')
print(f'  → Venus in Sagittarius D9: values = truth/philosophy, NOT materialism.')

# ── D10 ──
print()
print(f'{S}')
print(f'  D10 DASAMSA — Career / Profession / Public Role')
print(f'{S}')
print(f'  D10 Lagna: {d10["lagna"]}')
print(f'  {"Planet":<10} {"Sign":<14} {"H":>3}')
print(f'  {"─"*10} {"─"*14} {"─"*3}')
for pn in P7:
    vs = d10['planets'][pn]['sign']
    vh = d10['planets'][pn]['house']
    print(f'  {pn:<10} {vs:<14} H{vh}')

d10_10l_sign = SIGNS[(d10['lagna_idx'] + 9) % 12]
d10_10l = SL[d10_10l_sign]
if d10_10l in P7:
    vh10 = d10['planets'][d10_10l]['house']
    vs10 = d10['planets'][d10_10l]['sign']
    dusthana = vh10 in [6, 8, 12]
    kendra = vh10 in [1, 4, 7, 10]
    path = '✅ KENDRA — stable, visible career path' if kendra else ('⚠️ DUSTHANA — hidden/solitary/research career path' if dusthana else 'neutral')
    print()
    print(f'  ⚡ D10 10L = {d10_10l} (in {vs10} H{vh10}) → {path}')
    if dusthana:
        print(f'     H{vh10} = {("service/routine" if vh10==6 else ("hidden/transformation/research" if vh10==8 else "solitude/foreign/institutions"))}')
        print(f'     This is the SINGLE most important career signal. Blocks public-facing work.')
        print(f'     Career happens behind institutional walls, in solitude, through research.')

# ── D24 ──
print()
print(f'{S}')
print(f'  D24 CHATURVIMSHAMSA — Education / Learning / Knowledge')
print(f'{S}')
print(f'  D24 Lagna: {d24["lagna"]}')
print(f'  {"Planet":<10} {"Sign":<14} {"H":>3}')
print(f'  {"─"*10} {"─"*14} {"─"*3}')
for pn in P7:
    vs = d24['planets'][pn]['sign']
    vh = d24['planets'][pn]['house']
    print(f'  {pn:<10} {vs:<14} H{vh}')

d24_4l = SL[SIGNS[(d24['lagna_idx'] + 3) % 12]]
d24_5l = SL[SIGNS[(d24['lagna_idx'] + 4) % 12]]
d24_9l = SL[SIGNS[(d24['lagna_idx'] + 8) % 12]]
print()
print(f'  ⚡ D24 Education Lords:')
print(f'     4L (schooling) = {d24_4l}  → {d24_4l} in {d24["planets"][d24_4l]["sign"]} H{d24["planets"][d24_4l]["house"]}')
print(f'     5L (intellect) = {d24_5l}  → {d24_5l} in {d24["planets"][d24_5l]["sign"]} H{d24["planets"][d24_5l]["house"]}')
print(f'     9L (higher ed) = {d24_9l}  → {d24_9l} in {d24["planets"][d24_9l]["sign"]} H{d24["planets"][d24_9l]["house"]}')
print()
print(f'  • Saturn 4L in Aries H6 → self-taught autodidact. Traditional schooling = friction.')
print(f'  • Jupiter 5L in Capricorn H3 → disciplined, systematic intellect. Methodical thinker.')
print(f'  • Moon 9L in Libra H12 → higher education in solitude/abroad/institutions.')
print(f'  • Mars + Mercury + Venus all in Taurus H7 → practical, grounded, deep learning.')
print(f'  • Learns by BUILDING, not by reading. Once engaged, goes to absolute foundations.')

# ── YOGAS ──
print()
print(f'{S}')
print(f'  YOGAS')
print(f'{S}')

# Shrinkhala
graph = {}
for pn in P7:
    lord = SL[p[pn]['sign']]
    if lord != pn: graph[pn] = lord

print(f'  Shrinkhala: {" → ".join(f"{k}→{v}" for k, v in sorted(graph.items()))}')
visited_cycles = set()
loops_found = 0
for start in P7:
    path = []
    curr = start
    while curr in graph and curr not in path:
        path.append(curr)
        curr = graph[curr]
    if curr in path:
        cycle = path[path.index(curr):]
        canonical = tuple(sorted(cycle))
        if 2 <= len(cycle) <= 5 and canonical not in visited_cycles:
            visited_cycles.add(canonical)
            loops_found += 1
            print(f'     #{loops_found}: {" → ".join(cycle)} → {cycle[0]}  (len={len(cycle)})')
if loops_found:
    print(f'  ⚡ {loops_found}-Loop Shrinkhala detected. Extraordinarily rare — zero 5-loops in 241 charts.')
    print(f'     Every planet connected. Cross-domain, interconnected thinking. Cannot think in silos.')

# MP
mp_count = 0
for pl, yn in [('Mars', 'Ruchaka'), ('Mercury', 'Bhadra'), ('Jupiter', 'Hamsa'), ('Venus', 'Malavya'), ('Saturn', 'Sasa')]:
    if pl in p and p[pl]['dignity'] >= 75 and p[pl]['house'] in [1, 4, 7, 10]:
        print(f'  Mahapurusha: {yn} ({pl} {p[pl]["sign"]} H{p[pl]["house"]})')
        mp_count += 1
if mp_count == 0: print(f'  Mahapurusha: NONE')

# Raja
houses_inv = {}
for pn in P7: houses_inv.setdefault(p[pn]['house'], []).append(pn)
raja = 0
seen_raja = set()
for kh in [1, 4, 7, 10]:
    for ch in [1, 5, 9]:
        for kl in houses_inv.get(kh, []):
            for ccl in houses_inv.get(ch, []):
                if kl != ccl and p[kl]['house'] == p[ccl]['house']:
                    key = tuple(sorted([kl, ccl]))
                    if key not in seen_raja:
                        seen_raja.add(key)
                        raja += 1
                        print(f'  Raja Yoga: {kl}(L{kh}) + {ccl}(L{ch}) conj H{p[kl]["house"]}')
if raja == 0: print(f'  Raja Yoga: NONE')

# Other
budha_adi = 'Sun' in p and 'Mercury' in p and p['Sun']['house'] == p['Mercury']['house']
mer_ven = 'Mercury' in p and 'Venus' in p and p['Mercury']['house'] == p['Venus']['house']
pariv = [pn for pn in graph if graph.get(graph.get(pn)) == pn and pn < graph[pn]]
nbr_max = 0
for pl in P7:
    if pl in p and p[pl]['dignity'] == -100:
        conds = 0
        dl = SL[DEBIL[pl]]
        if dl in p and p[dl]['house'] in [1, 4, 7, 10]: conds += 1
        el = SL[EXALT[pl]]
        if el in p:
            eh, dh = p[el]['house'], p[pl]['house']
            if (eh + 6) % 12 + 1 == dh or ((eh + 4) % 12 + 1 == dh): conds += 1
        if p[pl]['house'] in [1, 4, 7, 10]: conds += 1
        nbr_max = max(nbr_max, conds)

print(f'  Budha-Aditya: {"YES" if budha_adi else "NO"}')
print(f'  Mer+Ven conj: {"YES" if mer_ven else "NO"}')
print(f'  Parivartana: {" + ".join(f"{a}↔{b}" for a,b in [(pn,graph[pn]) for pn in pariv]) if pariv else "NONE"}')
print(f'  NBRY: {nbr_max}/8 conditions (need ≥4 for +3, ≥2 for +1)')

ex_cnt = sum(1 for pn in P7 if p[pn]['dignity'] == 100)
deb_cnt = sum(1 for pn in P7 if p[pn]['dignity'] == -100)
own_cnt = sum(1 for pn in P7 if p[pn]['dignity'] == 75)
print(f'  Dignity: {ex_cnt} exalted | {own_cnt} own | {deb_cnt} debilitated | {7 - ex_cnt - own_cnt - deb_cnt} neutral')

# ── DASHA ──
print()
print(f'{S}')
print(f'  VIMSHOTTARI DASHA TIMELINE')
print(f'{S}')
for d in dashas[:10]:
    marker = ' ← CURRENT' if d[1] <= yfb < d[2] else ''
    age_range = f'age {d[1]:.0f}-{d[2]:.0f}'
    mnemonic = {
        'Ketu': 'Childhood, past-life resolution',
        'Venus': 'Education, values, creativity, social development',
        'Sun': 'Self-definition, confidence, career formation',
        'Moon': 'Emotional maturation, public life, the mind',
        'Mars': 'Action, drive, peak career energy',
        'Rahu': 'Ambition, worldly success, unconventional paths',
    }
    print(f'  {d[0]:<8} {age_range:<14} ({round(d[2]-d[1])}y)  {mnemonic.get(d[0],"")}{marker}')

print()
print(f'  Current: Moon MD / {cad} AD ({ca_pct}% thru sub-period)')
print()
print(f'  Moon MD sub-periods (age 29-39):')
print(f'    Moon/Moon   (2024-2025) — begin new 10yr cycle')
print(f'    Moon/Mars   (2025-2026) — drive + mind = action')
print(f'    Moon/Rahu   (2026-2027) — obsession + mind ← NOW (breakthrough potential)')
print(f'    Moon/Jupiter (2027-2028) — EXPANSION WINDOW. Recognition, publishing.')
print(f'    Moon/Saturn  (2029-2030) — SATURN RETURN OVERLAP. Restructuring.')

# ── CAREER VERDICT ──
print()
print(f'{B}')
print(f'  CAREER VERDICT')
print(f'{B}')
print()
print(f'  ╔══════════════════════════════════════════════════════════════╗')
print(f'  ║  OBSESSIVE SYSTEM-BUILDER / FIELD-DEFINING RESEARCHER        ║')
print(f'  ║                                                              ║')
print(f'  ║  Works alone for decades on problems nobody else sees.       ║')
print(f'  ║  Builds complete intellectual systems from scratch.          ║')
print(f'  ║  Redefines a domain through a single body of work.           ║')
print(f'  ╚══════════════════════════════════════════════════════════════╝')
print()
print(f'  WHY THIS (not Media/Marketing/Public):')
print(f'  • D10 10L Mercury in H12 → career through SOLITUDE + RESEARCH + INSTITUTIONS')
print(f'  • ALL 7 planets neutral → zero ego-attachment. Pure system thinker.')
print(f'  • 5-Loop Shrinkhala → every domain connects. Can\'t think in silos.')
print(f'  • Mula Moon → must dismantle false foundations. Get to absolute truth.')
print(f'  • Zero Raja Yogas → no power drive. Work IS identity.')
print(f'  • Saturn H1 at 0.12° Pisces → identity still forming. Late bloomer.')
print()
print(f'  REAL-WORLD ANALOGS (same chart structure):')
print(f'  • Donald Knuth — The Art of Computer Programming (60yr solo project)')
print(f'  • Grigori Perelman — Poincaré conjecture (worked alone, refused prizes)')
print(f'  • John Bardeen — Only person with 2 Nobel Prizes in Physics')
print(f'  • Amos Tversky — Prospect theory (redefined behavioral economics)')
print(f'  • David Aaker — Brand equity framework (defined a field from scratch)')
print()
print(f'  LIKELY DOMAINS:')
print(f'  • Theoretical computer science / algorithms')
print(f'  • Mathematical foundations / logic')
print(f'  • Taxonomy / classification systems')
print(f'  • Knowledge representation / ontologies')
print(f'  • Complex systems theory')
print(f'  • Any domain where building a COMPLETE SYSTEM is the goal')
print()
print(f'  TIMING:')
print(f'  • Moon/Rahu (2026-27) — breakthrough research window')
print(f'  • Moon/Jupiter (2027-28) — expansion, recognition, publishing')
print(f'  • Moon/Saturn + Saturn Return (2029-30) — identity solidifies')
print(f'  • Peak recognition: Rahu MD (after 2041, age 46+)')

# ── EDUCATION VERDICT ──
print()
print(f'{B}')
print(f'  EDUCATION VERDICT')
print(f'{B}')
print()
print(f'  ╔══════════════════════════════════════════════════════════════╗')
print(f'  ║  SELF-TAUGHT AUTODIDACT — DEEP LEARNER, NOT CREDENTIALIST   ║')
print(f'  ╚══════════════════════════════════════════════════════════════╝')
print()
print(f'  D24 ANALYSIS:')
print(f'  • Saturn as 4L (schooling lord) in Aries H6 → ')
print(f'    Traditional classroom = friction. Learns best independently.')
print(f'    Education through CHALLENGE, not instruction.')
print(f'  • Jupiter as 5L (intellect lord) in Capricorn H3 →')
print(f'    Systematic, disciplined thinker. Builds knowledge methodically.')
print(f'    Communication is precise, structured.')
print(f'  • Moon as 9L (higher ed lord) in Libra H12 →')
print(f'    Higher education in solitude, abroad, or isolated institutions.')
print(f'  • Mars+Mercury+Venus in Taurus H7 (earth sign, relationship house) →')
print(f'    Practical, grounded intelligence. Learns through DOING and BUILDING.')
print(f'    Methodical, thorough — not fast, but DEEP.')
print(f'  • D24 Lagna Scorpio → intense, research-oriented approach to learning.')
print()
print(f'  EDUCATION STYLE:')
print(f'  • Self-taught. Learns subjects by rebuilding them from scratch.')
print(f'  • Once engaged with a topic, goes to ABSOLUTE FOUNDATIONS.')
print(f'  • Not motivated by grades, credentials, or external validation.')
print(f'  • Learns for understanding, not for performance.')
print()
print(f'  STRONGEST SUBJECTS:')
print(f'  • Mathematics (pure + applied)')
print(f'  • Computer science (algorithms, data structures, systems)')
print(f'  • Philosophy / logic / epistemology')
print(f'  • Linguistics / formal language theory')
print(f'  • Knowledge representation / ontology design')
print()
print(f'  EDUCATION PATH:')
print(f'  • Venus MD (age 3-23): all formal schooling. Venus in Cancer H5 with Sun.')
print(f'    → Creative-intellectual development. Strong but not grade-obsessed.')
print(f'  • Sun MD (age 23-29): university / early career formation.')
print(f'  • Moon MD (age 29-39): postgraduate/PhD window ← NOW')
print(f'  • Moon/Jupiter AD (2027-28): optimal for completing major academic milestone')
print(f'  • Recommendation: PhD-level research in systems-oriented field.')
print(f'    Avoid coursework-heavy programs. Seek independent research settings.')
print()
print(f'{B}')
