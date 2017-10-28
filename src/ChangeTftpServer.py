'''
Created on Oct 5, 2010

@author: t22cf3p
'''
import sys
import Queue,threading
import httplib, base64
from nyl.uc.*username*.phone import PhoneInformation
from nyl.uc.*username*.CallManager import CallManager
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
userName="*username*";
password="*password*";    
url="https://"+host+"/realtimeservice/services/RisPort";

class TftpWorkInfo(object):
    def __init__(self,tftp,ip=None):
            self.ip=ip
            self.tftp=tftp
    
    
    def __str__(self):
        return "ip="+self.ip+" newTftp="+self.tftp
    
    def hasIp(self):
        if self.ip == None or self.ip=="":
            return False
        
        return True

if sys.argv.__len__()==4:
    backout=True
else:
    backout=False
          

def do_work(phone):
    try:
        pi = PhoneInformation(phone.ip, userName, password)
        pi.ChangeTftpServer(phone.tftp, backout)
        pi.Shutdown()
    except:
        print "Unexpected error:", sys.exc_info()[0]
    return
            
            
def worker():
    while True:
        tftpWork=q.get();
        print "got work tftpWork="+tftpWork
        do_work(tftpWork)     
        print "done work tftpWork="+tftpWork
        q.task_done()


q = Queue.Queue()
phoneIps = {}
for phone in listOfPhones:
    (name,tftp) = phone.strip().split().split(",")
    phoneIps[phone.strip()]=TftpWorkInfo(tftp)
    
request=CallManager.getPhoneRequest(phoneIps)
auth = base64.encodestring('%s:%s' % ("*username*", "*password*"))[:-1]
webservice =  httplib.HTTPS(host)
webservice.set_debuglevel(0)
webservice.putrequest("POST", "/realtimeservice/services/RisPort")
webservice.putheader("Host", host)
webservice.putheader("Authorization", "Basic %s" % auth)
webservice.putheader("User-Agent", "TFTPChanger")
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
        print phoneName+"=>"+ipAddress
        #"+ButtonMap.KEY1+"|"+ButtonMap.KEY6+" "+ButtonMap.SOFT_KEY2+"

#processThreads = [] 
numThreads=min(phoneIps.__len__(),10)
for i in xrange(0,numThreads):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
    #processThreads.append(t)
  
for phoneName in phoneIps:
    if not phoneIps[phoneName].hasIp():
        print "ERROR: phoneName="+phoneName+" has no ip, can't reset"
        continue
    else:
        tftpWork=phoneIps[phoneName]
        print "START: tftpWork="+tftpWork+"\n"
        q.put(tftpWork)
       
q.join()
print "done?"
