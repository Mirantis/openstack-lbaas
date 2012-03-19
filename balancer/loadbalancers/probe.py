# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

class Probe(Object):
    def __init__(self):
        self._id = ""
        self._name = ""
        self._type = ""
        self._description = ""
        self._probeInterval = 15
        self._passDetectInterval = 60
        self._failDetect = 3
    
    #more settings fields
        self._passDetectCount = 3
        self._receiveTimeout = 10
        self._isRouted = None
        self._port = ""
    
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    @property
    def type(self):
        return self._type_failDetect
    @type.setter
    def type(self, value):
        self._type = value
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, value):
        self._description = value
    @property
    def probeInterval(self):
        return self._probeInterval
    @probeInterval.setter
    def probeInterval(self, value):
        self._probeInterval = value
    @property
    def passDetectInterval(self):
        return self._passDetectInterval
    @passDetectInterval.setter
    def passDetectInterval(self, value):
        self._passDetectInterval = value
    @property
    def failDetect(self):
        return self._failDetect
    @failDetect.setter
    def failDetect(self, value):
        self._failDetect = value
    @property
    def passDetectCount(self, value):
        return self._passDetectCount
    @passDetectCount.setter
    def passDetectCount(self, value):
        self._passDetectCount = value
    @property
    def receiveTimeout(self):
        return self._receiveTimeout
    @receiveTimeout.setter
    def receiveTimeout(self, value):
        self._receiveTimeout = value
    @property
    def isRouted(self):
        return self._isRouted
    @isRouted.setter
    def isRouted(self, value):
        self._isRouted = value
    @property
    def port(self):
        return self._port
    @port.setter
    def port(self, value):
        self._port = value

class DNSprobe(Probe):
    def __init__(self):
        self._domainName = ""
    
    @property
    def domainName(self):
        return self._domainName
    @domainName.setter
    def domainName(self, value):
        self._domainName = value

class ECHOUDPprobe(Probe):
    def __init__(self):
        self._sendData = ""
        self._destIP = ""
    
    @property
    def sendData(self):
        return self._sendData
    @sendData.setter
    def sendData(self, value):
        self._sendData = value
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        sellf._destIP = value

class ECHOTCPprobe(ECHOUDPprobe):
    def __init__(self):
        self._tcpConnTerm = None
        self._openTimeout = 1
    
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value
    
class FINGERprobe(ECHOUDPprobe):
    pass

class FTPprobe(Probe):
    def __init__(self):
        self._destIP = ""
        self._tcpConnTerm = None
        self._openTimeout = 1
    
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        sellf._destIP = value    
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value    

class HTTPprobe(Probe):
    def __init__(self):
        self._requestMethodType = "GET"    
        self._requestHTTPurl = "/"
        self._appendPortHostTag = None
        self._destIPv4v6 = ""
        self._tcpConnTerm = None
        self._openTimeout = 1
        self._userName = ""
        self._password = ""
        self._confPassword = ""
        self._expectRegExp = ""
        self._expectRegExpOffset = ""
        self._hash = None
        self._hashString = ""
    
    @property
    def requestMethodType(self):
        return self._requestMethodType
    @requestMethodType.setter
    def requestMethodType(self, value):
        self._requestMethodType = value
    @property
    def requestHTTPurl(self):
        return self._requestHTTPurl
    @requestHTTPurl.setter
    def requestHTTPurl(self, value):
        self._requestHTTPurl = value
    @property
    def appendPortHostTag(self):
        return self._appendPortHostTag
    @appendPortHostTag.setter
    def appendPortHostTag(self, value):
        self._appendPortHostTag = value
    @property
    def destIPv4v6(self):
        return self._destIPv4v6
    @destIPv4v6.setter
    def destIPv4v6(self, value):
        self._destIPv4v6 = value
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value
    @property
    def userName(self):
        return self._userName
    @userName.setter
    def userName(self, value):
        self._userName = value
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._confPassword = value
    @property
    def expectRegExp(self):
        return self._expectRegExp
    @expectRegExp.setter
    def expectRegExp(self, value):
        self._expectRegExp = value
    @property
    def expectRegExpOffset(self):
        return self._expectRegExpOffset
    @expectRegExpOffset.setter
    def expectRegExpOffset(self, value):
        self._expectRegExpOffset = value
    @property
    def hash(self):
        return self._hash
    @hash.setter        
    def hash(self, value):
        self._hash = value
    @property
    def hashString(self):
        return self._hashString
    @hashString.setter
    def hashString(self, value):
        self._hashString = value
        

class HTTPSprobe(HTTPprobe):
    def __init__(self):
        self._cipher = None
        self._SSLversion = None
    
    @property
    def cipher(self):
        return self._cipher
    @cipher.setter
    def cipher(self, value):
        self._cipher = value
    @property
    def SSLversion(self):
        return self._SSLversion
    @SSLversion.setter
    def SSLversion(self, value):
        self._SSLversion = value

class ICMPprobe(Probe):
    pass
