#!/usr/bin/env python3
"""
COMPREHENSIVE VARGA + DASHA CROSS-REFERENCE
10 charts: VCs vs Academics vs Fraudsters
D1, D2, D9, D10, D24, D60 + Vimshottari dasha timeline
"""
import swisseph as swe
import json, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
      "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),
        ("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),
        ("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),
        ("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),
        ("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),
        ("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),
        ("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN = 360.0/27
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}

TZ_MAP = {
    "Peter Thiel": 1,
    "Marc Andreessen": -5,
    "Vinod Khosla": 5.5,
    "Paul Graham": 0,
    "Noam Chomsky": -5,
    "Carl Sagan": -5,
    "Richard Dawkins": 3,
    "Bernard Madoff": -4,
    "Elizabeth Holmes": -5,
    "Sam Bankman-Fried": -8,
}

CHARTS_RAW = [
    {"name":"Peter Thiel","category":"Venture Capitalist","birthday":"1967-10-11","birth_time":"04:15:00","location":"Frankfurt, Germany","coords":(50.1109,8.6821)},
    {"name":"Marc Andreessen","category":"Venture Capitalist","birthday":"1971-07-09","birth_time":"15:22:00","location":"Cedar Falls, Iowa","coords":(42.5275,-92.4455)},
    {"name":"Vinod Khosla","category":"Venture Capitalist","birthday":"1955-01-28","birth_time":"11:45:00","location":"Delhi, India","coords":(28.6139,77.2090)},
    {"name":"Paul Graham","category":"Venture Capitalist / Academic","birthday":"1964-11-13","birth_time":"08:12:00","location":"Weymouth, UK","coords":(50.6144,-2.4576)},
    {"name":"Noam Chomsky","category":"Academic / Professor","birthday":"1928-12-07","birth_time":"07:15:00","location":"Philadelphia, PA","coords":(39.9526,-75.1652)},
    {"name":"Carl Sagan","category":"Academic / Professor","birthday":"1934-11-09","birth_time":"17:05:00","location":"Brooklyn, NY","coords":(40.6782,-73.9442)},
    {"name":"Richard Dawkins","category":"Academic / Professor","birthday":"1941-03-26","birth_time":"06:15:00","location":"Nairobi, Kenya","coords":(-1.2921,36.8219)},
    {"name":"Bernard Madoff","category":"Corporate Bankruptcy / Fraud","birthday":"1938-04-29","birth_time":"07:35:00","location":"Queens, NY","coords":(40.7282,-73.7949)},
    {"name":"Elizabeth Holmes","category":"Corporate Bankruptcy / Fraud","birthday":"1984-02-03","birth_time":"14:10:00","location":"Washington, DC","coords":(38.9072,-77.0369)},
    {"name":"Sam Bankman-Fried","category":"Corporate Bankruptcy / Fraud","birthday":"1992-03-06","birth_time":"10:14:00","location":"Stanford, CA","coords":(37.4241,-122.1661)},
]

# Known life events for dasha cross-reference
LIFE_EVENTS = {
    "Elizabeth Holmes": [
        (2003, "Dropped out of Stanford to start Theranos"),
        (2014, "Theranos valued at $9B, Holmes worth $4.5B"),
        (2015, "WSJ exposé begins, Theranos fraud revealed"),
        (2018, "Charged with wire fraud by SEC"),
        (2022, "Convicted, sentenced to 11+ years"),
    ],
    "Sam Bankman-Fried": [
        (2019, "Founded FTX"),
        (2021, "FTX valued at $32B, SBF worth $26B"),
        (2022, "Nov: FTX collapses, files bankruptcy"),
        (2023, "Convicted of fraud, sentenced to 25 years"),
    ],
    "Bernard Madoff": [
        (1960, "Founded Bernard L. Madoff Investment Securities"),
        (1990, "Became NASDAQ chairman"),
        (2008, "Dec 11: Arrested, Ponzi scheme revealed — $64.8B fraud"),
        (2009, "Sentenced to 150 years"),
    ],
    "Peter Thiel": [
        (1998, "Co-founded PayPal"),
        (2002, "PayPal sold to eBay for $1.5B"),
        (2004, "First outside investor in Facebook ($500K→$1B)"),
        (2020, "Palantir IPO"),
    ],
    "Marc Andreessen": [
        (1994, "Co-founded Netscape"),
        (1995, "Netscape IPO — worth $58M at 24"),
        (2009, "Co-founded Andreessen Horowitz"),
    ],
    "Vinod Khosla": [
        (1982, "Co-founded Sun Microsystems"),
        (1986, "Sun IPO"),
        (2004, "Founded Khosla Ventures"),
    ],
    "Paul Graham": [
        (1998, "Sold Viaweb to Yahoo for $49M"),
        (2005, "Founded Y Combinator"),
    ],
    "Noam Chomsky": [
        (1957, "Published Syntactic Structures"),
        (1968, "The Responsibility of Intellectuals"),
    ],
    "Carl Sagan": [
        (1980, "Cosmos TV series airs — 500M viewers"),
        (1997, "Contact film released (wrote novel)"),
    ],
    "Richard Dawkins": [
        (1976, "Published The Selfish Gene"),
        (2006, "The God Delusion published"),
    ],
}

# ============================================================
# D1 COMPUTE (same as before)
# ============================================================
def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+NAK_SPAN: return n,l,(lon-s)/NAK_SPAN
    return "Revati","Mercury",0

def dg(p,s):
    if p in DEBIL and DEBIL[p]==s: return -100
    if p in EXALT and EXALT[p]==s: return 100
    if p in OWN and s in OWN[p]: return 75
    return 0

def compute_d1(name, birthday, birth_time, lat, lon, tz_offset):
    dt_local = datetime.strptime(f"{birthday}T{birth_time}", "%Y-%m-%dT%H:%M:%S")
    tz = timezone(timedelta(hours=tz_offset))
    dt_local = dt_local.replace(tzinfo=tz)
    dt_utc = dt_local.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                     dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    asc_trop, _ = swe.houses_ex(jd, lat, lon, b'A')
    ayan = swe.get_ayanamsa(jd)
    asc_sid = (asc_trop[0] - ayan) % 360
    asc_sign = SIGNS[int(asc_sid//30)]
    asc_idx = int(asc_sid//30)
    
    planets = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]; si = int(sid//30)
        nk, nl, _ = gn(sid)
        planets[pn] = {"sidereal": round(sid,4), "sign": sgn, "sign_idx": si,
                       "deg_in_sign": round(sid%30,4), "dignity": dg(pn,sgn),
                       "nakshatra": nk, "nakshatra_lord": nl}
    
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0] - ayan) % 360; kh = (rh + 180) % 360
    for pn, rl in [("Rahu", rh), ("Ketu", kh)]:
        sgn = SIGNS[int(rl//30)]; si = int(rl//30)
        nk, nl, _ = gn(rl)
        planets[pn] = {"sidereal": round(rl,4), "sign": sgn, "sign_idx": si,
                       "deg_in_sign": round(rl%30,4), "dignity": 0, "nakshatra": nk, "nakshatra_lord": nl}
    
    for pn in planets:
        planets[pn]["house"] = (planets[pn]["sign_idx"] - asc_idx) % 12 + 1
        planets[pn]["house_lord"] = SL[planets[pn]["sign"]]
    
    ms = planets["Moon"]["sidereal"]
    ml = mn = "?"; bal = 0
    for n, s, l in NAKS:
        if s <= ms < s + NAK_SPAN:
            elapsed = (ms - s) / NAK_SPAN
            bal = VIM_YRS[l] * (1.0 - elapsed)
            ml = l; mn = n; break
    
    return {
        "name": name, "ascendant": {"sign": asc_sign, "deg": round(asc_sid%30,4), "sidereal": round(asc_sid,4)},
        "planets": planets, "moon_nakshatra": {"name": mn, "lord": ml, "balance_yrs": round(bal,2)},
        "jd_ut": jd, "ayanamsa": ayan
    }


# ============================================================
# VARGA COMPUTATION (D2, D9, D10, D24, D60)
# ============================================================
def compute_varga(d1_chart, varga_name, division):
    """Compute varga divisional chart. division=2 for D2, 9 for D9 etc."""
    planets = d1_chart['planets']
    asc_sid = d1_chart['ascendant']['sidereal']
    
    varga_signs = {}
    for pn in planets:
        sid = planets[pn]['sidereal']
        # Standard varga computation: varga_longitude = (sidereal_longitude * division) % 360
        varga_lon = (sid * division) % 360
        varga_sign = SIGNS[int(varga_lon // 30)]
        varga_signs[pn] = varga_sign
    
    # Lagna in varga
    varga_lagna_lon = (asc_sid * division) % 360
    varga_lagna = SIGNS[int(varga_lagna_lon // 30)]
    varga_lagna_idx = SIGNS.index(varga_lagna)
    
    # Houses in varga
    varga_planets = {}
    for pn in planets:
        si = SIGNS.index(varga_signs[pn])
        house = (si - varga_lagna_idx) % 12 + 1
        varga_planets[pn] = {"sign": varga_signs[pn], "house": house}
    
    return {"varga": varga_name, "lagna": varga_lagna, "planets": varga_planets}


def analyze_varga(varga_chart, d1_chart, varga_name):
    """Extract key signals from a varga chart"""
    p = varga_chart['planets']
    lagna = varga_chart['lagna']
    lagna_idx = SIGNS.index(lagna)
    d1p = d1_chart['planets']
    
    signals = []
    
    if varga_name == 'D2':
        # Hora = Wealth. Check 2L, 11L, Jupiter, Venus
        h2l = SL[SIGNS[(lagna_idx+1)%12]]
        h11l = SL[SIGNS[(lagna_idx+10)%12]]
        for lord in [h2l, h11l]:
            if lord in p:
                if p[lord]['house'] in [1,2,5,9,11]:
                    signals.append(f"D2:{lord}(wealth lord) in H{p[lord]['house']} {p[lord]['sign']}")
        for b in ['Jupiter','Venus']:
            if b in p and p[b]['house'] in [1,2,5,9,11]:
                signals.append(f"D2:{b} in wealth house H{p[b]['house']}")
        # Compare D1 2L/11L with D2 position
        d1_asc = d1p['Sun']['sign_idx']  # approximate
                
    elif varga_name == 'D9':
        # Navamsa = Dharma, inner self, marriage, fortune in 2nd half of life
        h1l = SL[lagna]
        h5l = SL[SIGNS[(lagna_idx+4)%12]]
        h9l = SL[SIGNS[(lagna_idx+8)%12]]
        # Planets in own/exalt in D9 = strong dharma
        for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pl in p:
                s = p[pl]['sign']
                if pl in EXALT and EXALT[pl] == s:
                    signals.append(f"D9:{pl} EXALTED in {s}")
                elif pl in OWN and s in OWN[pl]:
                    signals.append(f"D9:{pl} OWN in {s}")
                elif pl in DEBIL and DEBIL[pl] == s:
                    signals.append(f"D9:⛔ {pl} DEBIL in {s}")
        # Vargottama: same sign in D1 and D9
        for pl in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pl in p and pl in d1_chart['planets']:
                if p[pl]['sign'] == d1_chart['planets'][pl]['sign']:
                    signals.append(f"D9:VARGOTTAMA {pl} in {p[pl]['sign']}")
        # 5H and 9H lords in D9
        for lname, lord in [("5L",h5l),("9L",h9l)]:
            if lord in p and p[lord]['house'] in [1,5,9]:
                signals.append(f"D9:{lname}({lord}) strong in H{p[lord]['house']}")
    
    elif varga_name == 'D10':
        # Dasamsa = Career, profession, public life
        h10l = SL[SIGNS[(lagna_idx+9)%12]]
        h7l = SL[SIGNS[(lagna_idx+6)%12]]
        h1l = SL[lagna]
        # 10L status
        if h10l in p:
            s = p[h10l]['sign']
            h = p[h10l]['house']
            if h in [1,4,7,10]:
                signals.append(f"D10:10L({h10l}) in kendra H{h} {s}")
            elif h in [6,8,12]:
                signals.append(f"D10:⛔ 10L({h10l}) in dusthana H{h}")
        # Planets in 10H
        for pl in p:
            if p[pl]['house'] == 10:
                signals.append(f"D10:{pl} in 10H ({p[pl]['sign']}) — prominence")
        # Compare D1 10L in D10
        d1_asc_sign = d1_chart['ascendant']['sign']
        d1_10l = SL[SIGNS[(SIGNS.index(d1_asc_sign)+9)%12]]
        if d1_10l in p:
            signals.append(f"D10:D1-10L({d1_10l}) in D10 H{p[d1_10l]['house']} {p[d1_10l]['sign']}")
    
    elif varga_name == 'D24':
        # Chaturvimsamsa = Education, learning, knowledge
        h5l = SL[SIGNS[(lagna_idx+4)%12]]
        h9l = SL[SIGNS[(lagna_idx+8)%12]]
        for lord, lname in [(h5l,'5L'),(h9l,'9L')]:
            if lord in p:
                h = p[lord]['house']
                if h in [1,5,9]:
                    signals.append(f"D24:{lname}({lord}) strong in H{h}")
                elif h in [6,8,12]:
                    signals.append(f"D24:⛔ {lname}({lord}) dusthana H{h}")
        # Mercury/Jupiter in D24
        for pl in ['Mercury','Jupiter']:
            if pl in p:
                h = p[pl]['house']
                s = p[pl]['sign']
                if h in [1,5,9] and s in OWN.get(pl,[]) + [EXALT.get(pl,'')]:
                    signals.append(f"D24:{pl} DIGNIFIED in H{h} {s}")
    
    elif varga_name == 'D60':
        # Shashtyamsa = Past life karma, ultimate destiny
        h1l = SL[lagna]
        h9l = SL[SIGNS[(lagna_idx+8)%12]]
        if h1l in p:
            signals.append(f"D60:LL({h1l}) in H{p[h1l]['house']} {p[h1l]['sign']}")
        if h9l in p:
            signals.append(f"D60:9L({h9l}) in H{p[h9l]['house']} {p[h9l]['sign']}")
        # Benefics/malefics in D60 lagna or 9H
        for pl in ['Jupiter','Venus','Sun','Mars','Saturn']:
            if pl in p and p[pl]['house'] in [1,9]:
                quality = "DIGNIFIED" if pl in OWN and p[pl]['sign'] in OWN[pl] else ""
                signals.append(f"D60:{pl} in H{p[pl]['house']} {p[pl]['sign']} {quality}")
        # Compare D1 lagna lord in D60
        d1_ll = SL[d1_chart['ascendant']['sign']]
        if d1_ll in p:
            signals.append(f"D60:D1-LL({d1_ll}) in D60 H{p[d1_ll]['house']} {p[d1_ll]['sign']}")
    
    return signals


# ============================================================
# VIMSHOTTARI DASHA COMPUTATION
# ============================================================
def compute_dasha_timeline(moon_nakshatra, birth_date, birth_time, tz_offset):
    """
    Compute full Vimshottari Mahadasha timeline with Antardasha.
    Returns list of (start_date, end_date, md_lord, ad_lord, md_yrs_total).
    """
    ml = moon_nakshatra['lord']
    balance = moon_nakshatra['balance_yrs']
    
    birth_dt = datetime.strptime(f"{birth_date}T{birth_time}", "%Y-%m-%dT%H:%M:%S")
    tz = timezone(timedelta(hours=tz_offset))
    birth_dt = birth_dt.replace(tzinfo=tz)
    
    # Find starting MD
    ml_idx = VIM_ORDER.index(ml)
    
    # Build full 120-year cycle starting from birth
    periods = []
    current_dt = birth_dt
    
    # First MD (partial)
    first_md = ml
    first_total = VIM_YRS[ml]
    first_remaining = balance
    
    # For the first MD, generate ADs for the remaining balance
    ad_list = []
    ad_start = 0  # elapsed fraction within this MD
    for ad_i in range(9):
        ad_lord = VIM_ORDER[(ml_idx + ad_i) % 9]
        ad_dur = VIM_YRS[ad_lord] / 120 * first_total
        if ad_start + ad_dur > (first_total - first_remaining):
            # This AD crosses into post-balance period
            overlap = (first_total - first_remaining) - ad_start
            if overlap > 0.001:
                ad_list.append((ad_lord, overlap))
            break
        if ad_start >= (first_total - first_remaining):
            break
        ad_list.append((ad_lord, ad_dur))
        ad_start += ad_dur
    
    # Remaining MDs (full)
    for md_i in range(1, 10):  # up to 10 MDs covers ~100+ years
        md_lord = VIM_ORDER[(ml_idx + md_i) % 9]
        md_total = VIM_YRS[md_lord]
        
        for ad_i in range(9):
            ad_lord = VIM_ORDER[(VIM_ORDER.index(md_lord) + ad_i) % 9]
            ad_dur = VIM_YRS[ad_lord] / 120 * md_total
            ad_list.append((md_lord, ad_lord, ad_dur))
    
    return ad_list


def get_dasha_at_date(d1_chart, event_year):
    """Get the MD/AD lords for a given calendar year (approximate)"""
    birth_dt_str = None
    for c in CHARTS_RAW:
        if c['name'] == d1_chart['name']:
            birth_dt_str = c['birthday']
            birth_time = c['birth_time']
            tz = TZ_MAP[c['name']]
            break
    
    if not birth_dt_str:
        return "?", "?"
    
    birth_dt = datetime.strptime(f"{birth_dt_str}T{birth_time}", "%Y-%m-%dT%H:%M:%S")
    birth_dt = birth_dt.replace(tzinfo=timezone(timedelta(hours=tz)))
    
    ml = d1_chart['moon_nakshatra']['lord']
    balance = d1_chart['moon_nakshatra']['balance_yrs']
    ml_idx = VIM_ORDER.index(ml)
    
    # Walk forward from birth through dasa periods
    event_dt = datetime(event_year, 6, 15, tzinfo=timezone(timedelta(hours=0)))  # mid-year approx
    years_from_birth = (event_dt - birth_dt).total_seconds() / (365.25 * 86400)
    
    elapsed = 0
    current_md = ml
    current_md_idx = ml_idx
    remaining = balance
    
    while elapsed + remaining <= years_from_birth:
        elapsed += remaining
        current_md_idx = (current_md_idx + 1) % 9
        current_md = VIM_ORDER[current_md_idx]
        remaining = VIM_YRS[current_md]
    
    # Now within this MD, find AD
    md_elapsed = years_from_birth - elapsed
    ad_idx = VIM_ORDER.index(current_md)
    ad_elapsed = 0
    current_ad = current_md
    
    for ad_i in range(9):
        ad_lord = VIM_ORDER[(ad_idx + ad_i) % 9]
        ad_dur = VIM_YRS[ad_lord] / 120 * VIM_YRS[current_md]
        if ad_elapsed + ad_dur > md_elapsed:
            current_ad = ad_lord
            break
        ad_elapsed += ad_dur
    
    return current_md, current_ad


# ============================================================
# MAIN
# ============================================================
print("="*130)
print("COMPREHENSIVE VARGA + DASHA CROSS-REFERENCE")
print("10 Charts: VCs vs Academics vs Fraudsters")
print("D1 + D2 + D9 + D10 + D24 + D60 + Vimshottari Timeline")
print("="*130)

# --- COMPUTE ALL D1 CHARTS ---
all_results = []
for c in CHARTS_RAW:
    print(f"Computing {c['name']}...")
    d1 = compute_d1(c['name'], c['birthday'], c['birth_time'], c['coords'][0], c['coords'][1], TZ_MAP[c['name']])
    d1['category'] = c['category']
    
    # Compute vargas
    vargas = {}
    varga_signals = {}
    for vname, vdiv in [('D2',2), ('D9',9), ('D10',10), ('D24',24), ('D60',60)]:
        v = compute_varga(d1, vname, vdiv)
        vargas[vname] = v
        varga_signals[vname] = analyze_varga(v, d1, vname)
    
    d1['vargas'] = vargas
    d1['varga_signals'] = varga_signals
    
    # Compute dasha for life events
    event_dashas = {}
    for year, desc in LIFE_EVENTS.get(c['name'], []):
        md, ad = get_dasha_at_date(d1, year)
        event_dashas[str(year)] = {'year': year, 'event': desc, 'md': md, 'ad': ad}
    d1['event_dashas'] = event_dashas
    
    all_results.append(d1)

# ============================================================
# ANALYSIS BY GROUP
# ============================================================
print(f"\n{'='*130}")
print("PART 1: D1 (RASI) COMPARISON")
print(f"{'='*130}")

for c in all_results:
    asc = c['ascendant']['sign']
    moon = c['planets']['Moon']
    print(f"\n{c['name']} ({c['category']})")
    print(f"  Lagna: {asc} {c['ascendant']['deg']:.1f}° | Moon: {moon['sign']} {moon['nakshatra']} ({moon['nakshatra_lord']})")
    
    # Key D1 dignities
    d1_d = []
    for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        pl = c['planets'][pn]
        tag = ""
        if pl['dignity'] == 100: tag = "EXALT"
        elif pl['dignity'] == 75: tag = "OWN"
        elif pl['dignity'] == -100: tag = "DEB"
        if tag:
            d1_d.append(f"{pn}:{tag}({pl['sign']} H{pl['house']})")
    print(f"  D1 dignities: {', '.join(d1_d) if d1_d else 'none strong'}")
    
    # Node axis
    ra = c['planets']['Rahu']
    ke = c['planets']['Ketu']
    print(f"  Rahu: H{ra['house']} {ra['sign']} | Ketu: H{ke['house']} {ke['sign']}")

# ============================================================
# PART 2: VARGA CROSS-COMPARISON
# ============================================================
print(f"\n{'='*130}")
print("PART 2: VARGA CROSS-COMPARISON (D2, D9, D10, D24, D60)")
print(f"{'='*130}")

# Compare fraud vs non-fraud patterns
fraud_names = [c['name'] for c in all_results if 'Fraud' in c['category']]
vc_names = [c['name'] for c in all_results if 'Venture Capitalist' in c['category'] and 'Academic' not in c['category']]
acad_names = [c['name'] for c in all_results if 'Academic' in c['category'] and 'Venture' not in c['category']]

for vname in ['D2','D9','D10','D24','D60']:
    print(f"\n--- {vname} ---")
    
    # Fraud group
    print(f"\n  💀 FRAUD GROUP:")
    for c in all_results:
        if c['name'] not in fraud_names: continue
        v = c['vargas'][vname]
        sig = c['varga_signals'][vname]
        lagna_lord = SL[v['lagna']]
        print(f"  {c['name']:<22} | Lagna: {v['lagna']:<10} LL:{lagna_lord:<8} | {'; '.join(sig) if sig else 'no key signals'}")
    
    # VC group
    print(f"\n  💰 VC GROUP:")
    for c in all_results:
        if c['name'] not in vc_names: continue
        v = c['vargas'][vname]
        sig = c['varga_signals'][vname]
        print(f"  {c['name']:<22} | Lagna: {v['lagna']:<10} | {'; '.join(sig) if sig else 'no key signals'}")
    
    # Academic group
    print(f"\n  📚 ACADEMIC GROUP:")
    for c in all_results:
        if c['name'] not in acad_names: continue
        v = c['vargas'][vname]
        sig = c['varga_signals'][vname]
        print(f"  {c['name']:<22} | Lagna: {v['lagna']:<10} | {'; '.join(sig) if sig else 'no key signals'}")

# ============================================================
# PART 3: DASHA CROSS-REFERENCE WITH LIFE EVENTS
# ============================================================
print(f"\n{'='*130}")
print("PART 3: DASHA CROSS-REFERENCE — Life Events vs Vimshottari Periods")
print(f"{'='*130}")

for c in all_results:
    events = c.get('event_dashas', {})
    if not events: continue
    print(f"\n--- {c['name']} ({c['category']}) ---")
    print(f"  Moon Nakshatra: {c['moon_nakshatra']['name']} ({c['moon_nakshatra']['lord']}), Balance: {c['moon_nakshatra']['balance_yrs']}y")
    for yr_key in sorted(events.keys()):
        ev = events[yr_key]
        # Add context: is this rahu or ketu period?
        tag = ""
        if ev['md'] in ['Rahu','Ketu']: tag = " 🔮"
        if ev['md'] == 'Rahu': tag = " 🌪️ RAHU MD"
        if ev['md'] == 'Ketu': tag = " 🔥 KETU MD"
        print(f"  {ev['year']}: {ev['event']}")
        print(f"         Dasha: {ev['md']} MD / {ev['ad']} AD{tag}")

# ============================================================
# PART 4: PATTERN DISCOVERY — What separates the groups?
# ============================================================
print(f"\n{'='*130}")
print("PART 4: PATTERN DISCOVERY — Group Discriminators")
print(f"{'='*130}")

# D9 analysis: fraudsters tend to have afflicted D9
print("\n--- D9 (Dharma) Patterns ---")
for c in all_results:
    d9 = c['vargas']['D9']
    sig = c['varga_signals']['D9']
    deb_planets = [s for s in sig if 'DEBIL' in s]
    vargottama = [s for s in sig if 'VARGOTTAMA' in s]
    exalted = [s for s in sig if 'EXALTED' in s]
    grp = "💀" if 'Fraud' in c['category'] else ("💰" if 'VC' in c['category'] and 'Academic' not in c['category'] else "📚")
    print(f"  {grp} {c['name']:<22} | {len(vargottama)} vargottama | {len(exalted)} exalted | {len(deb_planets)} debil")

# D10 analysis: career prominence
print("\n--- D10 (Career) Patterns ---")
for c in all_results:
    d10 = c['vargas']['D10']
    sig = c['varga_signals']['D10']
    in_10h = [s for s in sig if '10H' in s and 'prominence' in s]
    dusthana = [s for s in sig if '⛔' in s]
    grp = "💀" if 'Fraud' in c['category'] else ("💰" if 'VC' in c['category'] and 'Academic' not in c['category'] else "📚")
    print(f"  {grp} {c['name']:<22} | D10 Lagna: {d10['lagna']:<8} | 10H planets: {len(in_10h)} | Dusthana: {len(dusthana)}")

# D60 analysis: karmic patterns
print("\n--- D60 (Karma) Patterns ---")
for c in all_results:
    d60 = c['vargas']['D60']
    sig = c['varga_signals']['D60']
    grp = "💀" if 'Fraud' in c['category'] else ("💰" if 'VC' in c['category'] and 'Academic' not in c['category'] else "📚")
    d1_ll_sig = [s for s in sig if 'D1-LL' in s]
    print(f"  {grp} {c['name']:<22} | D60 Lagna: {d60['lagna']:<10} | {d1_ll_sig[0] if d1_ll_sig else 'no D1-LL signal'}")

# ============================================================
# PART 5: OPPORTUNITY WINDOW ANALYSIS
# ============================================================
print(f"\n{'='*130}")
print("PART 5: OPPORTUNITY WINDOWS — Dasha Periods at Key Life Events")
print(f"{'='*130}")

# Collect all peak-success events and their dasha periods
peak_events = []
for c in all_results:
    for yr_key, ev in sorted(c.get('event_dashas', {}).items()):
        if any(word in ev['event'].lower() for word in ['founded','ipo','sold','valued','published','worth','investor']):
            peak_events.append({
                'name': c['name'],
                'category': c['category'],
                'year': ev['year'],
                'event': ev['event'],
                'md': ev['md'],
                'ad': ev['ad'],
            })

# Also collect collapse events
collapse_events = []
for c in all_results:
    for yr_key, ev in sorted(c.get('event_dashas', {}).items()):
        if any(word in ev['event'].lower() for word in ['arrested','collapse','fraud','convicted','sentenced','charged']):
            collapse_events.append({
                'name': c['name'],
                'category': c['category'],
                'year': ev['year'],
                'event': ev['event'],
                'md': ev['md'],
                'ad': ev['ad'],
            })

print("\nPEAK SUCCESS EVENTS:")
from collections import Counter
md_counter = Counter(e['md'] for e in peak_events)
ad_counter = Counter(e['ad'] for e in peak_events)
print(f"  MD distribution: {dict(md_counter)}")
print(f"  AD distribution: {dict(ad_counter)}")

for e in peak_events:
    grp = "💀" if 'Fraud' in e['category'] else "💰📚"
    print(f"  {grp} {e['name']} | {e['year']} | {e['md']}/{e['ad']} | {e['event'][:60]}")

print("\nCOLLAPSE/FRAUD EVENTS:")
for e in collapse_events:
    print(f"  💀 {e['name']} | {e['year']} | {e['md']}/{e['ad']} | {e['event'][:60]}")

# --- SAVE ---
with open('/home/user/dataset/varga_dasha_10.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nSaved → /home/user/dataset/varga_dasha_10.json")
