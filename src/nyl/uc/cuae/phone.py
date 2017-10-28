'''
Created on Sep 30, 2009

@author: t22cf3p
'''
import httplib,urllib
import string
import base64 
import threading
import time
import sys

from xml.dom.minidom import parseString

class PhoneInformation(object):
    
    def __init__(self,ipAddress,user,password):
        '''
        Constructor
        '''
        
        self.runThreads = False
        self.ip = ipAddress
        self.user = user
        self.password = password
        self.device = {}
        self.network = {}
        self.ethernet = {}
        self.ports = {}
        self.streams = {}
        self.__screenShot = None
        
        self.sleepTime = 120
        self.screenSleepTime = 5
        self.authToken = 'Basic '+string.strip(base64.encodestring(user+':'+password))
                 
        self.deviceTimer = None
        self.networkTimer = None
        self.ethernetTimer = None
        self.portsTimer = None
        self.sreamTimer = None 
        self.screenTimer = None
        self.screenShotAvailiable = threading.Event()
        
    def GetInformation(self,keepUpdating):
        if keepUpdating:
            self.runThreads=True
        else:
            self.runThreads=False
            
        screenThread = threading.Thread(target=self.GetScreenShot()) 
        deviceThread = threading.Thread(target=self.GetDeviceInformation)
        networkThread = threading.Thread(target=self.GetNetworkInformation)
        ethernetThread = threading.Thread(target=self.GetEthernetInformation)
        portsThread =  threading.Thread(target=self.GetPortInformation)
        streamThread = threading.Thread(target=self.GetStreamInformation)
        
        screenThread.start()
        ethernetThread.start()
        deviceThread.start()
        networkThread.start()
        portsThread.start()
        streamThread.start()
        
        screenThread.join(60)
        ethernetThread.join(60)
        deviceThread.join(60)
        networkThread.join(60)
        portsThread.join(60)
        streamThread.join(60)
        return self
     
    def GetDeviceInformation(self):
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        conn.request('GET','/DeviceInformationX')
        r=conn.getresponse()
        if r.status == 200:
            self.device = self.__parseXml(r.read())
        else:
            self.device = {}
    
        conn.close()
        if self.runThreads:
            if self.deviceTimer != None:
                self.deviceTimer.cancel()
                
            self.deviceTimer = threading.Timer(self.sleepTime,self.GetDeviceInformation)
            self.deviceTimer.start()
            
        return self
        
    def GetNetworkInformation(self):
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        conn.request('GET','/NetworkConfigurationX')
        r=conn.getresponse()
        if r.status == 200:
            self.network = self.__parseXml(r.read())
        else:
            self.network = {}
        
        conn.close()
        if self.runThreads:
            if self.networkTimer != None:
                self.networkTimer.cancel()
                
            self.networkTimer = threading.Timer(self.sleepTime,self.GetNetworkInformation)
            self.networkTimer.start()
        return self
        
    def GetEthernetInformation(self):
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        conn.request('GET','/EthernetInformationX')
        r=conn.getresponse()
        if r.status == 200:
            self.ethernet = self.__parseXml(r.read())
        else:
            self.ethernet = {}
        
        conn.close()
        if self.runThreads:
            if self.ethernetTimer != None:
                self.ethernetTimer.cancel()
                
            self.ethernetTimer = threading.Timer(self.sleepTime,self.GetEthernetInformation)
            self.ethernetTimer.start()
        return self
            
    def GetPortInformation(self):
        self.ports = {}
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        counter=1
        conn.request('GET','/PortInformationX?'+str(counter))
        r=conn.getresponse()
        while r.status == 200:
            self.ports[str(counter)] = self.__parseXml(r.read())
            self.ports[str(counter)]['portId'] = str(counter);
            counter+=1
            conn.request('GET','/PortInformationX?'+str(counter))
            r=conn.getresponse()
            
        conn.close()
        if self.runThreads:
            if self.portsTimer != None:
                self.portsTimer.cancel()
            
            self.portsTimer = threading.Timer(self.sleepTime,self.GetPortInformation)
            self.portsTimer.start()
        return self
        
    def GetStreamInformation(self):
        self.streams = {}
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        counter=1
        conn.request('GET','/StreamingStatisticsX?'+str(counter))
        r=conn.getresponse()
        while r.status == 200:
            self.streams[str(counter)] = self.__parseXml(r.read())
            self.streams[str(counter)]['streamId'] = str(counter);
            counter+=1
            conn.request('GET','/StreamingStatisticsX?'+str(counter))
            r=conn.getresponse()
        
        conn.close()
        if self.runThreads:
            if self.sreamTimer != None:
                self.sreamTimer.cancel()
                
            self.sreamTimer = threading.Timer(self.sleepTime,self.GetStreamInformation)
            self.sreamTimer.start()
            
        return self
    
    def Shutdown(self):
        if self.runThreads:
            self.runThreads = False
        
        if self.deviceTimer != None:
            self.deviceTimer.cancel()
        
        if self.networkTimer != None:
            self.networkTimer.cancel()
        
        if self.ethernetTimer != None:
            self.ethernetTimer.cancel()
        
        if self.portsTimer != None:
            self.portsTimer.cancel()
        
        if self.sreamTimer != None:
            self.sreamTimer.cancel()
        
        if self.screenTimer != None:
            self.screenTimer.cancel()
    
    def ProcessMacro(self,macro,statusCallback):
        for key in macro.split():
            if key == ",":
                print "ip="+self.ip+" waiting (1)secs"
                time.sleep(1)
            else:
                print "ip="+self.ip+" sending key="+key
                self.__sendExecute(key);
        print "ip="+self.ip+" macro complete"
           
    def SendButton(self,button):
        self.__sendExecute(button)
  
    def ChangeTftpServer(self,tftpserver,removeTrustList=False):
        macro=""
        for i in xrange (0,tftpserver.__len__()):
            if(tftpserver[i] == "."):
                macro += " "+ButtonMap.SOFT_KEY2
            else:
                key=""
                exec("key=ButtonMap.KEY"+str(tftpserver[i]))
                macro += " "+key
        macro+=" , "+ButtonMap.SOFT_KEY3+" , "+ButtonMap.SOFT_KEY3
        
        
        if self.device.__len__()==0:
            self.GetDeviceInformation()
            
        if self.device['modelNumber'].find("7960") != -1 or self.device['modelNumber'].find("7940") != -1:
            macro=ButtonMap.KEY8+" , , "+ButtonMap.SOFT_KEY2+" "+macro
        else:
            macro=ButtonMap.KEY2+" , "+ButtonMap.KEY1+" , "+ButtonMap.KEY1+"|"+ButtonMap.KEY7+" , "+ButtonMap.SOFT_KEY2+" "+macro
            if removeTrustList==True:
                macro+= " , , , , , , , , "+ButtonMap.SOFT_KEY3+" , "+ButtonMap.KEY4+" , "+ButtonMap.KEY5+" , "+ButtonMap.KEY2+" , "+ButtonMap.SOFT_KEY2+" , "+ButtonMap.SOFT_KEY4+" , "+ButtonMap.SOFT_KEY2
        
        self.UnlockPhone()
        time.sleep(5)
        self.ProcessMacro(macro, "")
        return
        
          
    def UnlockPhone(self):
        conn =  httplib.HTTPConnection(self.ip)
        try:
            conn.set_debuglevel(0)
            headers = {"Content-type": "application/x-www-form-urlencoded",'Authorization':self.authToken}
            
            if self.device['modelNumber'].find("7960") != -1 or self.device['modelNumber'].find("7940") != -1:
                button=ButtonMap.SOFTKEY_EXIT
            else:
                button=ButtonMap.INIT_SETTINGS
                
            executeXML='''<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="'''+button+'''"/></CiscoIPPhoneExecute>'''
            params = urllib.urlencode({'XML': executeXML})
            conn.request('POST','/CGI/Execute',params,headers)
            r=conn.getresponse()
            responseBody = r.read()
            
            if r.status == 401:
                raise AuthenticationException(str(r.status)+" "+httplib.responses[r.status],responseBody)
            
            #for 7960's we have to be on the network config page
            if self.device['modelNumber'].find("7960") != -1 or self.device['modelNumber'].find("7940") != -1:
                executeXML='''<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="'''+ButtonMap.SETTINGS+'''"/>
                    <ExecuteItem Priority="1" URL="'''+ButtonMap.KEY3+'''"/></CiscoIPPhoneExecute>'''
            else:
                executeXML='''<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="'''+ButtonMap.SETTINGS+'''"/></CiscoIPPhoneExecute>'''
                
            params = urllib.urlencode({'XML': executeXML})
            conn.request('POST','/CGI/Execute',params,headers)
            r=conn.getresponse()
            responseBody = r.read()
            time.sleep(2)
            if r.status == 200 or r.status==303: #we get 303 back from 7960's
                r.read()
                executeXML='''<CiscoIPPhoneExecute><ExecuteItem Priority="0" URL="'''+ButtonMap.ASTERISK+'''"/>
                    <ExecuteItem Priority="1" URL="'''+ButtonMap.ASTERISK+'''"/>
                    <ExecuteItem Priority="1" URL="'''+ButtonMap.POUND+'''"/>
                    </CiscoIPPhoneExecute>'''
                params = urllib.urlencode({'XML': executeXML})
                conn.request('POST','/CGI/Execute',params,headers)
                r=conn.getresponse()
                responseBody = r.read()
                if r.status == 200 or r.status == 303: #we get 303 back from 7960's
                    return True
                else:
                    raise CommunicationException(str(r.status)+" "+httplib.responses[r.status],responseBody)
                
            else:
                raise CommunicationException(str(r.status)+" "+httplib.responses[r.status],responseBody)
        finally:
            conn.close()
        
    def __sendExecute(self,execute):
        conn =  httplib.HTTPConnection(self.ip)
        conn.set_debuglevel(0)
        itemCount=0
        items=""
        for button in execute.split("|"):
            if itemCount > 2:
                break;
            items+='<ExecuteItem Priority="%d" URL="%s"/>' %(itemCount,button)
            itemCount+=1
            
        executeXML='<CiscoIPPhoneExecute>%s</CiscoIPPhoneExecute>' % items
        params = urllib.urlencode({'XML': executeXML})
        headers = {"Content-type": "application/x-www-form-urlencoded",'Authorization':self.authToken}
        conn.request('POST','/CGI/Execute',params,headers)
        r=conn.getresponse()
        responseBody = r.read()
        conn.close()
        if r.status == 200 or r.status == 303: #we get 303 back from 7960's
            return True
        elif r.status == 401:
            raise AuthenticationException(str(r.status)+" "+httplib.responses[r.status],responseBody)
        else:
            raise CommunicationException(str(r.status)+" "+httplib.responses[r.status],responseBody)
                       
    def __parseXml(self,xmlString):
        domDoc=parseString(xmlString)
        objectDictionary = {}
        if domDoc.documentElement.childNodes.length > 0:
            for childNode in domDoc.documentElement.childNodes:
                if childNode.childNodes.length == 0:
                    objectDictionary[childNode.nodeName]="N/A"
                else:
                    objectDictionary[childNode.nodeName]=childNode.childNodes[0].nodeValue
        
        return objectDictionary

