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

import md5
import logging

from balancer.drivers.BaseDriver import (BaseDriver,  is_sequence)
from balancer.drivers.cisco_ace.Context import Context
from balancer.drivers.cisco_ace.XmlSender import XmlSender
import openstack.common.exception

logger = logging.getLogger(__name__)


class AceDriver(BaseDriver):
    def __init__(self):
        pass

    def send_data(self,  context,  XMLstr):
        s = XmlSender(context)
        tmp = s.deployConfig(context, XMLstr)
        if (tmp == 'OK'):
            return tmp
        else:
            raise openstack.common.exception.Invalid(tmp)

    def getContext(self, dev):
        logger.debug("Creating context with params: IP %s, Port: %s" % \
            (dev.ip,  dev.port))
        return Context(dev.ip, dev.port, dev.user,  dev.password)

    def createRServer(self, context, rserver):
        logger.debug("Creating the Real Server\n")
        if not self.checkNone(rserver.name):
            logger.error("Can't find rserver name")
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver type='" + rserver.type.lower() + "' name='" + \
            rserver.name + "'>\r\n"

        if self.checkNone(rserver.description):
            XMLstr = XMLstr + "  <description descr-string='" + \
                rserver.description + "'/>\r\n"

        if (rserver.type.lower() == "host"):
            if self.checkNone(rserver.address):
                XMLstr = XMLstr + "  <ip_address  "
                if (rserver.ipType.lower() == 'ipv4'):
                    XMLstr = XMLstr + "address='"
                else:
                    XMLstr = XMLstr + "ipv6-address='"
                XMLstr = XMLstr + rserver.address + "'/>\r\n"

            if self.checkNone(rserver.failOnAll):
                XMLstr = XMLstr + "  <fail-on-all/>\r\n"

            XMLstr = XMLstr + "  <weight value='" + str(rserver.weight) + \
                "'/>\r\n"
        else:
            if self.checkNone(rserver.webHostRedir):
                XMLstr = XMLstr + "  <webhost-redirection relocation-string='"\
                    + rserver.webHostRedir + "'/>\r\n"
                if self.checkNone(rserver.redirectionCode):
                    XMLstr = XMLstr + \
                    "  <webhost-redirection redirection-code='" + \
                    rserver.redirectionCode + "'/>\r\n"

        if (self.checkNone(rserver.maxCon) and self.checkNone(rserver.minCon)):
            XMLstr = XMLstr + "  <conn-limit max='" + str(rserver.maxCon) + \
                "' min='" + str(rserver.minCon) + "'/>\r\n"

        if self.checkNone(rserver.rateConnection):
            XMLstr = XMLstr + "  <rate-limit type='connection' value='" + \
                str(rserver.rateConnection) + "'/>\r\n"
        if self.checkNone(rserver.rateBandwidth):
            XMLstr = XMLstr + "  <rate-limit type='bandwidth' value='" + \
                str(rserver.rateBandwidth) + "'/>\r\n"

        if (rserver.state == "In Service"):
            XMLstr = XMLstr + "  <inservice/>\r\n"

        XMLstr = XMLstr + "</rserver>"

        return self.send_data(context,  XMLstr)

    def deleteRServer(self, context, rserver):
        if not self.checkNone(rserver.name):
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver sense='no' type='" + rserver.type.lower() + \
            "' name='" + rserver.name + "'></rserver>"

        return self.send_data(context,  XMLstr)

    def activateRServer(self,  context,  serverfarm,  rserver):
        if not self.checkNone(rserver.name):
            return 'RSERVER NAME ERROR'

        XMLstr = "<serverfarm type='" + serverfarm.type.lower() + \
            "' name='" + serverfarm.name + "'>"
        XMLstr = XMLstr + "  <rserver name='" + rserver.name + "'>\r\n  \
            </rserver>"
        XMLstr = XMLstr + "    <inservice/>\r\n"
        XMLstr = XMLstr + "  </rserver_sfarm>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def suspendRServer(self,  context,  serverfarm,  rserver):
        if not self.checkNone(rserver.name):
            return 'RSERVER NAME ERROR'

        XMLstr = "<serverfarm type='" + serverfarm.type.lower() + \
            "' name='" + serverfarm.name + "'>"
        XMLstr = XMLstr + "<rserver name='" + rserver.name + "'>\r\n  \
            </rserver>"
        XMLstr = XMLstr + "<inservice sense='no'/>\r\n"
        XMLstr = XMLstr + "</rserver_sfarm>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)
        
    def suspendRServerGlobal(self,  context,  rserver):
        if not self.checkNone(rserver.name):
            return 'RSERVER NAME ERROR'
        
        XMLstr = "<rserver name='" + rserver.name +"'>\r\n"
        XMLstr = XMLstr + "<inservice sense='no'/>"
        XMLstr = XMLstr +"</rserver>"
        return self.send_data(context,  XMLstr)
        
        

    def createProbe(self,  context,  probe):
        if not self.checkNone(probe.name):
            return 'PROBE NAME ERROR'
        type = probe.type.lower()
        if type == "connect":
            type = "tcp"

        probes_with_send_data = ['echo-udp',  'echo-tcp',  'finger',  'tcp',
                                'udp']
        probes_with_timeout = ['echo-tcp',  'finger',  'tcp',  'rtsp',  'http',
                                'https',  'imap',  'pop',  'sip-tcp',  'smtp',
                                'telnet']
        probes_with_credentials = ['http',  'https',  'imap',  'pop', 'radius']
        probes_with_regex = ['http',  'https',  'sip-tcp',  'sup-udp',  'tcp',
                                'udp']

        if ((type != 'echo-tcp') and (type != 'echo-udp')):
            XMLstr = "<probe_" + type + " type='" + type + "' name='" + \
                probe.name + "'>\r\n"
        else:
            XMLstr = "<probe_echo type='echo' conn-type='"
            if (type == 'echo-tcp'):
                XMLstr = XMLstr + "tcp' name='"
            else:
                XMLstr = XMLstr + "udp' name='"
            XMLstr = XMLstr + probe.name + "'>\r\n"

        if self.checkNone(probe.description):
            XMLstr = XMLstr + "  <description descr-string='" + \
                probe.description + "'/>\r\n"

        if self.checkNone(probe.probeInterval):
            XMLstr = XMLstr + "  <interval value='" + \
                str(probe.probeInterval) + "'/>\r\n"

        if (type != 'vm'):
            if self.checkNone(probe.passDetectInterval):
                XMLstr = XMLstr + "  <passdetect interval='" + \
                    str(probe.passDetectInterval) + "'/>\r\n"

            if self.checkNone(probe.passDetectCount):
                XMLstr = XMLstr + "  <passdetect count='" + \
                    str(probe.passDetectCount) + "'/>\r\n"

            if self.checkNone(probe.failDetect):
                XMLstr = XMLstr + "  <faildetect retry-count='" + \
                    str(probe.failDetect) + "'/>\r\n"

            if self.checkNone(probe.receiveTimeout):
                XMLstr = XMLstr + "  <receive timeout='" + \
                    str(probe.receiveTimeout) + "'/>\r\n"

            if ((type != 'icmp') and self.checkNone(probe.port)):
                XMLstr = XMLstr + "  <port value='" + str(probe.port) + \
                    "'/>\r\n"

            if (type != 'scripted'):
                if (self.checkNone(probe.destIP)):
                    XMLstr = XMLstr + "  <ip_address address='" + \
                        probe.destIP + "'"
                    if ((type != 'rtsp') and (type != 'sip-tcp') and \
                        (type != 'sip-udp')):
                        if self.checkNone(probe.isRouted):
                            XMLstr = XMLstr + " routing-option='routed'"
                    XMLstr = XMLstr + "/>\r\n"

            if (type == "dns"):
                if self.checkNone(probe.domainName):
                    XMLstr = XMLstr + "  <domain domain-name='" + \
                        probe.domainName + "'/>\r\n"

            if (probes_with_send_data.count(type) > 0):
                if self.checkNone(probe.sendData):
                    XMLstr = XMLstr + "  <send-data data='" + \
                        probe.sendData + "'/>\r\n"

            if (probes_with_timeout.count(type) > 0):
                if self.checkNone(probe.openTimeout):
                    XMLstr = XMLstr + "  <open timeout='" + \
                        str(probe.openTimeout) + "'/>"
                if self.checkNone(probe.tcpConnTerm):
                    XMLstr = XMLstr + "  <connection_term term='forced'/>\r\n"

            if (probes_with_credentials.count(type) > 0):
                if (self.checkNone(probe.userName) and \
                    self.checkNone(probe.password)):
                    XMLstr = XMLstr + "  <credentials username='" + \
                        probe.userName + "' password='" + probe.password
                    if (type == 'radius'):
                        if self.checkNone(probe.userSecret):
                            XMLstr = XMLstr + "' secret='" + probe.userSecret
                    XMLstr = XMLstr + "'/>\r\n"

            if (probes_with_regex.count(type) > 0):
                    if self.checkNone(probe.expectRegExp):
                        XMLstr = XMLstr + "  <expect_regex regex='" + \
                            probe.expectRegExp + "'"
                        if self.checkNone(probe.expectRegExpOffset):
                            XMLstr = XMLstr + " offset='" + \
                                str(probe.expectRegExpOffset) + "'"
                        XMLstr = XMLstr + "/>\r\n"

            if ((type == 'http') or (type == 'https')):
                if self.checkNone(probe.requestMethodType):
                    XMLstr = XMLstr + "  <request method='" + \
                        probe.requestMethodType.lower() + "' url='" + \
                        probe.requestHTTPurl.lower() + "'/>\r\n"

                if self.checkNone(probe.appendPortHostTag):
                    XMLstr = XMLstr + "  <append-port-hosttag/>\r\n"

                if self.checkNone(probe.hash):
                    XMLstr = XMLstr + "  <hash"
                    if self.checkNone(probe.hashString):
                        XMLstr = XMLstr + " hash-string='" + \
                            probe.hashString + "'"
                    XMLstr = XMLstr + "/>\r\n"

                if (type == 'https'):
                    if self.checkNone(probe.cipher):
                        XMLstr = XMLstr + "  <ssl cipher='" + \
                            probe.cipher + "'/>\r\n"
                    if self.checkNone(probe.SSLversion):
                        XMLstr = XMLstr + "  <ssl version='" + \
                            probe.SSLversion + "'/>\r\n"

            if ((type == 'pop') or (type == 'imap')):
                if self.checkNone(probe.requestCommand):
                    XMLstr = XMLstr + "  <request command='" + \
                        probe.requestCommand + "'/>\r\n"
                if (type == 'imap'):
                    if self.checkNone(probe.maibox):
                        XMLstr = XMLstr + "  <credentials mailbox='" + \
                            probe.maibox + "'/>\r\n"

            if (type == 'radius'):
                if self.checkNone(probe.NASIPaddr):
                    XMLstr = XMLstr + "  <nas ip_address='" + \
                        probe.NASIPaddr + "'/>\r\n"

            if (type == 'rtsp'):
                if self.checkNone(probe.requareHeaderValue):
                    XMLstr = XMLstr + \
                        "  <header header-name='Require' header-value='" + \
                        probe.requareHeaderValue + "'/>\r\n"

                if self.checkNone(probe.proxyRequareHeaderValue):
                    XMLstr = XMLstr + \
                        "  <header header-name='Proxy-Require' \
                        header-value='" + probe.proxyRequareHeaderValue \
                        + "'/>\r\n"

                if self.checkNone(probe.requestURL):
                    XMLstr = XMLstr + "  <request "
                    if self.checkNone(probe.requestMethodType):
                        XMLstr = XMLstr + "  method='" + \
                            probe.requestMethodType + "' "
                    XMLstr = XMLstr + "url='" + probe.requestURL + "'/>\r\n"

            # Need add download script section for this type
            if (type == 'scripted'):
                if self.checkNone(probe.scriptName):
                    XMLstr = XMLstr + "  <script_elem script-name='" + \
                        probe.scriptName
                    if self.checkNone(probe.scriptArgv):
                        XMLstr = XMLstr + "' script-arguments='" + \
                           probe.scriptArgv
                    XMLstr = XMLstr + "'/>\r\n"

            if ((type == 'sip-udp') and self.checkNone(probe.Rport)):
                XMLstr = XMLstr + "  <rport type='enable'/>\r\n"

            if (type == 'snmp'):
                if self.checkNone(probe.SNMPver):
                    XMLstr = XMLstr + "  <version value='" + probe.SNMPver + \
                        "'/>\r\n"
                    if self.checkNone(probe.SNMPComm):
                        XMLstr = XMLstr + "  <community community-string='" + \
                            probe.SNMPComm + "'/>\r\n"

        else:   # for type == vm
            if self.checkNone(probe.VMControllerName):
                XMLstr = XMLstr + "  <vm-controller name='" + \
                    probe.VMControllerName + "'/>\r\n"
                if (self.checkNone(probe.maxCPUburstThresh) or \
                    self.checkNone(probe.minCPUburstThresh)):
                    XMLstr = XMLstr + \
                        "  <load type='cpu' param='burst-threshold'"
                    if self.checkNone(probe.maxCPUburstThresh):
                        XMLstr = XMLstr + " max='" + \
                            probe.maxCPUburstThresh + "'"
                    if self.checkNone(probe.minCPUburstThresh):
                        XMLstr = XMLstr + " min='" + \
                            probe.minCPUburstThresh + "'"
                    XMLstr = XMLstr + "/>\r\n"
                if (self.checkNone(probe.maxMemBurstThresh) or \
                    self.checkNone(probe.minMemBurstThresh)):
                    XMLstr = XMLstr + \
                        "  <load type='mem' param='burst-threshold'"
                    if self.checkNone(probe.maxMemBurstThresh):
                        XMLstr = XMLstr + " max='" + probe.maxMemBurstThresh \
                            + "'"
                    if self.checkNone(probe.minMemBurstThresh):
                        XMLstr = XMLstr + " min='" + probe.minMemBurstThresh \
                            + "'"
                    XMLstr = XMLstr + "/>\r\n"

        if ((type != 'echo-tcp') and (type != 'echo-udp')):
            XMLstr = XMLstr + "</probe_" + type + ">\r\n"
        else:
            XMLstr = XMLstr + "</probe_echo>"

        return self.send_data(context,  XMLstr)

    def deleteProbe(self,  context,  probe):
        if not self.checkNone(probe.name):
            return 'PROBE NAME ERROR'
        type = probe.type.lower()
        if type == "connect":
            type = "tcp"

        if ((type != 'echo-tcp') and (type != 'echo-udp')):
            XMLstr = "<probe_" + type + " type='" + type + "' name='" + \
                probe.name + "' sense='no'>\r\n</probe_" + type + ">"
        else:
            XMLstr = "<probe_echo type='echo' conn-type='"
            if (type == 'echo-tcp'):
                XMLstr = XMLstr + "tcp' name='"
            else:
                XMLstr = XMLstr + "udp' name='"
            XMLstr = XMLstr + probe.name + "' sense='no'>\r\n</probe_echo>"

        return self.send_data(context,  XMLstr)

    def createServerFarm(self,  context,  serverfarm):
        if not self.checkNone(serverfarm.name):
            return "SERVER FARM NAME ERROR"

        XMLstr = "<serverfarm type='" + serverfarm.type.lower() + \
            "' name='" + serverfarm.name + "'>\r\n"

        if self.checkNone(serverfarm.description):
            XMLstr = XMLstr + "  <description descr-string='" + \
                serverfarm.description + "'/> \r\n"

        if self.checkNone(serverfarm.failAction):
            XMLstr = XMLstr + "  <failaction failaction-type='" + \
                serverfarm.failAction + "'/>\r\n"

        if self.checkNone(serverfarm._predictor):
            XMLstr = XMLstr + "  <predictor predictor-method='" + \
                serverfarm._predictor.type.lower() + "'/>\r\n"

        if self.checkNone(serverfarm._probes):
            for probe in serverfarm._probes:
                XMLstr = XMLstr + "  <probe_sfarm probe-name='" + \
                    probe.name + "'/>\r\n"

        if serverfarm.type.lower() == "host":
            if self.checkNone(serverfarm.failOnAll):
                XMLstr = XMLstr + "  <probe_sfarm probe-name='fail-on-all'/>\r\n"

            if self.checkNone(serverfarm.transparent):
                XMLstr = XMLstr + "  <transparent/>\r\n"

            if self.checkNone(serverfarm.partialThreshPercentage) and \
                self.checkNone(serverfarm.backInservice):
                XMLstr = XMLstr + "  <partial-threshold value='" + \
                    serverfarm.partialThreshPercentage + "' back-inservice='" \
                    + serverfarm.backInservice + "'/>\r\n"

            if self.checkNone(serverfarm.inbandHealthCheck):
                XMLstr = XMLstr + "  <inband-health check='" + \
                    serverfarm.inbandHealthCheck + "'"
                if serverfarm.inbandHealthCheck.lower == "log":
                    XMLstr = XMLstr + "threshold='" + \
                        str(serverfarm.connFailureThreshCount) + \
                        "' reset='" + str(serverfarm.resetTimeout) + \
                        "'"
                        #Do deploy if  resetTimeout='' ?

                if serverfarm.inbandHealthCheck.lower == "remove":
                    XMLstr = XMLstr + "threshold='" + \
                        str(serverfarm.connFailureThreshCount) + \
                        "' reset='" + str(serverfarm.resetTimeout) + \
                        "'  resume-service='" + \
                        str(serverfarm.resumeService) + "'"
                        #Do deploy if  resumeService='' ?
                XMLstr = XMLstr + "/>\r\n"

            if self.checkNone(serverfarm.dynamicWorkloadScale):
            # Need to upgrade (may include VM's)
                XMLstr = XMLstr + "<dws type='" + serverfarm.failAction + \
                    "'/>\r\n"

        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def deleteServerFarm(self,  context,  serverfarm):
        if not self.checkNone(serverfarm.name):
            return 'SERVER FARM NAME ERROR'

        XMLstr = "<serverfarm sense='no' name='" + serverfarm.name + \
            "'></serverfarm>"

        return self.send_data(context,  XMLstr)

    def addRServerToSF(self,  context,  serverfarm,  rserver):
    #rserver in sfarm may include many parameters !
        if not self.checkNone(serverfarm.name) or not \
            self.checkNone(rserver.name):
            return "ERROR"

        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr = XMLstr + "  <rserver_sfarm name='" + rserver.name + "'"
        if self.checkNone(rserver.port):
            XMLstr = XMLstr + " port='" + rserver.port + "'"
        XMLstr = XMLstr + ">\r\n"
        if self.checkNone(rserver.weight):
            XMLstr = XMLstr + "    <weight value='" + str(rserver.weight) + \
                "'/>\r\n"
        if self.checkNone(rserver.backupRS):
            XMLstr = XMLstr + "    <backup-rserver rserver-name='" + \
                rserver.backupRS + "'"
            if self.checkNone(rserver.backupRSport):
                XMLstr = XMLstr + " port='" + rserver.backupRSport + "'"
            XMLstr = XMLstr + "/>\r\n"
        if self.checkNone(rserver.maxCon) and self.checkNone(rserver.minCon):
            XMLstr = XMLstr + "    <conn-limit max='" + str(rserver.maxCon) + \
                "' min='" + str(rserver.minCon) + "'/>\r\n"

        # this parameters does not work
        #if self.checkNone(rserver.rateConnection):
        #    XMLstr = XMLstr+"    <rate-limit type='connection' value='"
        #+str(rserver.rateConnection)+"'/>\r\n"
        #if self.checkNone(rserver.rateBandwidth):
        #   XMLstr = XMLstr+"    <rate-limit type='bandwidth' value='bandwidth'
        # value='"+str(rserver.rateBandwidth)+"'/>\r\n"

        if self.checkNone(rserver.cookieStr):
            XMLstr = XMLstr + "    <cookie-string cookie-value='" + \
                rserver.cookieStr + "'/>\r\n"

