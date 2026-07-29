#!/usr/bin/env python3
import csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from date_only_nexus import chart_for_date
src='research/events/documented_events.csv'; out='outputs/saturn_transit_event_screen.csv'
rows=[]
for r in csv.DictReader(open(src,encoding='utf8')):
    c=chart_for_date(r['event_date']); s=c['midpoint_planets']['Saturn']; i=c['daily_interval']['Saturn']
    rows.append({**r,'saturn_sign':s['sign'],'saturn_degree':s['degree'],'saturn_longitude':s['longitude'],'saturn_speed_deg_day':s['speed_deg_day'],'saturn_retrograde_midpoint':s['retrograde'],'saturn_retrograde_stable_for_utc_day':i['retrograde_stable'],'saturn_sign_stable_for_utc_day':i['sign_stable']})
os.makedirs('outputs',exist_ok=True)
with open(out,'w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('events_screened',len(rows),'retrograde_midpoint',sum(x['saturn_retrograde_midpoint'] for x in rows))