class IMAPprobe(Probe):
    def __init__(self):
        self._userName = ""
        self._password = ""
        self._confPassword = ""
        self._destIP = ""
        self._tcpConnTerm = None
        self._openTimeout = 1
        self._maibox = ""
        self._requestCommand = ""
        
    @property
    def userName(self):
        return self._userName
    @userName.setter
    def userName(self, value):
        self._userName = value
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._confPassword = value
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        self._destIP = value
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value
    @property
    def maibox(self):
        return self._maibox
    @maibox.setter
    def maibox(self, value):
        self._maibox = value
    @property
    def requestCommand(self):
        return self._requestCommand
    @requestCommand.setter
    def requestCommand(self, value):
        self._requestCommand = value

class POPprobe(Probe):
    def __init__(self):
        self._userName = ""
        self._password = ""
        self._confPassword = ""
        self._destIP = ""
        self._tcpConnTerm = None
        self._openTimeout = 1
        self._requestCommand = ""        
    @property
    def userName(self):
        return self._userName
    @userName.setter
    def userName(self, value):
        self._userName = value
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._confPassword = value
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        self._destIP = value
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value
    @property
    def requestCommand(self):
        return self._requestCommand
    @requestCommand.setter
    def requestCommand(self, value):
        self._requestCommand = value

class RADIUSprobe(Probe):
    def __init__(self):
        self._userName = ""
        self._password = ""
        self._confPassword = ""
        self._userSecret = ""
        self._destIP = ""
        self._NASIPaddr = ""
    @property
    def userName(self):
        return self._userName
    @userName.setter
    def userName(self, value):
        self._userName = value
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._confPassword = value
    @property
    def userSecret(self):
        return self._userSecret
    @userSecret.setter
    def userSecret(self, value):
        self._userSecret = value
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        self._destIP = value
    @property
    def NASIPaddr(self):
        return self._NASIPaddr
    @NASIPaddr.setter
    def NASIPaddr(self, value):
        self._NASIPaddr = value

class RTSPprobe(Probe):
    def __init__(self):
        self._requareHeaderValue = ""
        self._proxyRequareHeaderValue = ""
        self._requestMethodType = None
        self._requestURL = ""
        self._destIP = ""
        self._tcpConnTerm = None
        self._openTimeout = 1      
    
    @property
    def requareHeaderValue(self):
        return self._requareHeaderValue
    @requareHeaderValue.setter
    def requareHeaderValue(self, value):
        self._requareHeaderValue = value
    @property
    def proxyRequareHeaderValue(self):
        return self._proxyRequareHeaderValue
    @proxyRequareHeaderValue.setter
    def proxyRequareHeaderValue(self, value):
        self._proxyRequareHeaderValue = value
    @property
    def requestMethodType(self):
        return self._requestMethodType
    @requestMethodType.setter
    def requestMethodType(self, value):
        self._requestMethodType = value
    @property
    def _requestURL(self):
        return self._requestURL
    @requestURL.setter
    def requestURL(self, value):
        self._requestURL = value
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        self._destIP = value
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value

class SCRIPTEDprobe(Probe):
    def __init__(self):
        self._scriptName = ""
        self._scriptArgv = ""
        self._copied = None
        self._proto = None
        self._userName = ""
        self._password = ""
        self._confPassword = ""
        self._sourceFileName = ""
    
    @property
    def scriptName(self):
        return self._scriptName
    @scriptName.setter
    def scriptName(self, value):
        self.__scriptName = value
    @property
    def scriptArgv(self):
        return self._scriptArgv
    @scriptArgv.setter
    def scriptArgv(self, value):
        self._scriptArgv = value
    @property
    def copied(self):
        return self._copied
    @copied.setter
    def copied(self, value):
        self._copied = value
    @property
    def proto(self):
        return self._proto
    @proto.setter
    def proto(self, value):
        self._proto = value
    @property
    def userName(self):
        return self._userName
    @userName.setter
    def userName(self, value):
        self._userName = value
    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, value):
        self._password = value
        self._confPassword = value    
    @property
    def sourceFileName(self):
        return self._sourceFileName
    @sourceFileName.setter
    def sourceFileName(self, value):
        self._sourceFileName = value

class SIPUDPprobe(Probe):
    def __init__(self):
        self._destIP = ""
        self._expectRegExp = ""
        self._expectRegExpOffset = ""
    @property
    def destIP(self):
        return self._destIP
    @destIP.setter
    def destIP(self, value):
        self._destIP = value
    @property
    def expectRegExp(self):
        return self._expectRegExp
    @expectRegExp.setter
    def expectRegExp(self, value):
        self._expectRegExp = value
    @property
    def expectRegExpOffset(self):
        return self._expectRegExpOffset
    @expectRegExpOffset.setter
    def expectRegExpOffset(self, value):
        self._expectRegExpOffset = value
        
class SIPTCPprobe(SIPUDPprobe):
    def __init__(self):
        self._tcpConnTerm = None
        self._openTimeout = 1
        
    @property
    def tcpConnTerm(self):
        return self._tcpConnTerm
    @tcpConnTerm.setter
    def tcpConnTerm(self, value):
        self._tcpConnTerm = value
    @property
    def openTimeout(self):
        return self._openTimeout
    @openTimeout.setter
    def openTimeout(self, value):
        self._openTimeout = value

class SMTPprobe():
    pass

    