class AuthenticationException(Exception):
    def __init__(self, value,response):
        self.value = value
        self.response = response
    
    def __str__(self):
        return repr(self.value)

class CommunicationException(Exception):
    def __init__(self, value, response):
        self.value = value
        self.response = response
        
    def __str__(self):
        return repr(self.value)
    
class ButtonMap(object):
    INIT_CALLHISTORY = "Init:CallHistory"
    INIT_SERVICES = "Init:Services"
    INIT_MESSAGES = "Init:Messages"
    INIT_DIRECTORIES = "Init:Directories"
    INIT_SETTINGS = "Init:Settings"
    
    SOFTKEY_BACK = "SoftKey:Back"
    SOFTKEY_CANCEL = "SoftKey:Cancel"
    SOFTKEY_EXIT = "SoftKey:Exit"
    SOFTKEY_NEXT = "SoftKey:Next"
    SOFTKEY_SEARCH = "SoftKey:Search"
    SOFTKEY_SELECT = "SoftKey:Select"
    SOFTKEY_SUBMIT = "SoftKey:Submit"
    SOFTKEY_UPDATE = "SoftKey:Update"
    SOFTKEY_DIAL = "SoftKey:Dial"
    SOFTKEY_EDITDIAL = "SoftKey:EditDial"
    SOFTKEY_DELETE = "SoftKey:<<"
    
    SOFT_KEY1 = "Key:Soft1"
    SOFT_KEY2 = "Key:Soft2"
    SOFT_KEY3 = "Key:Soft3"
    SOFT_KEY4 = "Key:Soft4"
    SOFT_KEY5 = "Key:Soft5"
    
    VOLUME_DOWN="Key:VolDwn"
    VOLUME_UP = "Key:VolUp"
    
    HEADSET = "Key:Headset"
    SPEAKER = "Key:Speaker"
    MUTE = "Key:Mute"
    
    NAV_LEFT = "Key:NavLeft"
    NAV_RIGHT = "Key:NavRight"
    NAV_SELECT = "Key:NavSelect"
    NAV_UP = "Key:NavUp"
    NAV_DOWN = "Key:NavDwn"
    
    INFO = "Key:Info"
    MESSAGES = "Key:Messages"
    SERVICES = "Key:Services"
    DIRECTORIES = "Key:Directories"
    SETTINGS = "Key:Settings"
    APPMENU = "Key:AppMenu"
    HOLD = "Key:Hold"   
    
    DISPLAY_ON = "Display:On:0"
    DISPLAY_OFF = "Display:Off:0"
    DISPLAY_DEFAULT = "Display:Default"
    
    PAUSE = "."
    ASTERISK = "Key:KeyPadStar"
    POUND = "Key:KeyPadPound"
    KEY0 = "Key:KeyPad0"
    KEY1 = "Key:KeyPad1"
    KEY2 = "Key:KeyPad2"
    KEY3 = "Key:KeyPad3"
    KEY4 = "Key:KeyPad4"
    KEY5 = "Key:KeyPad5"
    KEY6 = "Key:KeyPad6"
    KEY7 = "Key:KeyPad7"
    KEY8 = "Key:KeyPad8"
    KEY9 = "Key:KeyPad9"
          
    
    LINES_LINE1 = "Key:Line1"
    LINES_LINE2 = "Key:Line2"
    LINES_LINE3 = "Key:Line3"
    LINES_LINE4 = "Key:Line4"
    LINES_LINE5 = "Key:Line5"
    LINES_LINE6 = "Key:Line6"
    LINES_LINE7 = "Key:Line7"
    LINES_LINE8 = "Key:Line8"
    LINES_LINE9 = "Key:Line9"
    LINES_LINE10 = "Key:Line10"
    LINES_LINE11 = "Key:Line11"
    LINES_LINE12 = "Key:Line12"
    LINES_LINE13 = "Key:Line13"
    LINES_LINE14 = "Key:Line14"
    LINES_LINE15 = "Key:Line15"
    LINES_LINE16 = "Key:Line16"
    LINES_LINE17 = "Key:Line17"
    LINES_LINE18 = "Key:Line18"
    LINES_LINE19 = "Key:Line19"
    LINES_LINE20 = "Key:Line20"
    LINES_LINE21 = "Key:Line21"
    LINES_LINE22 = "Key:Line22"
    LINES_LINE23 = "Key:Line23"
    LINES_LINE24 = "Key:Line24"
    LINES_LINE25 = "Key:Line25"
    LINES_LINE26 = "Key:Line26"
    LINES_LINE27 = "Key:Line27"
    LINES_LINE28 = "Key:Line28"
    LINES_LINE29 = "Key:Line29"
    LINES_LINE30 = "Key:Line30"
    LINES_LINE31 = "Key:Line31"
    LINES_LINE32 = "Key:Line32"
    LINES_LINE33 = "Key:Line33"
    LINES_LINE34 = "Key:Line34"
   
    def __init__(self):       
        pass
   
        