#!/usr/bin/env python3
"""
P1-P9 FULL DATABASE CROSS-REFERENCE + NEW CHART INGESTION
Find which historical figures share closest planet-sign configs with each P-chart
"""
import swisseph as swe, json, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
VIM = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l
    return "Revati","Mercury"

def get_tz(p):
    if any(w in p for w in ['India','Calcutta','Bombay','Delhi','Madras','Mumbai','Hyderabad','Allahabad','British India','Punjab','Gujarat','Haryana','Tamil','Rajasthan','Maharashtra','Mewar','Maratha']): return 5.5
    if any(w in p for w in ['China','Taiwan','Shanghai','Guangdong','Beijing','Ming','Qing','Han','Tang','Song','Yuan','Sui']): return 8
    if any(w in p for w in ['Japan','Tokyo','Osaka','Edo','Kyoto']): return 9
    if any(w in p for w in ['UK','England','Scotland','Wales','Ireland','London','Oxford','Edinburgh','Bristol','Liverpool','Manchester','York','Norfolk','Essex','Devon','Sussex','Kent','Surrey','Hampshire','Berkshire','Wiltshire','Somerset','Dorset','Cornwall','Lancashire','Yorkshire','Northumberland','Cumberland','Westmorland','Durham','Nottingham','Derby','Stafford','Shropshire','Worcester','Hereford','Gloucester','Buckingham','Bedford','Huntingdon','Cambridge','Suffolk','Hertford','Lincoln','Cheshire','Monmouth','Glamorgan','Pembroke','Kingdom of England','Kingdom of Great Britain','Kingdom of Scotland','Kingdom of Ireland','British','Great Britain','Portsmouth']): return 0
    if any(w in p for w in ['Germany','France','Italy','Spain','Norway','Denmark','Sweden','Austria','Switzerland','Poland','Netherlands','Belgium','Czech','Hungary','Prussia','Saxony','Bavaria','Holy Roman','Austria-Hungary','Venice','Florence','Genoa','Papal','Tuscany','Lombardy','Piedmont','Milan','Naples','Sicily','Sardinia','Corsica','Normandy','Brittany','Aquitaine','Burgundy','Provence','Savoy','Alsace','Lorraine','Wurttemberg','Baden','Hesse','Hanover','Brunswick','Oldenburg','Mecklenburg','Pomerania','Silesia','Bohemia','Moravia','Slovakia','Slovenia','Galicia','Bukovina','Transylvania','Wallachia','Moldavia','Banat','Croatia','Dalmatia','Bosnia','Herzegovina','Montenegro','Serbia','Bulgaria','Albania','Macedonia','Thrace','Epirus','Thessaly','Peloponnese','Crete','Cyprus','Malta','Gibraltar','Luxembourg','Liechtenstein','Andorra','Monaco','San Marino','Vatican']): return 1
    if any(w in p for w in ['Russia','Moscow','Soviet','Ukraine','Belarus','Latvia','Lithuania','Estonia','Finland','Tsardom','Russian Empire','Russian SFSR','Kievan','Novgorod']): return 3
    if any(w in p for w in ['Brazil','Rio','São Paulo']): return -3
    if any(w in p for w in ['Argentina','Buenos']): return -3
    if any(w in p for w in ['Mexico','Guadalajara','Coyoacán']): return -6
    if any(w in p for w in ['South Africa','Pretoria','Johannesburg']): return 2
    if any(w in p for w in ['Canada','Ontario','Quebec','Toronto','Montreal','Vancouver']): return -5
    if any(w in p for w in ['Australia','Sydney','Melbourne','Adelaide']): return 10
    if any(w in p for w in ['New Zealand','Auckland']): return 12
    if any(w in p for w in ['Greenland','Iceland']): return 0
    if any(w in p for w in ['Iran','Tehran','Persia','Isfahan']): return 3.5
    if any(w in p for w in ['Turkey','Istanbul','Ottoman','Constantinople']): return 3
    if any(w in p for w in ['Greece','Athens']): return 2
    if any(w in p for w in ['Portugal','Lisbon']): return -1
    if any(w in p for w in ['Iraq','Baghdad','Babylon']): return 3
    if any(w in p for w in ['Pakistan','Karachi']): return 5
    if any(w in p for w in ['Morocco','Tangier']): return 0
    if any(w in p for w in ['Saudi Arabia','Riyadh','Mecca','Arabia']): return 3
    if any(w in p for w in ['Egypt','Cairo','Alexandria']): return 2
    return -5

