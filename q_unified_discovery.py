#!/usr/bin/env python3
"""Unified date-only discovery screen across all available Q features."""
import csv,json,os,math
from scipy.stats import fisher_exact
OUT='outputs/q_unified_discovery';os.makedirs(OUT,exist_ok=True)
e=list(csv.DictReader(open('outputs/q_all_event_sequence_test/events.csv')));c=list(csv.DictReader(open('outputs/q_all_event_sequence_test/controls.csv')))
PL=['Saturn','Mars','Venus','Jupiter','Rahu_mean','Ketu'];features=[]
for p in PL:features += [(f'{p}_same_natal_sign','same natal sign'),(f'{p}_within_3deg','within 3 degrees'),(f'{p}_retrograde','retrograde')]
results=[]
for f,label in features:
 a=sum(x[f]=='True' for x in e);b=len(e)-a;d=sum(x[f]=='True' for x in c);cc=len(c)-d
 # Haldane correction for ratios
 rr=((a+.5)/(len(e)+1))/((d+.5)/(len(c)+1));odds,p=fisher_exact([[a,b],[d,cc]])
 results.append({'feature':f,'description':label,'event_count':a,'event_rate':a/len(e),'control_count':d,'control_rate':d/len(c),'risk_ratio_continuity_corrected':rr,'odds_ratio':odds,'fisher_p':p})
results.sort(key=lambda x:x['risk_ratio_continuity_corrected'],reverse=True)
json.dump({'events':len(e),'controls':len(c),'features_tested':len(features),'results':results,'purpose':'hypothesis discovery only','limitations':['Candidate events not fully verified','Events dominated by death/career extraction','No wealth/success/failure labels','Multiple testing not confirmatory','Controls preliminary and rows are not independent']},open(OUT+'/summary.json','w'),indent=2)
with open(OUT+'/feature_rankings.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=results[0]);w.writeheader();w.writerows(results)
print(json.dumps({'events':len(e),'controls':len(c),'top_features':results[:8]},indent=2))
