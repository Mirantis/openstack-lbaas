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

from balancer.drivers.base_driver import BaseDriver

logger = logging.getLogger(__name__)


class DummyDriver(BaseDriver):
    def importCertificatesAndKeys(self):
        logger.debug("Called DummyDriver.importCertificatesAndKeys().")

    def createSSLProxy(self, SSLproxy):
        logger.debug("Called DummyDriver.createSSLProxy(%r)." % (SSLproxy,))

    def deleteSSLProxy(self, SSLproxy):
        logger.debug("Called DummyDriver.deleteSSLProxy(%r)." % (SSLproxy,))

    def addSSLProxyToVIP(self, vip, SSLproxy):
        logger.debug("Called DummyDriver.deleteSSLProxy(%r, %r)." % (vip, SSLproxy))

    def removeSSLProxyFromVIP(self, vip, SSLproxy):
        logger.debug("Called DummyDriver.removeSSLProxyFromVIP(%r, %r)." % (vip, SSLproxy))

    def createRServer(self, rserver):
        logger.debug("Called DummyDriver.createRServer(%r)." % (rserver,))

    def deleteRServer(self, rserver):
        logger.debug("Called DummyDriver.deleteRServer(%r)." % (rserver,))

    def activateRServer(self, serverfarm, rserver):
        logger.debug("Called DummyDriver.activateRServer(%r, %r)." % (serverfarm, rserver))

    def activateRServerGlobal(self, rserver):
        logger.debug("Called DummyDriver.activateRServerGlobal(%r)." % (rserver,))

    def suspendRServer(self, serverfarm, rserver):
        logger.debug("Called DummyDriver.suspendRServer(%r, %r)." % (serverfarm, rserver))

    def suspendRServerGlobal(self, rserver):
        logger.debug("Called DummyDriver.suspendRServerGlobal(%r)." % (rserver,))

    def createProbe(self, probe):
        logger.debug("Called DummyDriver.createProbe(%r)." % (probe,))

    def deleteProbe(self, probe):
        logger.debug("Called DummyDriver.deleteProbe(%r)." % (probe,))

    def createServerFarm(self, serverfarm):
        logger.debug("Called DummyDriver.createServerFarm(%r)." % (serverfarm,))

    def deleteServerFarm(self, serverfarm):
        logger.debug("Called DummyDriver.deleteServerFarm(%r)." % (serverfarm,))

    def addRServerToSF(self, serverfarm, rserver):
        logger.debug("Called DummyDriver.addRServerToSF(%r, %r)." % (serverfarm, rserver))

    def deleteRServerFromSF(self, serverfarm, rserver):
        logger.debug("Called DummyDriver.deleteRServerFromSF(%r, %r)." % (serverfarm, rserver))

    def addProbeToSF(self, serverfarm, probe):
        logger.debug("Called DummyDriver.addProbeToSF(%r, %r)." % (serverfarm, probe))

    def deleteProbeFromSF(self, serverfarm, probe):
        logger.debug("Called DummyDriver.deleteProbeFromSF(%r, %r)." % (serverfarm, probe))

    def createStickiness(self, sticky):
        logger.debug("Called DummyDriver.createStickiness(%r)." % (sticky,))

    def deleteStickiness(self, sticky):
        logger.debug("Called DummyDriver.deleteStickiness(%r)." % (sticky,))

    def createVIP(self, vip, sfarm):
        logger.debug("Called DummyDriver.createVIP(%r, %r)." % (vip, sfarm))

    def deleteVIP(self, vip):
        logger.debug("Called DummyDriver.deleteVIP(%r)." % (vip,))

    def getStatistics(self, serverfarm, rserver):
        logger.debug("Called DummyDriver.getStatistics(%r, %r)." % (serverfarm, rserver))
