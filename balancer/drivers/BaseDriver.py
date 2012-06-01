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
from balancer.core import commands


class DeviceRequestContext(commands.RollbackContext):
    def __init__(self, conf, device):
        self.conf = conf
        self.device = device


class BaseDriver(object):
    def __init__(self, conf, device_ref):
        self.conf = conf
        self.device_ref = device_ref

    def request_context(self):
        return commands.RollbackContextManager(
                DeviceRequestContext(self.conf, self))

    def checkNone(self, obj):
        if bool(obj):
            if obj != 'None':
                return True
        return False

    def importCertificatesAndKeys(self):
        pass

    def createSSLProxy(self, SSLproxy):
        pass

    def deleteSSLProxy(self, SSLproxy):
        pass

    def addSSLProxyToVIP(self, vip, SSLproxy):
        pass

    def removeSSLProxyFromVIP(self, vip, SSLproxy):
        pass

    def createRServer(self, rserver):
        pass

    def deleteRServer(self, rserver):
        pass

    def activateRServer(self, serverfarm, rserver):
        pass

    def activateRServerGlobal(self, rserver):
        pass

    def suspendRServer(self, serverfarm, rserver):
        pass

    def suspendRServerGlobal(self, rserver):
        pass

    def createProbe(self, probe):
        pass

    def deleteProbe(self, probe):
        pass

    def createServerFarm(self, serverfarm):
        pass

    def deleteServerFarm(self, serverfarm):
        pass

    def addRServerToSF(self, serverfarm, rserver):
        pass

    def deleteRServerFromSF(self, serverfarm, rserver):
        pass

    def addProbeToSF(self, serverfarm, probe):
        pass

    def deleteProbeFromSF(self, serverfarm, probe):
        pass

    def createStickiness(self, sticky):
        pass

    def deleteStickiness(self, sticky):
        pass

    def createVIP(self, vip, sfarm):
        pass

    def deleteVIP(self, vip):
        pass

    def getStatistics (self, serverfarm, rserver):
        pass


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
