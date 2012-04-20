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
        self.type = "HashAddrPredictor"


class HashURL(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.beginPattern = ""
        self.endPattern = ""
        self.type = "HashURL"


class HashContent(HashURL):
    def __init__(self):
        HashURL.__init__(self)
        self.length = ""
        self.offsetBytes = ""
        self.type = "HashContent"


class HashCookie(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.cookieName = ""
        self.type = "HashCookie"


class HashHeader(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.customHeader = ""
        self.definedHeader = None
        self.type = "HashHeader"


class HashLayer4(HashContent):
    def __init__(self):
        HashContent.__init__(self)
        self.type = "HashLayer4"
    pass


class LeastBandwidth(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.accessTime = None
        self.samples = None
        self.type = "LeastBandwidth"


class LeastConn(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.slowStartDur = None
        self.type = "LeastConnections"


class LeastLoaded(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.snmpProbe = ""
        self.autoAdjust = None
        self.weightConn = None
        self.type = "LeastLoaded"


class Response(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.responseType = ""
        self.samples = ""
        self.weightConn = None
        self.type = "Response"


class RoundRobin(BasePredictor):
    def __init__(self):
        BasePredictor.__init__(self)
        self.type = "RoundRobin"
    pass
