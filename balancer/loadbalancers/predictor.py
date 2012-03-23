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


class BasePredictor(Serializeable,  UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        self.type = None
        self.sf_id = None
        
class HashAddrPredictor(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.maskType = None
        self.ipNetmask = ""
        self.ipv6Prefix = ""

class HashURL(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.beginPattern = ""
        self.endPattern = ""

class HashContent(HashURL):
    def __init__(self):
        HashURL.__init__(self)
        self.length = ""
        self.offsetBytes = ""

class HashCookie(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.cookieName = ""

class HashHeader(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.customHeader = ""
        self.definedHeader = None

class HashLayer4(HashContent):
    def __init__(self):
        HashContent.__init__(self)
    pass

class LeastBandwidth(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.accessTime = None
        self.samples = None

class LeastConn(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.slowStartDur = None

class LeastLoaded(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.snmpProbe = ""
        self.autoAdjust = None
        self.weightConn = None

class Response(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.responseType = ""
        self.samples = ""
        self.weightConn = None

class RoundRobin(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
    pass
