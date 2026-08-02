#!/usr/bin/env python3
"""
MEGA CROSS-REFERENCE: ~435 charts across ALL outcome categories
Group by: Scientists, Criminals, Investors, Inventors, Dictators, Chefs, etc.
Find what separates each group at planet-sign-nakshatra level
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

COORDS = {
    "Centerville, Missouri, USA": (37.44, -90.96),
    "Kearney, Missouri, USA": (39.37, -94.36),
    "New York City, New York, USA": (40.7128, -74.0060),
    "Beaver, Utah, USA": (38.27, -112.64),
    "Mont Clare, Pennsylvania, USA": (40.14, -75.50),
    "Griffin, Georgia, USA": (33.25, -84.26),
    "Carthage, Missouri, USA": (37.18, -94.31),
    "Mitchell, Indiana, USA": (38.73, -86.47),
    "Lee's Summit, Missouri, USA": (38.91, -94.38),
    "Bonham, Texas, USA": (33.58, -96.18),
    "Tropea, Calabria, Italy": (38.68, 15.90),
    "Bronx, New York, USA": (40.8448, -73.8648),
    "Saint Paul, Minnesota, USA": (44.9537, -93.0900),
    "Salerno, Campania, Italy": (40.68, 14.77),
    "Memphis, Tennessee, USA": (35.1495, -90.0490),
    "Adairsville, Georgia, USA": (34.37, -84.93),
    "Rowena, Texas, USA": (31.65, -100.05),
    "Ellis County, Texas, USA": (32.38, -96.79),
    "Ash Grove, Missouri, USA": (37.32, -93.58),
    "Palermo, Sicily, Italy": (38.1157, 13.3615),
    "Castellammare del Golfo, Sicily, Italy": (38.027, 12.882),
    "Manhattan, New York, USA": (40.7831, -73.9712),
    "East Harlem, New York, USA": (40.795, -73.938),
    "Menfi, Sicily, Italy": (37.6, 12.97),
    "Worcester, Massachusetts, USA": (42.2626, -71.8023),
    "Brooklyn, New York, USA": (40.6782, -73.9442),
    "San Antonio, Texas, USA": (29.4241, -98.4936),
    "Fort Wayne, Indiana, USA": (41.0793, -85.1394),
    "Atlanta, Georgia, USA": (33.7490, -84.3880),
    "Long Beach, California, USA": (33.7701, -118.1937),
    "Willimantic, Connecticut, USA": (41.71, -72.21),
    "Los Angeles, California, USA": (34.0522, -118.2437),
    "Estherville, Iowa, USA": (43.40, -94.83),
    "Selbu, Norway": (63.22, 11.03),
    "Nottingham, England, UK": (52.9548, -1.1581),
    "Much Marcle, Herefordshire, England, UK": (51.99, -2.50),
    "Barnstaple, Devon, England, UK": (51.08, -4.06),
    "Bingley, West Yorkshire, England, UK": (53.85, -1.84),
    "Glasgow, Scotland, UK": (55.8642, -4.2518),
    "Crumpsall, Manchester, England, UK": (53.52, -2.24),
    "Yablochnoye, Sumy Oblast, Ukraine": (51.0, 34.5),
    "Mytishchi, Moscow Oblast, Russia": (55.91, 37.73),
    "Guamúchil, Sinaloa, Mexico": (25.47, -108.08),
    "Culiacán, Sinaloa, Mexico": (24.80, -107.39),
    "Badiraguato, Sinaloa, Mexico": (25.36, -107.55),
    "Matamoros, Tamaulipas, Mexico": (25.87, -97.50),
    "Aguililla, Michoacán, Mexico": (18.73, -102.78),
    "Armenia, Quindío, Colombia": (4.53, -75.68),
    "Medellín, Colombia": (6.2476, -75.5658),
    "St. Cloud, Minnesota, USA": (45.56, -94.16),
    "Ruse, Bulgaria": (43.85, 25.97),
    "Stanford, California, USA": (37.4241, -122.1661),
    "Boston, Massachusetts, USA": (42.3601, -71.0589),
    "Ukraine": (48.38, 31.17),
    "Milwaukee, Wisconsin, USA": (43.0389, -87.9065),
    "Houston, Texas, USA": (29.7604, -95.3698),
    "Orlando, Florida, USA": (28.5383, -81.3792),
    "Atmore, Alabama, USA": (31.02, -87.49),
    "Williamsburg, Virginia, USA": (37.27, -76.71),
    "Youngstown, Ohio, USA": (41.10, -80.65),
    "Brownfield, Texas, USA": (33.18, -102.27),
    "Leimen, Baden-Württemberg, Germany": (49.35, 8.69),
    "Barcelona, Spain": (41.3874, 2.1686),
    "Stockholm, Sweden": (59.3293, 18.0686),
    "Lanús, Argentina": (-34.70, -58.39),
    "Gateshead, Tyne and Wear, England, UK": (54.96, -1.60),
    "Ladysmith, British Columbia, Canada": (48.99, -123.82),
    "Braunau am Inn, Austria": (48.26, 13.03),
    "Munich, Germany": (48.1351, 11.5820),
    "Rheydt, Germany": (51.17, 6.44),
    "Rosenheim, Germany": (47.86, 12.13),
    "Halle an der Saale, Germany": (51.48, 11.97),
    "Solingen, Germany": (51.17, 7.08),
    "Scornicești, Romania": (44.56, 24.55),
    "Gjirokastër, Albania": (40.08, 20.14),
    "Požarevac, Serbia": (44.62, 21.18),
    "Petnjica, Montenegro": (42.92, 19.96),
    "Božanovići, Bosnia and Herzegovina": (43.68, 18.42),
    "Arthington, Liberia": (6.52, -10.68),
    "Bobangui, Central African Republic": (4.0, 18.5),
    "Addis Ababa, Ethiopia": (9.03, 38.74),
    "Hosh Bannaga, Sudan": (18.0, 33.0),
    "Sirte, Libya": (31.20, 16.59),
    "Kutama, Zimbabwe": (-17.0, 30.0),
    "Sarrat, Ilocos Norte, Philippines": (18.17, 120.65),
    "Muskegon, Michigan, USA": (43.2342, -86.2484),
    "International Falls, Minnesota, USA": (48.60, -93.41),
    "Berlin, Germany": (52.5200, 13.4050),
    "Peoria, Illinois, USA": (40.6936, -89.5890),
    "Sacramento, California, USA": (38.5816, -121.4944),
    "Kuchwada, Madhya Pradesh, India": (22.5, 77.0),
    "Baroda, Gujarat, India": (22.307, 73.181),
    "River Falls, Wisconsin, USA": (44.86, -92.62),
    "Chicago, Illinois, USA": (41.8781, -87.6298),
    "Galveston, Texas, USA": (29.3013, -94.7977),
    "Norwich, Connecticut, USA": (41.5243, -72.0758),
    "York, England, UK": (53.9591, -1.0815),
    "Fyresdal, Telemark, Norway": (59.19, 8.09),
    "Ambala, Punjab, India": (30.38, 76.78),
    "Devonport, Plymouth, England, UK": (50.38, -4.17),
    "Marylebone, London, England, UK": (51.52, -0.15),
    "Bournemouth, England, UK": (50.7192, -1.8808),
    "Bristol, England, UK": (51.4545, -2.5879),
    "Little Newcastle, Pembrokeshire, Wales, UK": (51.93, -4.94),
    "Kinsale, County Cork, Ireland": (51.71, -8.53),
    "England, UK": (52.355, -1.174),
    "Plymouth, Devon, England, UK": (50.37, -4.14),
    "Dundee, Scotland, UK": (56.4620, -2.9707),
    "Les Sables-d'Olonne, France": (46.50, -1.79),
    "Bridgetown, Barbados": (13.097, -59.618),
    "Johnstone, Renfrewshire, Scotland, UK": (55.84, -4.51),
    "Leeds, West Yorkshire, England, UK": (53.8008, -1.5491),
    "Villeneuve-Loubet, France": (43.66, 7.12),
    "Seattle, Washington, USA": (47.6062, -122.3321),
    "Collonges-au-Mont-d'Or, France": (45.82, 4.84),
    "Pasadena, California, USA": (34.1478, -118.1445),
    "Sankt Veit an der Glan, Austria": (46.77, 14.36),
    "L'Hospitalet de Llobregat, Catalonia, Spain": (41.36, 2.10),
    "Copenhagen, Denmark": (55.6761, 12.5683),
    "Orthez, France": (43.49, -0.77),
    "Poitiers, France": (46.58, 0.34),
    "Oceanside, California, USA": (33.1959, -117.3795),
    "Fall River, Massachusetts, USA": (41.7015, -71.1550),
    "Clavering, Essex, England, UK": (51.97, 0.14),
    "Columbus, Ohio, USA": (39.9612, -82.9988),
    "Evart, Michigan, USA": (43.90, -85.26),
    "Bucharest, Romania": (44.4268, 26.1025),
    "Lebanon, Ohio, USA": (39.435, -84.203),
    "Salem, Oregon, USA": (44.9429, -123.0351),
    "Baku, Azerbaijan": (40.4093, 49.8671),
    "Tønsberg, Norway": (59.27, 10.41),
    "Riga, Latvia": (56.9496, 24.1052),
    "New Orleans, Louisiana, USA": (29.9511, -90.0715),
    "Smiljan, Croatia": (44.56, 15.31),
    "Woolsthorpe-by-Colsterworth, England, UK": (52.81, -0.62),
    "Maida Vale, London, England, UK": (51.53, -0.19),
    "Bluefield, West Virginia, USA": (37.27, -81.22),
    "Brno, Czechia": (49.1951, 16.6068),
    "Queens, New York, USA": (40.7282, -73.7949),
    "Ulm, Germany": (48.4011, 9.9876),
    "Pisa, Italy": (43.7228, 10.4017),
    "Warsaw, Poland": (52.2297, 21.0122),
    "Oxford, England, UK": (51.7520, -1.2577),
    "La Paz, Bolivia": (-16.500, -68.150),
    "Feeding Hills, Massachusetts, USA": (42.07, -72.68),
    "Chiaravalle, Italy": (43.60, 13.33),
    "Burlington, Vermont, USA": (44.4759, -73.2121),
    "Hale's Ford, Virginia, USA": (37.13, -79.25),
    "Great Barrington, Massachusetts, USA": (42.196, -73.362),
    "Malden, Massachusetts, USA": (42.425, -71.066),
    "Miami, Florida, USA": (25.7617, -80.1918),
    "Humble, Texas, USA": (30.00, -95.26),
    "Figueres, Catalonia, Spain": (42.27, 2.96),
    "Dublin, Ireland": (53.3498, -6.2603),
    "Venice, Italy": (45.4408, 12.3155),
    "Pokrovskoye, Russia": (57.5, 66.5),
    "Paris, France": (48.8566, 2.3522),
    "Bethel, Connecticut, USA": (41.37, -73.41),
    "Florence, Italy": (43.7696, 11.2558),
    "Harima Province, Japan": (34.83, 134.70),
    "Braunschweig, Germany": (52.27, 10.52),
    "Basel, Switzerland": (47.5596, 7.5886),
    "Erode, Tamil Nadu, India": (11.34, 77.72),
    "Clermont-Ferrand, France": (45.78, 3.08),
    "Descartes, Indre-et-Loire, France": (46.97, 0.70),
    "Beaumont-de-Lommat, France": (43.88, 0.99),
    "London, England, UK": (51.5074, -0.1278),
    "Toruń, Poland": (53.0138, 18.5984),
    "Weil der Stadt, Germany": (48.75, 8.87),
    "Knutstorp Castle, Sweden": (55.94, 13.15),
    "Dole, France": (47.09, 5.49),
    "Darvel, Ayrshire, Scotland, UK": (55.59, -4.28),
    "Milan, Ohio, USA": (41.30, -82.61),
    "Edinburgh, Scotland, UK": (55.9533, -3.1883),
    "Dayton, Ohio, USA": (39.7589, -84.1916),
    "Millville, Indiana, USA": (39.93, -85.25),
    "Greenfield Township, Michigan, USA": (42.30, -83.20),
    "San Francisco, California, USA": (37.7749, -122.4194),
    "Pretoria, South Africa": (-25.7479, 28.2293),
    "Albuquerque, New Mexico, USA": (35.0853, -106.6056),
    "White Plains, New York, USA": (41.034, -73.7629),
    "Lansing, Michigan, USA": (42.7325, -84.5555),
    "Moscow, Russia": (55.7558, 37.6173),
    "Kolomna, Russia": (55.0833, 38.7833),
    "Helsinki, Finland": (60.1699, 24.9384),
    "San Jose, California, USA": (37.3382, -121.8863),
    "Budapest, Hungary": (47.4979, 19.0402),
    "Omaha, Nebraska, USA": (41.2565, -95.9345),
    "Detroit, Michigan, USA": (42.3314, -83.0458),
    "Cambridge, Massachusetts, USA": (42.3736, -71.1097),
    "Jackson Heights, New York, USA": (40.75, -73.88),
    "Chappaqua, New York, USA": (41.16, -73.77),
    "Acton, Massachusetts, USA": (42.48, -71.45),
    "New Bedford, Massachusetts, USA": (41.6362, -70.9342),
    "Hartford, Connecticut, USA": (41.7658, -72.6734),
    "Richford, New York, USA": (42.36, -76.20),
    "Dunfermline, Scotland, UK": (56.07, -3.44),
    "Staten Island, New York, USA": (40.5795, -74.1502),
    "Roxbury, New York, USA": (42.30, -74.57),
    "Pownal, Vermont, USA": (42.77, -73.23),
}

def get_tz(place):
    if any(w in place for w in ['India','Delhi','Mumbai','Kolkata','Punjab','Baroda','Erode','Madhya']): return 5.5
    if any(w in place for w in ['China','Taiwan','Singapore','Philippines']): return 8
    if 'Japan' in place: return 9
    if any(w in place for w in ['UK','England','Scotland','Wales','Ireland','London','Oxford','Bristol','Edinburgh','Glasgow','Manchester','Birmingham','Leeds','Devon','Essex','Plymouth','Bournemouth','Nottingham']): return 0
    if any(w in place for w in ['Germany','France','Italy','Spain','Norway','Czechia','Denmark','Sweden','Austria','Switzerland','Poland','Croatia','Serbia','Montenegro','Bosnia','Albania','Romania','Bulgaria','Belgium','Netherlands','Finland','Catalonia','Sicily','Calabria','Campania']): return 1
    if any(w in place for w in ['Russia','Moscow','Ukraine','Belarus','Latvia','Lithuania','Estonia','Azerbaijan']): return 3
    if 'Brazil' in place: return -3
    if 'Argentina' in place: return -3
    if 'South Africa' in place or 'Pretoria' in place: return 2
    if any(w in place for w in ['Mexico','La Tuna','Alamo','Culiacán','Badiraguato','Guamúchil','Matamoros','Aguililla']): return -6
    if any(w in place for w in ['Saudi Arabia','Iraq','Uganda','Kenya','Ethiopia','Sudan','Libya','Yemen']): return 3
    if any(w in place for w in ['Iran','Israel']): return 2
    if any(w in place for w in ['Canada','Toronto','Ladysmith']): return -5
    if any(w in place for w in ['Australia','Sydney']): return 10
    if any(w in place for w in ['Colombia','Medellín','Armenia','Bolivia']): return -5
    if 'Barbados' in place: return -4
    if 'Liberia' in place: return 0
    if 'Central African' in place: return 1
    if 'Zimbabwe' in place: return 2
    if 'Alaska' in place: return -9
    return -5

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
        planets[pn] = {"sign": sgn, "nakshatra": nk, "dignity": dignity}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0] - ayan) % 360
    for pn, rl in [("Rahu", rh), ("Ketu", (rh+180)%360)]:
        planets[pn] = {"sign": SIGNS[int(rl//30)], "nakshatra": gn(rl)[0], "dignity": 0}
    conj = []
    pl = list(planets.keys())
    for i in range(len(pl)):
        for j in range(i+1, len(pl)):
            if planets[pl[i]]['sign'] == planets[pl[j]]['sign']:
                conj.append(f"{pl[i]}+{pl[j]}")
    return planets, conj

# ============================================================
# ALL CHARTS WITH GROUP LABELS
# ============================================================
GROUPS = [
    ("Outlaw", [
        ("Jesse James","1847-09-05","Centerville, Missouri, USA"),
        ("Frank James","1843-01-10","Kearney, Missouri, USA"),
        ("Billy the Kid","1859-11-23","New York City, New York, USA"),
        ("Butch Cassidy","1866-04-13","Beaver, Utah, USA"),
        ("Sundance Kid","1867-01-01","Mont Clare, Pennsylvania, USA"),
        ("Doc Holliday","1851-08-14","Griffin, Georgia, USA"),
        ("Belle Starr","1848-02-05","Carthage, Missouri, USA"),
        ("Sam Bass","1851-07-21","Mitchell, Indiana, USA"),
        ("Cole Younger","1844-01-15","Lee's Summit, Missouri, USA"),
        ("John Wesley Hardin","1853-05-26","Bonham, Texas, USA"),
        ("Bonnie Parker","1910-10-01","Rowena, Texas, USA"),
        ("Clyde Barrow","1909-03-24","Ellis County, Texas, USA"),
        ("Ma Barker","1871-10-08","Ash Grove, Missouri, USA"),
        ("Charles Pretty Boy Floyd","1904-02-03","Adairsville, Georgia, USA"),
    ]),
    ("Mafia", [
        ("Albert Anastasia","1902-09-26","Tropea, Calabria, Italy"),
        ("Dutch Schultz","1902-01-07","Bronx, New York, USA"),
        ("George Bugs Moran","1893-08-21","Saint Paul, Minnesota, USA"),
        ("Arnold Rothstein","1882-01-17","New York City, New York, USA"),
        ("Frank Nitti","1886-01-27","Salerno, Campania, Italy"),
        ("George Machine Gun Kelly","1895-07-18","Memphis, Tennessee, USA"),
        ("Tommy Lucchese","1899-12-01","Palermo, Sicily, Italy"),
        ("Joseph Bonanno","1905-01-18","Castellammare del Golfo, Sicily, Italy"),
        ("Vincent Gigante","1928-03-29","Manhattan, New York, USA"),
        ("Carmine Galante","1910-02-21","East Harlem, New York, USA"),
        ("Joe Masseria","1886-01-17","Menfi, Sicily, Italy"),
        ("Salvatore Maranzano","1886-07-31","Castellammare del Golfo, Sicily, Italy"),
        ("Raymond Patriarca","1908-03-17","Worcester, Massachusetts, USA"),
        ("Nicky Scarfo","1929-03-08","Brooklyn, New York, USA"),
    ]),
    ("Serial Killer", [
        ("Rodney Alcala","1943-08-23","San Antonio, Texas, USA"),
        ("Dean Corll","1939-12-24","Fort Wayne, Indiana, USA"),
        ("Wayne Williams","1958-01-05","Atlanta, Georgia, USA"),
        ("Randy Kraft","1945-03-19","Long Beach, California, USA"),
        ("William Bonin","1947-01-08","Willimantic, Connecticut, USA"),
        ("Patrick Kearney","1939-09-24","Los Angeles, California, USA"),
        ("Robert Hansen","1939-02-15","Estherville, Iowa, USA"),
        ("Belle Gunness","1859-11-11","Selbu, Norway"),
        ("Harold Shipman","1946-01-14","Nottingham, England, UK"),
        ("Fred West","1941-09-29","Much Marcle, Herefordshire, England, UK"),
        ("Rosemary West","1953-11-29","Barnstaple, Devon, England, UK"),
        ("Peter Sutcliffe","1946-06-02","Bingley, West Yorkshire, England, UK"),
        ("Ian Brady","1938-01-02","Glasgow, Scotland, UK"),
        ("Myra Hindley","1942-07-23","Crumpsall, Manchester, England, UK"),
        ("Andrei Chikatilo","1936-10-16","Yablochnoye, Sumy Oblast, Ukraine"),
        ("Alexander Pichushkin","1974-04-09","Mytishchi, Moscow Oblast, Russia"),
    ]),
    ("Drug Lord", [
        ("Amado Carrillo Fuentes","1956-12-17","Guamúchil, Sinaloa, Mexico"),
        ("Miguel Ángel Félix Gallardo","1946-01-08","Culiacán, Sinaloa, Mexico"),
        ("Ernesto Fonseca Carrillo","1930-08-01","Badiraguato, Sinaloa, Mexico"),
        ("Rafael Caro Quintero","1952-10-24","Badiraguato, Sinaloa, Mexico"),
        ("Juan García Ábrego","1944-09-13","Matamoros, Tamaulipas, Mexico"),
        ("Osiel Cárdenas Guillén","1967-05-18","Matamoros, Tamaulipas, Mexico"),
        ("Nemesio Oseguera Cervantes","1966-07-17","Aguililla, Michoacán, Mexico"),
        ("Arturo Beltrán Leyva","1961-09-27","Badiraguato, Sinaloa, Mexico"),
        ("Carlos Lehder","1949-09-07","Armenia, Quindío, Colombia"),
        ("Jorge Luis Ochoa Vásquez","1950-09-30","Medellín, Colombia"),
        ("Fabio Ochoa Vásquez","1957-05-02","Medellín, Colombia"),
    ]),
    ("Dictator", [
        ("Adolf Hitler","1889-04-20","Braunau am Inn, Austria"),
        ("Heinrich Himmler","1900-10-07","Munich, Germany"),
        ("Joseph Goebbels","1897-10-29","Rheydt, Germany"),
        ("Hermann Göring","1893-01-12","Rosenheim, Germany"),
        ("Reinhard Heydrich","1904-03-07","Halle an der Saale, Germany"),
        ("Adolf Eichmann","1906-03-19","Solingen, Germany"),
        ("Nicolae Ceaușescu","1918-01-26","Scornicești, Romania"),
        ("Enver Hoxha","1908-10-16","Gjirokastër, Albania"),
        ("Slobodan Milošević","1941-08-20","Požarevac, Serbia"),
        ("Radovan Karadžić","1945-06-19","Petnjica, Montenegro"),
        ("Ratko Mladić","1942-03-12","Božanovići, Bosnia and Herzegovina"),
        ("Charles Taylor","1948-01-28","Arthington, Liberia"),
        ("Jean-Bédel Bokassa","1921-02-22","Bobangui, Central African Republic"),
        ("Mengistu Haile Mariam","1937-05-21","Addis Ababa, Ethiopia"),
        ("Omar al-Bashir","1944-01-01","Hosh Bannaga, Sudan"),
        ("Muammar Gaddafi","1942-06-07","Sirte, Libya"),
        ("Robert Mugabe","1924-02-21","Kutama, Zimbabwe"),
        ("Ferdinand Marcos","1917-09-11","Sarrat, Ilocos Norte, Philippines"),
    ]),
    ("Scientist/Genius", [
        ("Nikola Tesla","1856-07-10","Smiljan, Croatia"),
        ("Isaac Newton","1643-01-04","Woolsthorpe-by-Colsterworth, England, UK"),
        ("Alan Turing","1912-06-23","Maida Vale, London, England, UK"),
        ("John Nash","1928-06-13","Bluefield, West Virginia, USA"),
        ("Kurt Gödel","1906-04-28","Brno, Czechia"),
        ("J. Robert Oppenheimer","1904-04-22","New York City, New York, USA"),
        ("Richard Feynman","1918-05-11","Queens, New York, USA"),
        ("Albert Einstein","1879-03-14","Ulm, Germany"),
        ("Galileo Galilei","1564-02-15","Pisa, Italy"),
        ("Marie Curie","1867-11-07","Warsaw, Poland"),
        ("Stephen Hawking","1942-01-08","Oxford, England, UK"),
        ("Carl Friedrich Gauss","1777-04-30","Braunschweig, Germany"),
        ("Leonhard Euler","1707-04-15","Basel, Switzerland"),
        ("Srinivasa Ramanujan","1887-12-22","Erode, Tamil Nadu, India"),
        ("Blaise Pascal","1623-06-19","Clermont-Ferrand, France"),
        ("René Descartes","1596-03-31","Descartes, Indre-et-Loire, France"),
        ("Louis Pasteur","1822-12-27","Dole, France"),
        ("Alexander Fleming","1881-08-06","Darvel, Ayrshire, Scotland, UK"),
    ]),
    ("Inventor/Tech", [
        ("Thomas Edison","1847-02-11","Milan, Ohio, USA"),
        ("Alexander Graham Bell","1847-03-03","Edinburgh, Scotland, UK"),
        ("Orville Wright","1871-08-19","Dayton, Ohio, USA"),
        ("Wilbur Wright","1867-04-16","Millville, Indiana, USA"),
        ("Henry Ford","1863-07-30","Greenfield Township, Michigan, USA"),
        ("Steve Jobs","1955-02-24","San Francisco, California, USA"),
        ("Bill Gates","1955-10-28","Seattle, Washington, USA"),
        ("Elon Musk","1971-06-28","Pretoria, South Africa"),
        ("Jeff Bezos","1964-01-12","Albuquerque, New Mexico, USA"),
        ("Mark Zuckerberg","1984-05-14","White Plains, New York, USA"),
        ("Larry Page","1973-03-26","Lansing, Michigan, USA"),
        ("Sergey Brin","1973-08-21","Moscow, Russia"),
        ("Steve Wozniak","1950-08-11","San Jose, California, USA"),
        ("Linus Torvalds","1969-12-28","Helsinki, Finland"),
        ("Tim Berners-Lee","1955-06-08","London, England, UK"),
    ]),
    ("Investor/Tycoon", [
        ("George Soros","1930-08-12","Budapest, Hungary"),
        ("Warren Buffett","1930-08-30","Omaha, Nebraska, USA"),
        ("Carl Icahn","1936-02-16","Brooklyn, New York, USA"),
        ("Michael Milken","1946-07-04","Los Angeles, California, USA"),
        ("Ivan Boesky","1937-03-06","Detroit, Michigan, USA"),
        ("John Paulson","1955-12-14","Queens, New York, USA"),
        ("Jim Simons","1938-04-25","Cambridge, Massachusetts, USA"),
        ("Ray Dalio","1949-08-08","Jackson Heights, New York, USA"),
        ("Bill Ackman","1966-05-11","Chappaqua, New York, USA"),
        ("Jesse Livermore","1877-07-26","Acton, Massachusetts, USA"),
        ("Hetty Green","1834-11-21","New Bedford, Massachusetts, USA"),
        ("J.P. Morgan","1837-04-17","Hartford, Connecticut, USA"),
        ("John D. Rockefeller","1839-07-08","Richford, New York, USA"),
        ("Andrew Carnegie","1835-11-25","Dunfermline, Scotland, UK"),
        ("Cornelius Vanderbilt","1794-05-27","Staten Island, New York, USA"),
        ("Jay Gould","1836-05-27","Roxbury, New York, USA"),
        ("Jim Fisk","1835-04-01","Pownal, Vermont, USA"),
    ]),
    ("Chef", [
        ("Gordon Ramsay","1966-11-08","Johnstone, Renfrewshire, Scotland, UK"),
        ("Anthony Bourdain","1956-06-25","New York City, New York, USA"),
        ("Marco Pierre White","1961-12-11","Leeds, West Yorkshire, England, UK"),
        ("Auguste Escoffier","1846-10-28","Villeneuve-Loubet, France"),
        ("Julia Child","1912-08-15","Pasadena, California, USA"),
        ("Wolfgang Puck","1949-07-08","Sankt Veit an der Glan, Austria"),
    ]),
    ("Chess/Game Genius", [
        ("Bobby Fischer","1943-03-09","Chicago, Illinois, USA"),
        ("Garry Kasparov","1963-04-13","Baku, Azerbaijan"),
        ("Magnus Carlsen","1990-11-30","Tønsberg, Norway"),
        ("Mikhail Tal","1936-11-09","Riga, Latvia"),
        ("Paul Morphy","1837-06-22","New Orleans, Louisiana, USA"),
        ("Edward O. Thorp","1932-08-14","Chicago, Illinois, USA"),
    ]),
    ("Bankrupt Athlete", [
        ("Latrell Sprewell","1970-09-08","Milwaukee, Wisconsin, USA"),
        ("Vince Young","1983-05-18","Houston, Texas, USA"),
        ("Warren Sapp","1972-12-19","Orlando, Florida, USA"),
        ("Evander Holyfield","1962-10-19","Atmore, Alabama, USA"),
        ("Lawrence Taylor","1959-02-04","Williamsburg, Virginia, USA"),
        ("Boris Becker","1967-11-22","Leimen, Baden-Württemberg, Germany"),
        ("Diego Maradona","1960-10-30","Lanús, Argentina"),
    ]),
    ("Spy/Traitor", [
        ("Aldrich Ames","1941-05-26","River Falls, Wisconsin, USA"),
        ("Robert Hanssen","1944-04-18","Chicago, Illinois, USA"),
        ("Jonathan Pollard","1954-08-07","Galveston, Texas, USA"),
        ("Julius Rosenberg","1918-05-12","New York City, New York, USA"),
        ("Ethel Rosenberg","1915-09-28","New York City, New York, USA"),
        ("Benedict Arnold","1741-01-14","Norwich, Connecticut, USA"),
        ("Guy Fawkes","1570-04-13","York, England, UK"),
        ("Vidkun Quisling","1887-07-18","Fyresdal, Telemark, Norway"),
        ("Kim Philby","1912-01-01","Ambala, Punjab, India"),
    ]),
]

print(f"Computing {sum(len(g[1]) for g in GROUPS)} charts across {len(GROUPS)} groups...")

group_data = {}
total = 0
for group_name, members in GROUPS:
    charts = []
    for name, bday, place in members:
        try:
            p, conj = compute({"name": name, "birthday": bday, "place": place})
            charts.append({"name": name, "planets": p, "conjunctions": conj})
            total += 1
        except Exception as e:
            pass
    group_data[group_name] = charts
    print(f"  {group_name}: {len(charts)} computed")

print(f"\nTotal: {total} charts computed\n")

# ============================================================
# GROUP-LEVEL ANALYSIS
# ============================================================
print("="*120)
print("WHAT MAKES EACH GROUP DIFFERENT? Top Planetary Signatures per Group")
print("="*120)

for group_name, charts in sorted(group_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    n = len(charts)
    
    # Moon nakshatras
    moon_naks = Counter(c['planets']['Moon']['nakshatra'] for c in charts)
    
    # Dignities
    ex_counts = Counter()
    deb_counts = Counter()
    for c in charts:
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pn in c['planets']:
                d = c['planets'][pn]['dignity']
                if d == 100: ex_counts[pn] += 1
                elif d == -100: deb_counts[pn] += 1
    
    # Conjunctions
    all_conj = Counter()
    for c in charts:
        for conj in c['conjunctions']:
            all_conj[conj] += 1
    
    # Rahu signs
    rahu_signs = Counter(c['planets']['Rahu']['sign'] for c in charts)
    
    print(f"\n{'='*80}")
    print(f"  {group_name} (n={n})")
    print(f"{'='*80}")
    
    # Top moon nakshatras
    top_naks = [(nak, count, count/n*100) for nak, count in moon_naks.most_common(5)]
    print(f"  Moon Nakshatra: " + " | ".join(f"{n}({pct:.0f}%)" for n,_,pct in top_naks))
    
    # Dignities
    if ex_counts:
        top_ex = [(pn, c, c/n*100) for pn, c in ex_counts.most_common(3)]
        print(f"  Most Exalted:   " + " | ".join(f"{pn}({pct:.0f}%)" for pn,_,pct in top_ex if pct > 0))
    if deb_counts:
        top_deb = [(pn, c, c/n*100) for pn, c in deb_counts.most_common(3)]
        print(f"  Most Debil:     " + " | ".join(f"{pn}({pct:.0f}%)" for pn,_,pct in top_deb if pct > 0))
    
    # Top conjunctions
    top_conj = [(conj, c, c/n*100) for conj, c in all_conj.most_common(5)]
    print(f"  Conjunctions:   " + " | ".join(f"{conj}({pct:.0f}%)" for conj,_,pct in top_conj if pct > 10))
    
    # Rahu
    top_rahu = [(sign, c, c/n*100) for sign, c in rahu_signs.most_common(3)]
    print(f"  Rahu Sign:      " + " | ".join(f"{s}({pct:.0f}%)" for s,_,pct in top_rahu))

# ============================================================
# CROSS-GROUP DISCRIMINATORS
# ============================================================
print(f"\n{'='*120}")
print("CROSS-GROUP DISCRIMINATORS: Unique Signatures")
print(f"{'='*120}")

# Find markers that are UNIQUE or nearly unique to each group
all_moon_naks = defaultdict(lambda: defaultdict(int))
all_ex = defaultdict(lambda: defaultdict(int))
all_conj = defaultdict(lambda: defaultdict(int))

for group_name, charts in group_data.items():
    n = len(charts)
    for c in charts:
        all_moon_naks[group_name][c['planets']['Moon']['nakshatra']] += 1
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pn in c['planets'] and c['planets'][pn]['dignity'] == 100:
                all_ex[group_name][pn] += 1
        for conj in c['conjunctions']:
            all_conj[group_name][conj] += 1

print(f"\n{'Group':<22} {'Unique Signature (>3x any other group)'}")
print("-"*70)

for group_name, charts in sorted(group_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 4: continue
    n = len(charts)
    signatures = []
    
    # Check moon nakshatras
    for nak in all_moon_naks[group_name]:
        our_rate = all_moon_naks[group_name][nak] / n
        other_rates = [all_moon_naks[g][nak] / max(len(group_data[g]),1) 
                       for g in group_data if g != group_name and len(group_data[g]) >= 4]
        max_other = max(other_rates) if other_rates else 0
        if max_other > 0 and our_rate / max_other > 3:
            signatures.append(f"Moon {nak} ({our_rate*100:.0f}% vs {max_other*100:.0f}%)")
    
    # Check conjunctions
    for conj in all_conj[group_name]:
        our_rate = all_conj[group_name][conj] / n
        other_rates = [all_conj[g][conj] / max(len(group_data[g]),1)
                       for g in group_data if g != group_name and len(group_data[g]) >= 4]
        max_other = max(other_rates) if other_rates else 0
        if max_other > 0 and our_rate / max_other > 3 and our_rate > 0.2:
            signatures.append(f"{conj} conj ({our_rate*100:.0f}% vs {max_other*100:.0f}%)")
    
    if signatures:
        print(f"  {group_name:<22} {signatures[0]}")
        for sig in signatures[1:]:
            print(f"  {'':<22} {sig}")
    else:
        print(f"  {group_name:<22} (no unique signature at planet level)")

# Save
output = {g: [{"name": c['name'], "moon_nak": c['planets']['Moon']['nakshatra'],
               "moon_sign": c['planets']['Moon']['sign'],
               "rahu_sign": c['planets']['Rahu']['sign']} for c in charts]
          for g, charts in group_data.items()}
with open('dataset/mega_cross_reference.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved → dataset/mega_cross_reference.json")
