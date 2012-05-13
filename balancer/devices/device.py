# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0device.py
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import uuid
from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject


class LBDevice(Serializeable, UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)

        self.name = None
        self.type = "ACE"
        self.version = None
        self.supports_ipv6 = False
        self.requires_vip_ip = True
        self.has_acl = True
        self.supports_vlan = True
        self.ip = None
        self.port = None
        self.user = None
        self.password = None
        self.vip_vlan = 1
        self.localpath = None
        self.configfilepath = None
        self.remotepath = None
        self.interface = None
        self.concurrent_deploys = 2
