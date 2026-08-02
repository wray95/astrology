#!/usr/bin/env python3
"""
BLIND VALIDATION ENGINE — GENERIC, OUTCOME-BLIND prediction system.
===================================================================
Built for the external blind-validation protocol: takes ONLY birth data,
computes classical Vedic indicators (Swiss Ephemeris, Lahiri, LOCKED
divisional convention from scripts/varga_conventions.py), and emits
marriage/children predictions. It contains ZERO knowledge of any person's
actual life outcomes — no tuning, no labels, no P-series results baked in.

Input : data/blind_validation_people.json (id, birth fields, gender)
Output: dataset/blind_validation_predictions.json + console report.

Rules used (all classical, transparent):
  MARRIAGE
    karaka: Venus (male) / Jupiter (female)  [repo standing rule]
    D7 7th lord: kendra + dignity points
    karaka D7: dignity + house points
    Saturn aspect/sign in 7H: penalty
    Timing: karaka Mahadasha windows ∩ Jupiter transit of 7th sign
  CHILDREN
    D5 5th lord: trikona + dignity points
    Jupiter D5: house + dignity points
    Saturn in/aspecting 5H: penalty
    Timing: Jupiter MD windows ∩ Jupiter transit of 5th sign
  Scores: 0-100 heuristic (documented weights). Probability-by-30: monotone
  mapping of score. Confidence: from component coverage + birth-time caveat.
Transits: Jupiter sidereal position sampled monthly (SE), sign-entry dates
interpolated (±1-2 months; documented approximation).
"""
import json, sys, math
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "scripts")
import swisseph as swe
from varga_conventions import SIGNS, varga_index, varga_sign

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
P7 = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
PL_IDS = {"Sun":0,"Moon":1,"Mars":4,"Mercury":2,"Jupiter":5,"Venus":3,"Saturn":6}
EXALT = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
         "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}
DEBIL = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
         "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}
OWN = {"Sun":["Leo"],"Moon":["Cancer"],"Mars":["Aries","Scorpio"],
       "Mercury":["Gemini","Virgo"],"Jupiter":["Sagittarius","Pisces"],
       "Venus":["Taurus","Libra"],"Saturn":["Capricorn","Aquarius"]}
KENDRA = (1,4,7,10); TRIKONA = (1,5,9)
NAKS = [("Ashwini","Ketu"),("Bharani","Venus"),("Krittika","Sun"),("Rohini","Moon"),
        ("Mrigashira","Mars"),("Ardra","Rahu"),("Punarvasu","Jupiter"),("Pushya","Saturn"),
        ("Ashlesha","Mercury"),("Magha","Ketu"),("Purva Phalguni","Venus"),("Uttara Phalguni","Sun"),
        ("Hasta","Moon"),("Chitra","Mars"),("Swati","Rahu"),("Vishakha","Jupiter"),
        ("Anuradha","Saturn"),("Jyeshtha","Mercury"),("Mula","Ketu"),("Purva Ashadha","Venus"),
        ("Uttara Ashadha","Sun"),("Shravana","Moon"),("Dhanishtha","Mars"),("Shatabhisha","Rahu"),
        ("Purva Bhadrapada","Jupiter"),("Uttara Bhadrapada","Saturn"),("Revati","Mercury")]
VIM_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YRS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NOW = datetime(2026, 8, 3, tzinfo=timezone.utc)

def jd_of(person):
    dt = datetime(int(person["birth_date"][:4]), int(person["birth_date"][5:7]),
                  int(person["birth_date"][8:10]), int(person["birth_time"][:2]),
                  int(person["birth_time"][3:5]), int(person["birth_time"][6:8]),
                  tzinfo=timezone(timedelta(hours=person["tz"])))
    utc = dt.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)

def sidereal(jd, pid):
    lt, _ = swe.calc_ut(jd, pid)
    return (lt[0] - swe.get_ayanamsa(jd)) % 360

