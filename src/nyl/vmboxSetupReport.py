'''
Created on Oct 29, 2011

@author: t22cf3p
'''
from xml.dom import minidom
import urllib, httplib, base64
import sys

if __name__ == '__main__':
    pass

auth = base64.encodestring('%s:%s' % ("vmrest", "1qazXSW@"))[:-1]
headers = { "Host":"172.31.25.101", 
         "Authorization": "Basic %s" % auth,
         "User-Agent": "NYLSPlunkREST"
          }


page=1
numUsers=-1

conn =  httplib.HTTPS("172.31.25.101:8443")
conn.set_debuglevel(1)    

while True:
    if numUsers != 1 and page * 100 > numUsers:
        break;
     
    conn.putrequest("GET", "/vmrest/users?rowsPerPage=100&pageNumber="+page.__str__())
    conn.putheader("Host","172.31.25.101")
    conn.putheader("Authorization","Basic dm1yZXN0OjFxYXpYU1dA")
    conn.putheader("User-Agent", "NYLSPlunkREST")
    conn.endheaders()
    errcode, errmsg, headers = conn.getreply()
    ++page
    
    if errcode == 200:
        xmldoc = minidom.parseString(conn.getfile().read().strip())
        if(numUsers==-1):
            userField = xmldoc.getElementsByTagName("Users")
            userCount = int(userField.item(0).attributes.item(0).value)
            print userCount
        for userNode in xmldoc.getElementsByTagName("User"):
            alias = ""
            IsVmEnrolled ="" 
            IsSetForVmEnrollment=""
            
            for userInfo in userNode.childNodes:
                if userInfo.nodeName == "Alias":
                    alias = userInfo.childNodes.item(0).nodeValue
                elif userInfo.nodeName == "IsVmEnrolled":
                    IsVmEnrolled= userInfo.childNodes.item(0).nodeValue
                elif userInfo.nodeName == "IsSetForVmEnrollment":
                    IsSetForVmEnrollment= userInfo.childNodes.item(0).nodeValue
                    print alias+","+IsVmEnrolled+","+IsSetForVmEnrollment
                    break;
    
    #Users total="3849"

