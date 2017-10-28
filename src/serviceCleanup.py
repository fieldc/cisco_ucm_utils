'''
Created on Feb 29, 2012


@author: t22cf3p
'''

import httplib
import sys
from xml.dom import minidom


if __name__ == '__main__':
    pass
profileList  = ("")

for profName in profileList: 
    print "Processing name: "+profName
    request="""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/8.0">
       <soapenv:Body>
          <ns:getDeviceProfile sequence="1">
             <name>%s</name>
          </ns:getDeviceProfile>
       </soapenv:Body>
    </soapenv:Envelope>
    """ % (profName)
    
    webservice =  httplib.HTTPS("x.x.x.x:8443")
    webservice.set_debuglevel(1)
    webservice.putrequest("POST", "/axl/")
    webservice.putheader("Host", "x.x.x.x:8443")
    webservice.putheader("User-Agent", "NYL Configurator")
    webservice.putheader("Authorization","Basic Y3VhZToxcWF6WFNXQA==")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(request))
    webservice.putheader("SOAPAction","\"CUCM:DB ver=8.0 getDeviceProfile\"")
    webservice.endheaders()
    
    webservice.send(request)
     
    statuscode, statusmessage, header = webservice.getreply()
    print "Response: statuscode="+str(statuscode)+" statusmessage="+statusmessage+"\n"
    if statuscode!=200:
        print "Error Processing "+profName
        continue;
    
    print "headers: "+str(header)+"\n"
    res = webservice.getfile().read()
    print "response text: res="+res+"\n"
    
    xmldoc = minidom.parseString(res)
    uuid = (xmldoc.getElementsByTagName('deviceProfile')[0]).getAttribute('uuid')
    
    print "response uuid="+(xmldoc.getElementsByTagName('deviceProfile')[0]).getAttribute('uuid')+"\n"
    print str((xmldoc.getElementsByTagName('deviceProfile')[0]).getElementsByTagName("services"))+"\n"
    
    serviceNameList = {}
    serviceList=""
    
    for node in (xmldoc.getElementsByTagName('deviceProfile')[0]).getElementsByTagName("service"):
        print node.getElementsByTagName('name')[0].firstChild.nodeValue
        if node.getElementsByTagName('name')[0].firstChild.nodeValue == "Login":
            nodeStr = str(node.toxml())
            nodeStr = nodeStr.replace("<urlLabel/>", "<urlLabel>Login</urlLabel>")
            nodeStr = nodeStr.replace("<urlLabelAscii/>", "<urlLabelAscii>Login</urlLabelAscii>")
            serviceNameList[node.getElementsByTagName('name')[0].firstChild.nodeValue] = nodeStr
        else:
            serviceNameList[node.getElementsByTagName('name')[0].firstChild.nodeValue] = str(node.toxml())
        
    for svc in serviceNameList:
        serviceList += serviceNameList[svc]+"\n"
    
    
    updateRequest = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/8.0">
       <soapenv:Header/>
       <soapenv:Body>
          <ns:updateDeviceProfile sequence="?">
             <uuid>%s</uuid>
             <services>
             %s
             </services>
          </ns:updateDeviceProfile>
       </soapenv:Body>
    </soapenv:Envelope>""" % (uuid, serviceList)
    
    
    webservice =  httplib.HTTPS("x.x.x.x:8443")
    webservice.set_debuglevel(1)
    webservice.putrequest("POST", "/axl/")
    webservice.putheader("Host", "x.x.x.x:8443")
    webservice.putheader("User-Agent", "Configurator")
    webservice.putheader("Authorization","Basic ...")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(updateRequest))
    webservice.putheader("SOAPAction","\"CUCM:DB ver=8.0 updateDeviceProfile\"")
    webservice.endheaders()
    
    webservice.send(updateRequest)
     
    statuscode, statusmessage, header = webservice.getreply()
    print "Response: statuscode="+str(statuscode)+" statusmessage="+statusmessage+"\n"
    res = webservice.getfile().read()
    print "response text: res="+res+"\n"
