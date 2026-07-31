#!/usr/bin/env python3
"""
BILLIONAIRE vs CRIMINAL/BANKRUPT — Head-to-Head Planetary Comparison
No birth times — noon charts. Planet-sign, nakshatras, dignities, conjunctions.
"""
import swisseph as swe
import json, math
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
    "India": (20.5937, 78.9629),
    "Hyderabad, India": (17.3850, 78.4867),
    "Madurai, India": (9.9252, 78.1198),
    "Mobile, Alabama, USA": (30.6954, -88.0399),
    "Scarsdale, New York, USA": (40.9926, -73.7873),
    "Tehran, Iran": (35.6892, 51.3890),
    "West Godavari, Andhra Pradesh, India": (16.8, 81.5),
    "Mughal, Israel": (32.0, 34.9),
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
    "Brooklyn, New York, USA": (40.6782, -73.9442),
    "The Bronx, New York, USA": (40.8448, -73.8648),
    "Dorchester, Massachusetts, USA": (42.3, -71.07),
    "Milwaukee, Wisconsin, USA": (43.0389, -87.9065),
    "El Paso, Texas, USA": (31.7619, -106.4850),
    "Rochester, Michigan, USA": (42.6810, -83.1338),
    "Cincinnati, Ohio, USA": (39.1031, -84.5120),
    "Tyrone, Missouri, USA": (37.2, -91.9),
    "Pittsburgh, Pennsylvania, USA": (40.4406, -79.9959),
    "Newark, New Jersey, USA": (40.7357, -74.1724),
    "Oakland, California, USA": (37.8044, -122.2712),
    "Athens, Georgia, USA": (33.9519, -83.3576),
    "Severn, Maryland, USA": (39.1371, -76.6986),
    "Lansing, Michigan, USA": (42.7325, -84.5555),
    "Massapequa, New York, USA": (40.6696, -73.4721),
    "Dallas, Texas, USA": (32.7767, -96.7970),
    "Abbott, Texas, USA": (31.88, -97.07),
    "Zion, Illinois, USA": (42.4461, -87.8326),
    "Miami, Pennsylvania, USA": (40.0, -76.0),
    "Tampa, Florida, USA": (27.9506, -82.4572),
    "Paterson, New Jersey, USA": (40.9168, -74.1718),
    "Newport News, Virginia, USA": (37.0871, -76.4730),
    "Rionegro, Antioquia, Colombia": (6.155, -75.374),
    "Cartagena, Colombia": (10.3910, -75.5144),
    "Mariquita, Colombia": (5.198, -74.893),
    "Pacho, Cundinamarca, Colombia": (5.13, -74.16),
    "Lercara Friddi, Sicily, Italy": (37.75, 13.6),
    "Grodno, Belarus": (53.669, 23.813),
}

def get_tz(place):
    if 'India' in place or 'Delhi' in place or 'Mumbai' in place or 'Kolkata' in place or 'Pune' in place or 'Hyderabad' in place or 'Madurai' in place or 'Chandigarh' in place or 'Ludhiana' in place or 'Aligarh' in place or 'Patiala' in place or 'Muktsar' in place or 'Azhikode' in place or 'Bisam' in place or 'Bikaner' in place or 'West Godavari' in place:
        return 5.5
    if 'China' in place or 'Taiwan' in place: return 8
    if 'Japan' in place: return 9
    if 'UK' in place or 'London' in place or 'Ireland' in place or 'Scotland' in place: return 0
    if 'Germany' in place or 'France' in place or 'Italy' in place or 'Spain' in place or 'Hungary' in place or 'Paris' in place or 'Sicily' in place or 'Netherlands' in place or 'Denmark' in place or 'Switzerland' in place or 'Sweden' in place or 'Austria' in place or 'Belarus' in place or 'Latvia' in place or 'Poland' in place or 'Greece' in place:
        return 1
    if 'Russia' in place or 'Moscow' in place or 'Kolomna' in place or 'Kiev' in place or 'Ukraine' in place:
        return 3
    if 'Brazil' in place: return -3
    if 'South Africa' in place or 'Pretoria' in place or 'Welkom' in place: return 2
    if 'Mexico' in place: return -6
    if 'Yemen' in place: return 3
    if 'Iran' in place: return 3.5
    if 'Israel' in place: return 2
    if 'Canada' in place or 'Calgary' in place or 'Toronto' in place or 'Ottawa' in place:
        return -5
    if 'Australia' in place or 'Perth' in place: return 8
    if 'Colombia' in place or 'Cartagena' in place or 'Rionegro' in place or 'Mariquita' in place or 'Pacho' in place:
        return -5
    if 'Uzbekistan' in place: return 5
    return -5

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l
    return "Revati","Mercury"

