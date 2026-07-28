#!/usr/bin/env python3
"""FINAL GROUPS — Add late bloomers, leaders, philosophers, directors to group analysis"""
import swisseph as swe, json
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l
    return "Revati","Mercury"

def get_tz(p):
    if any(w in p for w in ['India','Delhi','Mumbai','Kolkata','Punjab','Gujarat','Haryana','Allahabad']): return 5.5
    if any(w in p for w in ['China','Taiwan','Singapore','Shanghai','Guangdong']): return 8
    if 'Japan' in p or 'Tokyo' in p: return 9
    if any(w in p for w in ['UK','England','Scotland','Wales','Ireland','London','Oxford','Edinburgh']): return 0
    if any(w in p for w in ['Germany','France','Italy','Spain','Norway','Denmark','Sweden','Austria','Switzerland','Poland','Netherlands','Belgium','Czech','Hungary','Prussia','Corsica']): return 1
    if any(w in p for w in ['Russia','Moscow','Soviet','Ukraine','Belarus','Latvia']): return 3
    if 'Brazil' in p: return -3
    if 'Argentina' in p: return -3
    if 'Venezuela' in p: return -4
    if 'Chile' in p: return -4
    if 'South Africa' in p: return 2
    if 'Mexico' in p: return -6
    if any(w in p for w in ['Iraq','Pakistan','Karachi']): return 3
    if 'Greece' in p or 'Athens' in p: return 2
    if 'Canada' in p or 'Ontario' in p or 'Vancouver' in p or 'Quebec' in p: return -5
    if 'Australia' in p: return 10
    if 'South Korea' in p or 'Daegu' in p: return 9
    return -5

