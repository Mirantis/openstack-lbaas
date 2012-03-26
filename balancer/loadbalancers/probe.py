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

from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject


class Probe(Serializeable,  UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        self.name = ""
        self.type = ""
        self.description = ""
        self.probeInterval = 15
        self.passDetectInterval = 60
        self.failDetect = 3
        
        self.delay = 15
        self.attemptsBeforeDeactivation = 3
        self.timeout = 60
    
    #more settings fields
        self.passDetectCount = 3
        self.receiveTimeout = 10
        self.isRouted = None
        self.port = ""

class DNSprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.domainName = ""
        

class ECHOUDPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.sendData = ""
        self.destIP = ""

class ECHOTCPprobe(ECHOUDPprobe):
    def __init__(self):
        ECHOUDPprobe.__init__(self)
        self.tcpConnTerm = None
        self.openTimeout = 1
    
class FINGERprobe(ECHOUDPprobe):
    def __init__(self):
        ECHOUDPprobe.__init__(self)
    pass

class FTPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1

class HTTPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.requestMethodType = "GET"    
        self.requestHTTPurl = "/"
        self.appendPortHostTag = None
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1
        self.userName = ""
        self.password = ""
        self.expectRegExp = ""
        self.expectRegExpOffset = ""
        self.hash = None
        self.hashString = ""
        self.headerName = ""
        self.headerValue = ""
        self.minExpectStatus = ""
        self.maxExpectStatus = ""
    
class HTTPSprobe(HTTPprobe):
    def __init__(self):
        HTTPprobe.__init__(self)
        self.cipher = None
        self.SSLversion = None

class ICMPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = None
    pass
    
class IMAPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.userName = ""
        self.password = ""
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1
        self.maibox = ""
        self.requestCommand = ""

class POPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.userName = ""
        self.password = ""
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1
        self.requestCommand = ""        

class RADIUSprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.userName = ""
        self.password = ""
        self.userSecret = ""
        self.destIP = ""
        self.NASIPaddr = ""

class RTSPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.requareHeaderValue = ""
        self.proxyRequareHeaderValue = ""
        self.requestMethodType = None
        self.requestURL = ""
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1      

class SCRIPTEDprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.scriptName = ""
        self.scriptArgv = ""
        self.copied = None
        self.proto = None
        self.userName = ""
        self.password = ""
        self.sourceFileName = ""
    
    
class SIPUDPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = ""
        self.expectRegExp = ""
        self.expectRegExpOffset = ""
        
class SIPTCPprobe(SIPUDPprobe):
    def __init__(self):
        SIPUDPprobe.__init__(self)
        self.tcpConnTerm = None
        self.openTimeout = 1
        

class SMTPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1
    
class SNMPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = ""
        self.SNMPComm = ""
        self.SNMPver = None
        

class TCPprobe(Probe):
    def __init__(self):
        Probe.__init__(self)
        self.destIP = ""
        self.tcpConnTerm = None
        self.openTimeout = 1
        self.expectRegExp = ""
        self.expectRegExpOffset = ""      

class TELNETprobe(SMTPprobe):
    def __init__(self):
        SMTPprobe.__init__(self)
    pass

class UDPprobe(ECHOUDPprobe):
    def __init__(self):
        ECHOUDPprobe.__init__(self)
        self.expectRegExp = ""
        self.expectRegExpOffset = ""   

class VMprobe(object):
    def __init__(self):
        self.id = None
        self.name = ""
        self.type = None
        self.description = ""
        self.probeInterval = 300
        self.maxCPUburstThresh = 99
        self.minCPUburstThresh = 99
        self.maxMemBurstThresh = 99
        self.minMemBurstThresh = 99
        self.VMControllerName = None
        


