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

from balancer.drivers.BaseDriver import (BaseDriver, is_sequence)
from balancer.drivers.cisco_ace.XmlSender import XmlSender
import openstack.common.exception

logger = logging.getLogger(__name__)


class AceDriver(BaseDriver):
    def __init__(self, conf, device_ref):
        super(self, AceDriver).__init__(conf, device_ref)
        self.xmlsender = XmlSender(device_ref)

    def send_data(self, cmd):
        tmp = self.xmlsender.deployConfig(cmd)
        return tmp

    def importCertificatesAndKeys(self):
        dev_extra = self.device_ref['extra']
        cmd = "do crypto import " + dev_extra['protocol']
        if self.checkNone(dev_extra['passphrase']):
            cmd += "passphrase " + dev_extra['passphrase'] + " "
        cmd += dev_extra['server_ip'] + " "
        cmd += dev_extra['server_user'] + " "
        cmd += dev_extra['file_name'] + " "
        cmd += dev_extra['file_name'] + "\n"
        cmd += dev_extra['server_password'] + "\n"

        return self.send_data(cmd)

    def createSSLProxy(self, SSLproxy):
        cmd = "ssl-proxy service " + SSLproxy.name + "\n"
        if self.checkNone(SSLproxy.cert):
            cmd += "cert " + SSLproxy.cert + "\n"
        if self.checkNone(SSLproxy.key):
            cmd += "key " + SSLproxy.key + "\n"

        if self.checkNone(SSLproxy.authGroup):
            cmd += "authgroup " + SSLproxy.authGroup + "\n"
        if self.checkNone(SSLproxy.ocspServer):
            cmd += "ocspserver " + SSLproxy.ocspServer + "\n"
        if self.checkNone(SSLproxy.ocspBestEffort):
            cmd += "oscpserver " + SSLproxy.ocspBestEffort + "\n"
        if self.checkNone(SSLproxy.crl):
            cmd += "crl " + SSLproxy.crl + "\n"
        if self.checkNone(SSLproxy.crlBestEffort):
            cmd += "crl best-effort"
        if self.checkNone(SSLproxy.chainGroup):
            cmd += "chaingroup " + SSLproxy.chainGroup + "\n"
        if self.checkNone(SSLproxy.CheckPriority):
            cmd += "revcheckprion " + SSLproxy.CheckPriority + "\n"

        return self.send_data(cmd)

    def deleteSSLProxy(self, SSLproxy):
        cmd = "no ssl-proxy service " + SSLproxy.name + "\n"

        return self.send_data(cmd)

    def addSSLProxyToVIP(self, vip,  SSLproxy):
        cmd = "policy-map multi-match global\n"
        cmd += "class " + vip['name'] + "\n"
        cmd += "ssl-proxy server " + SSLproxy.name + "\n"

        return self.send_data(cmd)

    def removeSSLProxyFromVIP(self, vip,  SSLproxy):
        cmd = "policy-map multi-match global\n"
        cmd += "class " + vip['name'] + "\n"
        cmd += "no ssl-proxy server " + SSLproxy.name + "\n"

        return self.send_data(cmd)

    def createRServer(self, rserver):
        srv_type = rserver['type'].lower()
        srv_extra = rserver['extra'] or {}

        cmd = "rserver " + srv_type + " " + rserver['name'] + "\n"

        descriptio = srv_extra.get('descriptio')
        if self.checkNone(description):
            cmd += "description " + description + "\n"

        if (srv_type == "host"):
            if self.checkNone(rserver['address']):
                cmd += "ip address " + rserver['address'] + "\n"
            if srv_extra.get('failOnAll'):
                cmd += "fail-on-all\n"
            cmd += "weight " + str(rserver['weight']) + "\n"
        else:
            webHostRedir = srv_extra.get('webHostRedir')
            if self.checkNone(webHostRedir):
                cmd += "webhost-redirection " + webHostRedir
                redirectionCode = srv_extra.get('redirectionCode')
                if self.checkNone(redirectionCode):
                    cmd += " " + redirectionCode
                cmd += "\n"

        maxCon = srv_extra.get('maxCon')
        minCon = srv_extra.get('minCon')
        if (self.checkNone(maxCon) and self.checkNone(minCon)):
            cmd += "conn-limit max " + str(maxCon) + \
                " min " + str(minCon) + "\n"

        rateConnection = srv_extra.get('rateConnection')
        if self.checkNone(rateConnection):
            cmd += "rate-limit connection " + \
                str(rateConnection) + "\n"
        rateBandwidth = srv_extra.get('rateBandwidth')
        if self.checkNone(rateBandwidth):
            cmd += "rate-limit bandwidth " + \
                str(rateBandwidth) + "\n"

        if (rserver['state'] == "In Service"):
            cmd += "inservice\n"

        return self.send_data(cmd)

    def deleteRServer(self, rserver):
        cmd = "no rserver " + rserver['name'] + "\n"
        return self.send_data(cmd)

    def activateRServer(self, serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        cmd += "\n"
        cmd += "inservice\n"
        return self.send_data(cmd)

    def activateRServerGlobal(self, rserver):
        cmd = "rserver " + rserver['name'] + "\n"
        cmd += "inservice\n"
        return self.send_data(cmd)

    def suspendRServer(self, serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        cmd += "\n"
        if (rserver['state'] == "standby"):
            cmd += "inservice standby\n"
        else:
            cmd += "no inservice\n"
        return self.send_data(cmd)

    def suspendRServerGlobal(self, rserver):
        cmd = "rserver " + rserver['name'] + "\n"
        cmd += "no inservice\n"
        return self.send_data(cmd)

    def createProbe(self, probe):
        pr_extra = probe['extra'] or {}
        pr_type = probe['type'].lower()
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
        pr_sd = ['echo udp', 'echo tcp',  'finger',  'tcp',  'udp']
        """ probes_with_timeout """
        pr_tm = ['echo tcp', 'finger',  'tcp',  'rtsp',  'http',
                 'https', 'imap',  'pop',  'sip-tcp',  'smtp',  'telnet']
        """ probes_with_credentials """
        pr_cr = ['http', 'https',  'imap',  'pop', 'radius']
        """ probes_with_regex """
        pr_rg = ['http', 'https',  'sip-tcp',  'sup-udp',  'tcp',  'udp']

        cmd = "probe " + pr_type + " " + probe['name'] + "\n"

        description = pr_extra.get('description')
        if self.checkNone(description):
            cmd += "description " + description + "\n"

        probeInterval = pr_extra.get('probeInterval')
        if self.checkNone(probeInterval):
            cmd += "interval " + str(probeInterval) + "\n"

        if (pr_type != 'vm'):
            passDetectInterval = pr_extra.get('passDetectInterval')
            if self.checkNone(passDetectInterval):
                cmd += "passdetect interval " + \
                    str(passDetectInterval) + "\n"

            passDetectCount = pr_extra.get('passDetectCount')
            if self.checkNone(passDetectCount):
                cmd += "passdetect count " + \
                    str(passDetectCount) + "\n"

            failDetect = pr_extra.get('failDetect')
            if self.checkNone(failDetect):
                cmd += "faildetect " + str(failDetect) + "\n"

            receiveTimeout = pr_extra.get('receiveTimeout')
            if self.checkNone(receiveTimeout):
                cmd += "receive " + str(receiveTimeout) + "\n"

            port = pr_extra.get('port')
            if ((pr_type != 'icmp') and self.checkNone(port)):
                cmd += "port " + str(port) + "\n"

            if (pr_type != 'scripted'):
                destIP = pr_extra.get('destIP')
                if (self.checkNone(destIP)):
                    cmd += "ip address " + destIP
                    isRoute = pr_extra.get('isRoute')
                    if ((pr_type != 'rtsp') and (pr_type != 'sip tcp') and \
                        (pr_type != 'sip udp') and \
                        self.checkNone(isRouted)):
                            cmd += " routed"
                    cmd += "\n"

            if (pr_type == "dns"):
                domainName = pr_extra.get('domainName')
                if self.checkNone(domainName):
                    cmd += "domain " + domainName + "\n"

            if (pr_sd.count(pr_type) > 0):
                sendData = pr_extra.get('sendData')
                if self.checkNone(sendData):
                    cmd += "send-data " + sendData + "\n"

            if (pr_tm.count(pr_type) > 0):
                openTimeout = pr_extra.get('openTimeout')
                if self.checkNone(openTimeout):
                    cmd += "open " + str(openTimeout) + "\n"
                tcpConnTerm = pr_extra.get('tcpConnTerm')
                if self.checkNone(tcpConnTerm):
                    cmd += "connection term forced\n"

            if (pr_cr.count(pr_type) > 0):
                userName = pr_extra.get('userName')
                password = pr_extra.get('password')
                if (self.checkNone(userName) and \
                    self.checkNone(password)):
                    cmd += "credentials " + userName
                    cmd += " " + password
                    if (type == 'radius'):
                        userSecret = pr_extra.get('userSecret')
                        if self.checkNone(userSecret):
                            cmd += " secret " + userSecret
                    cmd += "\n"

            if (pr_rg.count(pr_type) > 0):
                expectRegExp = pr_extra.get('expectRegExp')
                if self.checkNone(expectRegExp):
                    cmd += "expect regex " + expectRegExp
                    expectRegExpOffset = pr_extra.get('expectRegExpOffset')
                    if self.checkNone(expectRegExpOffset):
                        cmd += " offset " + str(expectRegExpOffset)
                    cmd += "\n"

            if ((pr_type == 'http') or (pr_type == 'https')):
                requestMethodType = pr_extra.get('requestMethodType')
                requestHTTPurl = pr_extra.get('requestHTTPurl')
                if self.checkNone(requestMethodType):
                    cmd += "request method " + \
                        requestMethodType.lower() + " url " + \
                        requestHTTPurl.lower() + "\n"

                appendPortHostTag = pr_extra.get('appendPortHostTag')
                if self.checkNone(appendPortHostTag):
                    cmd += "append-port-hosttag\n"

                hash = pr_extra.get('hash')
                if self.checkNone(hash):
                    cmd += "hash "
                    hashString = pr_extra.get(hashString)
                    if self.checkNone(hashString):
                        cmd += hashString
                    cmd += "\n"

                if (pr_type == 'https'):
                    cipher = pr_extra.get('cipher')
                    if self.checkNone(cipher):
                        cmd += "ssl cipher " + cipher + "\n"
                    SSLversion = pr_extra.get('SSLversion')
                    if self.checkNone(SSLversion):
                        cmd += "ssl version " + SSLversion + "\n"

            if ((pr_type == 'pop') or (pr_type == 'imap')):
                requestComman = pr_extra.get('requestComman')
                if self.checkNone(requestCommand):
                    cmd += "request command " + requestCommand + "\n"
                if (pr_type == 'imap'):
                    maibox = pr_extra.get('maibox')
                    if self.checkNone(maibox):
                        cmd += "credentials mailbox " + maibox + "\n"

            if (pr_type == 'radius'):
                NASIPaddr = pr_extra.get('NASIPaddr')
                if self.checkNone(NASIPaddr):
                    cmd += "nas ip address " + NASIPaddr + "\n"

            if (pr_type == 'rtsp'):
                equareHeaderValue = pr_extra.get('equareHeaderValue')
                if self.checkNone(requareHeaderValue):
                    cmd += "header require header-value " + \
                        requareHeaderValue + "\n"

                proxyRequareHeaderValue = pr_extra.get('proxyRequareHeaderValue')
                if self.checkNone(proxyRequareHeaderValue):
                    cmd += "header proxy-require header-value " + \
                        proxyRequareHeaderValue + "\n"

                requestUR = pr_extra.get('requestUR')
                if self.checkNone(requestURL):
                    requestMethodType = pr_extra.get('requestMethodType')
                    requestURL = pr_extra.get('requestURL')
                    if self.checkNone(requestMethodType):
                        cmd += "request method " + str(requestMethodType)
                        cmd += " url " + requestURL + "\n"

            if (pr_type == 'scripted'):
                scriptName = pr_extra.get('scriptName')
                if self.checkNone(scriptName):
                    cmd += "script " + scriptName
                    scriptArgv = pr_extra.get('scriptArgv')
                    if self.checkNone(scriptArgv):
                        cmd += " " + scriptArgv
                    cmd += "\n"

            Rport = pr_extra.get('Rport')
            if ((pr_type == 'sip-udp') and self.checkNone(Rport)):
                cmd += "rport enable\n"

            if (type == 'snmp'):
                SNMPver = pr_extra.get('SNMPver')
                if self.checkNone(SNMPver):
                    cmd += "version " + SNMPver + "\n"
                    SNMPComm = pr_extra.get('SNMPComm')
                    if self.checkNone(SNMPComm):
                        cmd += "community " + SNMPComm + "\n"

        else: # for type == vm
            VMControllerName = pr_extra.get('VMControllerName')
            if self.checkNone(VMControllerName):
                cmd += "vm-controller " + VMControllerName + "\n"
                maxCPUburstThresh = pr_extra.get('maxCPUburstThresh')
                minCPUburstThresh = pr_extra.get('minCPUburstThresh')
                if (self.checkNone(maxCPUburstThresh) and \
                    self.checkNone(minCPUburstThresh)):
                    cmd += "load cpu burst-threshold max " + \
                        maxCPUburstThresh + " min " + \
                        minCPUburstThresh + "\n"
                maxMemBurstThresh = pr_extra.get('maxMemBurstThresh')
                minMemBurstThresh = pr_extra.get('minMemBurstThresh')
                if (self.checkNone(maxMemBurstThresh) and \
                    self.checkNone(minMemBurstThresh)):
                    cmd += "load mem burst-threshold max " + \
                        maxMemBurstThresh + " min " + \
                        minMemBurstThresh + "\n"

        return self.send_data(cmd)

    def deleteProbe(self, probe):
        pr_type = probe['type'].lower()
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
        cmd = "no probe " + pr_type + " " + probe['name'] + "\n"
        return self.send_data(cmd)

    def createServerFarm(self, serverfarm):
        sf_type = serverfarm['type'].lower()
        sf_extra = serverfarm['extra'] or {}
        cmd = "serverfarm " + sf_type + " " + serverfarm['name'] + "\n"

        description = sf_extra.get('description')
        if self.checkNone(description):
            cmd += "description " + description + "\n"

        failAction = sf_extra.get('ailAction')
        if self.checkNone(failAction):
            cmd += "failaction " + failAction + "\n"

        if self.checkNone(serverfarm._predictor['type']):
            pr = serverfarm._predictor['type'].lower()
            if (pr == "leastbandwidth"):
                pr = "least-bandwidth"
                accessTime = serverfarm._predictor['extra'].get('accessTime')
                if self.CheckNone(accessTime):
                    pr += " assess-time " + accessTime
                accessTime = sf_extra.get('accessTime')
                if self.CheckNone(accessTime):
                    sample = serverfarm._predictor['extra']['sample']
                    pr += " samples " + sample
            elif (pr == "leastconnections"):
                pr = "leastconns slowstart " + \
                serverfarm._predictor.['extra']['slowStartDur']
            elif (pr == "leastloaded"):
                pr = "least-loaded probe " + \
                serverfarm._predictor['extra']['snmpProbe']
            cmd += "predictor " + pr + "\n"

        if (sf_type == "host"):
            failOnAll = sf_extra.get('failOnAll')
            if self.checkNone(failOnAll):
                cmd += "fail-on-all\n"

            transparen = sf_extra.get('transparen')
            if self.checkNone(transparent):
                cmd += "transparent\n"

            partialThreshPercentage = sf_extra.get('partialThreshPercentage')
            backInservice = sf_extra.get('backInservice')
            if self.checkNone(partialThreshPercentage) and \
                self.checkNone(backInservice):
                cmd += "partial-threshold " + \
                    str(partialThreshPercentage) + \
                    " back-inservice " + str(backInservice) + "\n"

            inbandHealthCheck = sf_extra.get('inbandHealthCheck')
            if self.checkNone(inbandHealthCheck):
                h_check = inbandHealthCheck.lower()
                cmd += "inband-health check " + h_check + " " + \
                       inbandHealthMonitoringThreshold + "\n"
                resetTimeout = sf_extra.get('resetTimeout')
                if ((h_check == "log") and \
                    self.checkNone(resetTimeout)):
                    cmd += str(serverfarm['connFailureThreshCount']) + \
                        " reset " + str(resetTimeout) + "\n"
                elif (h_check == "remove"):
                    resetTimeout = sf_extra.get('resetTimeout')
                    if (self.checkNone(resetTimeout)):
                        cmd += str(serverfarm['connFailureThreshCount']) + \
                        " reset " + str(resetTimeout) + "\n"
                    resumeService = sf_extra.get('resumeService')
                    if (self.checkNone(resumeService)):
                        cmd += "" + str(serverfarm['connFailureThreshCount']) + \
                        " resume-service " + \
                        str(serverfarm['resumeService']) + "\n"

            dynamicWorkloadScale = sf_extra.get('dynamicWorkloadScale')
            if self.checkNone(dynamicWorkloadScale):
                cmd += "dws " + dynamicWorkloadScale
                if (dynamicWorkloadScale == "burst"):
                    cmd += " probe " + serverfarm['VMprobe']
                cmd += "\n"
        return self.send_data(cmd)

    def deleteServerFarm(self, serverfarm):
        cmd = "no serverfarm " + serverfarm['name'] + "\n"
        return self.send_data(cmd)

    def addRServerToSF(self, serverfarm,  rserver):
        srv_extra = rserver['extra'] or {}

        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        cmd += "\n"

        if self.checkNone(rserver['weight']):
            cmd += "weight " + str(rserver['weight']) + "\n"
        backupRS = srv_extra.get('backupRS')
        if self.checkNone(backupRS):
            cmd += "backup-rserver " + backupRS
            backupRSport = srv_extra.get('backupRSport')
            if self.checkNone(backupRSport):
                cmd += " " + backupRSport
            cmd += "\n"
        maxCon = srv_extra.get('maxCon')
        minCon = srv_extra.get('minCon')
        if self.checkNone(maxCon) and self.checkNone(minCon):
            cmd += "conn-limit max " + str(maxCon) + \
                " min " + str(minCon) + "\n"

        rateConnection = srv_extra.get('rateConnection')
        if self.checkNone(rateConnection):
            cmd += "rate-limit connection " + \
                str(rateConnection) + "\n"
        rateBandwidth = srv_extra.get('rateBandwidth')
        if self.checkNone(rateBandwidth):
            cmd += "rate-limit bandwidth " + \
                str(rateBandwidth) + "\n"

        cookieStr = srv_extra.get('cookieStr')
        if self.checkNone(cookieStr):
            cmd += "cookie-string " + cookieStr + "\n"

        failOnAll = srv_extra.get('failOnAll')
        if self.checkNone(failOnAll):
            cmd += "fail-on-all\n"
        state = rs_extra.get('state')
        if self.checkNone(state):
            cmd += "inservice"
            if state.lower() == "standby":
                cmd += " standby"
            cmd += "\n"

        return self.send_data(cmd)

    def deleteRServerFromSF(self, serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "no rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        cmd += "\n"
        return self.send_data(cmd)

    def addProbeToSF(self, serverfarm,  probe):
        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "probe " + probe['name'] + "\n"
        return self.send_data(cmd)

    def deleteProbeFromSF(self, serverfarm,  probe):
        cmd = "serverfarm " + serverfarm['name'] + "\n"
        cmd += "no probe " + probe['name'] + "\n"
        return self.send_data(XMLstr)

    def createStickiness(self, sticky):
        name = sticky['name']
        sticky_type = sticky['type'].lower()
        st_extra = stciky['extra'] or {}
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

        cmd = "sticky " + sticky_type + " "
        if (sticky_type == "http-content"):
            cmd += name + "\n"
            offset = st_extra.get('offset')
            length = st_extra.get('length')
            beginPattern = st_extra.get('beginPattern')
            if self.checkNone(offset):
                cmd += "content offset " + str(offset) + "\n"
            if self.checkNone(length):
                cmd += "content length " + str(length) + "\n"
            if self.checkNone(beginPattern):
                endPattern = st_extra.get('endPattern')
                cmd += "content begin-pattern " + beginPattern
                if self.checkNone(endPattern):
                    cmd += " end-pattern " + endPattern
                cmd += "\n"
        elif sticky_type == "http-cookie":
            enableInsert = st_extra.get('enableInsert')
            offset = st_extra.get('offset')
            secondaryName = st_extra.get('secondaryName')
            cmd += st_extra['cookieName'] + " " + name + "\n"
            if self.checkNone(enableInsert):
                browserExpire = st_extra.get('browserExpire')
                cmd += "cookie insert"
                if self.checkNone(browserExpire):
                    cmd += " browser-expire"
                cmd += "\n"
            if self.checkNone(offset):
                length = st_extra.get('length')
                cmd += "cookie offset " + str(offset)
                if self.checkNone(length):
                    cmd += " length " + str(length)
                cmd += "\n"
            if self.checkNone(secondaryName):
                cmd += "cookie secondary " + secondaryName + "\n"
        elif sticky_type == "http-header":
            offset = st_extra.get('offset')
            cmd += sticky['headerName'] + " " + name + "\n"
            if self.checkNone(offset):
                length = st_extra.get('length')
                cmd += "header offset " + str(offset)
                if self.checkNone(length):
                    cmd += " length " + str(length)
                cmd += "\n"
        elif sticky_type == "ip-netmask":
            cmd += str(st_extra['netmask']) + " address " + \
                st_extra['addrType'] + " " + name + "\n"
            ipv6PrefixLength = st_extra.get('ipv6PrefixLength')
            if self.checkNone(ipv6PrefixLength):
                cmd += "v6-prefix " + str(ipv6PrefixLength) + "\n"
        elif sticky_type == "v6prefix":
            cmd += str(st_extra['prefixLength]') + " address " + \
                st_extra['addrType'].lower() + " " + name + "\n"
            netmask = st_extra.get('netmask')
            if self.checkNone(netmask):
                cmd += "ip-netmask " + str(netmask) + "\n"
        elif sticky_type == "layer4-payload":
            enableStickyForResponse = st_extra.get('enableStickyForResponse')
            offset = st_extra.get('offset')
            length = st_extra.get('length')
            beginPattern = st_extra.get('beginPattern')
            endPattern = st_extra.get('endPattern')
            cmd += name + "\n"
            if self.checkNone(enableStickyForResponse):
                cmd += "response sticky\n"
            if self.checkNone(offset) or self.checkNone(sticky.length) \
                or self.checkNone(beginPattern) or \
                self.checkNone(endPattern):
                cmd += "layer4-payload"
                if self.checkNone(offset):
                    cmd += " offset " + str(offset)
                if self.checkNone(length):
                    cmd += " length " + str(length)
                if self.checkNone(beginPattern):
                    cmd += " begin-pattern " + beginPattern
                if self.checkNone(endPattern) and not \
                    self.checkNone(length):
                    cmd += " end-pattern " + endPattern
                cmd += "\n"
        elif sticky_type == "radius":
            cmd += "framed-ip " + name + "\n"
        elif sticky_type == "rtsp-header":
            offset = st_extra.get('offset')
            length = st_extra.get('length'
            cmd += " Session " + name + "\n"
            if self.checkNone(offset):
                cmd += "header offset " + str(offset)
                if self.checkNone(length):
                    cmd += " length " + str(length)
            cmd += "\n"
        elif sticky_type == "sip-header":
            cmd += " Call-ID" + name + "\n"

        timeout = st_extra.get('timeout')
        timeoutActiveConn = st_extra.get('timeoutActiveConn')
        replicateOnHAPeer = st_extra.get('replicateOnHAPeer')
        if self.checkNone(timeout):
            cmd += "timeout " + str(timeout) + "\n"
        if self.checkNone(timeoutActiveConn):
            cmd += "timeout activeconns\n"
        if self.checkNone(replicateOnHAPeer):
            cmd += "replicate sticky\n"
        # temparary issue
        if self.checkNone(sticky['sf_id']):
            cmd += "serverfarm " + sticky['sf_id'] + "\n"
        # Please, do not remove it
        #if self.checkNone(sticky.serverFarm):
        #    cmd += "serverfarm " + sticky.serverFarm
        #    if self.checkNone(sticky.backupServerFarm):
        #        cmd += " backup " + sticky.backupServerFarm
        #        if self.checkNone(sticky.enableStyckyOnBackupSF):
        #            cmd += " sticky"
        #        if self.checkNone(sticky.aggregateState):
        #            cmd += " aggregate-state"
        #    cmd += "\n"

        return self.send_data(cmd)

    def deleteStickiness(self, sticky):
        name = sticky['name']
        sticky_type = sticky['type'].lower()
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

        cmd = "no sticky " + sticky_type + " "

        if (sticky_type == "http-content"):
            cmd += name + "\n"
        elif sticky_type == "http-cookie":
            cmd += st_extra['cookieName'] + " " + name + "\n"
        elif sticky_type == "http-header":
            cmd += st_extra['headerName'] + " " + name + "\n"
        elif sticky_type == "ip-netmask":
            cmd += str(st_extra['netmask']) + " address " + \
                st_extra['addrType'] + " " + name + "\n"
        elif sticky_type == "layer4-payload":
            cmd += name + "\n"
        elif sticky_type == "radius":
            cmd += name + "\n"
        elif sticky_type == "rtsp-header":
            cmd += " Session " + name + "\n"
        elif sticky_type == "sip-header":
            cmd += " Call-ID" + name + "\n"

        return self.send_data(cmd)

    def addACLEntry(self, vip):
        cmd = "access-list vip-acl extended permit ip any host " + \
            vip['address'] + "\n"
        return self.send_data(cmd)

    def deleteACLEntry(self, vip):
        cmd = "no access-list vip-acl extended permit ip any host " + \
              vip['address'] + "\n"
        return self.send_data(cmd)

    def createVIP(self, vip, sfarm):
        vip_extra = vip['extra'] or {}

        sn = "2"
        allVLANs = vip_extra.get('allVLANs')
        if self.checkNone(allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())

        # Add a access-list
        self.addACLEntry(vip)

        # Add a policy-map
        appProto = vip_extra['appProto']
        if appProto.lower() in ('other', 'http'):
            appProto = ""
        else:
            appProto = "_" + appProto.lower()

        description = vip_extra['description']

        cmd = "policy-map type loadbalance " + appProto + \
            " first-match " + vip['name'] + "-l7slb\n"
        cmd += "description " + description + "\n"
        cmd += "class class-default\n"
        cmd += "serverfarm " + sfarm['name']
        backupServerFarm = vip_extra.get('backupServerFarm')
        if self.checkNone(backupServerFarm):
            cmd += " backup " + backupServerFarm
        cmd += "\nexit\nexit\n"

        # Add a class-map
        proto = vip_extra['proto']
        cmd += "class-map match-all " + vip['name'] + "\n"
        cmd += "description " + description + "\n"
        cmd += "match virtual-address " + vip['address'] + \
            " " + str(vip['mask']) + " " + proto.lower()
        if proto.lower() != "any":
            cmd += " eq " + str(vip['port'])
        cmd += "\nexit\n"

        # Add a policy-map (multimatch) with class-map
        cmd += "policy-map multi-match " + pmap + "\n"
        cmd += "class " + vip['name'] + "\n"

        if self.checkNone(vip['status']):
            cmd += "loadbalance vip " + vip['status'].lower() + "\n"

        cmd += "loadbalance policy " + vip['name'] + "-l7slb\n"
        ICMPreply = vip_extra.get('ICMPreply')
        if self.checkNone(ICMPreply):
            cmd += "loadbalance vip icmp-reply\n"

        cmd += "exit\nexit\n"
        self.send_data(cmd)

        allVLANs = vip_extra.get('allVLANs')
        if self.checkNone(allVLANs):
            cmd = "service-policy input " + pmap + "\n"
            try:
                tmp = self.xmlsender.deployConfig(cmd)
            except:
                logger.warning("Got exception on acl set")
        else:
            # Add service-policy for necessary vlans
            VLAN = vip_extra['VLAN']
            if is_sequence(VLAN):
                for i in VLAN:
                    cmd = "interface vlan " + str(i) + "\n"
                    cmd += "service-policy input " + pmap + "\n"
                    self.send_data(cmd)

                    cmd = "interface vlan " + str(i) + "\n"
                    cmd += "access-group input vip-acl\n"
                    try:
                        # Try to add access list. if it is already
                        # assigned exception will occur
                        self.send_data(cmd)
                    except:
                        logger.warning("Got exception on acl set")

            else:
                    cmd = "interface vlan " + str(VLAN) + "\n"
                    cmd += "service-policy input " + pmap + "\n"
                    self.send_data(cmd)
                    cmd = "interface vlan " + str(VLAN) + "\n"
                    cmd += "access-group input vip-acl\n"
                    try:
                        self.send_data(cmd)
                    except:
                        logger.warning("Got exception on acl set")
        return 'OK'

    def deleteVIP(self, vip):
        vip_extra = vip['extra'] or {}

        allVLANs = vip_extra.get('allVLANs')
        if self.checkNone(allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())

        cmd = "policy-map multi-match " + pmap + "\n"
        cmd += " no class " + vip['name'] + "\n"
        self.send_data(cmd)

        cmd = "no class-map match-all " + vip['name'] + "\n"
        self.send_data(cmd)

        cmd = "no policy-map type loadbalance " + \
              "first-match " + vip['name'] + "-l7slb\n"

        self.send_data(cmd)

        cmd = "policy-map %s" % pmap
        tmp = self.xmlsender.getConfig(cmd)

        if (tmp.find("class") <= 0):
            if self.checkNone(allVLANs):
                cmd = "no service-policy input " + pmap + "\n"
                self.send_data(cmd)
            else:
                VLAN = vip_extra['VLAN']
                if is_sequence(VLAN):
                    for i in VLAN:
                        cmd = "interface vlan " + str(i) + "\n"
                        cmd += "no service-policy input " + pmap + "\n"
                        self.send_data(cmd)
                else:
                        cmd = "interface vlan " + str(VLAN) + "\n"
                        cmd += "no service-policy input " + pmap + "\n"
                        self.send_data(cmd)
            cmd = "no policy-map multi-match " + pmap + "\n"
            self.send_data(cmd)

        self.deleteACLEntry(vip)

        return "OK"