def compute_chart(name, bday, place):
    dt = datetime.strptime(f"{bday}T12:00:00", "%Y-%m-%dT%H:%M:%S")
    tz = timezone(timedelta(hours=get_tz(place)))
    dt = dt.replace(tzinfo=tz)
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
    ayan = swe.get_ayanamsa(jd)
    p = {}
    for pn, pid in PLANETS_MAP.items():
        lt, _ = swe.calc_ut(jd, pid); lt = lt[0]
        sid = (lt - ayan) % 360
        sgn = SIGNS[int(sid//30)]
        nk, nl = gn(sid)
        dig = 100 if EXALT.get(pn)==sgn else (75 if sgn in OWN.get(pn,[]) else (-100 if DEBIL.get(pn)==sgn else 0))
        p[pn] = {"sign":sgn,"nakshatra":nk,"dignity":dig}
    rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360
    p["Rahu"] = {"sign":SIGNS[int(rh//30)],"nakshatra":gn(rh)[0],"dignity":0}
    p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"nakshatra":gn((rh+180)%360)[0],"dignity":0}
    conj = []
    pl = list(p.keys())
    for i in range(len(pl)):
        for j in range(i+1,len(pl)):
            if p[pl[i]]['sign'] == p[pl[j]]['sign']:
                conj.append(f"{pl[i]}+{pl[j]}")
    return p, conj

NEW_GROUPS = [
    ("Late Bloomer Founder", [
        ("Ray Kroc","1902-10-05","Oak Park, Illinois, USA"),
        ("Colonel Sanders","1890-09-09","Henryville, Indiana, USA"),
        ("Sam Walton","1918-03-29","Kingfisher, Oklahoma, USA"),
        ("Martha Stewart","1941-08-03","Jersey City, New Jersey, USA"),
        ("Mary Kay Ash","1918-05-12","Hot Wells, Texas, USA"),
        ("Estée Lauder","1908-07-01","Queens, New York, USA"),
        ("Sara Blakely","1971-02-27","Clearwater, Florida, USA"),
        ("Vera Wang","1949-06-27","New York City, New York, USA"),
        ("Arianna Huffington","1950-07-15","Athens, Greece"),
        ("Amancio Ortega","1936-03-28","Busdongo de Arbas, León, Spain"),
        ("Momofuku Ando","1910-03-05","Chiayi, Taiwan"),
        ("Harland Sanders","1890-09-09","Henryville, Indiana, USA"),
    ]),
    ("Author", [
        ("J.K. Rowling","1965-07-31","Yate, Gloucestershire, England, UK"),
        ("Toni Morrison","1931-02-18","Lorain, Ohio, USA"),
        ("Charles Bukowski","1920-08-16","Andernach, Germany"),
        ("Tom Clancy","1947-04-12","Baltimore, Maryland, USA"),
        ("George R.R. Martin","1948-09-20","Bayonne, New Jersey, USA"),
        ("Bram Stoker","1847-11-08","Clontarf, Dublin, Ireland"),
        ("Daniel Defoe","1660-09-13","London, England, UK"),
        ("James Michener","1907-02-03","New York City, New York, USA"),
        ("Alex Haley","1921-08-11","Ithaca, New York, USA"),
        ("Stieg Larsson","1954-08-15","Skelleftehamn, Sweden"),
    ]),
    ("Late Bloomer Actor", [
        ("Morgan Freeman","1937-06-01","Memphis, Tennessee, USA"),
        ("Samuel L. Jackson","1948-12-21","Washington, D.C., USA"),
        ("Bryan Cranston","1956-03-07","Hollywood, Los Angeles, California, USA"),
        ("Alan Rickman","1946-02-21","Hammersmith, London, England, UK"),
        ("Harrison Ford","1942-07-13","Chicago, Illinois, USA"),
        ("Christoph Waltz","1956-10-04","Vienna, Austria"),
        ("Judi Dench","1934-12-09","York, North Yorkshire, England, UK"),
        ("Patrick Stewart","1940-07-13","Mirfield, West Yorkshire, England, UK"),
        ("Gene Hackman","1930-01-30","San Bernardino, California, USA"),
        ("Kathy Bates","1948-06-28","Memphis, Tennessee, USA"),
        ("Ian McKellen","1939-05-25","Burnley, Lancashire, England, UK"),
    ]),
    ("Artist", [
        ("Vincent van Gogh","1853-03-30","Zundert, Netherlands"),
        ("Grandma Moses","1860-09-07","Greenwich, New York, USA"),
        ("Paul Gauguin","1848-06-07","Paris, France"),
        ("Wassily Kandinsky","1866-12-16","Moscow, Russia"),
        ("Bob Ross","1942-10-29","Daytona Beach, Florida, USA"),
    ]),
    ("Statesman/Leader", [
        ("Winston Churchill","1874-11-30","Blenheim Palace, Oxfordshire, England, UK"),
        ("Abraham Lincoln","1809-02-12","Hodgenville, Kentucky, USA"),
        ("Mahatma Gandhi","1869-10-02","Porbandar, Gujarat, India"),
        ("Nelson Mandela","1918-07-18","Mvezo, South Africa"),
        ("Napoleon Bonaparte","1769-08-15","Ajaccio, Corsica, France"),
        ("George Washington","1732-02-22","Westmoreland County, Virginia, USA"),
        ("Franklin D. Roosevelt","1882-01-30","Hyde Park, New York, USA"),
        ("Theodore Roosevelt","1858-10-27","New York City, New York, USA"),
        ("Margaret Thatcher","1925-10-13","Grantham, Lincolnshire, England, UK"),
        ("Lee Kuan Yew","1923-09-16","Singapore"),
        ("Jawaharlal Nehru","1889-11-14","Allahabad, Uttar Pradesh, India"),
        ("Mikhail Gorbachev","1931-03-02","Privolnoye, Russian SFSR, Soviet Union"),
    ]),
    ("Philosopher", [
        ("Immanuel Kant","1724-04-22","Königsberg, Prussia"),
        ("Friedrich Nietzsche","1844-10-15","Röcken, Prussia, Germany"),
        ("Karl Marx","1818-05-05","Trier, Kingdom of Prussia"),
        ("Jean-Paul Sartre","1905-06-21","Paris, France"),
        ("Voltaire","1694-11-21","Paris, France"),
        ("Jean-Jacques Rousseau","1712-06-28","Geneva, Switzerland"),
        ("John Locke","1632-08-29","Wrington, Somerset, England, UK"),
        ("David Hume","1711-05-07","Edinburgh, Scotland, UK"),
        ("Arthur Schopenhauer","1788-02-22","Danzig, Polish-Lithuanian Commonwealth"),
        ("Baruch Spinoza","1632-11-24","Amsterdam, Netherlands"),
        ("Søren Kierkegaard","1813-05-05","Copenhagen, Denmark"),
        ("Hannah Arendt","1906-10-14","Linden, Hanover, Germany"),
        ("Michel Foucault","1926-10-15","Poitiers, France"),
        ("Bertrand Russell","1872-05-18","Trellech, Monmouthshire, Wales, UK"),
        ("Ludwig Wittgenstein","1889-04-26","Vienna, Austria"),
        ("Noam Chomsky","1928-12-07","Philadelphia, Pennsylvania, USA"),
    ]),
    ("Architect", [
        ("Frank Lloyd Wright","1867-06-08","Richland Center, Wisconsin, USA"),
        ("Antoni Gaudí","1852-06-25","Reus, Catalonia, Spain"),
        ("Zaha Hadid","1950-10-31","Baghdad, Iraq"),
        ("Le Corbusier","1887-10-06","La Chaux-de-Fonds, Switzerland"),
        ("Oscar Niemeyer","1907-12-15","Rio de Janeiro, Brazil"),
        ("I. M. Pei","1917-04-26","Guangzhou, Guangdong, China"),
        ("Frank Gehry","1929-02-28","Toronto, Ontario, Canada"),
        ("Norman Foster","1935-06-01","Reddish, Stockport, England, UK"),
        ("Renzo Piano","1937-09-14","Genoa, Italy"),
    ]),
    ("Astronaut", [
        ("Yuri Gagarin","1934-03-09","Klushino, Russian SFSR, Soviet Union"),
        ("Neil Armstrong","1930-08-05","Wapakoneta, Ohio, USA"),
        ("Buzz Aldrin","1930-01-20","Glen Ridge, New Jersey, USA"),
        ("Valentina Tereshkova","1937-03-06","Bolshoye Maslennikovo, Soviet Union"),
        ("John Glenn","1921-07-18","Cambridge, Ohio, USA"),
        ("Sally Ride","1951-05-26","Los Angeles, California, USA"),
        ("Chris Hadfield","1959-08-29","Sarnia, Ontario, Canada"),
        ("Mae Jemison","1956-10-17","Decatur, Alabama, USA"),
    ]),
    ("Film Director", [
        ("Alfred Hitchcock","1899-08-13","Leytonstone, London, England, UK"),
        ("Stanley Kubrick","1928-07-26","New York City, New York, USA"),
        ("Steven Spielberg","1946-12-18","Cincinnati, Ohio, USA"),
        ("Martin Scorsese","1942-11-17","Queens, New York, USA"),
        ("Akira Kurosawa","1910-03-23","Shinagawa, Tokyo, Japan"),
        ("Federico Fellini","1920-01-20","Rimini, Italy"),
        ("Ingmar Bergman","1918-07-14","Uppsala, Sweden"),
        ("Quentin Tarantino","1963-03-27","Knoxville, Tennessee, USA"),
        ("Christopher Nolan","1970-07-30","London, England, UK"),
        ("David Lynch","1946-01-20","Missoula, Montana, USA"),
        ("Francis Ford Coppola","1939-04-07","Detroit, Michigan, USA"),
        ("Orson Welles","1915-05-06","Kenosha, Wisconsin, USA"),
        ("James Cameron","1954-08-16","Kapuskasing, Ontario, Canada"),
        ("Hayao Miyazaki","1941-01-05","Bunkyo, Tokyo, Japan"),
        ("Charlie Chaplin","1889-04-16","Walworth, London, England, UK"),
    ]),
]

print(f"Computing {sum(len(g[1]) for g in NEW_GROUPS)} charts across {len(NEW_GROUPS)} new groups...")

total = 0
all_group_stats = {}
for gname, members in NEW_GROUPS:
    charts = []
    for name, bday, place in members:
        try:
            p, conj = compute_chart(name, bday, place)
            charts.append({"name":name,"planets":p,"conjunctions":conj})
            total += 1
        except: pass
    if len(charts) < 2: continue
    
    n = len(charts)
    moon_naks = Counter(c['planets']['Moon']['nakshatra'] for c in charts)
    ex = Counter(); deb = Counter()
    for c in charts:
        for pn in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
            if pn in c['planets']:
                d = c['planets'][pn]['dignity']
                if d == 100: ex[pn] += 1
                elif d == -100: deb[pn] += 1
    all_conj = Counter()
    for c in charts:
        for cj in c['conjunctions']: all_conj[cj] += 1
    
    top_nak = moon_naks.most_common(3)
    top_ex = [f"{pn}({c/n*100:.0f}%)" for pn,c in ex.most_common(2) if c/n > 0.05]
    top_deb = [f"{pn}({c/n*100:.0f}%)" for pn,c in deb.most_common(2) if c/n > 0.05]
    top_cj = [f"{cj}({c/n*100:.0f}%)" for cj,c in all_conj.most_common(3) if c/n > 0.15]
    
    all_group_stats[gname] = {
        "n": n,
        "moon_nak": [f"{nak}({cnt/n*100:.0f}%)" for nak,cnt in top_nak],
        "exalted": top_ex,
        "debilitated": top_deb,
        "conjunctions": top_cj,
    }
    print(f"  {gname}: {n} computed")

print(f"\nTotal: {total} new charts")
print(f"\n{'='*100}")
print("NEW GROUP SIGNATURES")
print(f"{'='*100}")
print(f"\n{'Group':<25} {'N':>3} {'Moon Nakshatra':<40} {'Exalted':<25} {'Debilitated':<25}")
print("-"*120)
for gname, s in sorted(all_group_stats.items(), key=lambda x: -x[1]['n']):
    print(f"{gname:<25} {s['n']:>3} {', '.join(s['moon_nak'][:3]):<40} {', '.join(s['exalted'][:2]):<25} {', '.join(s['debilitated'][:2]):<25}")

# Cross-group: what's unique?
print(f"\n{'='*100}")
print("CROSS-GROUP STANDOUTS")
print(f"{'='*100}")
for gname, s in sorted(all_group_stats.items(), key=lambda x: -x[1]['n']):
    # Check for moon nakshatras > 30%
    standout = []
    for nak_str in s['moon_nak']:
        pct = float(nak_str.split('(')[1].replace('%)',''))
        if pct >= 20: standout.append(f"🌙 {nak_str}")
    for ex_str in s['exalted']:
        pct = float(ex_str.split('(')[1].replace('%)',''))
        if pct >= 20: standout.append(f"⭐ {ex_str}")
    for deb_str in s['debilitated']:
        pct = float(deb_str.split('(')[1].replace('%)',''))
        if pct >= 20: standout.append(f"⚠️ {deb_str}")
    if standout:
        print(f"  {gname:<25} {' | '.join(standout)}")
    else:
        print(f"  {gname:<25} (no standout >20%)")

# Save
out = {}
for gname, members in NEW_GROUPS:
    out[gname] = [{"name":n,"bday":b,"place":p} for n,b,p in members]
with open('/home/user/dataset/new_groups_summary.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\nSaved")
