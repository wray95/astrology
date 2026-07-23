#!/usr/bin/env python3
"""Senath (Drik-link person, 14/05/2001, Houston proxy) - Navamsa (D9) + vargottama check.
Reuses the SAME Lahiri/ascendant formula from compute_lagna.py so results are consistent
with the existing Lagna/house module. Outputs D1->D9 for Lagna + 9 planets, vargottama flags.
"""
import math, datetime, json

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
# Senath Drik sidereal longitudes (sign index*30 + deg)
PLANETS = {
    "Sun":     1*30 + 0.232,    # Taurus 0.232
    "Moon":    9*30 + 24.326,   # Capricorn 24.326
    "Mars":    8*30 + 5.103,    # Sagittarius 5.103
    "Mercury": 1*30 + 20.779,   # Taurus 20.779
    "Jupiter": 1*30 + 22.635,   # Taurus 22.635
    "Venus":  11*30 + 17.27,    # Pisces 17.27
    "Saturn":  1*30 + 9.103,    # Taurus 9.103
    "Rahu":    2*30 + 14.717,   # Gemini 14.717
    "Ketu":    8*30 + 14.717,   # Sagittarius 14.717
}

def jd_from_utc(y,m,d,hh,mm,ss):
    if m<=2: y-=1; m+=12
    A=y//100; B=2-A+A//4
    f=(hh+(mm+ss/60.0)/60.0)/24.0
    return int(365.25*(y+4716))+int(30.6001*(m+1))+d+B-1524.5+f

def lahiri_ayanamsa(jd):
    days=jd-2415020.5; years=days/365.25
    return 22+27/60+59.92/3600+years*(50.2388475/3600)

def obliquity(jd):
    T=(jd-2451545.0)/36525.0
    return 23.4392911-0.0130041667*T-0.0000001639*T*T+0.0000005036*T*T*T

def local_sidereal(jd,lon_east):
    T=(jd-2451545.0)/36525.0
    gmst=(280.46061837+360.98564736629*(jd-2451545.0)+0.000387933*T*T-T*T*T/38710000.0)%360.0
    return (gmst+lon_east)%360.0

def ascendant_sidereal(jd,lat,lon_east):
    ramc=local_sidereal(jd,lon_east); eps=obliquity(jd)
    a=math.radians(ramc); phi=math.radians(lat); e=math.radians(eps)
    num=math.cos(a); den=-math.sin(a)*math.cos(e)+math.tan(phi)*math.sin(e)
    asc=math.degrees(math.atan2(num,den))%360.0
    target=(ramc+90.0)%360.0
    if abs((asc-target+180)%360-180)>90: asc=(asc+180)%360
    ay=lahiri_ayanamsa(jd)
    return (asc-ay)%360.0

def d9_sign(lon):
    s=int(lon//30)%12; d=lon%30
    n=int(d//(30.0/9.0))   # navamsa index 0..8
    if s%2==0:  # odd sign (Aries=0): forward
        return (s+n)%12, n
    else:       # even sign: reverse
        return (s-n)%12, n

# ---- Senath Houston proxy ----
# 14/05/2001 16:08:40 local, UTC-5 (astro-seek link) -> UTC 21:08:40
lat, lon_east = 29.75, -95.3667
jd = jd_from_utc(2001,5,14,21,8,40)
lagna_lon = ascendant_sidereal(jd, lat, lon_east)
lagna_d1 = int(lagna_lon//30)%12

print(f"JD={jd:.5f}  Ayanamsa={lahiri_ayanamsa(jd):.4f}")
print(f"Lagna sidereal = {lagna_lon:.3f}  -> {SIGNS[lagna_d1]} (deg {lagna_lon%30:.3f})")
print()
print(f"{'Body':8} {'D1 sign':10} {'D1°':>7} {'Nav#':>5} {'D9 sign':10} {'Vargottama':>11}")
print("-"*60)

rows=[]
lagna_d9, lagna_n = d9_sign(lagna_lon)
rows.append(("Lagna", lagna_d1, lagna_lon%30, lagna_n, lagna_d9))
for p,lon in PLANETS.items():
    d1=int(lon//30)%12; d=lon%30; d9,n=d9_sign(lon)
    rows.append((p,d1,d,d9,n))

for name,d1,d,d9,n in rows:
    vg = "YES" if d1==d9 else "-"
    print(f"{name:8} {SIGNS[d1]:10} {d:7.2f} {n+1:5} {SIGNS[d9]:10} {vg:>11}")

# Explicit focus lines
print()
lg_vg = "VARGOTTAMA" if lagna_d1==lagna_d9 else "not vargottama"
print(f">> VIRGO LAGNA: D1={SIGNS[lagna_d1]} , D9={SIGNS[lagna_d9]}  -> {lg_vg}")
rd1=int(PLANETS['Rahu']//30)%12; rd9,_=d9_sign(PLANETS['Rahu'])
jd1=int(PLANETS['Jupiter']//30)%12; jd9,_=d9_sign(PLANETS['Jupiter'])
print(f">> RAHU (now AD): D1={SIGNS[rd1]} , D9={SIGNS[rd9]}  -> {'VARGOTTAMA' if rd1==rd9 else 'not'}")
print(f">> GURU (next AD): D1={SIGNS[jd1]} , D9={SIGNS[jd9]}  -> {'VARGOTTAMA' if jd1==jd9 else 'not'}")
