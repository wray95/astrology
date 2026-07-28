#!/usr/bin/env python3
"""
FINAL DATASET INGESTION: ~526 new charts, grouped by category
Fast batch compute, Judge analysis, push to Git
"""
import swisseph as swe, json, math
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
import os

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS_MAP = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo","Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],"Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],"Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
SL = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
NAKS = [("Ashwini",0,"Ketu"),("Bharani",13.333,"Venus"),("Krittika",26.667,"Sun"),("Rohini",40,"Moon"),("Mrigashira",53.333,"Mars"),("Ardra",66.667,"Rahu"),("Punarvasu",80,"Jupiter"),("Pushya",93.333,"Saturn"),("Ashlesha",106.667,"Mercury"),("Magha",120,"Ketu"),("Purva Phalguni",133.333,"Venus"),("Uttara Phalguni",146.667,"Sun"),("Hasta",160,"Moon"),("Chitra",173.333,"Mars"),("Swati",186.667,"Rahu"),("Vishakha",200,"Jupiter"),("Anuradha",213.333,"Saturn"),("Jyeshtha",226.667,"Mercury"),("Mula",240,"Ketu"),("Purva Ashadha",253.333,"Venus"),("Uttara Ashadha",266.667,"Sun"),("Shravana",280,"Moon"),("Dhanishtha",293.333,"Mars"),("Shatabhisha",306.667,"Rahu"),("Purva Bhadrapada",320,"Jupiter"),("Uttara Bhadrapada",333.333,"Saturn"),("Revati",346.667,"Mercury")]

def gn(lon):
    lon %= 360
    for n,s,l in NAKS:
        if s <= lon < s+13.334: return n,l
    return "Revati","Mercury"

