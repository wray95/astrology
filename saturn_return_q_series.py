#!/usr/bin/env python3
"""Date-only Saturn-return cohort analysis.

Excludes the separately maintained P1-P9 names. Labels every remaining source
record Q1..Qn. No birth time, Ascendant, houses, D1 or D9 are used.
"""
import csv, json, os, sys
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(__file__))
from date_only_nexus import load_people, chart_for_date
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

P_NAMES={"polgahawela bappa","upulakshi","senith","niromi","senath","dewli","sineth","lakshi amma","lalith uncle"}
def ang(a,b): return abs((a-b+180)%360-180)
def sat_lon(ds):
    # Saturn-only calculation for speed; UTC noon is the date-only midpoint.
    j=swe.julday(ds.year,ds.month,ds.day,12.0)
    xx,_=swe.calc_ut(j,swe.SATURN,swe.FLG_SWIEPH|swe.FLG_SIDEREAL|swe.FLG_SPEED)
    return xx[0] % 360
def find_return(birth, natal_lon, lo, hi):
    # Daily midpoint grid; minimum angular distance is a date-only return estimate.
    start=birth+timedelta(days=round(lo*365.2425)); end=birth+timedelta(days=round(hi*365.2425))
    # Coarse scan followed by a local daily refinement: Saturn is slow, so this
    # is equivalent for a date-only return estimate but avoids millions of calls.
    best=None; d=start
    while d<=end:
        lon=sat_lon(d); err=ang(lon,natal_lon); cand=(err,d,lon)
        if best is None or cand[0]<best[0]: best=cand
        d+=timedelta(days=10)
    center=best[1]; best=None; d=max(start,center-timedelta(days=20)); stop=min(end,center+timedelta(days=20))
    while d<=stop:
        lon=sat_lon(d); err=ang(lon,natal_lon); cand=(err,d,lon)
        if best is None or cand[0]<best[0]: best=cand
        d+=timedelta(days=1)
    err,d,lon=best
    return {'date':d.isoformat(),'age_years':round((d-birth).days/365.2425,3),'saturn_longitude':round(lon,6),'angular_error_deg':round(err,6),'window_years':[lo,hi]}
def main():
    out='outputs/saturn_returns_q_series'; os.makedirs(out,exist_ok=True)
    people=load_people('data/births_people.json',0)
    excluded=[]; q=[]
    for p in people:
        if p['name'].strip().lower() in P_NAMES: excluded.append(p); continue
        q.append(p)
    rows=[]; charts={}; sign_counts={}
    for i,p in enumerate(q,1):
        birth=date.fromisoformat(p['birth_date']); c=chart_for_date(p['birth_date']); s=c['midpoint_planets']['Saturn']; natal=s['longitude']
        r1=find_return(birth,natal,25,35); r2=find_return(birth,natal,54,65)
        row={'q_id':f'Q{i}','source_person_id':p['person_id'],'name':p['name'],'birth_date':p['birth_date'],'birth_location':p.get('birth_location',''),'country':p.get('country',''),'occupation':p.get('occupation',''),'source_reliability':p.get('source_reliability','UNKNOWN'),'birth_time_used':False,'natal_saturn_longitude_utc_noon':natal,'natal_saturn_sign':s['sign'],'natal_saturn_degree':s['degree'],'natal_saturn_retrograde_at_midpoint':s['retrograde'],'first_return':r1,'second_return':r2,'event_data_available':False,'prediction_status':'Research-only; no person-linked event timeline available'}
        rows.append(row); charts[row['q_id']]=row; sign_counts[s['sign']]=sign_counts.get(s['sign'],0)+1
    fields=['q_id','source_person_id','name','birth_date','birth_location','country','occupation','source_reliability','birth_time_used','natal_saturn_longitude_utc_noon','natal_saturn_sign','natal_saturn_degree','natal_saturn_retrograde_at_midpoint','first_return_date','first_return_age_years','first_return_error_deg','second_return_date','second_return_age_years','second_return_error_deg','event_data_available','prediction_status']
    with open(os.path.join(out,'q_saturn_returns.csv'),'w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for x in rows:
            w.writerow({'q_id':x['q_id'],'source_person_id':x['source_person_id'],'name':x['name'],'birth_date':x['birth_date'],'birth_location':x['birth_location'],'country':x['country'],'occupation':x['occupation'],'source_reliability':x['source_reliability'],'birth_time_used':False,'natal_saturn_longitude_utc_noon':x['natal_saturn_longitude_utc_noon'],'natal_saturn_sign':x['natal_saturn_sign'],'natal_saturn_degree':x['natal_saturn_degree'],'natal_saturn_retrograde_at_midpoint':x['natal_saturn_retrograde_at_midpoint'],'first_return_date':x['first_return']['date'],'first_return_age_years':x['first_return']['age_years'],'first_return_error_deg':x['first_return']['angular_error_deg'],'second_return_date':x['second_return']['date'],'second_return_age_years':x['second_return']['age_years'],'second_return_error_deg':x['second_return']['angular_error_deg'],'event_data_available':False,'prediction_status':x['prediction_status']})
    with open(os.path.join(out,'q_saturn_returns.json'),'w',encoding='utf8') as f: json.dump({'method':'Date-only Saturn return analysis','rules':['Q series excludes separately maintained P1-P9 names','UTC noon is midpoint reference, not birth time','return dates are nearest daily midpoint to natal Saturn longitude','no houses, Ascendant, D1, D9 or birth times'],'excluded_p_records':excluded,'records':rows},f,ensure_ascii=False,indent=2)
    summary={'q_people':len(rows),'excluded_named_p_records_in_source':len(excluded),'natal_saturn_sign_counts':dict(sorted(sign_counts.items())),'event_timeline_records_linked':0,'return_precision':'date-only nearest daily UTC-noon estimate; not an exact time','generated_utc':datetime.now(timezone.utc).isoformat()}
    with open(os.path.join(out,'run_summary.json'),'w',encoding='utf8') as f: json.dump(summary,f,indent=2)
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