#        for i in range(len(rserver._probes)):
#            XMLstr = XMLstr + "    <probe_sfarm probe-name='" + \
#               rserver._probes[i] + "'/>\r\n"
        if self.checkNone(rserver.failOnAll):
            XMLstr = XMLstr + "    <probe_sfarm probe-name='fail-on-all'/>"
        if self.checkNone(rserver.state):
            if rserver.state.lower() == "inservice":
                XMLstr = XMLstr + "    <inservice/>\r\n"
            if rserver.state.lower() == "standby":
                XMLstr = XMLstr + "    <inservice mode='" + \
                    rserver.state.lower() + "'/>\r\n"
            if rserver.state.lower() == "outofservice":
                XMLstr = XMLstr + "    <inservice sense='no'/>\r\n"
        XMLstr = XMLstr + "  </rserver_sfarm>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def deleteRServerFromSF(self,  context,  serverfarm,  rserver):
        if not self.checkNone(serverfarm.name) or not \
            self.checkNone(rserver.name):
            return "ERROR"

        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr = XMLstr + "<rserver_sfarm sense='no' name='" + \
            rserver.name + "'"
        if self.checkNone(rserver.port):
            XMLstr = XMLstr + " port='" + rserver.port + "'"
        XMLstr = XMLstr + ">\r\n"
        XMLstr = XMLstr + "</rserver_sfarm>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def addProbeToSF(self,  context,  serverfarm,  probe):
        if not self.checkNone(serverfarm.name) or not \
            self.checkNone(probe.name):
            return "ERROR"

        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr = XMLstr + " <probe_sfarm probe-name='" + probe.name + "'/>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def deleteProbeFromSF(self,  context,  serverfarm,  probe):
        if not self.checkNone(serverfarm.name) or not \
            self.checkNone(probe.name):
            return "ERROR"

        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr = XMLstr + " <probe_sfarm sense='no' probe-name='" + \
            probe.name + "'/>\r\n"
        XMLstr = XMLstr + "</serverfarm>"

        return self.send_data(context,  XMLstr)

    def createStickiness(self,  context, sticky):
        if not self.checkNone(sticky.name):
            return "ERROR"

        name = sticky.name

        if sticky.type.lower() == "httpcontent":
            XMLstr = "<sticky http-content='http-content' \
                sticky-group-name='" + name + "'>\r\n"
            if self.checkNone(sticky.offset) or self.checkNone(sticky.length) \
                or self.checkNone(sticky.beginPattern) or \
                self.checkNone(sticky.endPattern):
                XMLstr = XMLstr + "<content "
                if self.checkNone(sticky.offset):
                    XMLstr = XMLstr + " offset='" + str(sticky.offset) + "'"
                if self.checkNone(sticky.length):
                    XMLstr = XMLstr + " length='" + str(sticky.length) + "'"
                if self.checkNone(sticky.beginPattern):
                    XMLstr = XMLstr + " begin-pattern_expression='" + \
                        sticky.beginPattern + "'"
                if self.checkNone(sticky.endPattern) and not \
                    self.checkNone(sticky.length):
                    XMLstr = XMLstr + " end-pattern_expression='eennndd'"
                XMLstr = XMLstr + "/>\r\n"

        if sticky.type.lower() == "httpcookie":
            XMLstr = "<sticky http-cookie='" + sticky.cookieName + \
                "' sticky-group-name='" + name + "'>\r\n"
            if self.checkNone(sticky.enableInsert):
                XMLstr = XMLstr + "<cookie config-type='insert'"
                if self.checkNone(sticky.enableInsert):
                    XMLstr = XMLstr + \
                        " specify-expire-keyword='browser-expire'"
                XMLstr = XMLstr + "/>\r\n"
            if self.checkNone(sticky.offset) or self.checkNone(sticky.length):
                XMLstr = XMLstr + "<cookie config-type='offset'"
                if self.checkNone(sticky.offset):
                    XMLstr = XMLstr + " offset-value='" + \
                        str(sticky.offset) + "'"
                if self.checkNone(sticky.length):
                    XMLstr = XMLstr + " length='" + str(sticky.length) + "'"
                XMLstr = XMLstr + "/>\r\n"
            if self.checkNone(sticky.secondaryName):
                XMLstr = XMLstr + "<cookie config-type='secondary' \
                    secondary-cookie-name='" + sticky.secondaryName + "'/>\r\n"

        if sticky.type.lower() == "httpheader":
            XMLstr = "<sticky http-header='" + sticky.headerName + \
                "' sticky-group-name='" + name + "'>\r\n"
            if self.checkNone(sticky.offset) or self.checkNone(sticky.length):
                XMLstr = XMLstr + "<header_offset"
                if self.checkNone(sticky.offset):
                    XMLstr = XMLstr + " offset='" + str(sticky.offset) + "'"
                if self.checkNone(sticky.length):
                    XMLstr = XMLstr + " length='" + str(sticky.length) + "'"
                XMLstr = XMLstr + "/>\r\n"

        if sticky.type.lower() == "ipnetmask":
            XMLstr = "<sticky sticky-type='ip-netmask' netmask='" + \
                str(sticky.netmask) + "' address='" + \
                sticky.addressType.lower() + "' sticky-group-name='" + \
                name + "'>\r\n"
            if self.checkNone(sticky.ipv6PrefixLength):
                XMLstr = XMLstr + "<v6-prefix prefix-length='" + \
                    str(sticky.ipv6PrefixLength) + "'/>\r\n"

        if sticky.type.lower() == "v6prefix":
            XMLstr = "<sticky sticky-type='v6-prefix' prefix-length='" + \
                str(sticky.prefixLength) + "' address='" + \
                sticky.addressType.lower() + "' sticky-group-name='" + \
                name + "'>\r\n"
            if self.checkNone(sticky):
                XMLstr = XMLstr + "<ip-netmask netmask='" + \
                    str(sticky.netmask) + "'/>\r\n"

        if sticky.type.lower() == "l4payload":
            XMLstr = "<sticky sticky-group-name='" + name + "'>\r\n"
            if self.checkNone(sticky.enableStickyForResponse):
                XMLstr = XMLstr + "<response response-info='sticky'/>\r\n"
            if self.checkNone(sticky.offset) or self.checkNone(sticky.length) \
                or self.checkNone(sticky.beginPattern) or \
                self.checkNone(sticky.endPattern):
                XMLstr = XMLstr + "<l4payload "
                if self.checkNone(sticky.offset):
                    XMLstr = XMLstr + " offset='" + str(sticky.offset) + "'"
                if self.checkNone(sticky.length):
                    XMLstr = XMLstr + " length='" + str(sticky.length) + "'"
                if self.checkNone(sticky.beginPattern):
                    XMLstr = XMLstr + " begin-pattern_expression='" + \
                        sticky.beginPattern + "'"
                if self.checkNone(sticky.endPattern) and not \
                    self.checkNone(sticky.length):
                    XMLstr = XMLstr + " end-pattern_expression='eennndd'"
                XMLstr = XMLstr + "/>\r\n"

        if sticky.type.lower() == "radius":
        # without sticky.radiusTypes
            XMLstr = "<sticky sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "rtspheader":
            XMLstr = "<sticky rtsp-header='Session' sticky-group-name='" + \
                name + "'>\r\n"
            if boot(sticky.offset) or boot(sticky.length):
                XMLstr = XMLstr + "<header_offset"
                if self.checkNone(sticky.offset):
                    XMLstr = XMLstr + " offset='" + str(sticky.offset) + "'"
                if self.checkNone(sticky.length):
                    XMLstr = XMLstr + " length='" + str(sticky.length) + "'"
                XMLstr = XMLstr + "/>\r\n"

        if sticky.type.lower() == "sipheader":
            XMLstr = "<sticky sip-header='Call-ID' sticky-group-name='" + \
                name + "'>\r\n"

        if self.checkNone(sticky.timeout):
            XMLstr = XMLstr + "<timeout timeout-value='" + \
                str(sticky.timeout) + "'/>\r\n"
        if self.checkNone(sticky.timeoutActiveConn):
            XMLstr = XMLstr + "<timeout config-type='activeconns'/>\r\n"
        if self.checkNone(sticky.replicateOnHAPeer):
            XMLstr = XMLstr + "<replicate replicate-info='sticky'/>\r\n"
        if self.checkNone(sticky.serverFarm):
            XMLstr = XMLstr + "<serverfarm_sticky sfarm-name='" + \
                sticky.serverFarm + "'"
            if self.checkNone(sticky.backupServerFarm):
                XMLstr = XMLstr + " backup='" + sticky.backupServerFarm + "' "
                if self.checkNone(sticky.enableStyckyOnBackupSF):
                    XMLstr = XMLstr + "sfarm-behaviour='sticky'"
                if self.checkNone(sticky.aggregateState):
                    XMLstr = XMLstr + " backup-sfarm-state='aggregate-state'"
            XMLstr = XMLstr + "/>\r\n"
        XMLstr = XMLstr + "</sticky>"

        return self.send_data(context,  XMLstr)

    def deleteStickiness(self,  context,   sticky):
        if not self.checkNone(sticky.name):
            return "ERROR"

        name = sticky.name

        if sticky.type.lower() == "httpcontent":
            XMLstr = "<sticky sense='no' http-content='http-content' \
                sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "httpcookie":
            XMLstr = "<sticky sense='no' http-cookie='" + sticky.cookieName + \
                "' sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "httpheader":
            XMLstr = "<sticky sense='no' http-header='" + sticky.headerName + \
                "' sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "ipnetmask":
            XMLstr = "<sticky sense='no' sticky-type='ip-netmask' netmask='" \
                + str(sticky.netmask) + "' address='" + \
                sticky.addressType.lower() + "' sticky-group-name='" + \
                name + "'>\r\n"

        if sticky.type.lower() == "v6prefix":
            XMLstr = "<sticky sense='no' sticky-type='v6-prefix' \
                prefix-length='" + str(sticky.prefixLength) + "' address='" + \
                sticky.addressType.lower() + "' sticky-group-name='" + \
                name + "'>\r\n"

        if sticky.type.lower() == "l4payload":
            XMLstr = "<sticky sense='no' sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "radius":
        # without sticky.radiusTypes
            XMLstr = "<sticky sense='no' sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "rtspheader":
            XMLstr = "<sticky sense='no' rtsp-header='Session' \
                sticky-group-name='" + name + "'>\r\n"

        if sticky.type.lower() == "sipheader":
            XMLstr = "<sticky sense='no' sip-header='Call-ID' \
                sticky-group-name='" + name + "'>\r\n"

        XMLstr = XMLstr + "</sticky>"

        return self.send_data(context,  XMLstr)
        
    def addACLEntry(self,  context,  vip):
            XMLstr = "<access-list id='vip-acl' config-type='extended' \
            perm-value='permit' protocol-name='ip' src-type='any' \
            host_dest-addr='" + vip.address + "'/>\r\n"
            try:
                self.send_data(context,  XMLstr)
            except:
                logger.warning("Got exception during deploying ACL. It could be ok.")
            

    def createVIP(self,  context, vip,  sfarm):
        if not self.checkNone(vip.name) or not self.checkNone(vip.name) \
            or not self.checkNone(vip.address):
            return "ERROR"

        sn = "2"
        if self.checkNone(vip.allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + md5.new(vip.VLAN).hexdigest()

        #  Add a access-list
        self.addACLEntry(context,  vip)

        # Add a policy-map
        if vip.appProto.lower() == "other" or vip.appProto.lower() == "http":
            vip.appProto = ""
        else:
            vip.appProto = "_" + vip.appProto.lower()

        XMLstr = "<policy-map_lb type='loadbalance" + vip.appProto + \
            "' match-type='first-match' pmap-name='" + vip.name + \
            "-l7slb'>\r\n"
        XMLstr = XMLstr + \
            "<class_pmap_lb match-cmap-default='class-default'>\r\n"
        XMLstr = XMLstr + "<serverfarm_pmap sfarm-name='" + sfarm.name + "'"
        if self.checkNone(vip.backupServerFarm):
            XMLstr = XMLstr + " backup-name='" + vip.backupServerFarm + "'"
        XMLstr = XMLstr + "/>\r\n"
        XMLstr = XMLstr + "</class_pmap_lb>\r\n"
        XMLstr = XMLstr + "</policy-map_lb>\r\n"

        # Add a class-map
        XMLstr = XMLstr + "<class-map match-type='match-all' name='" + \
            vip.name + "'>\r\n"
        XMLstr = XMLstr + "<match_virtual-addr seq-num='" + sn + \
            "' virtual-address='" + vip.address + "' net-mask='" + \
            str(vip.mask) + "'"
        XMLstr = XMLstr + " protocol-type='" + vip.proto.lower() + "'"
        if vip.proto.lower() != "any":
            XMLstr = XMLstr + " operator='eq' port-1='" + str(vip.port) + "'"
        XMLstr = XMLstr + "/>\r\n"
        XMLstr = XMLstr + "</class-map>\r\n"

        #  Add a policy-map (multimatch) with class-map
        XMLstr = XMLstr + "<policy-map_multimatch match-type='multi-match' \
            pmap-name='" + pmap + "'>\r\n"
        XMLstr = XMLstr + "<class match-cmap='" + vip.name + "'>\r\n"

        if self.checkNone(vip.status):
            XMLstr = XMLstr + "<loadbalance vip_config-type='" + \
                vip.status.lower() + "'/>\r\n"

        XMLstr = XMLstr + "<loadbalance policy='" + vip.name + "-l7slb'/>\r\n"
        if self.checkNone(vip.ICMPreply):
            XMLstr = XMLstr + \
                "<loadbalance vip_config-type='icmp-reply'/>\r\n"

        XMLstr = XMLstr + "</class>\r\n"
        XMLstr = XMLstr + "</policy-map_multimatch>\r\n"

        s = XmlSender(context)
        tmp = s.deployConfig(context, XMLstr)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        if self.checkNone(vip.allVLANs):
            XMLstr = "<service-policy type='input' name='" + pmap + "'/>"
        else:
            #  Add service-policy for necessary vlans
            if is_sequence(vip.VLAN):
                for i in vip.VLAN:
                    XMLstr = "<interface type='vlan' number='" + str(i) + \
                        "'>\r\n"
                    XMLstr = XMLstr + "<service-policy type='input' name='" + \
                        pmap + "'/>\r\n"
                    XMLstr = XMLstr + "</interface>"
                    tmp = s.deployConfig(context, XMLstr)
                    
                    XMLstr = "<interface type='vlan' number='" + str(i) + \
                        "'>\r\n"
                    XMLstr = XMLstr + \
                        "<access-group access-type='input' \
                        name='vip-acl'/>\r\n"
                    XMLstr = XMLstr + "</interface>"
                    try:
                        #Try to add access list. if it is already assigned exception will occur
                        tmp = s.deployConfig(context, XMLstr)
                    except:
                        logger.warning("Got exception on acl set")                    
                    
            else:
                    XMLstr = "<interface type='vlan' number='" + \
                        str(vip.VLAN) + "'>\r\n"
                    XMLstr = XMLstr + \
                        "<service-policy type='input' name='" + \
                        pmap + "'/>\r\n"
                    XMLstr = XMLstr + "</interface>"
                    tmp = s.deployConfig(context, XMLstr)
                    XMLstr = "<interface type='vlan' number='" + \
                        str(vip.VLAN) + "'>\r\n"
                    XMLstr = XMLstr + \
                        "<access-group access-type='input' \
                        name='vip-acl'/>\r\n"
                    XMLstr = XMLstr + "</interface>"
                    try:
                        tmp = s.deployConfig(context, XMLstr)
                    except:
                       logger.warning("Got exception on acl set")                    

        return 'OK'

    def deleteVIP(self,  context,  vip):
        if self.checkNone(vip.allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + md5.new(vip.VLAN).hexdigest()

        XMLstr = "<policy-map_multimatch match-type='multi-match' \
            pmap-name='" + pmap + "'>\r\n"
        XMLstr = XMLstr + "<class sense='no' match-cmap='" + \
            vip.name + "'>\r\n"
        XMLstr = XMLstr + "</class>\r\n"
        XMLstr = XMLstr + "</policy-map_multimatch>\r\n"
        logger.debug("pmap name is %s" % pmap)
        logger.debug("Trying to do %s" % XMLstr)
        s = XmlSender(context)
        tmp = s.deployConfig(context, XMLstr)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        #3) Delete policy-map, class-map and access-list
        if vip.appProto.lower() == "other" or vip.appProto.lower() == "http":
            vip.appProto = ""
        else:
            vip.appProto = "_" + vip.appProto.lower()
        XMLstr = "<policy-map_lb sense='no' type='loadbalance" + vip.appProto
        XMLstr = XMLstr + "' match-type='first-match' pmap-name='" + \
            vip.name + "-l7slb'>\r\n"
        XMLstr = XMLstr + "</policy-map_lb>\r\n"

        XMLstr = XMLstr + \
            "<class-map sense='no' match-type='match-all' name='" + \
            vip.name + "'>\r\n"
        XMLstr = XMLstr + "</class-map>\r\n"

        XMLstr = XMLstr + \
            "<access-list sense='no' id='vip-acl' \
            config-type='extended' perm-value='permit' "
        XMLstr = XMLstr + \
            "protocol-name='ip' src-type='any' host_dest-addr='" + \
            vip.address + "'/>\r\n"

        tmp = s.deployConfig(context, XMLstr)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        XMLstr = 'show running-config policy-map %s' % pmap
        last_policy_map = \
            self.checkNone(s.getConfig(context,  XMLstr).find('class'))

        if (last_policy_map):
            # Remove service-policy from VLANs
            #(Perform if deleted last VIP with it service-policy)
            if self.checkNone(vip.allVLANs):
                XMLstr = "<service-policy sense='no' type='input' name='" + \
                    pmap + "'/>"
            else:
                #  Add service-policy for necessary vlans
                if is_sequence(vip.VLAN):
                    for i in vip.VLAN:
                        XMLstr = "<interface type='vlan' number='" + \
                            str(i) + "'>\r\n"
                        XMLstr = XMLstr + \
                            "<service-policy sense='no' type='input' \
                            name='" + pmap + "'/>\r\n"
                        XMLstr = XMLstr + "</interface>"
                        tmp = s.deployConfig(context, XMLstr)

                        XMLstr = "<interface type='vlan' number='" + \
                            str(i) + "'>\r\n"
                        XMLstr = XMLstr + \
                            "<access-group sense='no' access-type='input' \
                            name='vip-acl'/>\r\n"
                        XMLstr = XMLstr + "</interface>"
                        tmp = s.deployConfig(context, XMLstr)
                else:
                        XMLstr = "<interface type='vlan' number='" + \
                            str(vip.VLAN) + "'>\r\n"
                        XMLstr = XMLstr + \
                            "<service-policy sense='no' type='input' \
                            name='" + pmap + "'/>\r\n"
                        XMLstr = XMLstr + "<access-group sense='no' \
                            access-type='input' name='vip-acl'/>\r\n"
                        XMLstr = XMLstr + "</interface>"
                        tmp = s.deployConfig(context, XMLstr)
        return "OK"
