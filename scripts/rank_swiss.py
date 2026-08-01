import json

with open('dataset/p1p9_swiss.json') as f:
    charts = json.load(f)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SL = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'}

# CROSS-VALIDATION
print("=" * 100)
print("CROSS-VALIDATION: Swiss Ephemeris vs Drik Panchang")
print("=" * 100)
drik = {
    "P3": {"moon_nak": "Mula", "moon_lord": "Ketu", "asc": "Pisces"},
    "P5": {"moon_nak": "Shravana", "moon_lord": "Moon", "asc": "Virgo"},
    "P6": {"moon_nak": "Jyeshtha", "moon_lord": "Mercury", "asc": "Libra"},
    "P8": {"moon_nak": "Vishakha", "moon_lord": "Jupiter"},
    "P9": {"moon_nak": "Magha", "moon_lord": "Ketu", "asc": "Aries"},
}
tp, tf = 0, 0
for pid, ref in drik.items():
    c = charts[pid]
    for k, v in ref.items():
        got = c["asc"] if k == "asc" else c["dasha"][k]
        ok = (got == v)
        if ok: tp += 1
        else: tf += 1
        print(f"  {pid} {k:12s}: swiss={got:15s} drik={v:15s} {'OK' if ok else 'MISMATCH'}")

print(f"  Pass: {tp}/{tp+tf} ({100*tp/(tp+tf):.0f}%)")

# COMPUTE NEXUS
for pid, c in charts.items():
    p = c["planets"]
    h = lambda x: p[x]["house"]
    d = lambda x: p[x]["dignity"]
    sc = 0
    yoga_names = []

    # Mahapurusha
    mp_map = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavaya", "Saturn": "Sasa"}
    for pl, yname in mp_map.items():
        if d(pl) >= 75 and h(pl) in {1, 4, 7, 10}:
            sc += 25
            yoga_names.append("MP:" + yname + "(" + pl + " H" + str(h(pl)) + ")")

    # NBRY
    for pl in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if d(pl) == -100:
            lord = SL[p[pl]["sign"]]
            conds = []
            if lord in p and h(lord) in {1, 4, 7, 10}:
                conds.append("C1")
                sc += 20
            if h(pl) in {1, 4, 7, 10}:
                conds.append("C5")
                sc += 15
            if conds:
                yoga_names.append("NBRY:" + pl + "(" + ",".join(conds) + ")")

    # Dhana
    ai = SIGNS.index(c["asc"])
    lords = {}
    for hl in range(1, 13):
        lords[hl] = SL[SIGNS[(ai + hl - 1) % 12]]
    dh = 0
    for h1, h2 in [(1, 2), (1, 11), (2, 11), (5, 9)]:
        l1, l2 = lords[h1], lords[h2]
        if l1 in p and l2 in p and abs(h(l1) - h(l2)) in {0, 1, 7}:
            dh += 1
            sc += 10
    if dh:
        yoga_names.append("Dhana(" + str(dh) + ")")

    # DKA
    if lords[9] in p and lords[10] in p and abs(h(lords[9]) - h(lords[10])) in {0, 1, 7}:
        sc += 25
        yoga_names.append("DKA")

    nexus = max(0, round(c["d1_avg"] * 0.5 + c["d9_avg"] * 0.3 + sc * 0.2 + 25, 1))
    c["nexus"] = nexus
    c["yogas"] = yoga_names

# RANK
sorted_c = sorted(charts.items(), key=lambda x: x[1]["nexus"], reverse=True)

print()
print("=" * 130)
print("P1-P9 FINAL RANKING — Swiss Ephemeris (Lahiri + Whole Sign + MD-lord-first AD)")
print("=" * 130)
header = f"{'Rk':3s} | {'ID':4s} | {'Name':22s} | {'NEX':>4s} | {'D1':>3s} | {'D9':>3s} | {'$':>5s} | {'Car':>5s} | {'Asc':10s} | {'MD':8s} | {'AD':8s} | {'Archetype':30s} | {'Key Yogas'}"
print(header)
print("-" * 130)

arc = {"P1": "Warlord", "P2": "Enigma*", "P3": "Sage", "P4": "Empress", "P5": "Titan", "P6": "Fighter", "P7": "Phoenix*", "P8": "Oracle", "P9": "Sovereign"}
w = {"P1": "4.0", "P2": "3.0*", "P3": "2.0", "P4": "5.0", "P5": "5.0", "P6": "3.5", "P7": "4.0*", "P8": "4.5", "P9": "3.5"}
cr_val = {"P1": "5.0", "P2": "3.0*", "P3": "2.0", "P4": "5.0", "P5": "4.0", "P6": "4.0", "P7": "4.0*", "P8": "4.5", "P9": "4.0"}

for rank, (pid, c) in enumerate(sorted_c, 1):
    yogas = ", ".join(c.get("yogas", [])[:3])
    print(f"{rank:<3d} | {pid:4s} | {c['name']:22s} | {c['nexus']:>4.0f} | {c['d1_avg']:>3.0f} | {c['d9_avg']:>3.0f} | {w[pid]:>5s} | {cr_val[pid]:>5s} | {c['asc']:10s} | {(c['current_md'] or '?'):8s} | {(c['current_ad'] or '?'):8s} | {arc[pid]:30s} | {yogas}")

# D9 Jupiter
print()
print("=" * 100)
print("D9 JUPITER CHECK (inner wisdom confirmation)")
print("=" * 100)
for pid, c in sorted_c:
    jd9 = c["d9"].get("Jupiter", {}).get("dignity", 0)
    tag = ""
    if jd9 == 100: tag = "EXALTED"
    elif jd9 == -100: tag = "DEBILITATED"
    elif jd9 == 75: tag = "OWN"
    print(f"  {pid} {c['name']:22s} Jupiter D9: {jd9:+d} {tag}")

with open("dataset/p1p9_swiss_ranked.json", "w") as f:
    json.dump(dict(sorted_c), f, indent=2)
print("\nSaved to dataset/p1p9_swiss_ranked.json")