def get_tz(p):
    if any(w in p for w in ['India','Delhi','Mumbai','Bombay','Calcutta','Madras','Punjab','Gujarat','Haryana','Tamil','Rajasthan','Maharashtra','Mewar','Maratha','Maurya','Gupta','Pataliputra']): return 5.5
    if any(w in p for w in ['China','Taiwan','Shanghai','Guangdong','Beijing','Nanjing','Ming','Qing','Han','Tang','Song','Yuan','Sui','Zhao','Chu','Henan','Jiangsu','Zhejiang','Shandong','Anhui']): return 8
    if any(w in p for w in ['Japan','Tokyo','Osaka','Edo','Kyoto','Heian','Nagoya','Hirado','Owari','Mikawa','Kai','Echigo','Shinano','Yamato','Asuka','Harima','Settsu','Wakayama','Ryukyu','Okinawa','Nagasaki','Chōsen']): return 9
    if any(w in p for w in ['Korea','Joseon','Goguryeo','Hanseong']): return 9
    if any(w in p for w in ['UK','England','Scotland','Wales','Ireland','London','Oxford','Edinburgh','Bristol','Liverpool','Manchester','York','Norfolk','Essex','Devon','Sussex','Kent','Surrey','Hampshire','Berkshire','Wiltshire','Somerset','Dorset','Cornwall','Lancashire','Yorkshire','Northumberland','Cumberland','Westmorland','Durham','Northampton','Warwick','Leicester','Nottingham','Derby','Stafford','Shropshire','Worcester','Hereford','Gloucester','Buckingham','Bedford','Huntingdon','Cambridge','Suffolk','Hertford','Rutland','Lincoln','Cheshire','Monmouth','Glamorgan','Pembroke','Kingdom of England','Kingdom of Great Britain','Kingdom of Scotland','Kingdom of Ireland','British','Great Britain','Northern Ireland']): return 0
    if any(w in p for w in ['Germany','France','Italy','Spain','Norway','Denmark','Sweden','Austria','Switzerland','Poland','Netherlands','Belgium','Czech','Hungary','Prussia','Saxony','Bavaria','Holy Roman','Austria-Hungary','Venice','Florence','Genoa','Papal','Tuscany','Lombardy','Piedmont','Milan','Naples','Sicily','Sardinia','Corsica','Normandy','Brittany','Aquitaine','Burgundy','Provence','Savoy','Alsace','Lorraine','Franche','Württemberg','Baden','Hesse','Hanover','Brunswick','Oldenburg','Mecklenburg','Pomerania','Silesia','Bohemia','Moravia','Slovakia','Slovenia','Galicia','Bukovina','Transylvania','Wallachia','Moldavia','Banat','Croatia','Dalmatia','Bosnia','Herzegovina','Montenegro','Serbia','Bulgaria','Albania','Macedonia','Thrace','Epirus','Thessaly','Peloponnese','Crete','Cyprus','Malta','Gibraltar','Luxembourg','Liechtenstein','Andorra','Monaco','San Marino','Vatican']): return 1
    if any(w in p for w in ['Russia','Moscow','Soviet','Ukraine','Belarus','Latvia','Lithuania','Estonia','Finland','Tsardom','Russian Empire','Russian SFSR','Kievan','Novgorod']): return 3
    if any(w in p for w in ['Brazil','Rio','São Paulo']): return -3
    if any(w in p for w in ['Argentina','Buenos']): return -3
    if any(w in p for w in ['Venezuela','Colombia','Peru','Bolivia','Ecuador','Chile','Uruguay','Paraguay']): return -5
    if any(w in p for w in ['Mexico','Guadalajara','Coyoacán','Aztec','Maya','Olmec','Toltec']): return -6
    if any(w in p for w in ['South Africa','Pretoria','Johannesburg','Cape Town','Zulu','Ndongo']): return 2
    if any(w in p for w in ['Kenya','Uganda','Tanzania','Ethiopia','Sudan','Libya','Egypt','Alexandria','Cairo','Thebes','Memphis']): return 2
    if any(w in p for w in ['Nigeria','Ghana','Ivory','Senegal','Mali','Gambia','Guinea','Sierra Leone','Liberia','Congo','Angola']): return 1
    if any(w in p for w in ['Pakistan','Karachi','Afghanistan']): return 5
    if any(w in p for w in ['Iran','Persia','Tehran','Isfahan','Shiraz','Achaemenid','Sasanian','Parthian','Safavid']): return 3.5
    if any(w in p for w in ['Iraq','Baghdad','Babylon','Nineveh','Assyria','Mesopotamia','Akkad','Sumer','Ur','Abbasid']): return 3
    if any(w in p for w in ['Turkey','Istanbul','Constantinople','Ottoman','Byzantine','Anatolia','Cappadocia','Sultanate of Rum']): return 3
    if any(w in p for w in ['Greece','Athens','Sparta','Macedon','Corinth','Thebes','Thessaloniki','Salonica']): return 2
    if any(w in p for w in ['Portugal','Lisbon','Madeira']): return -1
    if any(w in p for w in ['Romania','Bucharest']): return 2
    if any(w in p for w in ['Serbia','Belgrade','Montenegro','Bosnia']): return 1
    if any(w in p for w in ['Morocco','Tangier','Casablanca','Marrakech']): return 0
    if any(w in p for w in ['Tunisia','Carthage','Tunis']): return 1
    if any(w in p for w in ['Algeria','Algiers']): return 1
    if any(w in p for w in ['Israel','Jerusalem','Tel Aviv']): return 2
    if any(w in p for w in ['Syria','Damascus','Palmyra','Antioch']): return 3
    if any(w in p for w in ['Lebanon','Beirut','Tyre','Sidon']): return 2
    if any(w in p for w in ['Jordan','Amman','Petra']): return 3
    if any(w in p for w in ['Saudi Arabia','Riyadh','Mecca','Medina','Arabia']): return 3
    if any(w in p for w in ['Yemen','Aden']): return 3
    if any(w in p for w in ['Canada','Ontario','Quebec','Toronto','Montreal','Vancouver']): return -5
    if any(w in p for w in ['Australia','Sydney','Melbourne','Adelaide','Brisbane','Perth']): return 10
    if any(w in p for w in ['New Zealand','Auckland']): return 12
    if any(w in p for w in ['Greenland','Iceland']): return 0
    if any(w in p for w in ['Jamaica','Cuba','Haiti','Dominican','Bahamas','Barbados','Trinidad']): return -5
    if any(w in p for w in ['Philippines','Manila']): return 8
    if any(w in p for w in ['Vietnam','Indochina','French Indochina']): return 7
    if any(w in p for w in ['Burma','Myanmar','Rangoon']): return 6.5
    if any(w in p for w in ['Mongol','Mongolia','Karakorum','Ulaanbaatar']): return 8
    if any(w in p for w in ['Kazakhstan','Uzbekistan','Turkmenistan','Kyrgyzstan','Tajikistan','Samarkand','Bukhara','Khiva','Kokand']): return 5
    if any(w in p for w in ['Hawaii','Honolulu','Polynesia','Micronesia','Melanesia']): return -10
    if any(w in p for w in ['Guatemala','Honduras','El Salvador','Nicaragua','Costa Rica','Panama','Belize']): return -6
    return -5

