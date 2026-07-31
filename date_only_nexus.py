#!/usr/bin/env python3
"""Date-only NEXUS transit/reference-chart pipeline.

Strictly forbids birth time, Ascendant, houses, D1/D9 and other time-dependent
natal constructs. A civil date is represented by a UTC-day interval [00:00,24:00).
The midpoint is a reproducible reference instant; interval fields expose what is
stable versus uncertain across that day.
"""
from __future__ import annotations
import argparse, csv, json, math, os
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
import swisseph as swe

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PLANETS = {'Sun':swe.SUN,'Moon':swe.MOON,'Mercury':swe.MERCURY,'Venus':swe.VENUS,'Mars':swe.MARS,'Jupiter':swe.JUPITER,'Saturn':swe.SATURN,'Uranus':swe.URANUS,'Neptune':swe.NEPTUNE,'Pluto':swe.PLUTO,'Rahu_mean':swe.MEAN_NODE}
NAKSHATRAS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
NAK_SPAN = 360/27
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
SID_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

def jd(dt): return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600)
def norm(x): return x % 360
def signed_delta(a,b): return (a-b+180)%360-180
def sign(lon): return SIGNS[int(norm(lon)//30)]
def deg(lon): return norm(lon)%30
def nak(lon):
    i=int(norm(lon)//NAK_SPAN); return NAKSHATRAS[min(i,26)]
def angular(a,b): return abs(signed_delta(a,b))
def phase_angle(sun, moon): return norm(moon-sun)
def phase_name(p):
    names=['New Moon','Waxing Crescent','First Quarter','Waxing Gibbous','Full Moon','Waning Gibbous','Last Quarter','Waning Crescent']
    return names[int(((p+22.5)%360)//45)]
def tithi(p): return int(p//12)+1
def yoga(sun,moon): return int(norm(sun+moon)//(360/27))+1
def karana(p): return int(p//6)+1

def calc(julian):
    out={}
    for name,pid in PLANETS.items():
        xx,rf=swe.calc_ut(julian,pid,SID_FLAGS)
        lon=norm(xx[0]); speed=xx[3]
        out[name]={'longitude':round(lon,8),'sign':sign(lon),'degree':round(deg(lon),8),'retrograde':speed<0,'speed_deg_day':round(speed,8),'nakshatra':nak(lon)}
    # Ketu is opposite mean Rahu; not independently ephemeris-calculated.
    r=out['Rahu_mean']['longitude']; k=norm(r+180)
    out['Ketu']={'longitude':round(k,8),'sign':sign(k),'degree':round(deg(k),8),'retrograde':out['Rahu_mean']['retrograde'],'speed_deg_day':out['Rahu_mean']['speed_deg_day'],'nakshatra':nak(k)}
    return out

def aspects(pl, orb=6):
    names=list(pl); ans=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            x=angular(pl[a]['longitude'],pl[b]['longitude'])
            target=min([0,60,90,120,180], key=lambda z:abs(x-z))
            if abs(x-target)<=orb: ans.append({'a':a,'b':b,'separation':round(x,4),'aspect':target,'orb':round(abs(x-target),4)})
    return ans

def chart_for_date(date_s):
    d=datetime.strptime(date_s,'%Y-%m-%d').date()
    start=datetime(d.year,d.month,d.day,tzinfo=timezone.utc); end=start+timedelta(days=1); mid=start+timedelta(hours=12)
    a=calc(jd(start)); m=calc(jd(mid)); z=calc(jd(end))
    interval={}
    for p in m:
        vals=[a[p]['longitude'],z[p]['longitude']]
        interval[p]={'longitude_utc_00':a[p]['longitude'],'longitude_utc_24':z[p]['longitude'],'sign_at_00':a[p]['sign'],'sign_at_24':z[p]['sign'],'sign_stable':a[p]['sign']==z[p]['sign'],'retrograde_at_midpoint':m[p]['retrograde'],'retrograde_stable':a[p]['retrograde']==z[p]['retrograde']}
    sun=m['Sun']['longitude']; moon=m['Moon']['longitude']; ph=phase_angle(sun,moon)
    combust=[]
    for p in ['Mercury','Venus','Mars','Jupiter','Saturn']:
        if angular(m[p]['longitude'],sun)<=8.5: combust.append(p)
    # This is a date-only proximity proxy, not a claim that an eclipse occurred.
    eclipse_proxy = min(ph,abs(ph-180)) <= 18
    return {'date':date_s,'reference_time':'UTC noon midpoint (not birth time)','interval_utc':['00:00','24:00'],'midpoint_planets':m,'daily_interval':interval,'conjunctions_midpoint':aspects(m,orb=8),'major_aspects_midpoint':aspects(m,orb=6),'combustion_midpoint_8.5deg':combust,'lunar':{'phase_angle_deg':round(ph,6),'phase':phase_name(ph),'tithi_midpoint':tithi(ph),'tithi_is_time_sensitive':True,'yoga_midpoint':yoga(sun,moon),'yoga_is_time_sensitive':True,'karana_midpoint':karana(ph),'karana_is_time_sensitive':True,'nakshatra_midpoint':m['Moon']['nakshatra'],'nakshatra_is_time_sensitive':True,'eclipse_proximity_proxy':eclipse_proxy,'eclipse_proxy_definition':'Sun-Moon elongation <=18 degrees from New/Full Moon; not an eclipse catalogue or visibility calculation'},'limitations':['No birth time used','No Ascendant, houses, D1, D9 or time-dependent natal chart','UTC noon is a reproducible reference instant only; it is not an assumed birth time','Moon, combustion, aspects and lunar calendar fields may change within the civil date','Birth location is retained as metadata but cannot determine geocentric planetary longitude without a time']}

def load_people(path, limit):
    rows=json.load(open(path,encoding='utf8'))
    out=[]
    for i,r in enumerate(rows[:limit] if limit else rows):
        raw=r.get('birth_date','').strip(); date=''
        # datetime.strptime rejects some valid historical years without four digits;
        # parse the repository's dominant DD/MM/YYYY form explicitly.
        parts=raw.split('/')
        if len(parts)==3 and all(x.isdigit() for x in parts):
            dd,mm,yy=map(int,parts)
            if 1 <= yy <= 9999:
                try: date=f'{yy:04d}-{mm:02d}-{dd:02d}'; datetime.strptime(date,'%Y-%m-%d')
                except ValueError: date=''
        if not date:
            for fmt in ('%Y-%m-%d','%B %d, %Y'):
                try: date=datetime.strptime(raw,fmt).strftime('%Y-%m-%d'); break
                except ValueError: pass
        if not date: continue
        out.append({'person_id':r.get('id',f'BP{i+1:05d}'),'name':r.get('name',''),'birth_date':date,'birth_location':r.get('birth_city',''),'country':r.get('birth_country',''),'latitude':r.get('latitude'),'longitude':r.get('longitude'),'occupation':r.get('profession',''),'source_reliability':r.get('reliability','UNKNOWN'),'source_url':r.get('source_url',''),'birth_time_used':False})
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',default='data/births_people.json'); ap.add_argument('--out',default='outputs/date_only_nexus'); ap.add_argument('--limit',type=int,default=0); args=ap.parse_args()
    os.makedirs(args.out,exist_ok=True); people=load_people(args.input,args.limit); cache={}; rows=[]; summary=Counter()
    for n,p in enumerate(people,1):
        if p['birth_date'] not in cache: cache[p['birth_date']]=chart_for_date(p['birth_date'])
        c=cache[p['birth_date']]; mid=c['midpoint_planets'];
        row={**p,'reference_chart_date':p['birth_date'],'reference_chart_file_date':p['birth_date']+'.json','moon_sign':mid['Moon']['sign'],'moon_nakshatra':mid['Moon']['nakshatra'],'sun_sign':mid['Sun']['sign'],'lunar_phase':c['lunar']['phase'],'eclipse_proximity_proxy':c['lunar']['eclipse_proximity_proxy']}
        rows.append(row)
    summary['people']=len(rows); summary['unique_dates']=len(cache); summary['date_duplicates']=len(rows)-len(cache)
    with open(os.path.join(args.out,'people_date_only.csv'),'w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with open(os.path.join(args.out,'reference_charts_by_date.json'),'w',encoding='utf8') as f: json.dump(cache,f,ensure_ascii=False,indent=2)
    with open(os.path.join(args.out,'run_summary.json'),'w',encoding='utf8') as f: json.dump({'method':'Date-only NEXUS / transit reference charts','input':args.input,'counts':summary,'forbidden_fields':['birth_time','ascendant','houses','D1','D9'],'generated_utc':datetime.now(timezone.utc).isoformat()},f,indent=2)
    print(json.dumps({'people_processed':len(rows),'unique_birth_dates':len(cache),'output':args.out},indent=2))
if __name__=='__main__': main()
