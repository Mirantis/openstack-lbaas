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

    def send_data(self,  context,  cmd):
        s = XmlSender(context)
        tmp = s.deployConfig(context,  cmd)
        if (tmp == 'OK'):
            return tmp
        else:
            raise openstack.common.exception.Invalid(tmp)

    def getContext(self,  dev):
        logger.debug("Creating context with params: IP %s, Port: %s" % \
            (dev.ip,  dev.port))
        return Context(dev.ip, dev.port, dev.user,  dev.password)

    def createRServer(self,  context,  rserver):
        srv_type = rserver.type.lower()

        cmd = "rserver " + srv_type + " " + rserver.name + "\n"

        if self.checkNone(rserver.description):
            cmd += "description " + rserver.description + "\n"

        if (srv_type == "host"):
            if self.checkNone(rserver.address):
                cmd += "ip address " + rserver.address + "\n"
            if self.checkNone(rserver.failOnAll):
                cmd += "fail-on-all\n"
            cmd += "weight " + str(rserver.weight) + "\n"
        else:
            if self.checkNone(rserver.webHostRedir):
                cmd += "webhost-redirection " + rserver.webHostRedir
                if self.checkNone(rserver.redirectionCode):
                    cmd += " " + rserver.redirectionCode
                cmd += "\n"

        if (self.checkNone(rserver.maxCon) and self.checkNone(rserver.minCon)):
            cmd += "conn-limit max " + str(rserver.maxCon) + \
                " min " + str(rserver.minCon) + "\n"

        if self.checkNone(rserver.rateConnection):
            cmd += "rate-limit connection " + \
                str(rserver.rateConnection) + "\n"
        if self.checkNone(rserver.rateBandwidth):
            cmd += "rate-limit bandwidth " + \
                str(rserver.rateBandwidth) + "\n"

        if (rserver.state == "In Service"):
            cmd += "inservice\n"

        return self.send_data(context,  cmd)

    def deleteRServer(self, context, rserver):
        cmd = "no rserver " + rserver.name + "\n"
        return self.send_data(context,  cmd)

    def activateRServer(self,  context,  serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "rserver " + rserver.name + "\n"
        cmd += "inservice\n"
        return self.send_data(context,  cmd)

    def suspendRServer(self,  context,  serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "rserver " + rserver.name + "\n"
        cmd += "no inservice"
        return self.send_data(context,  cmd)
        
    def suspendRServerGlobal(self,  context,  rserver):
        cmd = "rserver " + rserver.name + "\n"
        cmd += "no inservice\n"
        return self.send_data(context,  cmd)

    def createProbe(self,  context,  probe):
        pr_type = probe.type.lower()
        if pr_type == "connect":
            pr_type = "tcp"
        if pr_type == "echo-tcp":
            pr_type = "echo tcp"
        if pr_type == "echo-udp":
            pr_type = "echo udp"
        if pr_type == "sip-tcp":
            pr_type = "sip tcp"
        if pr_type == "sip-udp":
            pr_type = "sip udp"
        """ probes_with_send_data """
        pr_sd = ['echo udp',  'echo tcp',  'finger',  'tcp',  'udp']
        """ probes_with_timeout """
        pr_tm = ['echo tcp',  'finger',  'tcp',  'rtsp',  'http',
                 'https',  'imap',  'pop',  'sip-tcp',  'smtp',  'telnet']
        """ probes_with_credentials """
        pr_cr = ['http',  'https',  'imap',  'pop', 'radius']
        """ probes_with_regex """
        pr_rg = ['http',  'https',  'sip-tcp',  'sup-udp',  'tcp',  'udp']

        cmd = "probe " + pr_type + " " + probe.name + "\n"

        if self.checkNone(probe.description):
            cmd += "description " + probe.description + "\n"

        if self.checkNone(probe.probeInterval):
            cmd += "interval " + str(probe.probeInterval) + "\n"

        if (pr_type != 'vm'):
            if self.checkNone(probe.passDetectInterval):
                cmd += "passdetect interval" + \
                    str(probe.passDetectInterval) + "\n"

            if self.checkNone(probe.passDetectCount):
                cmd += "passdetect count" + \
                    str(probe.passDetectCount) + "\n"

            if self.checkNone(probe.failDetect):
                cmd += "faildetect " + str(probe.failDetect) + "\n"

            if self.checkNone(probe.receiveTimeout):
                cmd += "receive " + str(probe.receiveTimeout) + "\n"

            if ((pr_type != 'icmp') and self.checkNone(probe.port)):
                cmd += "port " + str(probe.port) + "\n"

            if (pr_type != 'scripted'):
                if (self.checkNone(probe.destIP)):
                    cmd += "ip address " + probe.destIP
                    if ((pr_type != 'rtsp') and (pr_type != 'sip tcp') and \
                        (pr_type != 'sip udp') and \
                        self.checkNone(probe.isRouted)):
                            cmd += " routed"
                    cmd += "\n"

            if (pr_type == "dns"):
                if self.checkNone(probe.domainName):
                    cmd += "domain " + probe.domainName + "\n"

            if (pr_sd.count(pr_type) > 0):
                if self.checkNone(probe.sendData):
                    cmd += "send-data " + probe.sendData + "\n"

            if (pr_tm.count(pr_type) > 0):
                if self.checkNone(probe.openTimeout):
                    cmd += "open " + str(probe.openTimeout) + "\n"
                if self.checkNone(probe.tcpConnTerm):
                    cmd += "connection term forced\n"

            if (pr_cr.count(pr_type) > 0):
                if (self.checkNone(probe.userName) and \
                    self.checkNone(probe.password)):
                    cmd += "credentials " + probe.userName 
                    cmd += " " + probe.password
                    if (type == 'radius'):
                        if self.checkNone(probe.userSecret):
                            cmd += " secret " + probe.userSecret
                    cmd += "\n"

            if (pr_rg.count(pr_type) > 0):
                if self.checkNone(probe.expectRegExp):
                    cmd += "expect regex " + probe.expectRegExp
                    if self.checkNone(probe.expectRegExpOffset):
                        cmd += " offset " + str(probe.expectRegExpOffset)
                    cmd += "\n"

            if ((pr_type == 'http') or (pr_type == 'https')):
                if self.checkNone(probe.requestMethodType):
                    cmd += "request method " + \
                        probe.requestMethodType.lower() + " url " + \
                        probe.requestHTTPurl.lower() + "\n"

                if self.checkNone(probe.appendPortHostTag):
                    cmd += "append-port-hosttag\n"

                if self.checkNone(probe.hash):
                    cmd += "hash"
                    if self.checkNone(probe.hashString):
                        cmd += probe.hashString
                    cmd += "\n"

                if (pr_type == 'https'):
                    if self.checkNone(probe.cipher):
                        cmd += "ssl cipher " + probe.cipher + "\n"
                    if self.checkNone(probe.SSLversion):
                        cmd += "ssl version " + probe.SSLversion + "\n"

            if ((pr_type == 'pop') or (pr_type == 'imap')):
                if self.checkNone(probe.requestCommand):
                    cmd += "request command " + probe.requestCommand + "\n"
                if (pr_type == 'imap'):
                    if self.checkNone(probe.maibox):
                        cmd += "credentials mailbox" + probe.maibox + "\n"

            if (pr_type == 'radius'):
                if self.checkNone(probe.NASIPaddr):
                    cmd += "nas ip address " + probe.NASIPaddr + "\n"

            if (pr_type == 'rtsp'):
                if self.checkNone(probe.requareHeaderValue):
                    cmd += "header require header-value " + \
                        probe.requareHeaderValue + "\n"

                if self.checkNone(probe.proxyRequareHeaderValue):
                    cmd += "header proxy-require header-value " + \
                        probe.proxyRequareHeaderValue + "\n"

                if self.checkNone(probe.requestURL):
                    if self.checkNone(probe.requestMethodType):
                        cmd += "request method" + probe.requestMethodType
                        cmd += " url " + probe.requestURL + "\n"

            if (pr_type == 'scripted'):
                if self.checkNone(probe.scriptName):
                    cmd += "script " + probe.scriptName
                    if self.checkNone(probe.scriptArgv):
                        cmd += " " + probe.scriptArgv
                    cmd += "\n"

            if ((pr_type == 'sip-udp') and self.checkNone(probe.Rport)):
                cmd += "rport enable\n"

            if (type == 'snmp'):
                if self.checkNone(probe.SNMPver):
                    cmd += "version " + probe.SNMPver + "\n"
                    if self.checkNone(probe.SNMPComm):
                        cmd += "community " + probe.SNMPComm + "\n"

        else:   # for type == vm
            if self.checkNone(probe.VMControllerName):
                cmd += "vm-controller " + probe.VMControllerName + "\n"
                if (self.checkNone(probe.maxCPUburstThresh) and \
                    self.checkNone(probe.minCPUburstThresh)):
                    cmd += "load cpu burst-threshold max " + \
                        probe.maxCPUburstThresh + " min " + \
                        probe.minCPUburstThresh + "\n"
                if (self.checkNone(probe.maxMemBurstThresh) and \
                    self.checkNone(probe.minMemBurstThresh)):
                    cmd += "load mem burst-threshold max " + \
                        probe.maxMemBurstThresh + " min " + \
                        probe.minMemBurstThresh + "\n"

        return self.send_data(context,  cmd)

    def deleteProbe(self,  context,  probe):
        pr_type = probe.type.lower()
        if pr_type == "connect":
            pr_type = "tcp"
        if pr_type == "echo-tcp":
            pr_type = "echo tcp"
        if pr_type == "echo-udp":
            pr_type = "echo udp"
        if pr_type == "sip-tcp":
            pr_type = "sip tcp"
        if pr_type == "sip-udp":
            pr_type = "sip udp"
        cmd = "no probe " + pr_type + " " + probe.name + "\n"
        return self.send_data(context,  cmd)

    def createServerFarm(self,  context,  serverfarm):
        sf_type = serverfarm.type.lower()
        cmd = "serverfarm " + sf_type + " " + serverfarm.name + "\n"

        if self.checkNone(serverfarm.description):
            cmd += "description " + serverfarm.description + "\n"

        if self.checkNone(serverfarm.failAction):
            cmd += "failaction " + serverfarm.failAction + "\n"

        if self.checkNone(serverfarm.predictor):
            cmd += "predictor " + serverfarm._predictor.type.lower() + "\n"

        if (sf_type == "host"):
            if self.checkNone(serverfarm.failOnAll):
                cmd += "fail-on-all\n"

            if self.checkNone(serverfarm.transparent):
                cmd += "transparent\n"

            if self.checkNone(serverfarm.partialThreshPercentage) and \
                self.checkNone(serverfarm.backInservice):
                cmd += "partial-threshold " + \
                    str(serverfarm.partialThreshPercentage) + \
                    " back-inservice " + str(serverfarm.backInservice) + "\n"

            if self.checkNone(serverfarm.inbandHealthCheck):
                cmd += "inband-health check " + \
                    serverfarm.inbandHealthCheck + "\n"
                h_check = serverfarm.inbandHealthCheck.lower()
                if ((h_check == "log") and \
                    self.checkNone(serverfarm.resetTimeout)):
                    cmd += str(serverfarm.connFailureThreshCount) + \
                        " reset " + str(serverfarm.resetTimeout) + "\n"
                elif (h_check == "remove"):
                    if (self.checkNone(serverfarm.resetTimeout)):
                        cmd += str(serverfarm.connFailureThreshCount) + \
                        " reset " + str(serverfarm.resetTimeout) + "\n"
                    if (self.checkNone(serverfarm.resumeService)):
                        cmd += "" + str(serverfarm.connFailureThreshCount) + \
                        " resume-service " + \
                        str(serverfarm.resumeService) + "\n"

            if self.checkNone(serverfarm.dynamicWorkloadScale):
                cmd += "dws " + serverfarm.dynamicWorkloadScale
                if (serverfarm.dynamicWorkloadScale == "burst"):
                    cmd += " probe " + serverfarm.VMprobe
                cmd += "\n"
        return self.send_data(context,  cmd)

    def deleteServerFarm(self,  context,  serverfarm):
        cmd = "no serverfarm " + serverfarm.name + "\n"
        return self.send_data(context,  cmd)

    def addRServerToSF(self,  context,  serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "rserver " + rserver.name
        if self.checkNone(rserver.port):
            cmd += rserver.port
        cmd += "\n"

        if self.checkNone(rserver.weight):
            cmd += "weight " + str(rserver.weight) + "\n"
        if self.checkNone(rserver.backupRS):
            cmd += "backup-rserver " + rserver.backupRS
            if self.checkNone(rserver.backupRSport):
                cmd += " " + rserver.backupRSport
            cmd += "\n"
        if self.checkNone(rserver.maxCon) and self.checkNone(rserver.minCon):
            cmd += "conn-limit max " + str(rserver.maxCon) + \
                " min " + str(rserver.minCon) + "\n"

        if self.checkNone(rserver.rateConnection):
            cmd += "rate-limit connection " + \
                str(rserver.rateConnection) + "\n"
        if self.checkNone(rserver.rateBandwidth):
            cmd += "rate-limit bandwidth " + \
                str(rserver.rateBandwidth) + "\n"

        if self.checkNone(rserver.cookieStr):
            cmd += "cookie-string " + rserver.cookieStr + "\n"

        if self.checkNone(rserver.failOnAll):
            cmd += "fail-on-all\n"
        if self.checkNone(rserver.state):
            cmd += "inservice"
            if rserver.state.lower() == "standby":
                cmd += " standby"
            cmd += "\n"

        return self.send_data(context,  cmd)

    def deleteRServerFromSF(self,  context,  serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "no rserver " + rserver.name
        if self.checkNone(rserver.port):
            cmd += " " + rserver.port
        cmd += "\n"
        return self.send_data(context,  cmd)

    def addProbeToSF(self,  context,  serverfarm,  probe):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "probe " + probe.name + "\n"
        return self.send_data(context,  cmd)

    def deleteProbeFromSF(self,  context,  serverfarm,  probe):
        cmd = "serverfarm " + serverfarm.name + "\n"
        cmd += "no probe " + probe.name + "\n"
        return self.send_data(context,  XMLstr)

    def createStickiness(self,  context, sticky):
        name = sticky.name
        sticky_type = sticky.type.lower() 
        if sticky_type == "httpcontent":
            sticky_type = "http-content"
        if sticky_type == "httpcookie":
            sticky_type = "http-cookie"
        if sticky_type == "httpheader":
            sticky_type = "http-header"
        if sticky_type == "ipnetmask":
            sticky_type = "ip-netmask"
        if sticky_type == "l4payload":
            sticky_type = "layer4-payload"
        if sticky_type == "rtspheader":
            sticky_type = "rtsp-header"
        if sticky_type == "sipheader":
            sticky_type = "sip-header"

        cmd = "sticky " + sticky_type
        if (sticky_type == "http-content"):
            cmd += name + "\n"
            if self.checkNone(sticky.offset):
                cmd += "content offset " + str(sticky.offset) + "\n"
            if self.checkNone(sticky.length):
                cmd += "content length " + str(sticky.length) + "\n"
            if self.checkNone(sticky.beginPattern):
                cmd += "content begin-pattern " + sticky.beginPattern
                if self.checkNone(sticky.endPattern):
                    cmd += " end-pattern " + sticky.endPattern
                cmd += "\n"
        elif sticky_type == "http-cookie":
            cmd += sticky.cookieName + " " + name + "\n"
            if self.checkNone(sticky.enableInsert):
                cmd += "cookie insert"
                if self.checkNone(sticky.BrowserExp):
                    cmd += " browser-expire"
                cmd += "\n"
            if self.checkNone(sticky.offset):
                cmd += "cookie offset " + str(sticky.offset)
                if self.checkNone(sticky.length):
                    cmd += " length " + str(sticky.length)
                cmd += "\n"
            if self.checkNone(sticky.secondaryName):
                cmd += "cookie secondary " + sticky.secondaryName + "\n"
        elif sticky_type == "http-header":
            cmd += sticky.headerName + " " + name + "\n"
            if self.checkNone(sticky.offset):
                cmd += "header offset " + str(sticky.offset)
                if self.checkNone(sticky.length):
                    cmd += " length " + str(sticky.length)
                cmd += "\n"
        elif sticky_type == "ip-netmask":
            cmd += str(sticky.netmask) + " address " + \
                sticky.addrType + " " + name + "\n"
        elif sticky_type == "layer4-payload":
            cmd += name + "\n"
            if self.checkNone(sticky.enableStickyForResponse):
                cmd += "response sticky\n"
            if self.checkNone(sticky.offset) or self.checkNone(sticky.length) \
                or self.checkNone(sticky.beginPattern) or \
                self.checkNone(sticky.endPattern):
                cmd += "layer4-payload"
                if self.checkNone(sticky.offset):
                    cmd += " offset " + str(sticky.offset)
                if self.checkNone(sticky.length):
                    cmd += " length " + str(sticky.length)
                if self.checkNone(sticky.beginPattern):
                    cmd += " begin-pattern " + sticky.beginPattern
                if self.checkNone(sticky.endPattern) and not \
                    self.checkNone(sticky.length):
                    cmd += " end-pattern " + sticky.endPattern
                cmd += "\n"
        elif sticky_type == "radius":
            cmd += name + "\n"
        elif sticky_type == "rtsp-header":
            cmd += " Session " + name + "\n"
            if self.checkNone(sticky.offset):
                cmd += "header offset='" + str(sticky.offset)
                if self.checkNone(sticky.length):
                    cmd += " length='" + str(sticky.length)
            cmd += "\n"
        elif sticky_type == "sip-header":
            cmd += " Call-ID" + name + "\n"

        if self.checkNone(sticky.timeout):
            cmd += "timeout " + str(sticky.timeout) + "\n"
        if self.checkNone(sticky.timeoutActiveConn):
            cmd += "timeout activeconns\n"
        if self.checkNone(sticky.replicateOnHAPeer):
            cmd += "replicate sticky\n"
        if self.checkNone(sticky.serverFarm):
            cmd += "serverfarm " + sticky.serverFarm
            if self.checkNone(sticky.backupServerFarm):
                cmd += " backup " + sticky.backupServerFarm
                if self.checkNone(sticky.enableStyckyOnBackupSF):
                    cmd += " sticky"
                if self.checkNone(sticky.aggregateState):
                    cmd += " aggregate-state"
            cmd += "\n"

        return self.send_data(context, cmd)

    def deleteStickiness(self,  context,   sticky):
        name = sticky.name
        sticky_type = sticky.type.lower()
        if sticky_type == "httpcontent":
            sticky_type = "http-content"
        if sticky_type == "httpcookie":
            sticky_type = "http-cookie"
        if sticky_type == "httpheader":
            sticky_type = "http-header"
        if sticky_type == "ipnetmask":
            sticky_type = "ip-netmask"
        if sticky_type == "l4payload":
            sticky_type = "layer4-payload"
        if sticky_type == "rtspheader":
            sticky_type = "rtsp-header"
        if sticky_type == "sipheader":
            sticky_type = "sip-header"

        cmd = "no sticky " + sticky_type + " " + name + "\n"
        return self.send_data(context,  cmd)
        
    def addACLEntry(self,  context,  vip):
        cmd = "access-list ANY extended permit ip any host " + \
            vip.address + "\n"
        return self.send_data(context,  cmd)
            

    def createVIP(self,  context, vip,  sfarm):
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

        cmd = "policy-map type loadbalance " + vip.appProto + \
            " first-match " + vip.name + "-l7slb\n"
        cmd += "class class-default\n"
        cmd += "serverfarm " + sfarm.name
        if self.checkNone(vip.backupServerFarm):
            cmd += " backup " + vip.backupServerFarm
        cmd += "\nexit\nexit"

        # Add a class-map
        cmd += "class-map match-all " + vip.name + "\n"
        cmd += "match virtual-address " + vip.address + \
            " " + str(vip.mask) + vip.proto.lower()
        if vip.proto.lower() != "any":
            cmd += " eq " + str(vip.port)
        cmd += "\nexit\n"

        #  Add a policy-map (multimatch) with class-map
        cmd += "policy-map multimatch" + pmap + "\n"
        cmd += "class " + vip.name + "\n"

        if self.checkNone(vip.status):
            cmd += "loadbalance vip " + vip.status.lower() + "\n"

        cmd += "loadbalance policy " + vip.name + "-l7slb\n"
        if self.checkNone(vip.ICMPreply):
            cmd += "loadbalance vip icmp-reply\n"

        cmd += "exit\nexit\n"
        s = XmlSender(context)
        tmp = s.deployConfig(context,  cmd)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        if self.checkNone(vip.allVLANs):
            cmd = "service-policy input " + pmap + "\n"
            try:
                tmp = s.deployConfig(context,  cmd)
            except:
                logger.warning("Got exception on acl set")       
        else:
            #  Add service-policy for necessary vlans
            if is_sequence(vip.VLAN):
                for i in vip.VLAN:
                    cmd = "interface vlan " + str(i) + "\n"
                    cmd += "service-policy input " + pmap + "\n"
                    tmp = s.deployConfig(context,  cmd)
                    
                    cmd = "interface vlan " + str(i) + "\n"
                    cmd += "access-group input vip-acl\n"
                    try:
                        # Try to add access list. if it is already
                        # assigned exception will occur
                        tmp = s.deployConfig(context,  cmd)
                    except:
                        logger.warning("Got exception on acl set")                    
                    
            else:
                    cmd = "interface vlan" + str(vip.VLAN) + "\n"
                    cmd += "service-policy input " + pmap + "\n"
                    tmp = s.deployConfig(context,  cmd)
                    cmd = "interface vlan " + str(vip.VLAN) + "\n"
                    cmd += "access-group input vip-acl\n"
                    try:
                        tmp = s.deployConfig(context,  cmd)
                    except:
                       logger.warning("Got exception on acl set")                    
        return 'OK'

    def deleteVIP(self,  context,  vip):
        if self.checkNone(vip.allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + md5.new(vip.VLAN).hexdigest()

        cmd = "policy-map multi-match " + pmap + "\n"
        cmd += " no class " + vip.name + "\n"
        logger.debug("pmap name is %s" % pmap)
        logger.debug("Trying to do %s" % cmd)
        s = XmlSender(context)
        tmp = s.deployConfig(context,  cmd)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        # Delete policy-map, class-map and access-list
        if vip.appProto.lower() == "other" or vip.appProto.lower() == "http":
            vip.appProto = ""
        else:
            vip.appProto = "_" + vip.appProto.lower()
        cmd = "no policy-map type loadbalance " + vip.appProto
        cmd += " first-match " + vip.name + "-l7slb\n"

        cmd += "no class-map match-all " + vip.name + "\n"

        tmp = s.deployConfig(context,  cmd)
        if (tmp != 'OK'):
            raise openstack.common.exception.Invalid(tmp)

        cmd = 'show running-config policy-map %s' % pmap
        last_policy_map = \
            self.checkNone(s.getConfig(context,  cmd).find('class'))

        if (last_policy_map):
            # Remove service-policy from VLANs
            #(Perform if deleted last VIP with it service-policy)
            if self.checkNone(vip.allVLANs):
                cmd = "no service-policy input" + pmap + "\n"
                try:
                    tmp = s.deployConfig(context,  cmd)
                except:
                    logger.warning("Got exception on acl set")  
            else:
                #  Add service-policy for necessary vlans
                if is_sequence(vip.VLAN):
                    for i in vip.VLAN:
                        cmd = "interface vlan " + str(i) + "\n"
                        cmd += "no service-policy input " + pmap + "\n"
                        tmp = s.deployConfig(context,  cmd)

                        cmd = "interface vlan " + str(i) + "\n"
                        cmd += "no access-group input vip-acl\n"
                        tmp = s.deployConfig(context,  cmd)
                else:
                        cmd = "interface vlan " + str(vip.VLAN) + "\n"
                        cmd += "no service-policy input " + pmap + "\n"
                        cmd += "no access-group input vip-acl\n"
                        tmp = s.deployConfig(context,  cmd)
        return "OK"