def compute_noon(name, bday, place):
    try:
        parts = bday.split('-')
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y, m, d, 12, 0, 0)
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
            p[pn] = {"sign":sgn,"nakshatra":nk,"dignity":dig,"sidereal":round(sid,2)}
        rh, _ = swe.calc_ut(jd, swe.MEAN_NODE); rh = (rh[0]-ayan)%360
        p["Rahu"] = {"sign":SIGNS[int(rh//30)],"nakshatra":gn(rh)[0],"dignity":0}
        p["Ketu"] = {"sign":SIGNS[int(((rh+180)%360)//30)],"nakshatra":gn((rh+180)%360)[0],"dignity":0}
        conj = []
        pl = list(p.keys())
        for i in range(len(pl)):
            for j in range(i+1,len(pl)):
                if p[pl[i]]['sign'] == p[pl[j]]['sign']:
                    conj.append(f"{pl[i]}+{pl[j]}")
        return {"name":name,"year":y,"planets":p,"conjunctions":conj}
    except:
        return None

# ============================================================
# GROUP DEFINITIONS
# ============================================================
GROUPS = {
    "Pirate & Sea Warrior": [
        ("Blackbeard","1680-01-01","Bristol, Kingdom of England"),
        ("Bartholomew Roberts","1682-05-17","Little Newcastle, Pembrokeshire, Wales"),
        ("Zheng Yi Sao","1775-01-01","Guangdong, Qing Dynasty China"),
        ("Grace O'Malley","1530-01-01","County Mayo, Kingdom of Ireland"),
        ("Henry Morgan","1635-01-01","Llanrumney, Wales"),
        ("William Kidd","1645-01-22","Dundee, Scotland"),
        ("Anne Bonny","1697-03-08","Kinsale, Kingdom of Ireland"),
        ("Mary Read","1685-01-01","Kingdom of England"),
        ("Cheung Po Tsai","1783-01-01","Xinhui, Guangdong, Qing Dynasty China"),
        ("Francois l'Olonnais","1630-01-01","Les Sables-d'Olonne, Kingdom of France"),
        ("Hayreddin Barbarossa","1478-01-01","Lesbos, Ottoman Empire"),
        ("Dragut","1485-01-01","Bodrum, Ottoman Empire"),
        ("Sayyida al Hurra","1485-01-01","Emirate of Granada"),
        ("Andrea Doria","1466-11-30","Oneglia, Republic of Genoa"),
        ("Koxinga","1624-08-27","Hirado, Japan"),
        ("Pier Gerlofs Donia","1480-01-01","Kimswerd, Frisia, Holy Roman Empire"),
        ("Admiral Yi Sun-sin","1545-04-28","Hanseong, Joseon Dynasty"),
        ("Horatio Nelson","1758-09-29","Burnham Thorpe, Norfolk, Great Britain"),
        ("Michiel de Ruyter","1607-03-24","Vlissingen, Dutch Republic"),
        ("John Paul Jones","1747-07-06","Arbigland, Kirkcudbrightshire, Scotland"),
        ("Zheng He","1371-01-01","Kunming, Yunnan, Ming Dynasty"),
    ],
    "Legendary Warrior": [
        ("Miyamoto Musashi","1584-01-01","Harima Province, Japan"),
        ("Hattori Hanzo","1542-01-01","Mikawa Province, Japan"),
        ("Guan Yu","0160-01-01","Yuncheng, Hedong, Eastern Han Dynasty"),
        ("Sun Tzu","-0544-01-01","Wu State, Ancient China"),
        ("Genghis Khan","1162-05-31","Deluun Boldog, Mongol Empire"),
        ("Attila the Hun","0406-01-01","Pannonia, Hunnic Empire"),
        ("Alexander the Great","-0356-07-20","Pella, Macedon"),
        ("Leonidas I","-0540-01-01","Sparta, Ancient Greece"),
        ("Hannibal Barca","-0247-01-01","Carthage"),
        ("Julius Caesar","-0100-07-12","Rome, Roman Republic"),
        ("Scipio Africanus","-0236-01-01","Rome, Roman Republic"),
        ("Richard the Lionheart","1157-09-08","Oxford, Kingdom of England"),
        ("Saladin","1137-01-01","Tikrit, Abbasid Caliphate"),
        ("Khalid ibn al-Walid","0592-01-01","Mecca, Arabia"),
        ("Subutai","1175-01-01","Khentii Mountains, Mongolia"),
        ("Cyrus the Great","-0600-01-01","Anshan, Persis"),
        ("Belisarius","0505-01-01","Germania in Thrace, Byzantine Empire"),
        ("El Cid","1043-01-01","Vivar del Cid, Kingdom of Castile"),
        ("William Wallace","1270-01-01","Elderslie, Renfrewshire, Scotland"),
        ("Robert the Bruce","1274-07-11","Turnberry, Ayrshire, Scotland"),
        ("Vlad the Impaler","1431-11-10","Sighisoara, Voivodeship of Transylvania"),
        ("Skanderbeg","1405-05-06","Sine, Principality of Kastrioti"),
        ("Shaka Zulu","1787-07-01","Melmoth, Zulu Kingdom"),
        ("Yue Fei","1103-03-24","Tangyin, Henan, Song Dynasty"),
        ("Napoleon Bonaparte","1769-08-15","Ajaccio, Corsica, France"),
        ("Erwin Rommel","1891-11-15","Heidenheim, Kingdom of Wurttemberg, German Empire"),
        ("George Patton","1885-11-11","San Gabriel, California, USA"),
        ("Georgy Zhukov","1896-12-01","Strelkovka, Kaluga Governorate, Russian Empire"),
        ("Timur","1336-04-09","Kesh, Chagatai Khanate"),
        ("Babur","1483-02-14","Andijan, Timurid Empire"),
        ("Akbar the Great","1542-10-15","Umerkot, Mughal Empire"),
        ("Suleiman the Magnificent","1494-11-06","Trabzon, Ottoman Empire"),
        ("Mehmed II","1432-03-30","Edirne, Ottoman Empire"),
        ("Mustafa Kemal Ataturk","1881-05-19","Salonica, Ottoman Empire"),
        ("Sitting Bull","1831-01-01","Grand River, Dakota Territory, USA"),
        ("Crazy Horse","1840-01-01","Rapid Creek, Dakota Territory, USA"),
        ("Geronimo","1829-06-16","No-Doyohn Canyon, Mexico"),
        ("Tecumseh","1768-03-01","Chillicothe, Ohio, USA"),
        ("Charlemagne","0748-04-02","Frankish Kingdom"),
        ("Alfred the Great","0849-01-01","Wantage, Berkshire, Kingdom of Wessex"),
        ("Frederick Barbarossa","1122-01-01","Waiblingen, Duchy of Swabia"),
        ("Gustavus Adolphus","1594-12-19","Stockholm, Sweden"),
        ("Charles XII of Sweden","1682-06-17","Stockholm, Sweden"),
    ],
    "Martial Arts Master": [
        ("Ip Man","1893-10-01","Foshan, Guangdong, Qing Dynasty China"),
        ("Gichin Funakoshi","1868-11-10","Shuri, Ryukyu Kingdom"),
        ("Morihei Ueshiba","1883-12-14","Tanabe, Wakayama, Japan"),
        ("Jigoro Kano","1860-12-10","Mikage, Settsu Province, Japan"),
        ("Mas Oyama","1923-07-27","Gimje, Chosen, Japanese Empire"),
    ],
    "Japanese Daimyo": [
        ("Oda Nobunaga","1534-06-23","Nagoya Castle, Owari Province, Japan"),
        ("Toyotomi Hideyoshi","1537-03-17","Nakamura-ku, Nagoya, Japan"),
        ("Tokugawa Ieyasu","1543-01-31","Okazaki Castle, Mikawa Province, Japan"),
        ("Takeda Shingen","1521-12-01","Kai Province, Japan"),
        ("Uesugi Kenshin","1530-02-18","Echigo Province, Japan"),
        ("Minamoto no Yoshitsune","1159-01-01","Kyoto, Japan"),
    ],
    "Indian Warrior King": [
        ("Maharana Pratap","1540-05-09","Kumbhalgarh, Mewar, India"),
        ("Chhatrapati Shivaji","1630-02-19","Shivneri Fort, Maharashtra, India"),
        ("Bajirao I","1700-08-18","Dubere, Maratha Empire"),
        ("Lachit Borphukan","1622-11-24","Charaideo, Ahom Kingdom"),
        ("Ranjit Singh","1780-11-13","Gujranwala, Sikh Empire"),
    ],
    "Mathematician/Computer Scientist": [
        ("Ada Lovelace","1815-12-10","London, Kingdom of Great Britain"),
        ("Alan Turing","1912-06-23","London, England, UK"),
        ("Carl Friedrich Gauss","1777-04-30","Braunschweig, Duchy of Brunswick-Wolfenbuttel"),
        ("Leonhard Euler","1707-04-15","Basel, Old Swiss Confederacy"),
        ("Srinivasa Ramanujan","1887-12-22","Erode, Madras Presidency, British India"),
        ("Emmy Noether","1882-03-23","Erlangen, Kingdom of Bavaria, German Empire"),
        ("Kurt Godel","1906-04-28","Brunn, Austria-Hungary"),
        ("Grace Hopper","1906-12-09","New York City, New York, USA"),
        ("Euclid","-0325-01-01","Alexandria, Ptolemaic Kingdom"),
        ("Hypatia","0360-01-01","Alexandria, Eastern Roman Empire"),
        ("Henri Poincare","1854-04-29","Nancy, France"),
        ("David Hilbert","1862-01-23","Konigsberg, Kingdom of Prussia"),
        ("Bernhard Riemann","1826-09-17","Jameln, Kingdom of Hanover"),
        ("Evariste Galois","1811-10-25","Bourg-la-Reine, First French Empire"),
        ("Sophie Germain","1776-04-01","Paris, Kingdom of France"),
        ("Donald Knuth","1938-01-10","Milwaukee, Wisconsin, USA"),
        ("Edsger Dijkstra","1930-05-11","Rotterdam, Netherlands"),
        ("Barbara Liskov","1939-11-07","Los Angeles, California, USA"),
        ("Terence Tao","1975-07-17","Adelaide, Australia"),
        ("Katherine Johnson","1918-08-26","White Sulphur Springs, West Virginia, USA"),
        ("John von Neumann","1903-12-28","Budapest, Austria-Hungary"),
        ("Claude Shannon","1916-04-30","Petoskey, Michigan, USA"),
    ],
    "Physician/Medical Pioneer": [
        ("Edward Jenner","1749-05-17","Berkeley, Gloucestershire, Kingdom of Great Britain"),
        ("Louis Pasteur","1822-12-27","Dole, France"),
        ("Robert Koch","1843-12-11","Clausthal, Kingdom of Hanover"),
        ("Jonas Salk","1914-10-28","New York City, New York, USA"),
        ("Joseph Lister","1827-04-05","Upton, Essex, Kingdom of Great Britain"),
        ("Hippocrates","-0460-01-01","Kos, Ancient Greece"),
        ("Galen","0129-01-01","Pergamon, Roman Empire"),
        ("Andreas Vesalius","1514-12-31","Brussels, Habsburg Netherlands"),
        ("William Harvey","1578-04-01","Folkestone, Kingdom of England"),
        ("Ignaz Semmelweis","1818-07-01","Buda, Kingdom of Hungary"),
        ("Rosalind Franklin","1920-07-25","London, England, UK"),
        ("Elizabeth Blackwell","1821-02-03","Bristol, England, UK"),
        ("Tu Youyou","1930-12-30","Ningbo, Zhejiang, China"),
        ("Christiaan Barnard","1922-11-08","Beaufort West, Union of South Africa"),
        ("Alexander Fleming","1881-08-06","Darvel, Scotland, UK"),
    ],
    "Physicist/Astronomer": [
        ("Galileo Galilei","1564-02-15","Pisa, Duchy of Florence"),
        ("Isaac Newton","1643-01-04","Woolsthorpe-by-Colsterworth, Kingdom of England"),
        ("Albert Einstein","1879-03-14","Ulm, Kingdom of Wurttemberg, German Empire"),
        ("Johannes Kepler","1571-12-27","Weil der Stadt, Holy Roman Empire"),
        ("Nicolaus Copernicus","1473-02-19","Torun, Royal Prussia, Kingdom of Poland"),
        ("James Clerk Maxwell","1831-06-13","Edinburgh, Scotland, UK"),
        ("Michael Faraday","1791-09-22","Newington Butts, Surrey, Kingdom of Great Britain"),
        ("Stephen Hawking","1942-01-08","Oxford, England, UK"),
        ("Carl Sagan","1934-11-09","Brooklyn, New York, USA"),
        ("Edwin Hubble","1889-11-20","Marshfield, Missouri, USA"),
        ("Subrahmanyan Chandrasekhar","1910-10-19","Lahore, Punjab, British India"),
        ("Chien-Shiung Wu","1912-05-31","Liuhe, Ta Cang, Jiangsu, Republic of China"),
        ("Lise Meitner","1878-11-07","Vienna, Austria-Hungary"),
        ("Erwin Schrodinger","1887-08-12","Vienna, Austria-Hungary"),
        ("Werner Heisenberg","1901-12-05","Wurzburg, Kingdom of Bavaria, German Empire"),
        ("Paul Dirac","1902-08-08","Bristol, England, UK"),
        ("Enrico Fermi","1901-09-29","Rome, Kingdom of Italy"),
        ("J. Robert Oppenheimer","1904-04-22","New York City, New York, USA"),
        ("Vera Rubin","1928-07-23","Philadelphia, Pennsylvania, USA"),
        ("Arthur Eddington","1882-12-28","Kendal, England, UK"),
        ("Antoine Lavoisier","1743-08-26","Paris, Kingdom of France"),
        ("Dmitry Mendeleev","1834-02-08","Tobolsk, Russian Empire"),
        ("Dorothy Hodgkin","1910-05-12","Cairo, Khedivate of Egypt"),
        ("Alexander von Humboldt","1769-09-14","Berlin, Kingdom of Prussia"),
        ("Rachel Carson","1907-05-27","Springdale, Pennsylvania, USA"),
        ("Jane Goodall","1934-04-03","London, England, UK"),
    ],
    "Writer/Poet": [
        ("Homer","-0800-01-01","Ionia, Ancient Greece"),
        ("Dante Alighieri","1265-06-01","Florence, Republic of Florence"),
        ("William Shakespeare","1564-04-26","Stratford-upon-Avon, Kingdom of England"),
        ("Leo Tolstoy","1828-09-09","Yasnaya Polyana, Russian Empire"),
        ("Fyodor Dostoevsky","1821-11-11","Moscow, Russian Empire"),
        ("Victor Hugo","1802-02-26","Besancon, France"),
        ("Mark Twain","1835-11-30","Florida, Missouri, USA"),
        ("Edgar Allan Poe","1809-01-19","Boston, Massachusetts, USA"),
        ("Virginia Woolf","1882-01-25","London, England, UK"),
        ("George Orwell","1903-06-25","Motihari, Bengal Presidency, British India"),
        ("James Joyce","1882-02-02","Dublin, Ireland"),
        ("Jane Austen","1775-12-16","Steventon, Hampshire, Kingdom of Great Britain"),
        ("Emily Dickinson","1830-12-10","Amherst, Massachusetts, USA"),
        ("Maya Angelou","1928-04-04","St. Louis, Missouri, USA"),
        ("Jorge Luis Borges","1899-08-24","Buenos Aires, Argentina"),
        ("Haruki Murakami","1949-01-12","Kyoto, Japan"),
        ("Hans Christian Andersen","1805-04-02","Odense, Denmark"),
        ("Jules Verne","1828-02-08","Nantes, France"),
        ("H. G. Wells","1866-09-21","Bromley, Kent, England, UK"),
        ("Isaac Asimov","1920-01-02","Petrovichi, Russian SFSR"),
        ("Mary Shelley","1797-08-30","London, Kingdom of Great Britain"),
        ("Franz Kafka","1883-07-03","Prague, Austria-Hungary"),
        ("Marcel Proust","1871-07-10","Paris, France"),
        ("Charles Dickens","1812-02-07","Portsmouth, England, UK"),
        ("Miguel de Cervantes","1547-09-29","Alcala de Henares, Crown of Castile"),
        ("Oscar Wilde","1854-10-16","Dublin, Ireland"),
        ("Anton Chekhov","1860-01-29","Taganrog, Russian Empire"),
        ("Hermann Hesse","1877-07-02","Calw, German Empire"),
        ("Chinua Achebe","1930-11-16","Ogidi, British Nigeria"),
        ("Wole Soyinka","1934-07-13","Abeokuta, British Nigeria"),
        ("James Baldwin","1924-08-02","Harlem, New York, USA"),
        ("Rumi","1207-09-30","Balkh, Khwarazmian Empire"),
        ("Alexander Pushkin","1799-06-06","Moscow, Tsardom of Russia"),
        ("Murasaki Shikibu","0973-01-01","Heian-kyo, Japan"),
        ("Matsuo Basho","1644-01-01","Iga Province, Japan"),
    ],
    "Ancient Ruler": [
        ("Ramesses II","-1303-01-01","Memphis, New Kingdom Egypt"),
        ("Cleopatra VII","-0069-01-13","Alexandria, Ptolemaic Kingdom"),
        ("Hatshepsut","-1507-01-01","Thebes, New Kingdom Egypt"),
        ("Tutankhamun","-1341-01-01","Thebes, New Kingdom Egypt"),
        ("Hammurabi","-1810-01-01","Babylon, First Babylonian Empire"),
        ("Nebuchadnezzar II","-0634-01-01","Babylon, Neo-Babylonian Empire"),
        ("Darius the Great","-0550-01-01","Persis, Achaemenid Empire"),
        ("Ashoka the Great","-0304-08-12","Pataliputra, Maurya Empire"),
        ("Qin Shi Huang","-0259-01-01","Handan, Zhao State"),
        ("Emperor Taizong of Tang","0598-01-28","Wugong, Sui Dynasty China"),
        ("Wu Zetian","0624-02-17","Guangyuan, Tang Dynasty China"),
        ("King Sejong the Great","1397-05-07","Hanseong, Joseon Dynasty"),
        ("Augustus","-0063-09-23","Rome, Roman Republic"),
        ("Marcus Aurelius","0121-04-26","Rome, Roman Empire"),
        ("Constantine the Great","0272-02-27","Naissus, Roman Empire"),
        ("Justinian I","0482-05-11","Tauresium, Byzantine Empire"),
        ("Chandragupta Maurya","-0340-01-01","Pataliputra, Maurya Empire"),
        ("Hongwu Emperor","1328-10-21","Fengyang, Anhui, Yuan Dynasty"),
        ("Peter the Great","1672-06-09","Moscow, Tsardom of Russia"),
        ("Henry VIII","1491-06-28","Greenwich, Kingdom of England"),
    ],
    "Philanthropist/Tycoon": [
        ("Andrew Carnegie","1835-11-25","Dunfermline, Fife, Scotland"),
        ("John D. Rockefeller","1839-07-08","Richford, New York, USA"),
        ("Jamsetji Tata","1839-03-03","Navsari, Gujarat, British India"),
        ("Alfred Nobel","1833-10-21","Stockholm, Sweden"),
        ("J.P. Morgan","1837-04-17","Hartford, Connecticut, USA"),
        ("Cornelius Vanderbilt","1794-05-27","Staten Island, New York, USA"),
        ("Henry Ford","1863-07-30","Springwells Township, Michigan, USA"),
        ("Mansa Musa","1280-01-01","Mali Empire"),
        ("Cosimo de Medici","1389-09-27","Florence, Republic of Florence"),
        ("Hetty Green","1834-11-21","New Bedford, Massachusetts, USA"),
        ("John Jacob Astor","1763-07-17","Waldorf, Electoral Palatinate"),
        ("Azim Premji","1945-07-24","Bombay, British India"),
        ("Howard Hughes","1905-12-24","Humble, Texas, USA"),
    ],
    "Activist/Humanitarian": [
        ("Mahatma Gandhi","1869-10-02","Porbandar, Kathiawar Agency, British India"),
        ("Martin Luther King Jr.","1929-01-15","Atlanta, Georgia, USA"),
        ("Nelson Mandela","1918-07-18","Mvezo, Union of South Africa"),
        ("Mother Teresa","1910-08-26","Uskub, Ottoman Empire"),
        ("Harriet Tubman","1822-03-01","Dorchester County, Maryland, USA"),
        ("Frederick Douglass","1818-02-01","Talbot County, Maryland, USA"),
        ("Rosa Parks","1913-02-04","Tuskegee, Alabama, USA"),
        ("Cesar Chavez","1927-03-31","Yuma, Arizona, USA"),
        ("Desmond Tutu","1931-10-07","Klerksdorp, Union of South Africa"),
        ("Florence Nightingale","1820-05-12","Florence, Grand Duchy of Tuscany"),
        ("Sojourner Truth","1797-01-01","Swartekill, New York, USA"),
        ("Susan B. Anthony","1820-02-15","Adams, Massachusetts, USA"),
        ("Rigoberta Menchu","1959-01-09","Laj Chimel, Guatemala"),
        ("Steve Biko","1946-12-18","Tarkastad, Union of South Africa"),
        ("Thomas Sankara","1949-12-21","Yako, French Upper Volta"),
        ("Patrice Lumumba","1925-07-02","Onalua, Belgian Congo"),
        ("Ruby Bridges","1954-09-08","Tylertown, Mississippi, USA"),
        ("Malala Yousafzai","1997-07-12","Mingora, Khyber Pakhtunkhwa, Pakistan"),
    ],
    "Notorious Criminal": [
        ("Al Capone","1899-01-17","Brooklyn, New York, USA"),
        ("Pablo Escobar","1949-12-01","Rionegro, Colombia"),
        ("Lucky Luciano","1897-11-24","Lercara Friddi, Sicily, Kingdom of Italy"),
        ("Charles Manson","1934-11-12","Cincinnati, Ohio, USA"),
        ("Jesse James","1847-09-05","Kearney, Missouri, USA"),
        ("Billy the Kid","1859-11-23","New York City, New York, USA"),
        ("John Dillinger","1903-06-22","Indianapolis, Indiana, USA"),
        ("Bonnie Parker","1910-10-01","Rowena, Texas, USA"),
        ("Clyde Barrow","1909-03-24","Telico, Texas, USA"),
        ("Ned Kelly","1854-12-01","Beveridge, Victoria, British Empire"),
        ("Guy Fawkes","1570-04-13","York, Kingdom of England"),
        ("Meyer Lansky","1902-07-04","Grodno, Russian Empire"),
        ("Bugsy Siegel","1906-02-28","Brooklyn, New York, USA"),
        ("Griselda Blanco","1943-02-15","Cartagena, Colombia"),
    ],
    "Explorer": [
        ("Marco Polo","1254-09-15","Venice, Republic of Venice"),
        ("Christopher Columbus","1451-10-31","Genoa, Republic of Genoa"),
        ("Ferdinand Magellan","1480-02-04","Sabrosa, Kingdom of Portugal"),
        ("Vasco da Gama","1460-01-01","Sines, Kingdom of Portugal"),
        ("James Cook","1728-11-07","Marton, Yorkshire, Great Britain"),
        ("Roald Amundsen","1872-07-16","Borge, Norway"),
        ("Ernest Shackleton","1874-02-15","Kilkea, County Kildare, Ireland"),
        ("Amelia Earhart","1897-07-24","Atchison, Kansas, USA"),
        ("Ibn Battuta","1304-02-24","Tangier, Marinid Sultanate"),
        ("David Livingstone","1813-03-19","Blantyre, Lanarkshire, Scotland"),
        ("Sacagawea","1788-01-01","Lemhi County, Idaho, USA"),
        ("Meriwether Lewis","1774-08-18","Ivy, Virginia, USA"),
        ("William Clark","1770-08-01","Caroline County, Virginia, USA"),
        ("Francis Drake","1540-01-01","Tavistock, Devon, Kingdom of England"),
        ("Abel Tasman","1603-01-01","Lutjegast, Dutch Republic"),
    ],
    "Astronaut/Aviator": [
        ("Yuri Gagarin","1934-03-09","Klushino, Russian SFSR, Soviet Union"),
        ("Neil Armstrong","1930-08-05","Wapakoneta, Ohio, USA"),
        ("Buzz Aldrin","1930-01-20","Glen Ridge, New Jersey, USA"),
        ("Charles Lindbergh","1902-02-04","Detroit, Michigan, USA"),
        ("Valentina Tereshkova","1937-03-06","Maslennikovo, Russian SFSR, Soviet Union"),
        ("John Glenn","1921-07-18","Cambridge, Ohio, USA"),
        ("Sally Ride","1951-05-26","Los Angeles, California, USA"),
        ("Chris Hadfield","1959-08-29","Sarnia, Ontario, Canada"),
        ("Chuck Yeager","1923-02-13","Myra, West Virginia, USA"),
        ("Bessie Coleman","1892-01-26","Atlanta, Texas, USA"),
        ("Wernher von Braun","1912-03-23","Wirsitz, German Empire"),
        ("Sergei Korolev","1907-01-12","Zhytomyr, Russian Empire"),
    ],
    "Composer": [
        ("Johann Sebastian Bach","1685-03-31","Eisenach, Duchy of Saxe-Eisenach"),
        ("Wolfgang Amadeus Mozart","1756-01-27","Salzburg, Archbishopric of Salzburg"),
        ("Ludwig van Beethoven","1770-12-17","Bonn, Electorate of Cologne"),
        ("Antonio Vivaldi","1678-03-04","Venice, Republic of Venice"),
        ("Frederic Chopin","1810-03-01","Zelazowa Wola, Duchy of Warsaw"),
        ("Pyotr Ilyich Tchaikovsky","1840-05-07","Votkinsk, Russian Empire"),
        ("Johannes Brahms","1833-05-07","Hamburg, German Confederation"),
        ("Franz Schubert","1797-01-31","Himmelpfortgrund, Archduchy of Austria"),
        ("Joseph Haydn","1732-03-31","Rohrau, Archduchy of Austria"),
        ("Giuseppe Verdi","1813-10-10","Le Roncole, First French Empire"),
        ("Richard Wagner","1813-05-22","Leipzig, Kingdom of Saxony"),
        ("Claude Debussy","1862-08-22","Saint-Germain-en-Laye, Second French Empire"),
    ],
    "Artist": [
        ("Leonardo da Vinci","1452-04-15","Vinci, Republic of Florence"),
        ("Michelangelo","1475-03-06","Caprese, Republic of Florence"),
        ("Raphael","1483-03-28","Urbino, Duchy of Urbino"),
        ("Rembrandt","1606-07-15","Leiden, Dutch Republic"),
        ("Vincent van Gogh","1853-03-30","Zundert, Netherlands"),
        ("Pablo Picasso","1881-10-25","Malaga, Spain"),
        ("Claude Monet","1840-11-14","Paris, France"),
        ("Johannes Vermeer","1632-10-31","Delft, Dutch Republic"),
        ("Caravaggio","1571-09-29","Milan, Duchy of Milan"),
        ("Sandro Botticelli","1445-03-01","Florence, Republic of Florence"),
        ("Auguste Rodin","1840-11-12","Paris, France"),
        ("Salvador Dali","1904-05-11","Figueres, Spain"),
        ("Frida Kahlo","1907-07-06","Coyoacan, Mexico"),
        ("Henri Matisse","1869-12-31","Le Cateau-Cambresis, France"),
        ("Paul Cezanne","1839-01-19","Aix-en-Provence, France"),
        ("Gustav Klimt","1862-07-14","Baumgarten, Austrian Empire"),
        ("Hokusai","1760-10-31","Edo, Japan"),
    ],
    "Inventor/Engineer": [
        ("Thomas Edison","1847-02-11","Milan, Ohio, USA"),
        ("Nikola Tesla","1856-07-10","Smiljan, Austrian Empire"),
        ("Alexander Graham Bell","1847-03-03","Edinburgh, Scotland, UK"),
        ("James Watt","1736-01-19","Greenock, Renfrewshire, Scotland"),
        ("Johannes Gutenberg","1400-01-01","Mainz, Electorate of Mainz"),
        ("Guglielmo Marconi","1874-04-25","Bologna, Kingdom of Italy"),
        ("Benjamin Franklin","1706-01-17","Boston, Massachusetts Bay Colony"),
        ("Charles Babbage","1791-12-26","London, Kingdom of Great Britain"),
        ("Tim Berners-Lee","1955-06-08","London, England, UK"),
        ("Karl Benz","1844-11-25","Muhlburg, Grand Duchy of Baden"),
        ("Eli Whitney","1765-12-08","Westborough, Massachusetts, USA"),
        ("Louis Braille","1809-01-04","Coupvray, First French Empire"),
        ("Hedy Lamarr","1914-11-09","Vienna, Austria-Hungary"),
        ("Igor Sikorsky","1889-05-25","Kyiv, Russian Empire"),
        ("Rudolf Diesel","1858-03-18","Paris, Second French Empire"),
    ],
    "Architect": [
        ("Christopher Wren","1632-10-20","East Knoyle, Wiltshire, Kingdom of England"),
        ("Antoni Gaudi","1852-06-25","Reus, Spain"),
        ("Frank Lloyd Wright","1867-06-08","Richland Center, Wisconsin, USA"),
        ("Le Corbusier","1887-10-06","La Chaux-de-Fonds, Switzerland"),
        ("Filippo Brunelleschi","1377-01-01","Florence, Republic of Florence"),
        ("Andrea Palladio","1508-11-30","Padua, Republic of Venice"),
        ("Gustave Eiffel","1832-12-15","Dijon, France"),
        ("Louis Sullivan","1856-09-03","Boston, Massachusetts, USA"),
        ("Zaha Hadid","1950-10-31","Baghdad, Kingdom of Iraq"),
        ("Mimar Sinan","1488-05-09","Agirnas, Ottoman Empire"),
    ],
}

# ============================================================
# COMPUTE ALL
# ============================================================
print("="*80)
print(f"COMPUTING: {sum(len(v) for v in GROUPS.values())} charts across {len(GROUPS)} groups")
print("="*80)

all_results = {}
total = 0
errors = 0

for gname, members in GROUPS.items():
    charts = []
    for name, bday, place in members:
        c = compute_noon(name, bday, place)
        if c:
            charts.append(c)
            total += 1
        else:
            errors += 1
    all_results[gname] = charts
    if len(charts) > 0:
        print(f"  {gname:<30} {len(charts):>3}/{len(members)}")

print(f"\nComputed: {total} | Errors: {errors}")

# ============================================================
# QUICK STATS
# ============================================================
print(f"\n{'='*80}")
print("STACKED RANKING: Moon Nakshatra × Group")
print(f"{'='*80}")

for gname, charts in sorted(all_results.items(), key=lambda x: -len(x[1])):
    if len(charts) < 3: continue
    moon_naks = Counter(c['planets']['Moon']['nakshatra'] for c in charts)
    top = moon_naks.most_common(3)
    print(f"  {gname:<30} {len(charts):>3} | " + " | ".join(f"{n}({c/len(charts)*100:.0f}%)" for n,c in top))

# ============================================================
# SAVE & COMMIT
# ============================================================
dataset_out = {}
for gname, charts in all_results.items():
    dataset_out[gname] = [{"name":c['name'],"year":c['year'],
                           "moon_nak":c['planets']['Moon']['nakshatra'],
                           "moon_sign":c['planets']['Moon']['sign'],
                           "rahu_sign":c['planets']['Rahu']['sign'],
                           "sun_sign":c['planets']['Sun']['sign']} for c in charts]

with open('/home/user/dataset/historical_groups_final.json','w') as f:
    json.dump(dataset_out, f, indent=2)

print(f"\nSaved → /home/user/dataset/historical_groups_final.json")
print(f"Total historical charts: {total}")
