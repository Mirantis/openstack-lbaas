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


class BaseDriver(object):
    def getContext(self):
        return BaseContext()

    def checkNone(self, obj):
        if bool(obj):
            if obj != 'None':
                return True
        return False

    def importCertificatesAndKeys(self,  context):
        pass

    def createSSLProxy(self,  context,  SSLproxy):
        pass

    def deleteSSLProxy(self,  context,  SSLproxy):
        pass

    def addSSLProxyToVIP(self,  context,  vip,  SSLproxy):
        pass

    def removeSSLProxyFromVIP(self,  context,  vip,  SSLproxy):
        pass

    def createRServer(self,  context,  rserver):
        pass

    def deleteRServer(self,  context,  rserver):
        pass

    def activateRServer(self,  context,  serverfarm,  rserver):
        pass

    def suspendRServer(self,  context,  serverfarm,  rserver):
        pass

    def createProbe(self,  context,  probe):
        pass

    def deleteProbe(self,  context,  probe):
        pass

    def createServerFarm(self,  context,  serverfarm):
        pass

    def deleteServerFarm(self,  context,  serverfarm):
        pass

    def addRServerToSF(self,  context,  serverfarm,  rserver):
        pass

    def deleteRServerFromSF(self, context,  serverfarm,  rserver):
        pass

    def addProbeToSF(self,  context,  serverfarm,  probe):
        pass

    def deleteProbeFromSF(self,  context,  serverfarm,  probe):
        pass

    def createStickiness(self,  context,  sticky):
        pass

    def deleteStickiness(self,  context,  sticky):
        pass

    def createVIP(self,  context,  vip,  sfarm):
        pass

    def deleteVIP(self,  context,  vip):
        pass


class BaseContext(object):
    def __init__(self):
        self._params = {}

    def addParam(self,  name,  param):
        self._params[name] = param

    def getParam(self, name):
        return self._params.get(name,  None)


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
