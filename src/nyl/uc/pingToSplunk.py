'''
Created on Aug 9, 2012

@author: T22CF3P
'''

import re
import time

plog = open ("./full_pings.log","r")
spout = open("/tmp/splunk_rtt_log.txt","a+")


cutoff="";
for line in plog:
    if str(line).startswith("Wed") or str(line).startswith("Thu"):
        cutoff=str(line).strip()
        continue

cutoff = time.mktime(time.strptime(cutoff, "%c"))
plog.seek(0)
ts=""
for line in plog:
    if str(line).startswith("Wed") or str(line).startswith("Thu"):
        ts=str(line).strip()
        continue
 
    if ts=="":
        continue;
     
    ts = time.mktime(time.strptime(ts, "%c"))
    if ts<cutoff:
        continue
        
    info = re.match("^(?P<hostname>[^\s]+) is (?P<status>\w+)( \((?P<rtt>[0-9.]+) ms\))?$",line)
    if info.group('rtt') == None:
        rtt="-1"
    else:
        rtt=info.group('rtt')
    print "%s pinged_host=%s status=%s rtt=%s\n" % (ts,
                                                          info.group('hostname'),
                                                          info.group('status'),
                                                          info.group('rtt'))
    #spout.write("%s pinged_host=%s status=%s rtt=%s\n" % (ts, info.group('hostname'),info.group('status'),info.group('rtt')))
