#!/usr/bin/env python3
"""
100 BILLIONAIRE STATISTICAL ANALYSIS
No birth times available — analyze what we CAN:
- Planetary sign distributions vs expected
- Nakshatra clusters
- Dignity patterns (exalted/own/debilitated rates)
- Planet-to-planet conjunctions
- Rahu-Ketu axis patterns
- Sun-Moon relationships
- Compare vs ~100 random baseline births
"""
import swisseph as swe
import json, math, random
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],
       "Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),
        ("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),
        ("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),
        ("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),
        ("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),
        ("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),
        ("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]

# City coordinates for known birthplaces
CITY_COORDS = {
    "Pretoria, South Africa": (-25.7479, 28.2293),
    "Albuquerque, New Mexico, USA": (35.0853, -106.6056),
    "Seattle, Washington, USA": (47.6062, -122.3321),
    "White Plains, New York, USA": (41.034, -73.7629),
    "Omaha, Nebraska, USA": (41.2565, -95.9345),
    "Roubaix, France": (50.6927, 3.1778),
    "San Francisco, California, USA": (37.7749, -122.4194),
    "Bronx, New York, USA": (40.8448, -73.8648),
    "East Lansing, Michigan, USA": (42.737, -84.4839),
    "Moscow, Russia": (55.7558, 37.6173),
    "Detroit, Michigan, USA": (42.3314, -83.0458),
    "Boston, Massachusetts, USA": (42.3601, -71.0589),
    "Mexico City, Mexico": (19.4326, -99.1332),
    "Busdongo de Arbas, Spain": (42.9833, -5.7),
    "Aden, Yemen": (12.7855, 45.0187),
    "Ahmedabad, India": (23.0225, 72.5714),
    "Tainan, Taiwan": (22.9997, 120.2270),
    "Houston, Texas, USA": (29.7604, -95.3698),
    "Portland, Oregon, USA": (45.5152, -122.6784),
    "Welkom, South Africa": (-27.9833, 26.7333),
    "Blackheath, London, UK": (51.4647, 0.0071),
    "Hangzhou, Zhejiang, China": (30.2741, 120.1551),
    "Chaoyang, Shantou, Guangdong, China": (23.35, 116.68),
    "Tosu, Saga Prefecture, Japan": (33.3833, 130.5),
    "Ube, Yamaguchi, Japan": (33.95, 131.25),
    "Heilbronn, Germany": (49.1427, 9.2109),
    "Hamburg, Germany": (53.5511, 9.9937),
    "Bad Homburg, Germany": (50.2268, 8.6181),
    "Acquigny, France": (49.1667, 1.1667),
    "Paris, France": (48.8566, 2.3522),
    "Farigliano, Italy": (44.5167, 7.9167),
    "Milan, Italy": (45.4642, 9.1900),
    "Piacenza, Italy": (45.05, 9.7),
    "Failsworth, Lancashire, UK": (53.5167, -2.15),
    "Chicago, Illinois, USA": (41.8781, -87.6298),
    "Queens, New York, USA": (40.7282, -73.7949),
    "Daytona Beach, Florida, USA": (29.2108, -81.0228),
    "Philadelphia, Pennsylvania, USA": (39.9526, -75.1652),
    "Baltimore, Maryland, USA": (39.2904, -76.6122),
    "New York City, New York, USA": (40.7128, -74.0060),
    "Budapest, Hungary": (47.4979, 19.0402),
    "Frankfurt, Germany": (50.1109, 8.6821),
    "Cedar Falls, Iowa, USA": (42.5275, -92.4455),
    "London, UK": (51.5074, -0.1278),
    "Pune, India": (18.5204, 73.8567),
    "St. Louis, Missouri, USA": (38.6270, -90.1994),
    "Stanford, California, USA": (37.4241, -122.1661),
    "Los Angeles, California, USA": (34.0522, -118.2437),
    "Calgary, Alberta, Canada": (51.0447, -114.0719),
    "Niskayuna, New York, USA": (42.800, -73.883),
    "Atlanta, Georgia, USA": (33.7490, -84.3880),
    "Berkeley, California, USA": (37.8715, -122.2730),
    "Gainesville, Florida, USA": (29.6516, -82.3248),
    "Sao Paulo, Brazil": (-23.5505, -46.6333),
    "Kiev, Ukraine": (50.4501, 30.5234),
    "Michigan, USA": (42.5, -84.5),
    "Long Beach, California, USA": (33.7701, -118.1937),
    "Dromineer, County Tipperary, Ireland": (52.9167, -8.2667),
    "Salt Lake City, Utah, USA": (40.7608, -111.8910),
    "Perth, Australia": (-31.9505, 115.8605),
    "Jiangsu, China": (32.0617, 118.7917),
    "Kolomna, Russia": (55.0833, 38.7833),
    "Unknown": (0, 0),
    "Hyderabad, India": (17.3850, 78.4867),
    "Madurai, India": (9.9252, 78.1198),
    "Mobile, Alabama, USA": (30.6954, -88.0399),
    "Scarsdale, New York, USA": (40.9926, -73.7873),
    "Tehran, Iran": (35.6892, 51.3890),
    "West Godavari, Andhra Pradesh, India": (16.8, 81.5),
    "Mughal, Israel": (32.0, 34.9),  # approximate
    "Cold Spring Harbor, New York, USA": (40.87, -73.45),
    "Washington, D.C., USA": (38.9072, -77.0369),
    "Wausau, Wisconsin, USA": (44.9591, -89.6301),
    "Santa Clara, California, USA": (37.3541, -121.9552),
    "Ludhiana, India": (30.9010, 75.8573),
    "Aligarh, India": (27.8974, 78.0881),
    "New Delhi, India": (28.6139, 77.2090),
    "Patiala, India": (30.3398, 76.3869),
    "Muktsar, Punjab, India": (30.4833, 74.5167),
    "Chandigarh, India": (30.7333, 76.7794),
    "Azhikode, Kerala, India": (11.9, 75.35),
    "Bisam Cuttack, Odisha, India": (20.0, 84.0),
    "Mumbai, India": (19.0760, 72.8777),
    "Bikaner, Rajasthan, India": (28.0229, 73.3119),
    "Kolkata, India": (22.5726, 88.3639),
}

# Timezone approximations
def get_tz(place):
    if 'India' in place or 'Delhi' in place or 'Mumbai' in place or 'Kolkata' in place or 'Pune' in place or 'Hyderabad' in place or 'Madurai' in place or 'Chandigarh' in place or 'Ludhiana' in place or 'Aligarh' in place or 'Patiala' in place or 'Muktsar' in place or 'Azhikode' in place or 'Bisam' in place or 'Bikaner' in place or 'West Godavari' in place:
        return 5.5
    if 'China' in place or 'Taiwan' in place:
        return 8
    if 'Japan' in place:
        return 9
    if 'UK' in place or 'London' in place or 'Ireland' in place:
        return 0
    if 'Germany' in place or 'France' in place or 'Italy' in place or 'Spain' in place or 'Hungary' in place or 'Paris' in place:
        return 1
    if 'Russia' in place or 'Moscow' in place or 'Kolomna' in place or 'Kiev' in place or 'Ukraine' in place:
        return 3
    if 'Brazil' in place:
        return -3
    if 'South Africa' in place or 'Pretoria' in place or 'Welkom' in place:
        return 2
    if 'Mexico' in place:
        return -6
    if 'Yemen' in place:
        return 3
    if 'Iran' in place:
        return 3.5
    if 'Israel' in place:
        return 2
    if 'Canada' in place or 'Calgary' in place:
        return -7
    if 'Australia' in place or 'Perth' in place:
        return 8
    return -5  # Default USA

# Parse the user's JSON
BILLIONAIRES_JSON = """PASTE_HERE"""

# Instead, hardcode key ones with known birth dates & places
# Full list from user input
BILLIONAIRES = [
    {"name":"Elon Musk","birthday":"1971-06-28","place":"Pretoria, South Africa"},
    {"name":"Jeff Bezos","birthday":"1964-01-12","place":"Albuquerque, New Mexico, USA"},
    {"name":"Bill Gates","birthday":"1955-10-28","place":"Seattle, Washington, USA"},
    {"name":"Mark Zuckerberg","birthday":"1984-05-14","place":"White Plains, New York, USA"},
    {"name":"Warren Buffett","birthday":"1930-08-30","place":"Omaha, Nebraska, USA"},
    {"name":"Bernard Arnault","birthday":"1949-03-05","place":"Roubaix, France"},
    {"name":"Steve Jobs","birthday":"1955-02-24","place":"San Francisco, California, USA"},
    {"name":"Larry Ellison","birthday":"1944-08-17","place":"Bronx, New York, USA"},
    {"name":"Larry Page","birthday":"1973-03-26","place":"East Lansing, Michigan, USA"},
    {"name":"Sergey Brin","birthday":"1973-08-21","place":"Moscow, Russia"},
    {"name":"Steve Ballmer","birthday":"1956-03-24","place":"Detroit, Michigan, USA"},
    {"name":"Michael Bloomberg","birthday":"1942-02-14","place":"Boston, Massachusetts, USA"},
    {"name":"Carlos Slim Helu","birthday":"1940-01-28","place":"Mexico City, Mexico"},
    {"name":"Amancio Ortega","birthday":"1936-03-28","place":"Busdongo de Arbas, Spain"},
    {"name":"Mukesh Ambani","birthday":"1957-04-19","place":"Aden, Yemen"},
    {"name":"Gautam Adani","birthday":"1962-06-24","place":"Ahmedabad, India"},
    {"name":"Jensen Huang","birthday":"1963-02-17","place":"Tainan, Taiwan"},
    {"name":"Michael Dell","birthday":"1965-02-23","place":"Houston, Texas, USA"},
    {"name":"Phil Knight","birthday":"1938-02-24","place":"Portland, Oregon, USA"},
    {"name":"Mark Shuttleworth","birthday":"1973-09-18","place":"Welkom, South Africa"},
    {"name":"Richard Branson","birthday":"1950-07-18","place":"Blackheath, London, UK"},
    {"name":"Jack Ma","birthday":"1964-09-10","place":"Hangzhou, Zhejiang, China"},
    {"name":"Pony Ma","birthday":"1971-10-29","place":"Chaoyang, Shantou, Guangdong, China"},
    {"name":"Masayoshi Son","birthday":"1957-08-11","place":"Tosu, Saga Prefecture, Japan"},
    {"name":"Tadashi Yanai","birthday":"1949-02-07","place":"Ube, Yamaguchi, Japan"},
    {"name":"Dieter Schwarz","birthday":"1939-09-24","place":"Heilbronn, Germany"},
    {"name":"Klaus-Michael Kuehne","birthday":"1937-06-02","place":"Hamburg, Germany"},
    {"name":"Stefan Quandt","birthday":"1966-05-09","place":"Bad Homburg, Germany"},
    {"name":"Susanne Klatten","birthday":"1962-04-28","place":"Bad Homburg, Germany"},
    {"name":"Francois Pinault","birthday":"1936-08-21","place":"Acquigny, France"},
    {"name":"Alain Wertheimer","birthday":"1948-09-28","place":"Paris, France"},
    {"name":"Gerard Wertheimer","birthday":"1950-04-26","place":"Paris, France"},
    {"name":"Giovanni Ferrero","birthday":"1964-09-21","place":"Farigliano, Italy"},
    {"name":"Giorgio Armani","birthday":"1934-07-11","place":"Piacenza, Italy"},
    {"name":"Silvio Berlusconi","birthday":"1936-09-29","place":"Milan, Italy"},
    {"name":"James Ratcliffe","birthday":"1952-10-18","place":"Failsworth, Lancashire, UK"},
    {"name":"Ray Dalio","birthday":"1949-08-08","place":"Queens, New York, USA"},
    {"name":"Ken Griffin","birthday":"1968-10-15","place":"Daytona Beach, Florida, USA"},
    {"name":"Stephen Schwarzman","birthday":"1947-02-14","place":"Philadelphia, Pennsylvania, USA"},
    {"name":"David Rubenstein","birthday":"1949-08-11","place":"Baltimore, Maryland, USA"},
    {"name":"Leon Black","birthday":"1951-07-31","place":"New York City, New York, USA"},
    {"name":"Carl Icahn","birthday":"1936-02-16","place":"Queens, New York, USA"},
    {"name":"George Soros","birthday":"1930-08-12","place":"Budapest, Hungary"},
    {"name":"Peter Thiel","birthday":"1967-10-11","place":"Frankfurt, Germany"},
    {"name":"Marc Andreessen","birthday":"1971-07-09","place":"Cedar Falls, Iowa, USA"},
    {"name":"Ben Horowitz","birthday":"1966-06-13","place":"London, UK"},
    {"name":"Vinod Khosla","birthday":"1955-01-28","place":"Pune, India"},
    {"name":"John Doerr","birthday":"1951-06-29","place":"St. Louis, Missouri, USA"},
    {"name":"Reid Hoffman","birthday":"1967-08-05","place":"Stanford, California, USA"},
    {"name":"Travis Kalanick","birthday":"1976-08-06","place":"Los Angeles, California, USA"},
    {"name":"Garrett Camp","birthday":"1978-10-04","place":"Calgary, Alberta, Canada"},
    {"name":"Brian Chesky","birthday":"1981-08-29","place":"Niskayuna, New York, USA"},
    {"name":"Joe Gebbia","birthday":"1981-08-21","place":"Atlanta, Georgia, USA"},
    {"name":"Nathan Blecharczyk","birthday":"1983-08-26","place":"Boston, Massachusetts, USA"},
    {"name":"Evan Spiegel","birthday":"1990-06-04","place":"Los Angeles, California, USA"},
    {"name":"Bobby Murphy","birthday":"1988-04-01","place":"Berkeley, California, USA"},
    {"name":"Dustin Moskovitz","birthday":"1984-05-22","place":"Gainesville, Florida, USA"},
    {"name":"Eduardo Saverin","birthday":"1982-03-19","place":"Sao Paulo, Brazil"},
    {"name":"Jan Koum","birthday":"1976-02-24","place":"Kiev, Ukraine"},
    {"name":"Brian Acton","birthday":"1972-02-17","place":"Michigan, USA"},
    {"name":"Palmer Luckey","birthday":"1992-09-19","place":"Long Beach, California, USA"},
    {"name":"John Collison","birthday":"1990-08-06","place":"Dromineer, County Tipperary, Ireland"},
    {"name":"Patrick Collison","birthday":"1988-09-09","place":"Dromineer, County Tipperary, Ireland"},
    {"name":"Whitney Wolfe Herd","birthday":"1989-07-01","place":"Salt Lake City, Utah, USA"},
    {"name":"Melanie Perkins","birthday":"1987-05-13","place":"Perth, Australia"},
    {"name":"Sam Bankman-Fried","birthday":"1992-03-06","place":"Stanford, California, USA"},
    {"name":"Changpeng Zhao","birthday":"1977-02-05","place":"Jiangsu, China"},
    {"name":"Vitalik Buterin","birthday":"1994-01-31","place":"Kolomna, Russia"},
    {"name":"Satoshi Nakamoto","birthday":"1975-04-05","place":"Unknown"},
    {"name":"Satya Nadella","birthday":"1967-08-19","place":"Hyderabad, India"},
    {"name":"Sundar Pichai","birthday":"1972-06-10","place":"Madurai, India"},
    {"name":"Tim Cook","birthday":"1960-11-01","place":"Mobile, Alabama, USA"},
    {"name":"Andy Jassy","birthday":"1968-01-13","place":"Scarsdale, New York, USA"},
    {"name":"Dara Khosrowshahi","birthday":"1969-05-28","place":"Tehran, Iran"},
    {"name":"Arvind Krishna","birthday":"1962-01-01","place":"West Godavari, Andhra Pradesh, India"},
    {"name":"Shantanu Narayen","birthday":"1963-05-27","place":"Hyderabad, India"},
    {"name":"Lisa Su","birthday":"1969-11-07","place":"Tainan, Taiwan"},
    {"name":"Safra Catz","birthday":"1961-12-01","place":"Mughal, Israel"},
    {"name":"Ginni Rometty","birthday":"1957-07-29","place":"Chicago, Illinois, USA"},
    {"name":"Meg Whitman","birthday":"1956-08-04","place":"Cold Spring Harbor, New York, USA"},
    {"name":"Sheryl Sandberg","birthday":"1969-08-28","place":"Washington, D.C., USA"},
    {"name":"Marissa Mayer","birthday":"1975-05-30","place":"Wausau, Wisconsin, USA"},
    {"name":"Susan Wojcicki","birthday":"1968-07-05","place":"Santa Clara, California, USA"},
    {"name":"Bhavish Aggarwal","birthday":"1985-08-28","place":"Ludhiana, India"},
    {"name":"Vijay Shekhar Sharma","birthday":"1978-07-08","place":"Aligarh, India"},
    {"name":"Kunal Bahl","birthday":"1983-11-04","place":"New Delhi, India"},
    {"name":"Rohit Bansal","birthday":"1983-05-09","place":"Patiala, India"},
    {"name":"Deepinder Goyal","birthday":"1983-01-26","place":"Muktsar, Punjab, India"},
    {"name":"Sriharsha Majety","birthday":"1986-07-16","place":"Hyderabad, India"},
    {"name":"Kalyan Krishnamurthy","birthday":"1972-01-01","place":"India"},
    {"name":"Sachin Bansal","birthday":"1981-08-05","place":"Chandigarh, India"},
    {"name":"Binny Bansal","birthday":"1983-12-30","place":"Chandigarh, India"},
    {"name":"Byju Raveendran","birthday":"1980-11-30","place":"Azhikode, Kerala, India"},
    {"name":"Ritesh Agarwal","birthday":"1993-11-16","place":"Bisam Cuttack, Odisha, India"},
    {"name":"Falguni Nayar","birthday":"1963-02-19","place":"Mumbai, India"},
    {"name":"Radhakishan Damani","birthday":"1954-03-24","place":"Bikaner, Rajasthan, India"},
    {"name":"Kumar Mangalam Birla","birthday":"1967-06-14","place":"Kolkata, India"},
    {"name":"Uday Kotak","birthday":"1959-03-15","place":"Mumbai, India"},
    {"name":"Azim Premji","birthday":"1945-07-24","place":"Mumbai, India"},
]

print(f"Loaded {len(BILLIONAIRES)} billionaires/tech leaders")
print("⚠️ NO BIRTH TIMES — computing noon charts. No lagna, houses, vargas, or dasha available.")
print("Analyzing: planet signs, nakshatras, dignities, conjunctions, Rahu-Ketu axis\n")

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l,(lon-s)/13.334
    return "Revati","Mercury",0

def compute_noon_chart(c):
    dt_str = f"{c['birthday']}T12:00:00"
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
    tz_ofs = get_tz(c['place'])
    dt = dt.replace(tzinfo=timezone(timedelta(hours=tz_ofs)))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                     dt_utc.hour + dt_utc.minute/60)
    ayan = swe.get_ayanamsa(jd)
    
    planets = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]
        nk, nl, _ = gn(sid)
        dignity = 0
        if pn in EXALT and EXALT[pn] == sgn: dignity = 100
        elif pn in OWN and sgn in OWN[pn]: dignity = 75
        elif pn in DEBIL and DEBIL[pn] == sgn: dignity = -100
        planets[pn] = {"sign": sgn, "nakshatra": nk, "nakshatra_lord": nl, "dignity": dignity,
                        "sidereal": round(sid,2)}
    
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0] - ayan) % 360
    for pn, rl in [("Rahu", rh), ("Ketu", (rh+180)%360)]:
        sgn = SIGNS[int(rl//30)]
        nk, nl, _ = gn(rl)
        planets[pn] = {"sign": sgn, "nakshatra": nk, "nakshatra_lord": nl, "dignity": 0}
    
    # Conjunctions (same sign)
    conjunctions = []
    plist = list(planets.keys())
    for i in range(len(plist)):
        for j in range(i+1, len(plist)):
            if planets[plist[i]]['sign'] == planets[plist[j]]['sign']:
                conjunctions.append(f"{plist[i]}+{plist[j]}")
    
    return planets, conjunctions

# Compute all
all_charts = []
for c in BILLIONAIRES:
    try:
        planets, conj = compute_noon_chart(c)
        all_charts.append({"name": c['name'], "planets": planets, "conjunctions": conj})
    except Exception as e:
        print(f"  ERROR {c['name']}: {e}")

print(f"Computed {len(all_charts)}/{len(BILLIONAIRES)} charts\n")

# ============================================================
# STATISTICAL ANALYSIS
# ============================================================

# 1. Planet sign distribution
print("="*100)
print("1. PLANET SIGN DISTRIBUTION (top 3 most common signs per planet)")
print("="*100)

for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu']:
    signs = [c['planets'][pn]['sign'] for c in all_charts if pn in c['planets']]
    counter = Counter(signs)
    total = len(signs)
    expected = total / 12  # Expected under uniform
    print(f"\n{pn} (n={total}):")
    for sign, count in counter.most_common(5):
        ratio = count / expected
        bar = "█" * int(ratio * 5)
        print(f"  {sign:<12} {count:>3} ({count/total*100:5.1f}%) | ratio={ratio:.2f}x {bar}")

# 2. Dignity rates
print(f"\n{'='*100}")
print("2. DIGNITY RATES — Exalted, Own, Debilitated")
print(f"{'='*100}")

dignity_counts = defaultdict(lambda: {"exalted":0,"own":0,"debil":0,"neutral":0})
total_planets = 0
for c in all_charts:
    for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        if pn in c['planets']:
            total_planets += 1
            d = c['planets'][pn]['dignity']
            if d == 100: dignity_counts[pn]["exalted"] += 1
            elif d == 75: dignity_counts[pn]["own"] += 1
            elif d == -100: dignity_counts[pn]["debil"] += 1
            else: dignity_counts[pn]["neutral"] += 1

# Expected rates: 1/12 exalted, ~2/12 own, 1/12 debilitated
print(f"{'Planet':<10} {'Exalted':>8} ({'exp':>4}) {'Own':>8} ({'exp':>4}) {'Debil':>8} ({'exp':>4}) {'Sample':>6}")
print("-"*70)
for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
    n = sum(dignity_counts[pn].values())
    exp_ex = n/12; exp_own = n*2/12; exp_deb = n/12
    ex = dignity_counts[pn]['exalted']
    ow = dignity_counts[pn]['own']
    db = dignity_counts[pn]['debil']
    print(f"{pn:<10} {ex:>8} ({exp_ex:>4.0f}) {ow:>8} ({exp_own:>4.0f}) {db:>8} ({exp_deb:>4.0f}) {n:>6}")

# Overall dignity rates
all_ex = sum(d['exalted'] for d in dignity_counts.values())
all_own = sum(d['own'] for d in dignity_counts.values())
all_deb = sum(d['debil'] for d in dignity_counts.values())
print(f"\n  OVERALL: Exalted={all_ex}/{total_planets} ({all_ex/total_planets*100:.1f}% vs 8.3% expected)")
print(f"           Own={all_own}/{total_planets} ({all_own/total_planets*100:.1f}% vs 16.7% expected)")
print(f"           Debilitated={all_deb}/{total_planets} ({all_deb/total_planets*100:.1f}% vs 8.3% expected)")

# 3. Nakshatra analysis
print(f"\n{'='*100}")
print("3. NAKSHATRA CLUSTERS — Moon Nakshatra Distribution")
print(f"{'='*100}")

moon_naks = [c['planets']['Moon']['nakshatra'] for c in all_charts if 'Moon' in c['planets']]
nak_counter = Counter(moon_naks)
print(f"\nMoon Nakshatras (n={len(moon_naks)}, expected ~{len(moon_naks)/27:.1f} per nakshatra):")
for nak, count in nak_counter.most_common(10):
    ratio = count / (len(moon_naks)/27)
    bar = "█" * min(int(ratio * 3), 30)
    print(f"  {nak:<20} {count:>3} ({count/len(moon_naks)*100:5.1f}%) | {ratio:.2f}x {bar}")

# Nakshatra lord distribution
nak_lords = [c['planets']['Moon']['nakshatra_lord'] for c in all_charts if 'Moon' in c['planets']]
nl_counter = Counter(nak_lords)
print(f"\nMoon Nakshatra LORDS:")
for lord, count in nl_counter.most_common():
    exp = len(nak_lords) * {'Ketu':2,'Venus':3,'Sun':3,'Moon':3,'Mars':3,'Rahu':2,'Jupiter':3,'Saturn':3,'Mercury':3}[lord]/27
    print(f"  {lord:<10} {count:>3} ({count/len(nak_lords)*100:5.1f}%) | expected ~{exp:.0f}")

# 4. Conjunction patterns
print(f"\n{'='*100}")
print("4. PLANETARY CONJUNCTIONS — Same-sign pairings")
print(f"{'='*100}")

all_conj = []
for c in all_charts:
    all_conj.extend(c['conjunctions'])
conj_counter = Counter(all_conj)
print(f"\nTop conjunctions (n={len(all_charts)} charts):")
for conj, count in conj_counter.most_common(15):
    print(f"  {conj:<20} {count:>3} charts ({count/len(all_charts)*100:5.1f}%)")

# 5. Rahu-Ketu specific
print(f"\n{'='*100}")
print("5. RAHU SIGN DISTRIBUTION")
print(f"{'='*100}")

rahu_signs = [c['planets']['Rahu']['sign'] for c in all_charts if 'Rahu' in c['planets']]
rs_counter = Counter(rahu_signs)
for sign, count in rs_counter.most_common():
    print(f"  Rahu in {sign:<12} {count:>3} ({count/len(rahu_signs)*100:5.1f}%)")

# 6. SUN-MOON relationship
print(f"\n{'='*100}")
print("6. SUN-MOON RELATIONSHIP (approximate, noon charts)")
print(f"{'='*100}")

sun_signs = [c['planets']['Sun']['sign'] for c in all_charts]
moon_signs = [c['planets']['Moon']['sign'] for c in all_charts]

# Sun-Moon same sign
same_sign = sum(1 for s,m in zip(sun_signs, moon_signs) if s == m)
print(f"  Sun-Moon same sign: {same_sign}/{len(all_charts)} ({same_sign/len(all_charts)*100:.1f}%)")

# Sun-Moon trine (5th/9th from each other)
trine_count = 0
for s,m in zip(sun_signs, moon_signs):
    si, mi = SIGNS.index(s), SIGNS.index(m)
    diff = (mi - si) % 12
    if diff in [4, 8]:  # 5th or 9th
        trine_count += 1
print(f"  Sun-Moon trine (5/9): {trine_count}/{len(all_charts)} ({trine_count/len(all_charts)*100:.1f}%)")

# 7. Top individual patterns
print(f"\n{'='*100}")
print("7. INDIVIDUAL NOTABLE CHARTS (most dignified planets)")
print(f"{'='*100}")

chart_scores = []
for c in all_charts:
    p = c['planets']
    ex_count = sum(1 for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] 
                   if pn in p and p[pn]['dignity'] == 100)
    own_count = sum(1 for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
                    if pn in p and p[pn]['dignity'] == 75)
    deb_count = sum(1 for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
                    if pn in p and p[pn]['dignity'] == -100)
    chart_scores.append((c['name'], ex_count, own_count, deb_count, c['conjunctions']))

chart_scores.sort(key=lambda x: -(x[1]*2 + x[2] - x[3]))

print(f"\n{'Name':<25} {'Exalted':>7} {'Own':>5} {'Debil':>5} {'Top Conjunctions'}")
print("-"*75)
for name, ex, ow, db, conj in chart_scores[:20]:
    print(f"{name:<25} {ex:>7} {ow:>5} {db:>5} {', '.join(conj[:3])}")

print(f"\n...and bottom 10 (most debilitated):")
for name, ex, ow, db, conj in chart_scores[-10:]:
    print(f"{name:<25} {ex:>7} {ow:>5} {db:>5} {', '.join(conj[:3])}")

# Save
out = {"charts": all_charts, "stats": {
    "total": len(all_charts),
    "moon_nakshatra_distribution": dict(nak_counter.most_common()),
    "rahu_sign_distribution": dict(rs_counter.most_common()),
    "top_conjunctions": dict(conj_counter.most_common(15)),
}}
with open('dataset/billionaire_noon_analysis.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved → dataset/billionaire_noon_analysis.json")
