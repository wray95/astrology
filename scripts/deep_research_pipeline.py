#!/usr/bin/env python3
"""
DEEP RESEARCH PIPELINE: ~300 new charts × 15 groups
— Cross-reference, transit analysis, AI-driven pattern discovery
"""
import swisseph as swe, json, math
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]
NAK_SPAN = 360.0/27

TZ_MAP = {}
def get_tz(p):
    if any(w in p for w in ['India','Calcutta','Bombay','Delhi','Madras','Mumbai','Hyderabad','Allahabad','Punjab','Gujarat','Haryana','Tamil','Rajasthan','Karnal','British India']): return 5.5
    if any(w in p for w in ['China','Taiwan','Shanghai','Guangdong','Ming','Beijing','Nanjing']): return 8
    if any(w in p for w in ['Japan','Tokyo','Osaka','Edo']): return 9
    if any(w in p for w in ['Korea','Seoul','Joseon']): return 9
    if any(w in p for w in ['UK','England','Scotland','Wales','Ireland','London','Oxford','Edinburgh','Bristol','Norfolk','Essex','Devon','York','Hertfordshire','British','Kingdom of England']): return 0
    if any(w in p for w in ['Germany','France','Italy','Spain','Norway','Denmark','Sweden','Austria','Switzerland','Poland','Netherlands','Belgium','Czech','Hungary','Prussia','Saxony','Bavaria','Holy Roman','Austria-Hungary','Venice','Florence','Genoa','Papal','Tuscany','Lombardy','Piedmont','Milan','Naples','Sicily','Sardinia','Corsica']): return 1
    if any(w in p for w in ['Russia','Moscow','Soviet','Ukraine','Belarus','Latvia','Lithuania','Estonia','Finland','Grand Duchy','Tsardom','Russian Empire','Russian SFSR']): return 3
    if 'Brazil' in p or 'Rio' in p or 'São Paulo' in p: return -3
    if 'Argentina' in p or 'Buenos' in p: return -3
    if 'Venezuela' in p or 'Caracas' in p: return -4
    if 'Chile' in p: return -4
    if 'Mexico' in p or 'Guadalajara' in p or 'Coyoacán' in p: return -6
    if 'Colombia' in p: return -5
    if 'Peru' in p: return -5
    if 'South Africa' in p or 'Pretoria' in p or 'Johannesburg' in p: return 2
    if 'Kenya' in p or 'Nairobi' in p or 'Nyeri' in p: return 3
    if 'Pakistan' in p or 'Karachi' in p or 'Mingora' in p: return 5
    if 'Jamaica' in p: return -5
    if 'Canada' in p or 'Ontario' in p or 'Quebec' in p or 'Toronto' in p: return -5
    if 'Australia' in p or 'Sydney' in p or 'Cootamundra' in p: return 10
    if 'New Zealand' in p or 'Auckland' in p: return 12
    if 'Nepal' in p: return 5.75
    if 'Burma' in p or 'Rangoon' in p: return 6.5
    if 'Ghana' in p or 'Gold Coast' in p: return 0
    if 'Ethiopia' in p: return 3
    if 'Mongol' in p or 'Mongolia' in p: return 8
    if 'Arabia' in p or 'Mecca' in p or 'Abbasid' in p or 'Iraq' in p or 'Baghdad' in p: return 3
    if 'Seljuk' in p or 'Khwarazm' in p: return 4
    if 'Ottoman' in p or 'Skopje' in p: return 2
    if 'Carthage' in p: return 1
    if 'Macedon' in p or 'Greece' in p or 'Salonica' in p: return 2
    if 'Portugal' in p or 'Lisbon' in p or 'Madeira' in p: return 0
    if 'Romania' in p: return 2
    if 'Serbia' in p or 'Belgrade' in p: return 1
    if 'Morocco' in p or 'Tangier' in p: return 0
    if 'Greenland' in p: return -3
    if 'Cuba' in p: return -5
    if 'Philippines' in p: return 8
    if 'Vietnam' in p or 'Indochina' in p: return 7
    if 'Denmark' in p or 'Copenhagen' in p: return 1
    if 'Turkey' in p or 'Istanbul' in p: return 3
    return -5

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+NAK_SPAN: return n,l
    return "Revati","Mercury"

