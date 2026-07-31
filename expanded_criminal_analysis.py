#!/usr/bin/env python3
"""
EXPANDED CRIMINAL/BROKE ANALYSIS — ~120 new charts + 39 existing vs 99 billionaires
Tests: do markers hold with larger N? New sub-patterns?
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

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l
    return "Revati","Mercury"

CITY_COORDS = {
    "La Tuna, Badiraguato, Mexico": (25.5, -107.5),
    "Alamo, Sinaloa, Mexico": (25.0, -107.5),
    "Cassano all'Ionio, Calabria, Italy": (39.783, 16.317),
    "Palermo, Sicily, Italy": (38.1157, 13.3615),
    "Brooklyn, New York, USA": (40.6782, -73.9442),
    "Chicago, Illinois, USA": (41.8781, -87.6298),
    "Tufino, Campania, Italy": (40.95, 14.567),
    "Tampa, Florida, USA": (27.9506, -82.4572),
    "Tunis, Tunisia": (36.8065, 10.1815),
    "Jersey City, New Jersey, USA": (40.7282, -74.0776),
    "Wisconsin Rapids, Wisconsin, USA": (44.3836, -89.8173),
    "La Crosse, Wisconsin, USA": (43.8014, -91.2396),
    "Washington, D.C., USA": (38.9072, -77.0369),
    "Pittsburg, Kansas, USA": (37.4109, -94.7050),
    "Salt Lake City, Utah, USA": (40.7608, -111.8910),
    "Gilmanton, New Hampshire, USA": (43.4167, -71.4167),
    "Crete, Indiana, USA": (41.45, -87.62),
    "Houston, Texas, USA": (29.7604, -95.3698),
    "Spur, Texas, USA": (33.476, -100.856),
    "Yatsushiro, Kumamoto, Japan": (32.5, 130.6),
    "Gori, Georgia": (41.98, 44.11),
    "Predappio, Italy": (44.1, 12.0),
    "Prek Sbauv, Cambodia": (11.5, 105.0),
    "Koboko, Uganda": (3.4, 31.0),
    "Al-Awja, Iraq": (34.5, 43.7),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753),
    "Lockport, New York, USA": (43.17, -78.69),
    "Lapeer, Michigan, USA": (43.05, -83.32),
    "Tokmok, Kyrgyzstan": (42.84, 75.3),
    "Elista, Russia": (46.32, 44.27),
    "Asan, South Korea": (36.78, 127.0),
    "Lakewood, Colorado, USA": (39.7047, -105.0814),
    "Wichita, Kansas, USA": (37.6872, -97.3301),
    "Kingston, New Hampshire, USA": (42.93, -71.05),
    "Oslo, Norway": (59.9139, 10.7522),
    "New Orleans, Louisiana, USA": (29.9511, -90.0715),
    "Bel Air, Maryland, USA": (39.535, -76.348),
    "Freeport, Illinois, USA": (42.29, -89.62),
    "Alpena, Michigan, USA": (45.06, -83.43),
    "Obljaj, Bosnia and Herzegovina": (44.17, 16.46),
    "Sindh, Pakistan": (25.0, 69.0),
    "New York City, New York, USA": (40.7128, -74.0060),
    "Domodedovo, Russia": (55.44, 37.76),
    "Bnei Brak, Israel": (32.08, 34.83),
    "Mexia, Texas, USA": (31.68, -96.48),
    "Lugo, Emilia-Romagna, Italy": (44.42, 11.91),
    "Hostinné, Czechia": (50.54, 15.72),
    "Bronx, New York, USA": (40.8448, -73.8648),
    "Selma, Alabama, USA": (32.41, -87.02),
    "Edmonton, Alberta, Canada": (53.5461, -113.4938),
    "Wellsville, New York, USA": (42.12, -77.95),
    "Flushing, New York, USA": (40.765, -73.817),
    "Layton, Utah, USA": (41.06, -111.97),
    "Tel Aviv, Israel": (32.0853, 34.7818),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Inglewood, California, USA": (33.9617, -118.3531),
    "Watford, Hertfordshire, UK": (51.655, -0.396),
    "Pont-l'Abbé, Brittany, France": (47.87, -4.22),
    "Tema, Ghana": (5.63, -0.02),
    "Benton Harbor, Michigan, USA": (42.12, -86.45),
    "Trenton, New Jersey, USA": (40.2206, -74.7597),
    "Santa Ana, California, USA": (33.7455, -117.8677),
    "Anchorage, Alaska, USA": (61.2181, -149.9003),
    "Norfolk, Virginia, USA": (36.8508, -76.2859),
    "Goose Creek, Texas, USA": (29.76, -94.97),
    "Toronto, Ontario, Canada": (43.6532, -79.3832),
    "San Jose, California, USA": (37.3382, -121.8863),
    "Singapore": (1.3521, 103.8198),
    "Los Angeles, California, USA": (34.0522, -118.2437),
    "Garden City, Kansas, USA": (37.97, -100.87),
    "East Harlem, New York, USA": (40.795, -73.938),
    "Compton, California, USA": (33.8958, -118.2201),
    "Buffalo, New York, USA": (42.8864, -78.8784),
    "Dallas, Texas, USA": (32.7767, -96.7970),
    "Mount Vernon, New York, USA": (40.9126, -73.8371),
    "Nashville, Tennessee, USA": (36.1627, -86.7816),
    "Columbus, Ohio, USA": (39.9612, -82.9988),
    "Miami, Florida, USA": (25.7617, -80.1918),
    "Sydney, New South Wales, Australia": (-33.8688, 151.2093),
    "Thousand Oaks, California, USA": (34.1706, -118.8376),
    "London, England, UK": (51.5074, -0.1278),
    "Memphis, Tennessee, USA": (35.1495, -90.0490),
    "Sharonville, Ohio, USA": (39.28, -84.41),
    "Albany, New York, USA": (42.6526, -73.7562),
    "Woodbridge, Connecticut, USA": (41.36, -73.01),
    "Atlanta, Georgia, USA": (33.7490, -84.3880),
    "Denver, Colorado, USA": (39.7392, -104.9903),
    "Staten Island, New York, USA": (40.5795, -74.1502),
    "Newport, Rhode Island, USA": (41.4901, -71.3128),
    "Tilden, Nebraska, USA": (42.04, -97.83),
    "Preetz, Schleswig-Holstein, Germany": (54.24, 10.28),
    "Maisons-Laffitte, France": (48.95, 2.15),
    "Cinderford, Gloucestershire, UK": (51.82, -2.5),
    "Kiel, Germany": (54.3233, 10.1228),
    "Austin, Texas, USA": (30.2672, -97.7431),
    "Townsville, Queensland, Australia": (-19.2590, 146.8169),
    "Elizabeth City, North Carolina, USA": (36.30, -76.22),
    "Crescent, Oklahoma, USA": (36.05, -97.57),
    "Saronno, Lombardy, Italy": (45.63, 9.04),
}

def get_tz(place):
    if any(w in place for w in ['India','Delhi','Mumbai','Kolkata']): return 5.5
    if any(w in place for w in ['China','Taiwan','Singapore']): return 8
    if 'Japan' in place: return 9
    if any(w in place for w in ['UK','England','Scotland','Ireland','London','Hertfordshire','Gloucestershire']): return 0
    if any(w in place for w in ['Germany','France','Italy','Spain','Norway','Czechia','Bosnia','Sicily','Lombardy','Calabria','Campania','Emilia-Romagna','Brittany','Schleswig-Holstein']): return 1
    if any(w in place for w in ['Russia','Moscow','Domodedovo','Kyrgyzstan','Elista']): return 3
    if 'Brazil' in place: return -3
    if 'South Africa' in place: return 2
    if any(w in place for w in ['Mexico','La Tuna','Alamo']): return -6
    if any(w in place for w in ['Yemen','Saudi Arabia','Iraq','Uganda','Kenya','Tunisia']): return 3
    if any(w in place for w in ['Iran','Israel','Bnei Brak','Tel Aviv']): return 2
    if 'Canada' in place or 'Toronto' in place or 'Edmonton' in place: return -6
    if 'Australia' in place or 'Sydney' in place or 'Townsville' in place: return 10
    if 'Colombia' in place: return -5
    if 'Pakistan' in place or 'Sindh' in place: return 5
    if 'South Korea' in place or 'Seoul' in place: return 9
    if 'Cambodia' in place: return 7
    if 'Georgia' in place and 'Gori' in place: return 4
    if 'Ghana' in place: return 0
    if 'Alaska' in place: return -9
    if 'Hawaii' in place: return -10
    return -5

EXPANDED_CRIMINALS = [
    {"name":"Joaquin Guzman","birthday":"1957-04-04","place":"La Tuna, Badiraguato, Mexico","subcat":"Drug Lord"},
    {"name":"Ismael Zambada Garcia","birthday":"1948-01-01","place":"Alamo, Sinaloa, Mexico","subcat":"Drug Lord"},
    {"name":"Frank Costello","birthday":"1891-01-26","place":"Cassano all'Ionio, Calabria, Italy","subcat":"Mafia"},
    {"name":"Carlo Gambino","birthday":"1902-08-24","place":"Palermo, Sicily, Italy","subcat":"Mafia"},
    {"name":"Paul Castellano","birthday":"1915-06-26","place":"Brooklyn, New York, USA","subcat":"Mafia"},
    {"name":"Sammy Gravano","birthday":"1945-03-12","place":"Brooklyn, New York, USA","subcat":"Mafia"},
    {"name":"Vito Genovese","birthday":"1897-11-21","place":"Tufino, Campania, Italy","subcat":"Mafia"},
    {"name":"Tony Accardo","birthday":"1906-04-28","place":"Chicago, Illinois, USA","subcat":"Mafia"},
    {"name":"Sam Giancana","birthday":"1908-05-24","place":"Chicago, Illinois, USA","subcat":"Mafia"},
    {"name":"Santo Trafficante Jr.","birthday":"1914-11-15","place":"Tampa, Florida, USA","subcat":"Mafia"},
    {"name":"Carlos Marcello","birthday":"1910-02-06","place":"Tunis, Tunisia","subcat":"Mafia"},
    {"name":"Henry Hill","birthday":"1943-06-11","place":"Brooklyn, New York, USA","subcat":"Mafia"},
    {"name":"Richard Kuklinski","birthday":"1935-04-11","place":"Jersey City, New Jersey, USA","subcat":"Hitman"},
    {"name":"Arthur Shawcross","birthday":"1945-06-06","place":"Wisconsin Rapids, Wisconsin, USA","subcat":"Serial Killer"},
    {"name":"Ed Gein","birthday":"1906-08-27","place":"La Crosse, Wisconsin, USA","subcat":"Serial Killer"},
    {"name":"Albert Fish","birthday":"1870-05-19","place":"Washington, D.C., USA","subcat":"Serial Killer"},
    {"name":"David Berkowitz","birthday":"1953-06-01","place":"Brooklyn, New York, USA","subcat":"Serial Killer"},
    {"name":"Dennis Rader","birthday":"1945-03-09","place":"Pittsburg, Kansas, USA","subcat":"Serial Killer"},
    {"name":"Gary Ridgway","birthday":"1949-02-18","place":"Salt Lake City, Utah, USA","subcat":"Serial Killer"},
    {"name":"H.H. Holmes","birthday":"1861-05-16","place":"Gilmanton, New Hampshire, USA","subcat":"Serial Killer"},
    {"name":"Jim Jones","birthday":"1931-05-13","place":"Crete, Indiana, USA","subcat":"Cult Leader"},
    {"name":"David Koresh","birthday":"1959-08-17","place":"Houston, Texas, USA","subcat":"Cult Leader"},
    {"name":"Marshall Applewhite","birthday":"1931-05-17","place":"Spur, Texas, USA","subcat":"Cult Leader"},
    {"name":"Shoko Asahara","birthday":"1955-03-02","place":"Yatsushiro, Kumamoto, Japan","subcat":"Cult Leader"},
    {"name":"Joseph Stalin","birthday":"1878-12-18","place":"Gori, Georgia","subcat":"Dictator"},
    {"name":"Benito Mussolini","birthday":"1883-07-29","place":"Predappio, Italy","subcat":"Dictator"},
    {"name":"Pol Pot","birthday":"1925-05-19","place":"Prek Sbauv, Cambodia","subcat":"Dictator"},
    {"name":"Idi Amin","birthday":"1925-05-17","place":"Koboko, Uganda","subcat":"Dictator"},
    {"name":"Saddam Hussein","birthday":"1937-04-28","place":"Al-Awja, Iraq","subcat":"Dictator"},
    {"name":"Osama bin Laden","birthday":"1957-03-10","place":"Riyadh, Saudi Arabia","subcat":"Terrorist"},
    {"name":"Timothy McVeigh","birthday":"1968-04-23","place":"Lockport, New York, USA","subcat":"Terrorist"},
    {"name":"Ted Kaczynski","birthday":"1942-05-22","place":"Chicago, Illinois, USA","subcat":"Terrorist"},
    {"name":"Dzhokhar Tsarnaev","birthday":"1993-07-22","place":"Tokmok, Kyrgyzstan","subcat":"Terrorist"},
    {"name":"Tamerlan Tsarnaev","birthday":"1986-10-21","place":"Elista, Russia","subcat":"Terrorist"},
    {"name":"Seung-Hui Cho","birthday":"1984-01-18","place":"Asan, South Korea","subcat":"Mass Shooter"},
    {"name":"Dylan Klebold","birthday":"1981-09-11","place":"Lakewood, Colorado, USA","subcat":"Mass Shooter"},
    {"name":"Eric Harris","birthday":"1981-04-09","place":"Wichita, Kansas, USA","subcat":"Mass Shooter"},
    {"name":"Adam Lanza","birthday":"1992-04-22","place":"Kingston, New Hampshire, USA","subcat":"Mass Shooter"},
    {"name":"Anders Behring Breivik","birthday":"1979-02-13","place":"Oslo, Norway","subcat":"Terrorist"},
    {"name":"Lee Harvey Oswald","birthday":"1939-10-18","place":"New Orleans, Louisiana, USA","subcat":"Assassin"},
    {"name":"John Wilkes Booth","birthday":"1838-05-10","place":"Bel Air, Maryland, USA","subcat":"Assassin"},
    {"name":"Charles J. Guiteau","birthday":"1841-09-08","place":"Freeport, Illinois, USA","subcat":"Assassin"},
    {"name":"Leon Czolgosz","birthday":"1873-05-05","place":"Alpena, Michigan, USA","subcat":"Assassin"},
    {"name":"Gavrilo Princip","birthday":"1894-07-25","place":"Obljaj, Bosnia and Herzegovina","subcat":"Assassin"},
    {"name":"Sunny Balwani","birthday":"1965-06-13","place":"Sindh, Pakistan","subcat":"Corporate Fraud"},
    {"name":"Billy McFarland","birthday":"1991-12-11","place":"New York City, New York, USA","subcat":"Fraudster"},
    {"name":"Anna Sorokin","birthday":"1991-01-23","place":"Domodedovo, Russia","subcat":"Fraudster"},
    {"name":"Simon Leviev","birthday":"1990-09-27","place":"Bnei Brak, Israel","subcat":"Fraudster"},
    {"name":"Martin Shkreli","birthday":"1983-03-17","place":"Brooklyn, New York, USA","subcat":"Corporate Fraud"},
    {"name":"Allen Stanford","birthday":"1950-03-24","place":"Mexia, Texas, USA","subcat":"Corporate Fraud"},
    {"name":"Charles Ponzi","birthday":"1882-03-03","place":"Lugo, Emilia-Romagna, Italy","subcat":"Fraudster"},
    {"name":"Victor Lustig","birthday":"1890-01-04","place":"Hostinné, Czechia","subcat":"Fraudster"},
    {"name":"Frank Abagnale","birthday":"1948-04-27","place":"Bronx, New York, USA","subcat":"Fraudster"},
    {"name":"Bernard Ebbers","birthday":"1941-08-27","place":"Edmonton, Alberta, Canada","subcat":"Corporate Fraud"},
    {"name":"John Rigas","birthday":"1924-11-14","place":"Wellsville, New York, USA","subcat":"Corporate Fraud"},
    {"name":"Lou Pearlman","birthday":"1954-06-19","place":"Flushing, New York, USA","subcat":"Corporate Fraud"},
    {"name":"Trevor Milton","birthday":"1982-04-06","place":"Layton, Utah, USA","subcat":"Corporate Fraud"},
    {"name":"Adam Neumann","birthday":"1979-02-09","place":"Tel Aviv, Israel","subcat":"Corporate Fraud"},
    {"name":"Do Kwon","birthday":"1991-09-06","place":"Seoul, South Korea","subcat":"Corporate Fraud"},
    {"name":"Barry Minkow","birthday":"1966-03-22","place":"Inglewood, California, USA","subcat":"Corporate Fraud"},
    {"name":"Nick Leeson","birthday":"1967-02-25","place":"Watford, Hertfordshire, UK","subcat":"Corporate Fraud"},
    {"name":"Jerome Kerviel","birthday":"1977-01-11","place":"Pont-l'Abbé, Brittany, France","subcat":"Corporate Fraud"},
    {"name":"Kweku Adoboli","birthday":"1980-05-21","place":"Tema, Ghana","subcat":"Corporate Fraud"},
    {"name":"Dennis Rodman","birthday":"1961-05-13","place":"Trenton, New Jersey, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Antoine Walker","birthday":"1976-08-12","place":"Chicago, Illinois, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Lenny Dykstra","birthday":"1963-02-10","place":"Santa Ana, California, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Curt Schilling","birthday":"1966-11-14","place":"Anchorage, Alaska, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Wayne Newton","birthday":"1942-04-03","place":"Norfolk, Virginia, USA","subcat":"Bankrupt Celebrity"},
    {"name":"David Cassidy","birthday":"1950-04-12","place":"New York City, New York, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Gary Busey","birthday":"1944-06-29","place":"Goose Creek, Texas, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Corey Haim","birthday":"1971-12-23","place":"Toronto, Ontario, Canada","subcat":"Bankrupt Celebrity"},
    {"name":"Dustin Diamond","birthday":"1977-01-07","place":"San Jose, California, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Tila Tequila","birthday":"1981-10-24","place":"Singapore","subcat":"Bankrupt Celebrity"},
    {"name":"Heidi Fleiss","birthday":"1965-12-30","place":"Los Angeles, California, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Joe Exotic","birthday":"1963-03-05","place":"Garden City, Kansas, USA","subcat":"Bankrupt Celebrity"},
    {"name":"Tupac Shakur","birthday":"1971-06-16","place":"East Harlem, New York, USA","subcat":"Musician/Fallen"},
    {"name":"The Notorious B.I.G.","birthday":"1972-05-21","place":"Brooklyn, New York, USA","subcat":"Musician/Fallen"},
    {"name":"Eazy-E","birthday":"1964-09-07","place":"Compton, California, USA","subcat":"Musician/Fallen"},
    {"name":"Rick James","birthday":"1948-02-01","place":"Buffalo, New York, USA","subcat":"Musician/Fallen"},
    {"name":"Vanilla Ice","birthday":"1967-10-31","place":"Dallas, Texas, USA","subcat":"Musician/Fallen"},
    {"name":"DMX","birthday":"1970-12-18","place":"Mount Vernon, New York, USA","subcat":"Musician/Fallen"},
    {"name":"Coolio","birthday":"1963-08-01","place":"Compton, California, USA","subcat":"Musician/Fallen"},
    {"name":"Sean Kingston","birthday":"1990-02-03","place":"Miami, Florida, USA","subcat":"Musician/Fallen"},
    {"name":"Damon Dash","birthday":"1971-05-03","place":"New York City, New York, USA","subcat":"Musician/Fallen"},
    {"name":"Iggy Azalea","birthday":"1990-06-07","place":"Sydney, New South Wales, Australia","subcat":"Musician/Fallen"},
    {"name":"Amanda Bynes","birthday":"1986-04-03","place":"Thousand Oaks, California, USA","subcat":"Troubled Celebrity"},
    {"name":"Anna Nicole Smith","birthday":"1967-11-28","place":"Houston, Texas, USA","subcat":"Troubled Celebrity"},
    {"name":"Janice Dickinson","birthday":"1955-02-15","place":"Brooklyn, New York, USA","subcat":"Troubled Celebrity"},
    {"name":"Tom Girardi","birthday":"1939-06-03","place":"Denver, Colorado, USA","subcat":"Corporate Fraud"},
    {"name":"Jen Shah","birthday":"1973-10-04","place":"Salt Lake City, Utah, USA","subcat":"Fraudster"},
    {"name":"Joe Giudice","birthday":"1972-05-22","place":"Saronno, Lombardy, Italy","subcat":"Fraudster"},
    {"name":"Mike Sorrentino","birthday":"1982-07-04","place":"Staten Island, New York, USA","subcat":"Fraudster"},
    {"name":"Richard Hatch","birthday":"1961-04-08","place":"Newport, Rhode Island, USA","subcat":"Fraudster"},
    {"name":"L. Ron Hubbard","birthday":"1911-03-13","place":"Tilden, Nebraska, USA","subcat":"Cult Leader"},
    {"name":"Keith Raniere","birthday":"1960-08-26","place":"Brooklyn, New York, USA","subcat":"Cult Leader"},
    {"name":"Allison Mack","birthday":"1982-07-29","place":"Preetz, Schleswig-Holstein, Germany","subcat":"Cult Member"},
    {"name":"Ghislaine Maxwell","birthday":"1961-12-25","place":"Maisons-Laffitte, France","subcat":"Sex Criminal"},
    {"name":"Jeffrey Epstein","birthday":"1953-01-20","place":"Brooklyn, New York, USA","subcat":"Sex Criminal"},
    {"name":"John McAfee","birthday":"1945-09-18","place":"Cinderford, Gloucestershire, UK","subcat":"Fugitive"},
    {"name":"Kim Dotcom","birthday":"1974-01-21","place":"Kiel, Germany","subcat":"Fugitive"},
    {"name":"Ross Ulbricht","birthday":"1984-03-27","place":"Austin, Texas, USA","subcat":"Fugitive"},
    {"name":"Julian Assange","birthday":"1971-07-03","place":"Townsville, Queensland, Australia","subcat":"Fugitive"},
    {"name":"Edward Snowden","birthday":"1983-06-21","place":"Elizabeth City, North Carolina, USA","subcat":"Fugitive"},
    {"name":"Chelsea Manning","birthday":"1987-12-17","place":"Crescent, Oklahoma, USA","subcat":"Fugitive"},
    {"name":"Aaron Swartz","birthday":"1986-11-08","place":"Chicago, Illinois, USA","subcat":"Fugitive"},
    {"name":"Elizabeth Holmes","birthday":"1984-02-03","place":"Washington, D.C., USA","subcat":"Corporate Fraud"},
]

def compute(c):
    dt = datetime.strptime(f"{c['birthday']}T12:00:00", "%Y-%m-%dT%H:%M:%S")
    tz_ofs = get_tz(c['place'])
    dt = dt.replace(tzinfo=timezone(timedelta(hours=tz_ofs)))
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
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

print(f"Computing {len(EXPANDED_CRIMINALS)} expanded criminal/broke charts...")
expanded = []
for c in EXPANDED_CRIMINALS:
    try:
        p, conj = compute(c)
        expanded.append({"name": c['name'], "planets": p, "conjunctions": conj, "subcat": c['subcat']})
    except Exception as e:
        pass

print(f"Computed: {len(expanded)} new charts")

# Load existing billionaire and criminal data
with open('dataset/billionaire_noon_analysis.json') as f:
    bil_data = json.load(f)

# ============================================================
# COMPARATIVE ANALYSIS
# ============================================================

# Compute markers for all
def get_markers(chart):
    p = chart['planets']
    moon = p.get('Moon', {})
    return {
        'moon_ardra': moon.get('nakshatra') == 'Ardra',
        'moon_jyeshtha': moon.get('nakshatra') == 'Jyeshtha',
        'moon_ashwini': moon.get('nakshatra') == 'Ashwini',
        'moon_deb': moon.get('dignity', 0) == -100,
        'moon_mula': moon.get('nakshatra') == 'Mula',
        'mars_sat_conj': 'Mars' in p and 'Saturn' in p and p['Mars']['sign'] == p['Saturn']['sign'],
        'mer_ven_conj': 'Mercury' in p and 'Venus' in p and p['Mercury']['sign'] == p['Venus']['sign'],
        'sun_mer_conj': 'Sun' in p and 'Mercury' in p and p['Sun']['sign'] == p['Mercury']['sign'],
        'jup_exalted': p.get('Jupiter',{}).get('dignity',0) == 100,
        'sat_exalted': p.get('Saturn',{}).get('dignity',0) == 100,
        'mars_exalted': p.get('Mars',{}).get('dignity',0) == 100,
        'bad_count': 0,  # computed below
        'good_count': 0,
    }

# Billionaire markers (from existing analysis)
bil_markers = []
for c in bil_data.get('charts', []):
    m = get_markers(c)
    m['bad_count'] = sum([m['moon_ardra'], m['moon_jyeshtha'], m['moon_ashwini'], m['moon_deb'], m['mars_sat_conj']])
    m['good_count'] = sum([m['mer_ven_conj'], m['sun_mer_conj'], m['jup_exalted'], m['sat_exalted'], m['mars_exalted']])
    bil_markers.append(m)

# Expanded criminal markers
exp_markers = []
for c in expanded:
    m = get_markers(c)
    m['bad_count'] = sum([m['moon_ardra'], m['moon_jyeshtha'], m['moon_ashwini'], m['moon_deb'], m['mars_sat_conj']])
    m['good_count'] = sum([m['mer_ven_conj'], m['sun_mer_conj'], m['jup_exalted'], m['sat_exalted'], m['mars_exalted']])
    m['name'] = c['name']
    m['subcat'] = c.get('subcat', '?')
    exp_markers.append(m)

n_bil = len(bil_markers)
n_exp = len(exp_markers)

print(f"\nComparing: {n_bil} billionaires vs {n_exp} criminals/broke")

print(f"\n{'='*100}")
print("MARKER VALIDATION — Expanded N={n_bil+n_exp}")
print(f"{'='*100}")

markers_to_test = [
    ('moon_ardra', 'Moon Ardra', 'BAD'),
    ('moon_jyeshtha', 'Moon Jyeshtha', 'BAD'),
    ('moon_ashwini', 'Moon Ashwini', 'BAD'),
    ('moon_deb', 'Moon Debilitated', 'BAD'),
    ('mars_sat_conj', 'Mars+Sat conjunction', 'BAD'),
    ('mer_ven_conj', 'Mercury+Venus conj', 'GOOD'),
    ('sun_mer_conj', 'Sun+Mercury conj', 'GOOD'),
    ('jup_exalted', 'Jupiter Exalted', 'GOOD'),
    ('sat_exalted', 'Saturn Exalted', 'GOOD'),
    ('mars_exalted', 'Mars Exalted', 'GOOD'),
]

print(f"\n{'Marker':<25} {'💰 Billionaire':>15} {'💀 Criminal':>15} {'Δ':>8} {'Ratio':>8} {'Verdict'}")
print("-"*90)

for key, label, expected in markers_to_test:
    bil_rate = sum(1 for m in bil_markers if m[key]) / n_bil * 100
    exp_rate = sum(1 for m in exp_markers if m[key]) / n_exp * 100
    diff = bil_rate - exp_rate
    ratio = bil_rate / exp_rate if exp_rate > 0 else float('inf')
    
    if expected == 'BAD':
        # Higher in criminals = confirmed
        verdict = '✓ CONFIRMED' if diff < -5 else ('~ WEAK' if diff < 0 else '✗ REVERSED')
    else:
        verdict = '✓ CONFIRMED' if diff > 5 else ('~ WEAK' if diff > 0 else '✗ REVERSED')
    
    print(f"{label:<25} {bil_rate:>14.1f}% {exp_rate:>14.1f}% {diff:>+7.1f}% {ratio:>7.1f}x {verdict}")

# Overall bad count distribution
print(f"\n{'='*100}")
print("BAD MARKER COUNT DISTRIBUTION")
print(f"{'='*100}")

for label, markers in [('💰 Billionaires', bil_markers), ('💀 Criminals', exp_markers)]:
    bad_dist = Counter(m['bad_count'] for m in markers)
    has_any = sum(1 for m in markers if m['bad_count'] >= 1) / len(markers) * 100
    has_multi = sum(1 for m in markers if m['bad_count'] >= 2) / len(markers) * 100
    print(f"\n{label} (n={len(markers)}):")
    for bc in range(4):
        pct = bad_dist.get(bc, 0) / len(markers) * 100
        bar = '█' * int(pct / 2)
        print(f"  {bc} bad markers: {bad_dist.get(bc, 0):>3} ({pct:>5.1f}%) {bar}")
    print(f"  ≥1 bad marker: {has_any:.0f}%  |  ≥2 bad markers: {has_multi:.0f}%")

# SUBCATEGORY ANALYSIS
print(f"\n{'='*100}")
print("SUBCATEGORY BREAKDOWN — Which criminals have the strongest signals?")
print(f"{'='*100}")

subcats = defaultdict(list)
for m in exp_markers:
    subcats[m.get('subcat','?')].append(m)

print(f"\n{'Subcategory':<25} {'N':>4} {'Bad≥1':>7} {'Bad≥2':>7} {'MoonArdra':>10} {'MoonJyesh':>10} {'MoonDeb':>9} {'Ma+Sa':>7}")
print("-"*85)
for scat, markers in sorted(subcats.items(), key=lambda x: -len(x[1])):
    n = len(markers)
    bad1 = sum(1 for m in markers if m['bad_count'] >= 1) / n * 100
    bad2 = sum(1 for m in markers if m['bad_count'] >= 2) / n * 100
    ardra = sum(1 for m in markers if m['moon_ardra']) / n * 100
    jyesh = sum(1 for m in markers if m['moon_jyeshtha']) / n * 100
    moondeb = sum(1 for m in markers if m['moon_deb']) / n * 100
    marsat = sum(1 for m in markers if m['mars_sat_conj']) / n * 100
    print(f"{scat:<25} {n:>4} {bad1:>6.0f}% {bad2:>6.0f}% {ardra:>9.0f}% {jyesh:>9.0f}% {moondeb:>8.0f}% {marsat:>6.0f}%")

# Individual worst charts
print(f"\n{'='*100}")
print("TOP 15 WORST CHARTS (most bad markers)")
print(f"{'='*100}")

all_marked = [(m['name'], m['bad_count'], m.get('subcat','?')) for m in exp_markers]
all_marked.sort(key=lambda x: -x[1])
for i, (name, bc, sc) in enumerate(all_marked[:15], 1):
    print(f"  {i:>2}. {name:<30} {bc} bad markers [{sc}]")

# Save
output = {
    "n_billionaires": n_bil,
    "n_criminals": n_exp,
    "billionaire_markers": {k: sum(1 for m in bil_markers if m[k])/n_bil for k,_dummy,_dummy2 in markers_to_test},
    "criminal_markers": {k: sum(1 for m in exp_markers if m[k])/n_exp for k,_dummy,_dummy2 in markers_to_test},
    "expanded_charts": [{"name": c['name'], "subcat": c.get('subcat','?'), 
                         "moon_nak": c['planets']['Moon']['nakshatra'],
                         "moon_dignity": c['planets']['Moon']['dignity']} for c in expanded],
}
with open('dataset/expanded_criminal_validation.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved → dataset/expanded_criminal_validation.json")