def compute_noon(name, bday, place):
    try:
        parts = bday.split('-')
        y,m,d = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y,m,d,12,0,0)
        dt = dt.replace(tzinfo=timezone(timedelta(hours=get_tz(place))))
        dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
        ayan = swe.get_ayanamsa(jd)
        p = {}
        for pn, pid in PLANETS_MAP.items():
            lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
            sid = (lt-ayan)%360
            sgn = SIGNS[int(sid//30)]
            nk, nl = gn(sid)
            dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
            p[pn] = {"sign":sgn,"nakshatra":nk,"dignity":dig}
        rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360
        p["Rahu"] = {"sign":SIGNS[int(rh//30)],"nakshatra":gn(rh)[0],"dignity":0}
        p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"nakshatra":gn((rh+180)%360)[0],"dignity":0}
        return {"name":name,"planets":p}
    except:
        return None

# ============================================================
# P1-P9 BIRTH DATA
# ============================================================
P_CHARTS = [
    {"id":"P1","name":"Polgahawela Bappa","birthday":"1962-05-27","birth_time":"03:38:54","lat":7.3381,"lon":80.3003,"tz":5.5},
    {"id":"P2","name":"Upulakshi","birthday":"1997-03-14","birth_time":"12:00:00","lat":6.9355,"lon":79.8487,"tz":5.5,"note":"PLACEHOLDER TOB"},
    {"id":"P3","name":"Senith","birthday":"1995-08-07","birth_time":"21:18:00","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P4","name":"Niromi","birthday":"1967-04-25","birth_time":"08:17:37","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P5","name":"Senath","birthday":"2001-05-14","birth_time":"16:08:40","lat":6.9355,"lon":79.8487,"tz":5.5},
    {"id":"P6","name":"Dewli","birthday":"2005-10-08","birth_time":"08:22:00","lat":6.9097,"lon":79.8900,"tz":5.5},
    {"id":"P7","name":"Sineth","birthday":"2005-04-05","birth_time":"16:05:48","lat":6.9271,"lon":79.8612,"tz":5.5,"note":"Lagna TBD"},
    {"id":"P8","name":"Lakshi Amma","birthday":"1963-11-16","birth_time":"09:04:15","lat":7.486,"lon":80.362,"tz":5.5},
    {"id":"P9","name":"Lalith Uncle","birthday":"1970-08-31","birth_time":"21:55:30","lat":7.2931,"lon":80.635,"tz":5.5},
]

# Compute P-charts with real birth times
def compute_p1p9():
    results = []
    for c in P_CHARTS:
        dt = datetime.strptime(f"{c['birthday']}T{c['birth_time']}", "%Y-%m-%dT%H:%M:%S")
        dt = dt.replace(tzinfo=timezone(timedelta(hours=c['tz'])))
        dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
        ayan = swe.get_ayanamsa(jd)
        p = {}
        for pn, pid in PLANETS_MAP.items():
            lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
            sid = (lt-ayan)%360
            sgn = SIGNS[int(sid//30)]
            nk, nl = gn(sid)
            dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
            p[pn] = {"sign":sgn,"nakshatra":nk,"dignity":dig}
        rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360
        p["Rahu"] = {"sign":SIGNS[int(rh//30)],"nakshatra":gn(rh)[0],"dignity":0}
        p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"nakshatra":gn((rh+180)%360)[0],"dignity":0}
        results.append({"id":c['id'],"name":c['name'],"planets":p,"note":c.get('note','')})
    return results

# ============================================================
# NEW FILM/ACTOR CHARTS
# ============================================================
NEW_FILM = [
    # Film pioneers
    ("Auguste Lumiere","1862-10-19","Besancon, France"),
    ("Louis Lumiere","1864-10-05","Besancon, France"),
    ("Georges Melies","1861-12-08","Paris, France"),
    ("Alice Guy-Blache","1873-07-01","Saint-Mande, France"),
    ("Eadweard Muybridge","1830-04-09","Kingston upon Thames, England, UK"),
    ("D. W. Griffith","1875-01-22","Crestwood, Kentucky, USA"),
    ("Charlie Chaplin","1889-04-16","London, England, UK"),
    ("Buster Keaton","1895-10-04","Piqua, Kansas, USA"),
    ("Harold Lloyd","1893-04-20","Burchard, Nebraska, USA"),
    ("Mary Pickford","1892-04-08","Toronto, Ontario, Canada"),
    ("Douglas Fairbanks","1883-05-23","Denver, Colorado, USA"),
    ("Rudolph Valentino","1895-05-06","Castellaneta, Kingdom of Italy"),
    ("Lillian Gish","1893-10-14","Springfield, Ohio, USA"),
    ("Lon Chaney","1883-04-01","Colorado Springs, Colorado, USA"),
    ("Sergei Eisenstein","1898-01-23","Riga, Russian Empire"),
    ("Dziga Vertov","1896-01-02","Bialystok, Russian Empire"),
    ("F. W. Murnau","1888-12-28","Bielefeld, German Empire"),
    ("Fritz Lang","1890-12-05","Vienna, Austria-Hungary"),
    ("Carl Theodor Dreyer","1889-02-03","Copenhagen, Denmark"),
    ("Jean Renoir","1894-09-15","Paris, France"),
    # Directors
    ("Alfred Hitchcock","1899-08-13","London, England, UK"),
    ("Orson Welles","1915-05-06","Kenosha, Wisconsin, USA"),
    ("Akira Kurosawa","1910-03-23","Tokyo, Japan"),
    ("Yasujiro Ozu","1903-12-12","Tokyo, Japan"),
    ("Kenji Mizoguchi","1898-05-16","Tokyo, Japan"),
    ("Federico Fellini","1920-01-20","Rimini, Kingdom of Italy"),
    ("Ingmar Bergman","1918-07-14","Uppsala, Sweden"),
    ("Stanley Kubrick","1928-07-26","New York City, New York, USA"),
    ("Satyajit Ray","1921-05-02","Calcutta, British India"),
    ("Andrei Tarkovsky","1932-04-04","Zavrazhye, Russian SFSR, Soviet Union"),
    ("Jean-Luc Godard","1930-12-03","Paris, France"),
    ("Francois Truffaut","1932-02-06","Paris, France"),
    ("Michelangelo Antonioni","1912-09-29","Ferrara, Kingdom of Italy"),
    ("Luchino Visconti","1906-11-02","Milan, Kingdom of Italy"),
    ("Roberto Rossellini","1906-05-08","Rome, Kingdom of Italy"),
    ("Luis Bunuel","1900-02-22","Calanda, Spain"),
    ("Billy Wilder","1906-06-22","Sucha Beskidzka, Austria-Hungary"),
    ("Frank Capra","1897-05-18","Bisacquino, Sicily, Kingdom of Italy"),
    ("John Ford","1894-02-01","Cape Elizabeth, Maine, USA"),
    ("Howard Hawks","1896-05-30","Goshen, Indiana, USA"),
    ("Ernst Lubitsch","1892-01-28","Berlin, German Empire"),
    ("William Wyler","1902-07-01","Mulhausen, Alsace-Lorraine, German Empire"),
    ("Vittorio De Sica","1901-07-07","Sora, Kingdom of Italy"),
    ("Sergio Leone","1929-01-03","Rome, Kingdom of Italy"),
    ("Steven Spielberg","1946-12-18","Cincinnati, Ohio, USA"),
    ("Martin Scorsese","1942-11-17","Queens, New York City, New York, USA"),
    ("Francis Ford Coppola","1939-04-07","Detroit, Michigan, USA"),
    ("George Lucas","1944-05-14","Modesto, California, USA"),
    ("Ridley Scott","1937-11-30","South Shields, England, UK"),
    ("David Lynch","1946-01-20","Missoula, Montana, USA"),
    ("Hayao Miyazaki","1941-01-05","Tokyo, Japan"),
    ("Agnes Varda","1928-05-30","Ixelles, Belgium"),
    ("Chantal Akerman","1950-06-06","Brussels, Belgium"),
    ("Abbas Kiarostami","1940-06-22","Tehran, Iran"),
    ("Pedro Almodovar","1949-09-25","Calzada de Calatrava, Spain"),
    ("Krzysztof Kieslowski","1941-06-27","Warsaw, Poland"),
    # Stage & Golden Age actors
    ("Sarah Bernhardt","1844-10-22","Paris, France"),
    ("Eleonora Duse","1858-10-03","Vigevano, Kingdom of Lombardy-Venetia"),
    ("Laurence Olivier","1907-05-22","Dorking, Surrey, England, UK"),
    ("John Gielgud","1904-04-14","London, England, UK"),
    ("Humphrey Bogart","1899-12-25","New York City, New York, USA"),
    ("Marlon Brando","1924-04-03","Omaha, Nebraska, USA"),
    ("James Dean","1931-02-08","Marion, Indiana, USA"),
    ("Katharine Hepburn","1907-05-12","Hartford, Connecticut, USA"),
    ("Audrey Hepburn","1929-05-04","Ixelles, Brussels, Belgium"),
    ("Marilyn Monroe","1926-06-01","Los Angeles, California, USA"),
    ("Bette Davis","1908-04-05","Lowell, Massachusetts, USA"),
    ("Ingrid Bergman","1915-08-29","Stockholm, Sweden"),
    ("Greta Garbo","1905-09-18","Stockholm, Sweden"),
    ("Spencer Tracy","1900-04-05","Milwaukee, Wisconsin, USA"),
    ("Cary Grant","1904-01-18","Bristol, England, UK"),
    ("Clark Gable","1901-02-01","Cadiz, Ohio, USA"),
    ("James Stewart","1908-05-20","Indiana, Pennsylvania, USA"),
    ("Elizabeth Taylor","1932-02-27","London, England, UK"),
    ("Sophia Loren","1934-09-20","Rome, Kingdom of Italy"),
    ("Marcello Mastroianni","1924-09-28","Fontana Liri, Kingdom of Italy"),
    ("Toshiro Mifune","1920-04-01","Qingdao, China"),
    ("Takashi Shimura","1905-03-12","Ikuno, Hyogo, Japan"),
    ("Gene Kelly","1912-08-23","Pittsburgh, Pennsylvania, USA"),
    ("Fred Astaire","1899-05-10","Omaha, Nebraska, USA"),
    ("Judy Garland","1922-06-10","Grand Rapids, Minnesota, USA"),
    ("Joan Crawford","1906-03-23","San Antonio, Texas, USA"),
    ("Jack Nicholson","1937-04-22","Neptune City, New Jersey, USA"),
    ("Robert De Niro","1943-08-17","New York City, New York, USA"),
    ("Al Pacino","1940-04-25","New York City, New York, USA"),
    ("Meryl Streep","1949-06-22","Summit, New Jersey, USA"),
    ("Daniel Day-Lewis","1957-04-29","London, England, UK"),
    ("Sidney Poitier","1927-02-20","Miami, Florida, USA"),
    ("Cantinflas","1911-08-12","Mexico City, Mexico"),
    ("Jean Gabin","1904-05-17","Paris, France"),
    ("Alain Delon","1935-11-08","Sceaux, France"),
    ("Jean-Paul Belmondo","1933-04-09","Neuilly-sur-Seine, France"),
    ("Catherine Deneuve","1943-10-22","Paris, France"),
    ("Brigitte Bardot","1934-09-28","Paris, France"),
    ("Max von Sydow","1929-04-10","Lund, Sweden"),
    ("Liv Ullmann","1938-12-16","Tokyo, Japan"),
    ("Anna Magnani","1908-03-07","Rome, Kingdom of Italy"),
    ("Soumitra Chatterjee","1935-01-19","Calcutta, British India"),
    ("Uttam Kumar","1926-09-03","Calcutta, British India"),
    ("Amitabh Bachchan","1942-10-11","Allahabad, British India"),
]

# ============================================================
# MAIN
# ============================================================
print("="*80)
print("P1-P9 FULL DATABASE CROSS-REFERENCE + NEW CHARTS")
print("="*80)

# Compute P1-P9
p_charts = compute_p1p9()
print(f"P1-P9 computed: {len(p_charts)}")

# Compute new film charts
print(f"Computing {len(NEW_FILM)} film/actor charts...")
film_charts = []
for name, bday, place in NEW_FILM:
    c = compute_noon(name, bday, place)
    if c: film_charts.append(c)

print(f"Computed: {len(film_charts)}")

# Load existing database
import os, glob
import os, glob
all_db = []
data_dir = '/home/user/dataset'
for fn in ['nexus_v4_benchmark.json']:
    path = os.path.join(data_dir, fn)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            for r in data:
                if 'planets' in r or 'name' in r:
                    all_db.append(r)

# Also add film charts to the comparison pool
comparison_pool = []
for c in all_db:
    name = c.get('name','')
    planets = c.get('planets',{})
    if planets and name:
        comparison_pool.append({'name':name,'planets':planets})

for c in film_charts:
    comparison_pool.append(c)

print(f"Comparison pool: {len(comparison_pool)} charts")

# ============================================================
# PLANET-SIGN SIMILARITY
# ============================================================
def planet_sign_similarity(p1_planets, p2_planets):
    """Count how many of 7 classical planets share the same sign"""
    matches = 0
    for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        s1 = p1_planets.get(pn,{}).get('sign')
        s2 = p2_planets.get(pn,{}).get('sign') if isinstance(p2_planets.get(pn),dict) else p2_planets.get(pn,{}).get('sign') if isinstance(p2_planets.get(pn,{}),dict) else None
        # Handle both dict and string planets
        if isinstance(p2_planets.get(pn), dict):
            s2 = p2_planets[pn].get('sign')
        elif isinstance(p2_planets.get(pn), str):
            s2 = p2_planets[pn]
        else:
            s2 = None
        if s1 and s2 and s1 == s2:
            matches += 1
    return matches

print(f"\n{'='*80}")
print("TOP 5 HISTORICAL MATCHES FOR EACH P-CHART (planet-sign similarity)")
print(f"{'='*80}")

for pc in p_charts:
    pid = pc['id']; pname = pc['name']
    pp = pc['planets']
    
    # Show P-chart planet signs
    p_sigs = {pn: pp[pn]['sign'] for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']}
    
    # Compare against all
    matches = []
    for c in comparison_pool:
        cname = c.get('name','?')
        if cname == pname: continue
        sim = planet_sign_similarity(pp, c.get('planets',{}))
        if sim >= 3:
            matches.append((cname, sim))
    
    matches.sort(key=lambda x: -x[1])
    top5 = matches[:5]
    
    tier = "(REF ONLY)" if pc.get('note') else ""
    print(f"\n{pid} {pname} {tier}")
    print(f"  Signs: Sun:{p_sigs['Sun']} | Moon:{p_sigs['Moon']} | Mars:{p_sigs['Mars']} | Mer:{p_sigs['Mercury']} | Jup:{p_sigs['Jupiter']} | Ven:{p_sigs['Venus']} | Sat:{p_sigs['Saturn']}")
    print(f"  Top matches (≥3 matching signs):")
    for name, sim in top5:
        print(f"    {name:<35} {sim}/7 matching signs")

# ============================================================
# GROUP FILM CHARTS
# ============================================================
print(f"\n{'='*80}")
print("FILM/ACTOR DATASET — Moon Nakshatra Distribution")
print(f"{'='*80}")

moon_naks = Counter()
for c in film_charts:
    moon = c['planets'].get('Moon',{})
    nak = moon.get('nakshatra','?')
    moon_naks[nak] += 1

print(f"\n{len(film_charts)} film/actor charts:")
for nak, count in moon_naks.most_common(15):
    pct = count/len(film_charts)*100
    bar = '█' * int(pct)
    print(f"  {nak:<20} {count:>3} ({pct:>5.1f}%) {bar}")

# Save
film_out = [{"name":c['name'],"moon_nak":c['planets']['Moon']['nakshatra'],"moon_sign":c['planets']['Moon']['sign']} for c in film_charts]
with open('/home/user/dataset/film_actor_dataset.json','w') as f:
    json.dump(film_out, f, indent=2)
print(f"\nSaved → /home/user/dataset/film_actor_dataset.json")
