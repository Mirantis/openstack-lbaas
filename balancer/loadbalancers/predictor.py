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

class BasePredictor(Object):
    def __init__(self):
        self._type = None
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, value):
        self._type = value
        
class HashAddrPredictor(BasePredictor):
    def __init__(self):
        self._maskType = None
        self._ipNetmask = ""
        self._ipv6Prefix = ""
        
    @property
    def maskType(self):
        return self._maskType
    @maskType.setter
    def maskType(self, value):
        self._maskType = value
    @property
    def ipNetmask(self):
        return self._ipNetmask
    @ipNetmask.setter
    def ipNetmask(self, value):
        self._ipNetmask = value
    @property
    def ipv6Prefix(self):
        return self._ipv6Prefix
    @ipv6Prefix.setter
    def ipv6Prefix(self, value):
        self._ipv6Prefix = value

class HashURL(BasePredictor):
    def __init__(self):
        self._beginPattern = ""
        self._endPattern = ""
    
    @property
    def beginPattern(self):
        return self._beginPattern
    @beginPattern.setter
    def beginPattern(self, value):
        self._beginPattern = value
    @property
    def endPattern(self):
        return self._endPattern
    @endPattern.setter
    def endPattern(self, value):
        self._endPattern = value

class HashContent(HashURL):
    def __init__(self):
        self._length = ""
        self._offsetBytes = ""
    
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, value):
        self._length = value
    @property
    def offsetBytes(self):
        return self._offsetBytes
    @offsetBytes.setter
    def offsetBytes(self, value):
        self._offsetBytes = value

class HashCookie(BasePredictor):
    def __init__(self):
        self._cookieName = ""
    
    @property
    def cookieName(self):
        return self._cookieName
    @cookieName.setter
    def cookieName(self, value):
        self._cookieName = value

class HashHeader(BasePredictor):
    def __init__(self):
        self._customHeader = ""
        self._definedHeader = None
    
    @property
    def customHeader(self):
        return self._customHeader
    @customHeader.setter
    def customHeader(self, value):
        self._customHeader = value
    @property
    def definedHeader(self):
        return self._definedHeader
    @definedHeader.setter
    def definedHeader(self, value):
        self._definedHeader = value

class HashLayer4(HashContent):
    pass

class LeastBandwidth(BasePredictor):
    def __init__(self):
        self._accessTime = ""
        self._samples = ""
    
    @property
    def accessTime(self):
        return self._accessTime
    @accessTime.setter
    def accessTime(self, value):
        self._accessTime = value
    @property
    def samples(self):
        return self._samples
    @samples.setter
    def samples(self, value):
        self._samples = value

class LeastConn(BasePredictor):
    def __init__(self):
        self._slowStartDur = ""
    
    @property
    def slowStartDur(self):
        return self._slowStartDur
    @slowStartDur.setter
    def slowStartDur(self, value):
        self._slowStartDur = value

class LeastLoaded(BasePredictor):
    def __init__(self):
        self._snmpProbe = ""
        self._autoAdjust = None
        self._weightConn = None
    
    @property
    def snmpProbe(self):
        return self._snmpProbe
    @snmpProbe.setter
    def snmpProbe(self, value):
        self._snmpProbe = value
    @property
    def autoAdjust(self):
        return self._autoAdjust
    @autoAdjust.setter
    def autoAdjust(self, value):
        self._autoAdjust = value
    @property
    def weightConn(self):
        return self._weightConn
    @weightConn.setter
    def weightConn(self, value):
        self._weightConn = value

class Response(BasePredictor):
    def __init__(self):
        self._responseType = ""
        self._samples = ""
        self._weightConn = None
    
    @property
    def responseType(self):
        return self._responseType
    @responseType.setter
    def responseType(self, value):
        self._responseType = value
    @property
    def samples(self):
        return self._samples
    @samples.setter
    def samples(self, value):
        self._samples = value
    @property
    def weightConn(self):
        return self._weightConn
    @weightConn.setter
    def weightConn(self, value):
        self._weightConn = value

class RounRobin(BasePredictor):
    pass
