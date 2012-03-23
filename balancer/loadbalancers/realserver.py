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


class RealServer(Serializeable,  UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)        

        self.sf_id = None
        self.name = ""
        self.type = "Host"
        self.webHostRedir = ""
        self.ipType = "IPv4"
        self.address = ""
        self.port = ""
        self.state= "InService" #StandBy, OutOfService
        self.opstate = "InService"
        self.description = ""
        self.failOnAll = None
        self.minCon = 4000000
        self.maxCon = 4000000
        self.weight = 8
        self.probes = []
        self.rateBandwidth = ""
        self.rateConnection = ""
        self.backupRS = ""
        self.backupRSport = ""
        self.created = None
        self.updated = None
        self.status = None
        self.condition = "ENABLED"
