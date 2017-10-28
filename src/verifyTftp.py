'''
Created on Oct 6, 2010

@author: t22cf3p
'''

import sys
import Queue
import threading
import httplib, base64
from nyl.uc.cuae.CallManager import CallManager
from nyl.uc.cuae.phone import PhoneInformation
from xml.dom import minidom

if sys.argv.__len__() < 3:
    print "verifyTftp.py [hostname] [filename]"
    sys.exit(1)
    
    
filename = sys.argv[2]
try:
    listOfPhones = open(filename,'r')
except:
    print "Error opening filename="+filename, sys.exc_info()[0]
    sys.exit(1)
    
    
host=sys.argv[1]
userName="";
password="";
url="https://"+host+"/realtimeservice/services/RisPort";


def do_work(ip):
#    try:
    phone = PhoneInformation(ip, userName, password)
    phone.GetDeviceInformation()
    phone.GetNetworkInformation()
    print "TFTPInfo: device="+phone.device["HostName"] +" tftpserver1="+ phone.network["TFTPServer1"] +" versionID="+phone.device["versionID"]+" appLoadID="+phone.device["appLoadID"]+" bootLoadID="+phone.device["bootLoadID"]
#    except:
#        print "Unexpected error:", sys.exc_info()[0]
    return
            
            
def worker():
    while True:
        ip=q.get();
        do_work(ip)     
        q.task_done()


q = Queue.Queue()
phoneIps = {}
for phone in listOfPhones:
    (name,tftp) = phone.strip().split().split(",")
    phoneIps[name]=None
    
    
request=CallManager.getPhoneRequest(phoneIps)
auth = base64.encodestring('%s:%s' % ("cuae", "1qazXSW@"))[:-1]
webservice =  httplib.HTTPS(host)
webservice.set_debuglevel(0)
webservice.putrequest("POST", "/realtimeservice/services/RisPort")
webservice.putheader("Host", host)
webservice.putheader("Authorization", "Basic %s" % auth)
webservice.putheader("User-Agent", "AXL")
webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
webservice.putheader("Content-length", "%d" % len(request))
webservice.putheader("SOAPAction", "\"SelectCmDevice\"")
webservice.endheaders()
webservice.send(request)
statuscode, statusmessage, header = webservice.getreply()

response = webservice.getfile().read()
webservice.close()
xmldoc = minidom.parseString(response)

for xmlPhoneNode in xmldoc.getElementsByTagName('CmDevices'):
    for xmlPhone in xmlPhoneNode.childNodes:
        phoneName=xmlPhone.getElementsByTagName('Name')[0].firstChild.nodeValue
        ipAddress=xmlPhone.getElementsByTagName('IpAddress')[0].firstChild.nodeValue
        phoneIps[phoneName]=ipAddress
        #print phoneName+"=>"+ipAddress

processThreads = [] 
for i in xrange(0,8):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
    processThreads.append(t)
    

for phoneName in phoneIps:
    if phoneIps[phoneName] == None:
        print "ERROR: phoneName="+phoneName+" has no ip, can't check\n"
        continue
    else:
        ip=phoneIps[phoneName]
        q.put(ip)
       
q.join()
print "done"
