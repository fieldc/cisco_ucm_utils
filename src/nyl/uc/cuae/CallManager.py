'''
Created on Oct 6, 2010

@author: t22cf3p
'''

class CallManager(object):
    '''
    classdocs
    '''
    @staticmethod
    def getPhoneRequest(phones):
        itemList=""
        selectItemList=""
        request = """<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                    xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:tns="http://schemas.cisco.com/ast/soap/"
                    xmlns:types="http://schemas.cisco.com/ast/soap/encodedTypes"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                <soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <tns:SelectCmDevice>
                        <CmSelectionCriteria href="#criteria"/>
                    </tns:SelectCmDevice>
                    <tns:CmSelectionCriteria id="criteria" xsi:type="tns:CmSelectionCriteria">
                        <Class xsi:type="tns:Class">Phone</Class>
                        <SelectBy xsi:type="tns:CmSelectBy">Name</SelectBy>
                        <SelectItems href="#phones" />
                    </tns:CmSelectionCriteria>
                    <soapenc:Array id="phones" soapenc:arrayType="tns:SelectItem[{0}]">
                        {1}
                    </soapenc:Array>
                    {2}
                </soap:Body>
            </soap:Envelope>""" 
        for i in xrange(0,phones.__len__()):
            itemList+='<Item href="#id'+str(i)+'"/>'
            selectItemList += """<tns:SelectItem id="id%s" xsi:type="tns:SelectItem"><Item xsi:type="xsd:string">%s</Item></tns:SelectItem>""" % (str(i),phones.keys()[i])
        
        request=request.format(phones.__len__(),itemList,selectItemList)
        return request
            
    def __init__(self):
        '''
        Constructor
        '''
        pass