def compute(c, label):
    dt = datetime.strptime(f"{c['birthday']}T12:00:00", "%Y-%m-%dT%H:%M:%S")
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
        nk, nl = gn(sid)
        dignity = 0
        if pn in EXALT and EXALT[pn] == sgn: dignity = 100
        elif pn in OWN and sgn in OWN[pn]: dignity = 75
        elif pn in DEBIL and DEBIL[pn] == sgn: dignity = -100
        planets[pn] = {"sign": sgn, "nakshatra": nk, "nakshatra_lord": nl, "dignity": dignity}
    
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0] - ayan) % 360
    for pn, rl in [("Rahu", rh), ("Ketu", (rh+180)%360)]:
        sgn = SIGNS[int(rl//30)]
        nk, nl = gn(rl)
        planets[pn] = {"sign": sgn, "nakshatra": nk, "nakshatra_lord": nl, "dignity": 0}
    
    conjunctions = []
    plist = list(planets.keys())
    for i in range(len(plist)):
        for j in range(i+1, len(plist)):
            if planets[plist[i]]['sign'] == planets[plist[j]]['sign']:
                conjunctions.append(f"{plist[i]}+{plist[j]}")
    
    return planets, conjunctions

# ============================================================
# GROUP DEFINITIONS
# ============================================================

# Billionaires: first 99 entries from the user's list (up through Azim Premji)
BILLIONAIRE_NAMES = [
    "Elon Musk","Jeff Bezos","Bill Gates","Mark Zuckerberg","Warren Buffett",
    "Bernard Arnault","Steve Jobs","Larry Ellison","Larry Page","Sergey Brin",
    "Steve Ballmer","Michael Bloomberg","Carlos Slim Helu","Amancio Ortega",
    "Mukesh Ambani","Gautam Adani","Jensen Huang","Michael Dell","Phil Knight",
    "Mark Shuttleworth","Richard Branson","Jack Ma","Pony Ma","Masayoshi Son",
    "Tadashi Yanai","Dieter Schwarz","Klaus-Michael Kuehne","Stefan Quandt",
    "Susanne Klatten","Francois Pinault","Alain Wertheimer","Gerard Wertheimer",
    "Giovanni Ferrero","Leonardo Del Vecchio Jr.","Giorgio Armani","Silvio Berlusconi",
    "James Ratcliffe","Michael Pritzker","Thomas Pritzker","Ray Dalio","Ken Griffin",
    "Stephen Schwarzman","David Rubenstein","Leon Black","Carl Icahn","George Soros",
    "Peter Thiel","Marc Andreessen","Ben Horowitz","Vinod Khosla","John Doerr",
    "Reid Hoffman","Travis Kalanick","Garrett Camp","Brian Chesky","Joe Gebbia",
    "Nathan Blecharczyk","Evan Spiegel","Bobby Murphy","Dustin Moskovitz","Eduardo Saverin",
    "Jan Koum","Brian Acton","Palmer Luckey","John Collison","Patrick Collison",
    "Whitney Wolfe Herd","Melanie Perkins","Sam Bankman-Fried","Changpeng Zhao",
    "Vitalik Buterin","Satoshi Nakamoto","Satya Nadella","Sundar Pichai","Tim Cook",
    "Andy Jassy","Dara Khosrowshahi","Arvind Krishna","Shantanu Narayen","Lisa Su",
    "Safra Catz","Ginni Rometty","Meg Whitman","Sheryl Sandberg","Marissa Mayer",
    "Susan Wojcicki","Bhavish Aggarwal","Vijay Shekhar Sharma","Kunal Bahl","Rohit Bansal",
    "Deepinder Goyal","Sriharsha Majety","Kalyan Krishnamurthy","Sachin Bansal","Binny Bansal",
    "Byju Raveendran","Ritesh Agarwal","Falguni Nayar","Radhakishan Damani",
    "Kumar Mangalam Birla","Uday Kotak","Azim Premji",
]
BILLIONAIRE_SET = set(BILLIONAIRE_NAMES)

# BAD/BROKE: criminals, fraudsters, bankrupt
BAD_BROKE_NAMES = [
    "Pablo Escobar","Al Capone","John Dillinger","Ted Bundy","Griselda Blanco",
    "Gilberto Rodriguez Orejuela","Jose Gonzalo Rodriguez Gacha","Lucky Luciano",
    "Meyer Lansky","Bugsy Siegel","John Gotti","Whitey Bulger","Jeffrey Dahmer",
    "John Wayne Gacy","Richard Ramirez","Aileen Wuornos","Charles Manson",
    "Bernie Madoff","Kenneth Lay","Jeffrey Skilling","Dennis Kozlowski","Jordan Belfort",
    "Mike Tyson","MC Hammer","Kim Basinger","Toni Braxton","Walt Disney",
    "Donald Trump","Marvin Gaye","Larry King","Burt Reynolds","Stephen Baldwin",
    "Meat Loaf","Willie Nelson","Gary Coleman","Abby Lee Miller","50 Cent",
    "Michael Vick","Aaron Carter","Teresa Giudice",
]
BAD_BROKE_SET = set(BAD_BROKE_NAMES)

# Parse the full user lists (both groups from the two JSON arrays)
# We'll use the actual JSON data from the user

# Billionaire list (first array, first 99)
billionaire_charts_data = [
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
    {"name":"Leonardo Del Vecchio Jr.","birthday":"1995-05-06","place":"Milan, Italy"},
    {"name":"Giorgio Armani","birthday":"1934-07-11","place":"Piacenza, Italy"},
    {"name":"Silvio Berlusconi","birthday":"1936-09-29","place":"Milan, Italy"},
    {"name":"James Ratcliffe","birthday":"1952-10-18","place":"Failsworth, Lancashire, UK"},
    {"name":"Michael Pritzker","birthday":"1950-10-11","place":"Chicago, Illinois, USA"},
    {"name":"Thomas Pritzker","birthday":"1950-06-06","place":"Chicago, Illinois, USA"},
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

# Bad/Broke (second array)
bad_broke_charts = [
    {"name":"Pablo Escobar","birthday":"1949-12-01","place":"Rionegro, Antioquia, Colombia"},
    {"name":"Al Capone","birthday":"1899-01-17","place":"New York City, New York, USA"},
    {"name":"John Dillinger","birthday":"1903-06-22","place":"Indianapolis, Indiana, USA"},
    {"name":"Ted Bundy","birthday":"1946-11-24","place":"Burlington, Vermont, USA"},
    {"name":"Griselda Blanco","birthday":"1943-02-15","place":"Cartagena, Colombia"},
    {"name":"Gilberto Rodriguez Orejuela","birthday":"1939-02-01","place":"Mariquita, Colombia"},
    {"name":"Jose Gonzalo Rodriguez Gacha","birthday":"1947-05-14","place":"Pacho, Cundinamarca, Colombia"},
    {"name":"Lucky Luciano","birthday":"1897-11-24","place":"Lercara Friddi, Sicily, Italy"},
    {"name":"Meyer Lansky","birthday":"1902-07-04","place":"Grodno, Belarus"},
    {"name":"Bugsy Siegel","birthday":"1906-02-28","place":"Brooklyn, New York, USA"},
    {"name":"John Gotti","birthday":"1940-10-27","place":"The Bronx, New York, USA"},
    {"name":"Whitey Bulger","birthday":"1929-09-03","place":"Dorchester, Massachusetts, USA"},
    {"name":"Jeffrey Dahmer","birthday":"1960-05-21","place":"Milwaukee, Wisconsin, USA"},
    {"name":"John Wayne Gacy","birthday":"1942-03-17","place":"Chicago, Illinois, USA"},
    {"name":"Richard Ramirez","birthday":"1960-02-29","place":"El Paso, Texas, USA"},
    {"name":"Aileen Wuornos","birthday":"1956-02-29","place":"Rochester, Michigan, USA"},
    {"name":"Charles Manson","birthday":"1934-11-12","place":"Cincinnati, Ohio, USA"},
    {"name":"Bernie Madoff","birthday":"1938-04-29","place":"Queens, New York, USA"},
    {"name":"Kenneth Lay","birthday":"1942-04-15","place":"Tyrone, Missouri, USA"},
    {"name":"Jeffrey Skilling","birthday":"1953-11-25","place":"Pittsburgh, Pennsylvania, USA"},
    {"name":"Dennis Kozlowski","birthday":"1946-11-16","place":"Newark, New Jersey, USA"},
    {"name":"Jordan Belfort","birthday":"1962-07-09","place":"Queens, New York, USA"},
    {"name":"Mike Tyson","birthday":"1966-06-30","place":"Brooklyn, New York, USA"},
    {"name":"MC Hammer","birthday":"1962-03-30","place":"Oakland, California, USA"},
    {"name":"Toni Braxton","birthday":"1967-10-07","place":"Severn, Maryland, USA"},
    {"name":"Walt Disney","birthday":"1901-12-05","place":"Chicago, Illinois, USA"},
    {"name":"Donald Trump","birthday":"1946-06-14","place":"Queens, New York, USA"},
    {"name":"Marvin Gaye","birthday":"1939-04-02","place":"Washington, D.C., USA"},
    {"name":"Larry King","birthday":"1933-11-19","place":"Brooklyn, New York, USA"},
    {"name":"Burt Reynolds","birthday":"1936-02-11","place":"Lansing, Michigan, USA"},
    {"name":"Stephen Baldwin","birthday":"1966-05-12","place":"Massapequa, New York, USA"},
    {"name":"Meat Loaf","birthday":"1947-09-27","place":"Dallas, Texas, USA"},
    {"name":"Willie Nelson","birthday":"1933-04-29","place":"Abbott, Texas, USA"},
    {"name":"Gary Coleman","birthday":"1968-02-08","place":"Zion, Illinois, USA"},
    {"name":"Abby Lee Miller","birthday":"1965-09-21","place":"Miami, Pennsylvania, USA"},
    {"name":"50 Cent","birthday":"1975-07-06","place":"Queens, New York, USA"},
    {"name":"Michael Vick","birthday":"1980-06-26","place":"Newport News, Virginia, USA"},
    {"name":"Aaron Carter","birthday":"1987-12-07","place":"Tampa, Florida, USA"},
    {"name":"Teresa Giudice","birthday":"1972-05-18","place":"Paterson, New Jersey, USA"},
]

print(f"Loading: {len(billionaire_charts_data)} billionaires vs {len(bad_broke_charts)} criminals/bankrupts")
print("Computing noon charts...\n")

def compute_group(charts, label):
    results = []
    for c in charts:
        try:
            p, conj = compute(c, label)
            results.append({"name": c['name'], "planets": p, "conjunctions": conj})
        except Exception as e:
            pass
    return results

billionaires = compute_group(billionaire_charts_data, "BILLIONAIRE")
bad_broke = compute_group(bad_broke_charts, "BAD/BROKE")

print(f"Computed: {len(billionaires)} billionaires | {len(bad_broke)} bad/broke\n")

def group_stats(group, label):
    stats = {"planet_signs": defaultdict(Counter), "dignities": defaultdict(Counter),
             "moon_naks": Counter(), "conjunctions": Counter()}
    for c in group:
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pn in c['planets']:
                sgn = c['planets'][pn]['sign']
                stats["planet_signs"][pn][sgn] += 1
                dig = c['planets'][pn]['dignity']
                stats["dignities"][pn][dig] += 1
        stats["moon_naks"][c['planets']['Moon']['nakshatra']] += 1
        for conj in c['conjunctions']:
            stats["conjunctions"][conj] += 1
    return stats

b_stats = group_stats(billionaires, "BILLIONAIRE")
bb_stats = group_stats(bad_broke, "BAD/BROKE")

print("="*100)
print("HEAD-TO-HEAD: BILLIONAIRES (n=" + str(len(billionaires)) + ") vs CRIMINALS/BANKRUPT (n=" + str(len(bad_broke)) + ")")
print("="*100)

# 1. DIGNITY COMPARISON
print(f"\n{'='*100}")
print("1. DIGNITY RATES — Billionaire vs Criminal/Bankrupt")
print(f"{'='*100}")

for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
    bn = len(billionaires)
    bbn = len(bad_broke)
    
    b_ex = b_stats["dignities"][pn][100] / bn * 100
    bb_ex = bb_stats["dignities"][pn][100] / bbn * 100
    
    b_own = b_stats["dignities"][pn][75] / bn * 100
    bb_own = bb_stats["dignities"][pn][75] / bbn * 100
    
    b_deb = b_stats["dignities"][pn][-100] / bn * 100
    bb_deb = bb_stats["dignities"][pn][-100] / bbn * 100
    
    d_ex = b_ex - bb_ex
    d_own = b_own - bb_own
    d_deb = b_deb - bb_deb
    
    print(f"\n{pn}:")
    print(f"  Exalted:   B={b_ex:.1f}% | BB={bb_ex:.1f}% | Δ={'+' if d_ex>0 else ''}{d_ex:.1f}% | {'💰 MORE' if d_ex>0 else '💀 MORE' if d_ex<0 else '—'}")
    print(f"  Own:       B={b_own:.1f}% | BB={bb_own:.1f}% | Δ={'+' if d_own>0 else ''}{d_own:.1f}% | {'💰 MORE' if d_own>0 else '💀 MORE' if d_own<0 else '—'}")
    print(f"  Debil:     B={b_deb:.1f}% | BB={bb_deb:.1f}% | Δ={'+' if d_deb>0 else ''}{d_deb:.1f}% | {'💰 MORE' if d_deb>0 else '💀 MORE' if d_deb<0 else '—'}")

# 2. KEY CONJUNCTIONS
print(f"\n{'='*100}")
print("2. CONJUNCTION RATES — What separates the groups?")
print(f"{'='*100}")

key_conj = ['Sun+Mercury','Sun+Venus','Mars+Venus','Mercury+Venus','Sun+Mars','Moon+Mars',
            'Moon+Saturn','Venus+Saturn','Mars+Saturn','Mercury+Saturn','Jupiter+Ketu']

print(f"\n{'Conjunction':<18} {'💰 Billionaire':>15} {'💀 Bad/Broke':>15} {'Δ':>8} {'Signal'}")
print("-"*70)
for conj in key_conj:
    b_rate = b_stats["conjunctions"][conj] / len(billionaires) * 100
    bb_rate = bb_stats["conjunctions"][conj] / len(bad_broke) * 100
    diff = b_rate - bb_rate
    signal = "💰💰💰" if diff > 8 else ("💰💰" if diff > 4 else ("💰" if diff > 1 else ("💀" if diff < -4 else ("—"))))
    print(f"{conj:<18} {b_rate:>14.1f}% {bb_rate:>14.1f}% {diff:>+7.1f}% {signal}")

# 3. MOON NAKSHATRA
print(f"\n{'='*100}")
print("3. MOON NAKSHATRA — Biggest Differences")
print(f"{'='*100}")

all_naks = set(list(b_stats["moon_naks"].keys()) + list(bb_stats["moon_naks"].keys()))
nak_diffs = []
for nak in all_naks:
    b_rate = b_stats["moon_naks"][nak] / len(billionaires) * 100
    bb_rate = bb_stats["moon_naks"][nak] / len(bad_broke) * 100
    nak_diffs.append((nak, b_rate, bb_rate, b_rate - bb_rate))

nak_diffs.sort(key=lambda x: -abs(x[3]))

print(f"\n{'Nakshatra':<20} {'💰 Billionaire':>14} {'💀 Bad/Broke':>14} {'Δ':>8} {'Leans'}")
print("-"*70)
for nak, b_rate, bb_rate, diff in nak_diffs[:15]:
    leans = "💰 BILLIONAIRE" if diff > 0 else "💀 BAD/BROKE"
    print(f"{nak:<20} {b_rate:>13.1f}% {bb_rate:>13.1f}% {diff:>+7.1f}% {leans}")

# 4. RAHU SIGN COMPARISON
print(f"\n{'='*100}")
print("4. RAHU SIGN — Billionaire vs Bad/Broke")
print(f"{'='*100}")

print(f"\n{'Sign':<14} {'💰 Billionaire':>14} {'💀 Bad/Broke':>14} {'Δ':>8}")
print("-"*60)
for sign in SIGNS:
    b_count = sum(1 for c in billionaires if c['planets']['Rahu']['sign'] == sign)
    bb_count = sum(1 for c in bad_broke if c['planets']['Rahu']['sign'] == sign)
    b_rate = b_count / len(billionaires) * 100
    bb_rate = bb_count / len(bad_broke) * 100
    diff = b_rate - bb_rate
    flag = " ←💰" if diff > 3 else (" ←💀" if diff < -3 else "")
    print(f"{sign:<14} {b_rate:>13.1f}% {bb_rate:>13.1f}% {diff:>+7.1f}%{flag}")

# 5. OVERALL SUMMARY
print(f"\n{'='*100}")
print("5. SUMMARY: What Separates Billionaires from Criminals/Bankrupts?")
print(f"{'='*100}")

# Aggregate dignities
b_total_dig = defaultdict(int)
bb_total_dig = defaultdict(int)
for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
    for dig_val in [100, 75, -100, 0]:
        b_total_dig[dig_val] += b_stats["dignities"][pn][dig_val]
        bb_total_dig[dig_val] += bb_stats["dignities"][pn][dig_val]

b_total = sum(b_total_dig.values())
bb_total = sum(bb_total_dig.values())

print(f"\nOverall Dignity (all 7 planets × N):")
print(f"  Exalted:   B={b_total_dig[100]/b_total*100:.1f}% | BB={bb_total_dig[100]/bb_total*100:.1f}% | Δ={b_total_dig[100]/b_total*100 - bb_total_dig[100]/bb_total*100:+.1f}%")
print(f"  Own:       B={b_total_dig[75]/b_total*100:.1f}% | BB={bb_total_dig[75]/bb_total*100:.1f}% | Δ={b_total_dig[75]/b_total*100 - bb_total_dig[75]/bb_total*100:+.1f}%")
print(f"  Debil:     B={b_total_dig[-100]/b_total*100:.1f}% | BB={bb_total_dig[-100]/bb_total*100:.1f}% | Δ={b_total_dig[-100]/b_total*100 - bb_total_dig[-100]/bb_total*100:+.1f}%")

# Count charts with at least 1 debilitated planet
b_has_deb = sum(1 for c in billionaires if any(c['planets'][pn]['dignity'] == -100 for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if pn in c['planets']))
bb_has_deb = sum(1 for c in bad_broke if any(c['planets'][pn]['dignity'] == -100 for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if pn in c['planets']))
print(f"\n  At least 1 debilitated planet: B={b_has_deb/len(billionaires)*100:.1f}% | BB={bb_has_deb/len(bad_broke)*100:.1f}%")

# Save
out = {
    "billionaire_count": len(billionaires),
    "bad_broke_count": len(bad_broke),
    "billionaire_stats": dict(b_stats["moon_naks"]),
    "bad_broke_stats": dict(bb_stats["moon_naks"]),
}
with open('dataset/billionaire_vs_criminal_stats.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved → dataset/billionaire_vs_criminal_stats.json")
