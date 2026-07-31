#!/usr/bin/env python3
import csv,json,os
from datetime import date
from date_only_nexus import chart_for_date
P=[('P1','Polgahawela Bappa','1962-05-27'),('P2','Upulakshi','1997-03-14'),('P3','Senith','1995-08-07'),('P4','Niromi','1967-04-25'),('P5','Senath','2001-05-14'),('P6','Dewli','2005-10-08'),('P7','Sineth','2005-04-05'),('P8','Lakshi Amma','1963-11-16'),('P9','Lalith Uncle','1970-08-31')]
EX={'Sun':'Aries','Moon':'Taurus','Mars':'Capricorn','Mercury':'Virgo','Jupiter':'Cancer','Venus':'Pisces','Saturn':'Libra'}
out='outputs/p_date_only_reanalysis';os.makedirs(out,exist_ok=True);rows=[]
for pid,name,d in P:
 c=chart_for_date(d);m=c['midpoint_planets']; ex=[x for x,s in EX.items() if m[x]['sign']==s]
 row={'p_id':pid,'name':name,'birth_date':d,'exalted_planets_sign_only':'|'.join(ex) or 'None','exalted_count':len(ex),'saturn_sign':m['Saturn']['sign'],'saturn_degree':m['Saturn']['degree'],'saturn_return_status':'separate date-only Saturn-return file'}
 for x in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']:row[f'{x}_sign']=m[x]['sign'];row[f'{x}_degree']=m[x]['degree']
 rows.append(row)
with open(out+'/p_date_only_positions.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
json.dump({'method':'Date-only P-series reanalysis','records':len(rows),'event_evidence_for_P':0,'ranking_change_from_Q_transit_data':'none_supported','reason':'Q event candidates have no verified outcomes and no P-linked event timeline'},open(out+'/summary.json','w'),indent=2)
print(json.dumps({'records':len(rows),'event_evidence_for_P':0},indent=2))