def chart(person):
    jd = jd_of(person)
    houses_ex = swe.houses_ex(jd, person["birth_lat"], person["birth_lon"], b"A")
    asc_trop = houses_ex[0][0]
    asc = (asc_trop - swe.get_ayanamsa(jd)) % 360
    li = int(asc // 30)
    pl = {}
    for pn in P7:
        lon = sidereal(jd, PL_IDS[pn])
        pl[pn] = {"lon": lon, "sign": SIGNS[int(lon // 30)],
                  "house": (int(lon // 30) - li) % 12 + 1}
    return {"jd": jd, "lagna": SIGNS[li], "lagna_idx": li, "asc_lon": asc, "planets": pl}

def dignity(pn, sign):
    if sign == EXALT.get(pn): return 100
    if sign in OWN.get(pn, []): return 75
    if sign == DEBIL.get(pn): return -100
    return 0

def varga(ch, n):
    asc_lon = ch["asc_lon"]                     # REAL ascendant longitude
    v = {"asc_idx": varga_index(asc_lon, n)}
    for pn in P7:
        idx = varga_index(ch["planets"][pn]["lon"], n)
        v[pn] = {"sign": SIGNS[idx], "idx": idx,
                 "house": (idx - v["asc_idx"]) % 12 + 1,
                 "dignity": dignity(pn, SIGNS[idx])}
    return v

def vimshottari(jd):
    moon = sidereal(jd, 1)
    nak = int(moon // (360/27))
    lord = NAKS[nak][1]
    span = 360/27
    frac = (moon % span) / span
    li = VIM_ORDER.index(lord)
    mds = []
    t0 = jd
    for k in range(18):   # 2 full cycles so far-future windows are represented
        lord_k = VIM_ORDER[(li + k) % 9]
        yrs = VIM_YRS[lord_k] * (1 - frac if k == 0 else 1)
        mds.append({"lord": lord_k, "start_jd": t0, "years": yrs})
        t0 += yrs * 365.25
    return mds

def md_windows(mds, lord, until=2055):
    wins = []
    for m in mds:
        if m["lord"] != lord: continue
        s = datetime(2000,1,1,tzinfo=timezone.utc) + timedelta(days=(m["start_jd"] - 2451545.0))
        e = s + timedelta(days=m["years"]*365.25)
        wins.append({"start": s, "end": e})
    return wins

def fmt(dt):
    return dt.strftime("%Y-%m") if dt else None

def next_window(wins, transit_str=None, anchor=NOW):
    """First karaka-MD window still active/future; combine with transit."""
    future = [w for w in wins if w["end"] >= anchor]
    if not future:
        return None, "karaka MD ended and no return within horizon"
    w = future[0]
    start = w["start"] if w["start"] > anchor else anchor
    if transit_str:
        ty, tm = int(transit_str[:4]), int(transit_str[5:7])
        tdt = datetime(ty, tm, 1, tzinfo=timezone.utc)
        if tdt > start:
            start = tdt
    if start > w["end"]:
        return None, "MD and transit windows do not overlap in horizon"
    return {"start": fmt(start), "end": fmt(w["end"])}, None

def jupiter_sign_entries(target_sign_idx, from_date=NOW, months=72):
    """First entry of sidereal Jupiter into target sign (approx, ±1-2 months)."""
    jd0 = swe.julday(from_date.year, from_date.month, from_date.day, 0)
    for k in range(1, months):
        jd = jd0 + k*30.44
        lon = sidereal(jd, 5)
        if int(lon // 30) == target_sign_idx:
            d = datetime(2000,1,1,tzinfo=timezone.utc) + timedelta(days=jd-2451545.0)
            return d.strftime("%Y-%m")
    return None

def predict(person):
    ch = chart(person)
    d7 = varga(ch, 7); d5 = varga(ch, 5)
    mds = vimshottari(ch["jd"])
    gender = person.get("gender", "M")
    karaka = "Venus" if gender == "M" else "Jupiter"
    lagna_idx = ch["lagna_idx"]

    # ---- MARRIAGE ----
    s7l_sign = SIGNS[(d7["asc_idx"] + 6) % 12]
    s7l = next(p for p in P7 if s7l_sign in OWN.get(p, []))
    m = 0; reasons = []
    if d7[s7l]["house"] in KENDRA:
        m += 20; reasons.append(f"D7 7L({s7l}) in kendra (+20)")
    if d7[s7l]["dignity"] >= 75:
        m += 15; reasons.append(f"D7 7L {s7l} dignified (+15)")
    if d7[karaka]["dignity"] >= 75:
        m += 15; reasons.append(f"D7 {karaka} dignified (+15)")
    if d7[karaka]["house"] in KENDRA:
        m += 15; reasons.append(f"D7 {karaka} in kendra (+15)")
    if d7["Saturn"]["house"] == 7 or (d7["Saturn"]["house"] == 1):
        m -= 10; reasons.append("D7 Saturn 7H/1H penalty (-10)")
    if ch["planets"]["Saturn"]["house"] == 7:
        m -= 10; reasons.append("D1 Saturn 7H penalty (-10)")
    m = max(0, min(100, m))
    kar_wins = md_windows(mds, karaka)
    j7 = jupiter_sign_entries((lagna_idx + 6) % 12)
    mwin, mnote = next_window(kar_wins, j7)
    p30 = round(min(0.95, max(0.05, m / 100.0 * 0.9 + 0.05)), 3)

    # ---- CHILDREN ----
    s5l_sign = SIGNS[(d5["asc_idx"] + 4) % 12]
    s5l = next(p for p in P7 if s5l_sign in OWN.get(p, []))
    c = 0; creasons = []
    if d5[s5l]["house"] in TRIKONA:
        c += 20; creasons.append(f"D5 5L({s5l}) in trikona (+20)")
    if d5[s5l]["dignity"] >= 75:
        c += 15; creasons.append(f"D5 5L {s5l} dignified (+15)")
    if d5["Jupiter"]["dignity"] >= 75:
        c += 15; creasons.append("D5 Jupiter dignified (+15)")
    if d5["Jupiter"]["house"] in (4, 5):
        c += 15; creasons.append(f"D5 Jupiter H{d5['Jupiter']['house']} (+15)")
    if d5["Saturn"]["house"] == 5:
        c -= 10; creasons.append("D5 Saturn 5H penalty (-10)")
    if ch["planets"]["Saturn"]["house"] == 5:
        c -= 10; creasons.append("D1 Saturn 5H penalty (-10)")
    c = max(0, min(100, c))
    jup_wins = md_windows(mds, "Jupiter")
    j5 = jupiter_sign_entries((lagna_idx + 4) % 12)
    cwin, cnote = next_window(jup_wins, j5)
    cp30 = round(min(0.95, max(0.05, c / 100.0 * 0.9 + 0.05)), 3)

    conf = round(0.5 + 0.15 * (len(reasons) + len(creasons)) / 10, 2)
    return {
        "id": person["id"], "name": person["name"],
        "marriage": {"score": m, "probability_by_30": p30, "window": mwin,
                     "window_note": mnote, "karaka": karaka,
                     "karaka_md_windows": [{"start": fmt(w["start"]), "end": fmt(w["end"])} for w in kar_wins],
                     "jupiter_7th_transit": j7, "reasons": reasons},
        "children": {"score": c, "probability_by_30": cp30, "window": cwin,
                     "window_note": cnote,
                     "jupiter_md_windows": [{"start": fmt(w["start"]), "end": fmt(w["end"])} for w in jup_wins],
                     "jupiter_5th_transit": j5, "reasons": creasons},
        "confidence": conf,
        "caveats": ["±1-2mo transit approximation", "birth-time ±1h untested",
                    "Vimshottari from Moon nakshatra (Lahiri)"]
    }

if __name__ == "__main__":
    people = json.load(open("data/blind_validation_people.json"))["people"]
    out = []
    for p in people:
        r = predict(p)
        out.append(r)
        print(f"\n{'='*64}\n{r['id']} {r['name']}  (gender {p['gender']}, conf {r['confidence']})")
        print(f"  MARRIAGE  score={r['marriage']['score']}  p(by30)={r['marriage']['probability_by_30']}  window={r['marriage']['window']}")
        for x in r["marriage"]["reasons"]: print(f"      + {x}")
        print(f"  CHILDREN  score={r['children']['score']}  p(by30)={r['children']['probability_by_30']}  window={r['children']['window']}")
        for x in r["children"]["reasons"]: print(f"      + {x}")
    json.dump({"engine_version": "blind_v1", "generated": NOW.isoformat(),
               "predictions": out}, open("dataset/blind_validation_predictions.json", "w"), indent=1)
    print("\nWrote dataset/blind_validation_predictions.json")
