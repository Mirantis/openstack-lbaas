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
        super(DeviceRequestContext, self).__init__()
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
        raise NotImplementedError

    def createSSLProxy(self, SSLproxy):
        raise NotImplementedError

    def deleteSSLProxy(self, SSLproxy):
        raise NotImplementedError

    def addSSLProxyToVIP(self, vip, SSLproxy):
        raise NotImplementedError

    def removeSSLProxyFromVIP(self, vip, SSLproxy):
        raise NotImplementedError

    def createRServer(self, rserver):
        raise NotImplementedError

    def deleteRServer(self, rserver):
        raise NotImplementedError

    def activateRServer(self, serverfarm, rserver):
        raise NotImplementedError

    def activateRServerGlobal(self, rserver):
        raise NotImplementedError

    def suspendRServer(self, serverfarm, rserver):
        raise NotImplementedError

    def suspendRServerGlobal(self, rserver):
        raise NotImplementedError

    def createProbe(self, probe):
        raise NotImplementedError

    def deleteProbe(self, probe):
        raise NotImplementedError

    def createServerFarm(self, serverfarm):
        raise NotImplementedError

    def deleteServerFarm(self, serverfarm):
        raise NotImplementedError

    def addRServerToSF(self, serverfarm, rserver):
        raise NotImplementedError

    def deleteRServerFromSF(self, serverfarm, rserver):
        raise NotImplementedError

    def addProbeToSF(self, serverfarm, probe):
        raise NotImplementedError

    def deleteProbeFromSF(self, serverfarm, probe):
        raise NotImplementedError

    def createStickiness(self, sticky):
        raise NotImplementedError

    def deleteStickiness(self, sticky):
        raise NotImplementedError

    def createVIP(self, vip, sfarm):
        raise NotImplementedError

    def deleteVIP(self, vip):
        raise NotImplementedError

    def getStatistics(self, serverfarm, rserver):
        raise NotImplementedError


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
