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
import vlan

from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject

class VirtualServer(Serializeable,  UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        self.name = ""
        self.ipVersion = "IPv4"
        self.address = ""
        self.mask = "255.255.255.255"
        self.proto = "TCP"
        self.appProto = "Other"
        self.port = "any"
        self.allVLANs = None
        self.VLAN = [] #need to describe in new module
        self.connParameterMap = None #need to describe in new module
        self.KALAPtagName = ""
        self.KALAPprimaryOutOfServ = None
        self.ICMPreply = "None"
        self.status = "inservice"
        
        self.protocolInspect = None #need to describe in new module
        self.appAccelAndOpt = None #need to describe in new module
        self.L7LoadBalancing = None #need to describe in new module
        self.sf_id = None
        self.lb_id = None
        self.backupServerFarm = None
        self.SSLproxyServName = None #need to describe in new module
        self.defaultL7LBAction = None #need to describe in new module
        self.SSLinitiation = None #need to describe in new module
        self.NAT = [] #need to describe in new module
        self.created = None
        self.updated = None
