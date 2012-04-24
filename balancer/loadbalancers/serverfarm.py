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
import predictor
import probe
import realserver
import sticky

from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject


class ServerFarm(Serializeable,  UniqueObject):
    def __init__(self):

        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        self.lb_id = None
        self.name = ""
        self.type = "host"
        self.description = ""
        self.failAction = None
        self.inbandHealthCheck = None
        self.connFailureThreshCount = ""
        self.resetTimeout = ""
        self.resumeService = ""
        self.transparent = None
        self.dynamicWorkloadScale = None
        self.vmProbeName = ""
        self.failOnAll = None
        self.partialThreshPercentage = 0
        self.backInservice = 0
        self._probes = []
        self._rservers = []
        self._predictor = predictor.RoundRobin()
        self._sticky = []
        self.retcodeMap = ""
        self.status = "ACTIVE"
        self.created = None
        self.updated = None