def compute_chart(name, bday, place):
    try:
        ymd = bday.split('-')
        y, m, d = int(ymd[0]), int(ymd[1]), int(ymd[2])
        dt = datetime(y, m, d, 12, 0, 0)
        tz = timezone(timedelta(hours=get_tz(place)))
        dt = dt.replace(tzinfo=tz)
        dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
        ayan = swe.get_ayanamsa(jd)
        p = {}
        for pn, pid in PLANETS.items():
            lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
            sid = (lt - ayan) % 360
            sgn = SIGNS[int(sid//30)]
            nk, nl = gn(sid)
            dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
            p[pn] = {"sign":sgn,"nakshatra":nk,"dignity":dig,"sidereal":round(sid,2)}
        rh, _ = swe.calc_ut(jd, swe.MEAN_NODE)
        rh = (rh[0]-ayan)%360
        p["Rahu"] = {"sign":SIGNS[int(rh//30)],"nakshatra":gn(rh)[0],"dignity":0}
        p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"nakshatra":gn((rh+180)%360)[0],"dignity":0}
        conj = []
        pl = list(p.keys())
        for i in range(len(pl)):
            for j in range(i+1,len(pl)):
                if p[pl[i]]['sign'] == p[pl[j]]['sign']:
                    conj.append(f"{pl[i]}+{pl[j]}")
        return {"name":name,"planets":p,"conjunctions":conj,"birth_year":y}
    except Exception as e:
        return None

# ============================================================
# NEW GROUPS
# ============================================================
NEW_GROUPS = {
    "Architect": [
        ("Frank Lloyd Wright","1867-06-08","Richland Center, Wisconsin, USA"),
        ("Antoni Gaudi","1852-06-25","Reus, Spain"),
        ("Zaha Hadid","1950-10-31","Baghdad, Iraq"),
        ("Le Corbusier","1887-10-06","La Chaux-de-Fonds, Switzerland"),
        ("I. M. Pei","1917-04-26","Guangzhou, Republic of China"),
        ("Oscar Niemeyer","1907-12-15","Rio de Janeiro, Brazil"),
        ("Frank Gehry","1929-02-28","Toronto, Ontario, Canada"),
        ("Norman Foster","1935-06-01","Stockport, England, UK"),
        ("Renzo Piano","1937-09-14","Genoa, Italy"),
        ("Rem Koolhaas","1944-11-17","Rotterdam, Netherlands"),
        ("Tadao Ando","1941-09-13","Osaka, Japan"),
        ("Maya Lin","1959-10-05","Athens, Ohio, USA"),
        ("Louis Sullivan","1856-09-03","Boston, Massachusetts, USA"),
    ],
    "Tech Founder": [
        ("Bill Gates","1955-10-28","Seattle, Washington, USA"),
        ("Steve Jobs","1955-02-24","San Francisco, California, USA"),
        ("Steve Wozniak","1950-08-11","San Jose, California, USA"),
        ("Tim Berners-Lee","1955-06-08","London, England, UK"),
        ("Linus Torvalds","1969-12-28","Helsinki, Finland"),
        ("Mark Zuckerberg","1984-05-14","White Plains, New York, USA"),
        ("Larry Page","1973-03-26","Lansing, Michigan, USA"),
        ("Sergey Brin","1973-08-21","Moscow, Russian SFSR, Soviet Union"),
        ("Elon Musk","1971-06-28","Pretoria, South Africa"),
        ("Jeff Bezos","1964-01-12","Albuquerque, New Mexico, USA"),
        ("Gordon Moore","1929-01-03","San Francisco, California, USA"),
        ("Marc Andreessen","1971-07-09","Cedar Falls, Iowa, USA"),
        ("Jensen Huang","1963-02-17","Tainan, Taiwan"),
        ("Satya Nadella","1967-08-19","Hyderabad, India"),
        ("Sundar Pichai","1972-06-10","Madurai, Tamil Nadu, India"),
    ],
    "Film Director": [
        ("Alfred Hitchcock","1899-08-13","Leytonstone, Essex, England, UK"),
        ("Steven Spielberg","1946-12-18","Cincinnati, Ohio, USA"),
        ("Stanley Kubrick","1928-07-26","Manhattan, New York, USA"),
        ("Akira Kurosawa","1910-03-23","Tokyo, Japan"),
        ("Martin Scorsese","1942-11-17","Queens, New York, USA"),
        ("Christopher Nolan","1970-07-30","London, England, UK"),
        ("Quentin Tarantino","1963-03-27","Knoxville, Tennessee, USA"),
        ("Federico Fellini","1920-01-20","Rimini, Italy"),
        ("Ingmar Bergman","1918-07-14","Uppsala, Sweden"),
        ("Francis Ford Coppola","1939-04-07","Detroit, Michigan, USA"),
        ("Orson Welles","1915-05-06","Kenosha, Wisconsin, USA"),
        ("Charlie Chaplin","1889-04-16","London, England, UK"),
        ("Hayao Miyazaki","1941-01-05","Tokyo, Japan"),
        ("Satyajit Ray","1921-05-02","Calcutta, British India"),
        ("James Cameron","1954-08-16","Kapuskasing, Ontario, Canada"),
        ("George Lucas","1944-05-14","Modesto, California, USA"),
        ("David Lynch","1946-01-20","Missoula, Montana, USA"),
        ("Ridley Scott","1937-11-30","South Shields, England, UK"),
    ],
    "Military Commander": [
        ("Alexander the Great","-0356-07-20","Pella, Macedon"),
        ("Julius Caesar","-0100-07-12","Rome, Roman Republic"),
        ("Genghis Khan","1162-05-31","Deluun Boldog, Mongol Empire"),
        ("Hannibal Barca","-0247-01-01","Carthage"),
        ("Saladin","1137-01-01","Tikrit, Abbasid Caliphate"),
        ("Erwin Rommel","1891-11-15","Heidenheim, German Empire"),
        ("George S. Patton","1885-11-11","San Gabriel, California, USA"),
        ("Horatio Nelson","1758-09-29","Burnham Thorpe, Norfolk, England, UK"),
        ("Vo Nguyen Giap","1911-08-25","Loc Thuy, French Indochina"),
    ],
    "Composer": [
        ("Ludwig van Beethoven","1770-12-17","Bonn, Electorate of Cologne"),
        ("Wolfgang Amadeus Mozart","1756-01-27","Salzburg, Archbishopric of Salzburg"),
        ("Johann Sebastian Bach","1685-03-31","Eisenach, Saxe-Eisenach"),
        ("Frederic Chopin","1810-03-01","Zelazowa Wola, Duchy of Warsaw"),
        ("Pyotr Ilyich Tchaikovsky","1840-05-07","Votkinsk, Russian Empire"),
        ("Franz Schubert","1797-01-31","Himmelpfortgrund, Archduchy of Austria"),
        ("Johannes Brahms","1833-05-07","Hamburg, German Confederation"),
        ("Antonio Vivaldi","1678-03-04","Venice, Republic of Venice"),
        ("Giuseppe Verdi","1813-10-10","Le Roncole, First French Empire"),
        ("Richard Wagner","1813-05-22","Leipzig, Kingdom of Saxony"),
        ("Claude Debussy","1862-08-22","Saint-Germain-en-Laye, France"),
        ("Igor Stravinsky","1882-06-17","Oranienbaum, Russian Empire"),
        ("Sergei Rachmaninoff","1873-04-01","Semyonovo, Russian Empire"),
        ("Giacomo Puccini","1858-12-22","Lucca, Grand Duchy of Tuscany"),
    ],
    "Athlete": [
        ("Muhammad Ali","1942-01-17","Louisville, Kentucky, USA"),
        ("Michael Jordan","1963-02-17","Brooklyn, New York, USA"),
        ("Pele","1940-10-23","Tres Coracoes, Minas Gerais, Brazil"),
        ("Diego Maradona","1960-10-30","Lanus, Buenos Aires, Argentina"),
        ("Lionel Messi","1987-06-24","Rosario, Santa Fe, Argentina"),
        ("Cristiano Ronaldo","1985-02-05","Funchal, Madeira, Portugal"),
        ("Usain Bolt","1986-08-21","Sherwood Content, Jamaica"),
        ("Serena Williams","1981-09-26","Saginaw, Michigan, USA"),
        ("Roger Federer","1981-08-08","Basel, Switzerland"),
        ("Michael Phelps","1985-06-30","Baltimore, Maryland, USA"),
        ("Tom Brady","1977-08-03","San Mateo, California, USA"),
        ("LeBron James","1984-12-30","Akron, Ohio, USA"),
        ("Tiger Woods","1975-12-30","Cypress, California, USA"),
        ("Lewis Hamilton","1985-01-07","Stevenage, Hertfordshire, England, UK"),
    ],
    "Artist": [
        ("Leonardo da Vinci","1452-04-15","Vinci, Republic of Florence"),
        ("Michelangelo","1475-03-06","Caprese, Republic of Florence"),
        ("Vincent van Gogh","1853-03-30","Zundert, Netherlands"),
        ("Pablo Picasso","1881-10-25","Malaga, Spain"),
        ("Claude Monet","1840-11-14","Paris, France"),
        ("Salvador Dali","1904-05-11","Figueres, Spain"),
        ("Frida Kahlo","1907-07-06","Coyoacan, Mexico"),
        ("Andy Warhol","1928-08-06","Pittsburgh, Pennsylvania, USA"),
        ("Jackson Pollock","1912-01-28","Cody, Wyoming, USA"),
        ("Rembrandt van Rijn","1606-07-15","Leiden, Dutch Republic"),
        ("Gustav Klimt","1862-07-14","Baumgarten, Austrian Empire"),
        ("Edvard Munch","1863-12-12","Loten, Norway"),
        ("Banksy","1974-07-28","Bristol, England, UK"),
    ],
    "Explorer": [
        ("Christopher Columbus","1451-10-31","Genoa, Republic of Genoa"),
        ("Ferdinand Magellan","1480-02-04","Sabrosa, Kingdom of Portugal"),
        ("Marco Polo","1254-09-15","Venice, Republic of Venice"),
        ("James Cook","1728-11-07","Marton, Yorkshire, England, UK"),
        ("Roald Amundsen","1872-07-16","Borge, Ostfold, Norway"),
        ("Ernest Shackleton","1874-02-15","Kilkea, County Kildare, Ireland"),
        ("Edmund Hillary","1919-07-20","Auckland, New Zealand"),
        ("Jacques Cousteau","1910-06-11","Saint-Andre-de-Cubzac, France"),
    ],
    "Polymath/Nobel": [
        ("Benjamin Franklin","1706-01-17","Boston, Massachusetts Bay"),
        ("Marie Curie","1867-11-07","Warsaw, Russian Empire"),
        ("Richard Feynman","1918-05-11","Queens, New York, USA"),
        ("Blaise Pascal","1623-06-19","Clermont-Ferrand, France"),
        ("Rabindranath Tagore","1861-05-07","Calcutta, British India"),
        ("Martin Luther King Jr.","1929-01-15","Atlanta, Georgia, USA"),
        ("Nelson Mandela","1918-07-18","Mvezo, Union of South Africa"),
        ("Mother Teresa","1910-08-26","Skopje, Ottoman Empire"),
        ("Niels Bohr","1885-10-07","Copenhagen, Denmark"),
        ("Max Planck","1858-04-23","Kiel, Duchy of Holstein"),
        ("Linus Pauling","1901-02-28","Portland, Oregon, USA"),
        ("Gabriel Garcia Marquez","1927-03-06","Aracataca, Colombia"),
        ("Toni Morrison","1931-02-18","Lorain, Ohio, USA"),
        ("John von Neumann","1903-12-28","Budapest, Austria-Hungary"),
    ],
}

print("="*100)
print("DEEP RESEARCH PIPELINE: Computing + Analyzing ~200 New Charts")
print("="*100)

total_new = sum(len(v) for v in NEW_GROUPS.values())
print(f"Groups: {len(NEW_GROUPS)} | Charts: {total_new}\n")

all_data = {}
for gname, members in NEW_GROUPS.items():
    charts = []
    for name, bday, place in members:
        c = compute_chart(name, bday, place)
        if c: charts.append(c)
    all_data[gname] = charts
    print(f"  {gname:<25} {len(charts):>3}/{len(members)} computed")

total = sum(len(v) for v in all_data.values())
print(f"\nTotal computed: {total}")

# ============================================================
# DEEP STATISTICAL ANALYSIS
# ============================================================
print(f"\n{'='*100}")
print("CROSS-GROUP STATISTICAL ANALYSIS")
print(f"{'='*100}")

# 1. Moon Nakshatra by group
print(f"\n--- MOON NAKSHATRA SIGNATURES ---")
print(f"{'Group':<22} {'N':>3}  {'Top Moon Nakshatras'}")
print("-"*70)
for gname, charts in sorted(all_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    moon_naks = Counter(c['planets']['Moon']['nakshatra'] for c in charts)
    top = [f"{n}({c/len(charts)*100:.0f}%)" for n,c in moon_naks.most_common(4)]
    print(f"{gname:<22} {len(charts):>3}  {', '.join(top)}")

# 2. Dignity patterns
print(f"\n--- DIGNITY PATTERNS ---")
for gname, charts in sorted(all_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    ex = Counter(); deb = Counter()
    for c in charts:
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            d = c['planets'][pn]['dignity']
            if d == 100: ex[pn] += 1
            elif d == -100: deb[pn] += 1
    n = len(charts)
    top_ex = [f"{pn}({c/n*100:.0f}%)" for pn,c in ex.most_common(2) if c/n >= 0.1]
    top_deb = [f"{pn}({c/n*100:.0f}%)" for pn,c in deb.most_common(2) if c/n >= 0.1]
    print(f"  {gname:<22} ⭐ {', '.join(top_ex) if top_ex else '—':<20} ⚠️ {', '.join(top_deb) if top_deb else '—'}")

# 3. Conjunction patterns
print(f"\n--- KEY CONJUNCTIONS ---")
for gname, charts in sorted(all_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    all_conj = Counter()
    for c in charts:
        for cj in c['conjunctions']: all_conj[cj] += 1
    n = len(charts)
    top = [f"{cj}({c/n*100:.0f}%)" for cj,c in all_conj.most_common(3) if c/n >= 0.15]
    print(f"  {gname:<22} {' | '.join(top) if top else '—'}")

# ============================================================
# COMPARATIVE: GROUPS vs EACH OTHER
# ============================================================
print(f"\n{'='*100}")
print("WHAT MAKES EACH GROUP UNIQUE? (vs all other groups combined)")
print(f"{'='*100}")

all_other_naks = Counter()
all_other_ex = Counter()
all_other_deb = Counter()
all_other_conj = Counter()
all_other_n = 0

for gname, charts in all_data.items():
    for c in charts:
        all_other_naks[c['planets']['Moon']['nakshatra']] += 1
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            d = c['planets'][pn]['dignity']
            if d == 100: all_other_ex[pn] += 1
            if d == -100: all_other_deb[pn] += 1
        for cj in c['conjunctions']: all_other_conj[cj] += 1
        all_other_n += 1

for gname, charts in sorted(all_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 4: continue
    n = len(charts)
    other_n = all_other_n - n
    
    # Find overrepresented nakshatras
    over_naks = []
    for nak in set(c['planets']['Moon']['nakshatra'] for c in charts):
        our = sum(1 for c in charts if c['planets']['Moon']['nakshatra']==nak) / n
        other = (all_other_naks[nak] - sum(1 for c in charts if c['planets']['Moon']['nakshatra']==nak)) / max(other_n,1)
        if our > 0.15 and our > other * 2:
            over_naks.append(f"{nak}({our*100:.0f}% vs {other*100:.0f}%)")
    
    over_ex = []
    for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        our = sum(1 for c in charts if c['planets'][pn]['dignity']==100) / n
        other = (all_other_ex[pn] - sum(1 for c in charts if c['planets'][pn]['dignity']==100)) / max(other_n,1)
        if our > 0.15 and our > other * 2:
            over_ex.append(f"{pn} EX(our={our*100:.0f}% other={other*100:.0f}%)")
    
    markers = over_naks + over_ex
    if markers:
        print(f"  {gname:<22} {' | '.join(markers[:3])}")
    else:
        print(f"  {gname:<22} (no uniquely overrepresented marker)")

# ============================================================
# TRANSIT-LEVEL ANALYSIS
# ============================================================
print(f"\n{'='*100}")
print("TRANSIT ANALYSIS: Key Planetary Periods for Each Group")
print(f"{'='*100}")

# For each group, check what transits were happening at key ages
KEY_AGES = [21, 28, 35, 42, 50]  # Common breakthrough ages

for gname, charts in sorted(all_data.items(), key=lambda x: -len(x[1])):
    if len(charts) < 4: continue
    
    # Saturn return windows (age 28-30)
    saturn_return_signs = Counter()
    jupiter_peak_signs = Counter()
    
    for c in charts:
        by = c['birth_year']
        # Saturn at age 29 (Saturn return)
        sat_return_year = by + 29
        try:
            jd = swe.julday(sat_return_year, 6, 15, 12)
            ayan = swe.get_ayanamsa(jd)
            lt, _ = swe.calc_ut(jd, 6); lt = lt[0]  # Saturn=6
            sat_sign = SIGNS[int((lt-ayan)%360//30)]
            saturn_return_signs[sat_sign] += 1
        except: pass
        
        # Jupiter at age 35 (peak productivity)
        jup_year = by + 35
        try:
            jd = swe.julday(jup_year, 6, 15, 12)
            ayan = swe.get_ayanamsa(jd)
            lt, _ = swe.calc_ut(jd, 5); lt = lt[0]  # Jupiter=5
            jup_sign = SIGNS[int((lt-ayan)%360//30)]
            jupiter_peak_signs[jup_sign] += 1
        except: pass
    
    n = len(charts)
    top_sat = [f"{s}({c/n*100:.0f}%)" for s,c in saturn_return_signs.most_common(2)]
    top_jup = [f"{s}({c/n*100:.0f}%)" for s,c in jupiter_peak_signs.most_common(2)]
    
    print(f"  {gname:<22} Saturn Return: {', '.join(top_sat):<25} Jupiter@35: {', '.join(top_jup)}")

# ============================================================
# AI-DRIVEN INSIGHTS
# ============================================================
print(f"\n{'='*100}")
print("AI-DRIVEN DEEP INSIGHTS")
print(f"{'='*100}")

# Find the most "extreme" groups on each dimension
dimensions = {}
for gname, charts in all_data.items():
    if len(charts) < 4: continue
    n = len(charts)
    moon_naks = Counter(c['planets']['Moon']['nakshatra'] for c in charts)
    # How concentrated is the Moon nakshatra distribution?
    top_pct = max(c/n for c in moon_naks.values())
    
    ex_count = sum(1 for c in charts for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if c['planets'][pn]['dignity']==100)
    deb_count = sum(1 for c in charts for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'] if c['planets'][pn]['dignity']==-100)
    
    dimensions[gname] = {
        'n': n,
        'nakshatra_concentration': top_pct,
        'exalted_rate': ex_count/(n*7),
        'debil_rate': deb_count/(n*7),
        'top_nak': moon_naks.most_common(1)[0][0] if moon_naks else '?',
    }

print(f"\n{'Group':<22} {'N':>3} {'Top Nak%':>8} {'Exalted%':>9} {'Debil%':>8} {'Top Nak':<14}")
print("-"*70)
for gname, d in sorted(dimensions.items(), key=lambda x: -x[1]['nakshatra_concentration']):
    print(f"{gname:<22} {d['n']:>3} {d['nakshatra_concentration']*100:>7.0f}% {d['exalted_rate']*100:>8.1f}% {d['debil_rate']*100:>7.1f}% {d['top_nak']:<14}")

# Most concentrated = strongest occupational signature
most_concentrated = sorted(dimensions.items(), key=lambda x: -x[1]['nakshatra_concentration'])[:3]
print(f"\nMost concentrated Moon nakshatras (strongest occupational signal):")
for gname, d in most_concentrated:
    print(f"  {gname}: {d['top_nak']} ({d['nakshatra_concentration']*100:.0f}% concentration)")

# ============================================================
# SAVE
# ============================================================
output = {}
for gname, charts in all_data.items():
    output[gname] = [{"name":c['name'],"moon_nak":c['planets']['Moon']['nakshatra'],
                       "moon_sign":c['planets']['Moon']['sign'],
                       "rahu_sign":c['planets']['Rahu']['sign'],
                       "year":c['birth_year']} for c in charts]

with open('dataset/deep_research_groups.json','w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved → dataset/deep_research_groups.json")
