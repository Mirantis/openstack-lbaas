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
import urllib2
import base64
import logging
from balancer.drivers.base_driver import BaseDriver, is_sequence
import openstack.common.exception

logger = logging.getLogger(__name__)

def deployConfig(self,  s):
    request = urllib2.Request(self.url)
    request.add_header("Authorization", self.authheader)
    d = """xml_cmd=<request_raw>\nconfigure\n%s\nend\n</request_raw>""" % s
    logger.debug("send data to ACE:\n" + d)
    try:
        message = urllib2.urlopen(request, d)
        s = message.read()
    except (Exception):
        return Exception
    logger.debug("data from ACE:\n" + s)
    if (s.find('XML_CMD_SUCCESS') > 0):
        return 'OK'
    else:
        return Exception

def getConfig(self,  s):
    request = urllib2.Request(self.url)
    request.add_header("Authorization", self.authheader)
    data = """xml_cmd=<request_raw>\nshow runn %s\n</request_raw>""" % s
    logger.debug("send data to ACE:\n" + data)
    try:
        message = urllib2.urlopen(request, data)
        s = message.read()
    except (Exception):
        return Exception
    logger.debug("data from ACE:\n" + s)
    return s

class AceDriver(BaseDriver):
    def __init__(self,  conf,  device_ref):
        super(AceDriver, self).__init__(conf, device_ref)
        self.url = "https://%s:%s/bin/xml_agent" % (device_ref['ip'],
                                                    device_ref['port'])
        base64str = base64.encodestring('%s:%s' % \
            (device_ref['login'], device_ref['password']))[:-1]
        self.authheader = "Basic %s" % base64str

    def importCertificatesAndKeys(self):
        dev_extra = self.device_ref.get('extra') or {}
        cmd = "do crypto import " + dev_extra['protocol'] + " "
        if dev_extra.get('passphrase'):
            cmd += "passphrase " + dev_extra['passphrase'] + " "
        cmd += dev_extra['server_ip'] + " " + dev_extra['server_user'] + \
               " " + dev_extra['file_name'] + " " + dev_extra['file_name'] + \
               "\n" + dev_extra['server_password']
        deployConfig(cmd)

    def createSSLProxy(self,  SSLproxy):
        cmd = "ssl-proxy service " + SSLproxy['name']
        if SSLproxy.get('cert'):
            cmd += "\ncert " + SSLproxy['cert']
        if SSLproxy.get('key'):
            cmd += "\nkey " + SSLproxy['key']
        if SSLproxy.get('authGroup'):
            cmd += "\nauthgroup " + SSLproxy['authGroup']
        if SSLproxy.get('ocspServer'):
            cmd += "\nocspserver " + SSLproxy['ocspServer']
        if SSLproxy.get('ocspBestEffort'):
            cmd += "\noscpserver " + SSLproxy['ocspBestEffort']
        if SSLproxy.get('crl'):
            cmd += "\ncrl " + SSLproxy['crl']
        if SSLproxy.get('crlBestEffort'):
            cmd += "\ncrl best-effort"
        if SSLproxy.get('chainGroup'):
            cmd += "\nchaingroup " + SSLproxy['chainGroup']
        if SSLproxy.get('CheckPriority'):
            cmd += "\nrevcheckprion " + SSLproxy['CheckPriority']
        deployConfig(cmd)

    def deleteSSLProxy(self, SSLproxy):
        cmd = "no ssl-proxy service " + SSLproxy['name']
        deployConfig(cmd)

    def addSSLProxyToVIP(self,  vip,  SSLproxy):
        cmd = "policy-map multi-match global\nclass " + vip['name'] + \
              "\nssl-proxy server " + SSLproxy['name']
        deployConfig(cmd)

    def removeSSLProxyFromVIP(self,  vip,  SSLproxy):
        cmd = "policy-map multi-match global\nclass " + vip['name'] + \
              "\nno ssl-proxy server " + SSLproxy['name']
        deployConfig(cmd)

    def createVLAN(self,  vlan):
        cmd = "int vlan " + vlan['number'] + "\nip address" + vlan['ip'] + \
              " " + vlan['netmask'] + "\nno shutdown"
        deployConfig(cmd)

    def deleteVLAN(self,  vlan):
        cmd = "no int vlan " + vlan['number']
        deployConfig(cmd)

    def createNATpool(self,  NATpool):
        cmd = "int vlan " + NATpool['vlan'] + \
              "\nnat-pool " + NATpool['number'] + " " + NATpool['ip']
        if NATpool.get('ip2'):
            cmd += " " + NATpool['ip2']
        cmd += " " + NATpool['netmask']
        if NATpool.get('pat'):
            cmd += " pat"
        deployConfig(cmd)

    def deleteNATpool(self,  NATpool):
        cmd = "int vlan " + NATpool['vlan'] + \
              "\nno nat-pool " + NATpool['number']
        deployConfig(cmd)

    def addNATpoolToVIP(self,  NATpool,  vip):
        cmd = "policy-map multi-match "
        vip_extra = vip.get('extra') or {}
        if vip_extra.get('allVLANs'):
            cmd += "global"
        else:
            cmd += "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())
        cmd += "\nclass " + vip['name'] + \
               "\nnat dynamic " + NATpool['number'] + \
               " vlan " + NATpool['vlan']
        deployConfig(cmd)

    def deleteNATpoolFromVIP(self,  NATpool,  vip):
        cmd = "policy-map multi-match "
        vip_extra = vip.get('extra') or {}
        if vip_extra.get('allVLANs'):
            cmd += "global"
        else:
            cmd += "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())
        cmd += "\nclass " + vip['name'] + \
               "\nno nat dynamic " + NATpool['number'] + \
               " vlan " + NATpool['vlan']
        deployConfig(cmd)

    def createRServer(self, rserver):
        srv_type = rserver['type'].lower()
        srv_extra = rserver.get('extra') or {}
        cmd = "\nrserver " + srv_type + " " + rserver['name']
        if srv_extra.get('description'):
            cmd += "\ndescription " + srv_extra['description']
        if (srv_type == "host"):
            if self.checkNone(rserver['address']):
                cmd += "\nip address " + rserver['address']
            if srv_extra.get('failOnAll'):
                cmd += "\nfail-on-all"
            cmd += "\nweight " + str(rserver['weight'])
        else:
            if srv_extra.get('webHostRedir'):
                cmd += "\nwebhost-redirection " + srv_extra['webHostRedir']
                if srv_extra.get('redirectionCode'):
                    cmd += " " + str(srv_extra['redirectionCode'])
        if (srv_extra.get('maxCon') and srv_extra.get('minCon')):
            cmd += "\nconn-limit max " + str(srv_extra['maxCon']) + \
                " min " + str(srv_extra['minCon'])
        if srv_extra.get('rateConnection'):
            cmd += "\nrate-limit connection " + \
                   str(srv_extra['rateConnection'])
        if srv_extra.get('rateBandwidth'):
            cmd += "\nrate-limit bandwidth " + str(srv_extra['rateBandwidth'])
        if (rserver['state'] == "In Service"):
            cmd += "\ninservice"
        deployConfig(cmd)

    def deleteRServer(self, rserver):
        cmd = "no rserver " + rserver['name']
        deployConfig(cmd)

    def activateRServer(self, serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm['name'] + "\n" + \
              "rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        cmd += "\ninservice"
        deployConfig(cmd)

    def activateRServerGlobal(self, rserver):
        cmd = "rserver " + rserver['name'] + "\ninservice"
        deployConfig(cmd)

    def suspendRServer(self, serverfarm,  rserver):
        cmd = "serverfarm " + serverfarm['name'] + "\n" + \
              "rserver " + rserver['name']
        if self.checkNone(rserver['port']):
            cmd += " " + rserver['port']
        if (rserver['state'] == "standby"):
            cmd += "\ninservice standby"
        else:
            cmd += "\nno inservice"
        deployConfig(cmd)

    def suspendRServerGlobal(self, rserver):
        cmd = "rserver " + rserver['name'] + "\nno inservice"
        deployConfig(cmd)

    def createProbe(self, probe):
        pr_extra = probe.get('extra') or {}
        pr_type = probe['type'].lower().replace('-', ' ')
        if pr_type == "connect":
            pr_type = "tcp"
        pr_sd = ['echo udp', 'echo tcp',  'finger',  'tcp',  'udp']
        pr_tm = ['echo tcp', 'finger',  'tcp',  'rtsp',  'http',
                 'https', 'imap',  'pop',  'sip-tcp',  'smtp',  'telnet']
        pr_cr = ['http', 'https',  'imap',  'pop', 'radius']
        pr_rg = ['http', 'https',  'sip-tcp',  'sup-udp',  'tcp',  'udp']
        cmd = "\nprobe " + pr_type + " " + probe['name']
        if pr_extra.get('description'):
            cmd += "\ndescription " + pr_extra['description']
        if pr_extra.get('probeInterval'):
            cmd += "\ninterval " + str(pr_extra['probeInterval'])
        if (pr_type != 'vm'):
            if pr_extra.get('passDetectInterval'):
                cmd += "\npassdetect interval " + \
                       str(pr_extra['passDetectInterval'])
            if pr_extra.get('passDetectCount'):
                cmd += "\npassdetect count " + str(pr_extra['passDetectCount'])
            if pr_extra.get('failDetect'):
                cmd += "\nfaildetect " + str(pr_extra['failDetect'])
            if pr_extra.get('receiveTimeout'):
                cmd += "\nreceive " + str(pr_extra['receiveTimeout'])
            if ((pr_type != 'icmp') and pr_extra.get('port')):
                cmd += "\nport " + str(pr_extra['port'])
            if (pr_type != 'scripted'):
                if pr_extra.get('destIP'):
                    cmd += "\nip address " + pr_extra['destIP']
                    if ((pr_type != 'rtsp') and (pr_type != 'sip tcp') and \
                        (pr_type != 'sip udp') and pr_extra.get('isRoute')):
                            cmd += " routed"
            if (pr_type == "dns"):
                if pr_extra.get('domainName'):
                    cmd += "\ndomain " + pr_extra['domainName']
            if (pr_sd.count(pr_type) > 0):
                if pr_extra.get('sendData'):
                    cmd += "\nsend-data " + pr_extra['sendData']
            if (pr_tm.count(pr_type) > 0):
                if pr_extra.get('openTimeout'):
                    cmd += "\nopen " + str(pr_extra['openTimeout'])
                if pr_extra.get('tcpConnTerm'):
                    cmd += "\nconnection term forced"
            if (pr_cr.count(pr_type) > 0):
                if (pr_extra.get('userName') and pr_extra.get('password')):
                    cmd += "\ncredentials " + pr_extra['userName'] + \
                           " " + pr_extra['password']
                    if (pr_type == 'radius'):
                        if pr_extra.get('userSecret'):
                            cmd += " secret " + pr_extra['userSecret']
            if (pr_rg.count(pr_type) > 0):
                if pr_extra.get('expectRegExp'):
                    cmd += "\nexpect regex " + pr_extra['expectRegExp']
                    if pr_extra.get('expectRegExpOffset'):
                        cmd += " offset " + str(pr_extra['expectRegExpOffset'])
            if ((pr_type == 'http') or (pr_type == 'https')):
                if pr_extra.get('requestMethodType'):
                    cmd += "\nrequest method " + \
                        pr_extra['requestMethodType'].lower() + \
                        " url " + pr_extra['requestHTTPurl'].lower()
                if pr_extra.get('appendPortHostTag'):
                    cmd += "\nappend-port-hosttag"
                if pr_extra.get('hash'):
                    cmd += "\nhash "
                    if pr_extra.get('hashString'):
                        cmd += pr_extra['hashString']
                if (pr_type == 'https'):
                    if pr_extra.get('cipher'):
                        cmd += "\nssl cipher " + pr_extra['cipher']
                    if pr_extra.get('SSLversion'):
                        cmd += "\nssl version " + pr_extra['SSLversion']
            if ((pr_type == 'pop') or (pr_type == 'imap')):
                if pr_extra.get('requestComman'):
                    cmd += "\nrequest command " + pr_extra['requestComman']
                if (pr_type == 'imap'):
                    if pr_extra.get('mailbox'):
                        cmd += "\ncredentials mailbox " + pr_extra['mailbox']
            if (pr_type == 'radius'):
                if pr_extra.get('NASIPaddr'):
                    cmd += "\nnas ip address " + pr_extra['NASIPaddr']
            if (pr_type == 'rtsp'):
                if pr_extra.get('equareHeaderValue'):
                    cmd += "\nheader require header-value " + \
                        pr_extra['equareHeaderValue']
                if pr_extra.get('proxyRequareHeaderValue'):
                    cmd += "\nheader proxy-require header-value " + \
                        pr_extra['proxyRequareHeaderValue']
                if pr_extra.get('requestURL'):
                    if pr_extra.get('requestMethodType'):
                        cmd += "\nrequest method " + \
                            str(pr_extra['requestMethodType']) + \
                            " url " + pr_extra['requestURL']
            if (pr_type == 'scripted'):
                if pr_extra.get('scriptName'):
                    cmd += "\nscript " + pr_extra['scriptName']
                    if pr_extra.get('scriptArgv'):
                        cmd += " " + pr_extra['scriptArgv']
            if ((pr_type == 'sip-udp') and pr_extra.get('Rport')):
                cmd += "\nrport enable"
            if (type == 'snmp'):
                if pr_extra.get('SNMPver'):
                    cmd += "\nversion " + pr_extra['SNMPver']
                    if pr_extra.get('SNMPComm'):
                        cmd += "\ncommunity " + pr_extra['SNMPComm']
        else:  # for type == vm
            if pr_extra.get('VMControllerName'):
                cmd += "vm-controller " + pr_extra['VMControllerName']
                if (pr_extra.get('maxCPUburstThresh') and \
                    pr_extra.get('minCPUburstThresh')):
                    cmd += "\nload cpu burst-threshold max " + \
                        pr_extra['maxCPUburstThresh'] + " min " + \
                        pr_extra['minCPUburstThresh']
                if (pr_extra.get('maxMemBurstThresh') and \
                    pr_extra.get('minMemBurstThresh')):
                    cmd += "\nload mem burst-threshold max " + \
                        pr_extra['maxMemBurstThresh'] + " min " + \
                        pr_extra['minMemBurstThresh']
        deployConfig(cmd)

    def deleteProbe(self, probe):
        pr_type = probe['type'].lower().replace('-', ' ')
        if pr_type == "connect":
            pr_type = "tcp"
        cmd = "no probe " + pr_type + " " + probe['name']
        deployConfig(cmd)

    def createServerFarm(self, sf):
        sf_type = sf['type'].lower()
        sf_extra = sf.get('extra') or {}
        cmd = "serverfarm " + sf_type + " " + sf['name']
        if sf_extra.get('description'):
            cmd += "\ndescription " + sf_extra['description']
        if sf_extra.get('failAction'):
            cmd += "\nfailaction " + sf_extra['failAction']
        if sf._predictor.get('type'):
            pr = sf._predictor['type'].lower()
            if (pr == "leastbandwidth"):
                pr = "least-bandwidth"
                accessTime = sf._predictor['extra'].get('accessTime')
                if accessTime:
                    pr += " assess-time " + accessTime
                if sf_extra.get('accessTime'):
                    pr += " samples " + sf._predictor['extra']['sample']
            elif (pr == "leastconnections"):
                pr = "leastconns slowstart " + \
                     sf._predictor['extra']['slowStartDur']
            elif (pr == "leastloaded"):
                pr = "least-loaded probe " + \
                     sf._predictor['extra']['snmpProbe']
            cmd += "\npredictor " + pr
        if (sf_type == "host"):
            if sf_extra.get('failOnAll'):
                cmd += "\nfail-on-all"
            if sf_extra.get('transparen'):
                cmd += "\ntransparent"
            if sf_extra.get('partialThreshPercentage') and \
               sf_extra.get('backInservice'):
                cmd += "\npartial-threshold " + \
                    str(sf_extra['partialThreshPercentage']) + " back-" + \
                    "inservice " + str(sf_extra['backInservice'])
            if sf_extra.get('inbandHealthCheck'):
                h_check = sf_extra['inbandHealthCheck'].lower()
                cmd += "\ninband-health check " + h_check + " " + \
                       sf_extra['inbandHealthMonitoringThreshold']
                if sf_extra.get('resetTimeout'):
                    cmd += " " + str(sf['connFailureThreshCount']) + \
                        " reset " + str(sf_extra['resetTimeout'])
                if (h_check == "remove" and sf_extra.get('resumeService')):
                    cmd += " " + str(sf['connFailureThreshCount']) + \
                        " resume-service " + str(sf_extra['resumeService'])
            if sf_extra.get('dynamicWorkloadScale'):
                cmd += "\ndws " + sf_extra['dynamicWorkloadScale']
                if (sf_extra['dynamicWorkloadScale'] == "burst"):
                    cmd += " probe " + sf['VMprobe']
        deployConfig(cmd)

    def deleteServerFarm(self, sf):
        cmd = "no serverfarm " + sf['name']
        self.deployConfig(cmd)

    def addRServerToSF(self, sf,  rserver):
        srv_extra = rserver.get('extra') or {}
        cmd = "serverfarm " + sf['name'] + "\nrserver " + rserver['name']
        if rserver.get('port'):
            cmd += " " + rserver['port']
        if rserver.get('weight'):
            cmd += "\nweight " + str(rserver['weight'])
        if srv_extra.get('backupRS'):
            cmd += "\nbackup-rserver " + srv_extra['backupRS']
            if srv_extra.get('backupRSport'):
                cmd += " " + str(srv_extra['backupRSport'])
        if srv_extra.get('maxCon') and srv_extra.get('minCon'):
            cmd += "\nconn-limit max " + str(srv_extra['maxCon']) + \
                   " min " + str(srv_extra['minCon'])
        if srv_extra.get('rateConnection'):
            cmd += "\nrate-limit connection " + \
                   str(srv_extra['rateConnection'])
        if srv_extra.get('rateBandwidth'):
            cmd += "\nrate-limit bandwidth " + str(srv_extra['rateBandwidth'])
        if srv_extra.get('cookieStr'):
            cmd += "\ncookie-string " + srv_extra['cookieStr']
        if srv_extra.get('failOnAll'):
            cmd += "\nfail-on-all"
        if rs_extra.get('state'):
            cmd += "\ninservice"
            if rs_extra.get('state').lower() == "standby":
                cmd += " standby"
        deployConfig(cmd)

    def deleteRServerFromSF(self, sf,  rserver):
        cmd = "serverfarm " + sf['name'] + "\nno rserver " + rserver['name']
        if rserver.get('port'):
            cmd += " " + rserver['port']
        deployConfig(cmd)

    def addProbeToSF(self, sf,  probe):
        cmd = "serverfarm " + sf['name'] + "\nprobe " + probe['name']
        deployConfig(cmd)

    def deleteProbeFromSF(self, sf,  probe):
        cmd = "serverfarm " + sf['name'] + "\nno probe " + probe['name']
        deployConfig(cmd)

    def createStickiness(self, sticky):
        name = sticky['name']
        sticky_type = sticky['type'].lower().replace('httpc', 'http-c')
        sticky_type = sticky_type.replace('header', '-header')
        sticky_type = sticky_type.replace('l4', 'layer4-')
        st_extra = sticky.get('extra') or {}
        cmd = "sticky " + sticky_type + " "
        if (sticky_type == "http-content"):
            cmd += name + "\n"
            if st_extra.get('offset'):
                cmd += "content offset " + str(st_extra['offset']) + "\n"
            if st_extra.get('length'):
                cmd += "content length " + str(st_extra['length']) + "\n"
            if st_extra.get('beginPattern'):
                cmd += "content begin-pattern " + st_extra['beginPattern']
                if st_extra.get('endPattern'):
                    cmd += " end-pattern " + st_extra['endPattern']
        elif sticky_type == "http-cookie":
            cmd += st_extra['cookieName'] + " " + name
            if st_extra.get('enableInsert'):
                cmd += "\ncookie insert"
                if st_extra.get('browserExpire'):
                    cmd += " browser-expire"
            if st_extra.get('offset'):
                cmd += "\ncookie offset " + str(st_extra['offset'])
                if st_extra.get('length'):
                    cmd += " length " + str(st_extra['length'])
            if st_extra.get('secondaryName'):
                cmd += "\ncookie secondary " + st_extra['secondaryName']
        elif sticky_type == "http-header":
            cmd += sticky['headerName'] + " " + name
            if st_extra.get('offset'):
                cmd += "\nheader offset " + str(st_extra['offset'])
                if st_extra.get('length'):
                    cmd += " length " + str(st_extra['length'])
        elif sticky_type == "ip-netmask":
            cmd += str(st_extra['netmask']) + " address " + \
                st_extra['addrType'] + " " + name
            if st_extra.get('ipv6PrefixLength'):
                cmd += "\nv6-prefix " + str(st_extra['ipv6PrefixLength'])
        elif sticky_type == "v6prefix":
            cmd += str(st_extra['prefixLength']) + " address " + \
                st_extra['addrType'].lower() + " " + name
            if st_extra.get('netmask'):
                cmd += "\nip-netmask " + str(st_extra['netmask'])
        elif sticky_type == "layer4-payload":
            cmd += name + "\n"
            if st_extra.get('enableStickyForResponse'):
                cmd += "response sticky"
            if st_extra.get('offset') or st_extra.get('length') \
                or st_extra.get('endPattern') or st_extra.get('beginPattern'):
                cmd += "\nlayer4-payload"
                if st_extra.get('offset'):
                    cmd += " offset " + str(st_extra['offset'])
                if st_extra.get('length'):
                    cmd += " length " + str(st_extra['length'])
                if st_extra.get('beginPattern'):
                    cmd += " begin-pattern " + st_extra['beginPattern']
                if st_extra.get('endPattern') and not st_extra.get('length'):
                    cmd += " end-pattern " + st_extra['endPattern']
        elif sticky_type == "radius":
            cmd += "framed-ip " + name
        elif sticky_type == "rtsp-header":
            cmd += " Session " + name
            if st_extra.get('offset'):
                cmd += "\nheader offset " + str(st_extra['offset'])
                if st_extra.get('length'):
                    cmd += " length " + str(st_extra['length'])
        elif sticky_type == "sip-header":
            cmd += " Call-ID" + name
        if st_extra.get('timeout'):
            cmd += "\ntimeout " + str(st_extra['timeout']) + ""
        if st_extra.get('timeoutActiveConn'):
            cmd += "\ntimeout activeconns"
        if st_extra.get('replicateOnHAPeer'):
            cmd += "\nreplicate sticky"
        # temparary issue
        if st_extra.get('sf_id'):
            cmd += "\nserverfarm " + sticky['sf_id']
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
        deployConfig(cmd)

    def deleteStickiness(self, sticky):
        name = sticky['name']
        sticky_type = sticky['type'].lower().replace('httpc', 'http-c')
        sticky_type = sticky_type.replace('header', '-header')
        sticky_type = sticky_type.replace('l4', 'layer4-')
        cmd = "no sticky " + sticky_type + " "
        if sticky_type in ("http-content", "layer4-payload", "radius"):
            cmd += name
        elif sticky_type == "http-cookie":
            cmd += st_extra['cookieName'] + " " + name
        elif sticky_type == "http-header":
            cmd += st_extra['headerName'] + " " + name
        elif sticky_type == "ip-netmask":
            cmd += str(st_extra['netmask']) + " address " + \
                st_extra['addrType'] + " " + name
        elif sticky_type == "rtsp-header":
            cmd += " Session " + name
        elif sticky_type == "sip-header":
            cmd += " Call-ID" + name
        deployConfig(cmd)

    def createVIP(self, vip, sfarm):
        vip_extra = vip.get('extra') or {}
        allVLANs = vip_extra.get('allVLANs')
        if self.checkNone(allVLANs):
            pmap = "global"
        else:
            pmap = "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())
        cmd = "access-list vip-acl extended permit ip any host " + \
              vip['address']
        deployConfig(cmd)
        appProto = vip_extra.get('appProto')
        if appProto.lower() in ('other', 'http'):
            appProto = ""
        else:
            appProto = "_" + appProto.lower()
        cmd = "policy-map type loadbalance " + appProto + \
            " first-match " + vip['name'] + "-l7slb\n" + \
            "description " + vip_extra['description'] + "\n" + \
            "class class-default\nserverfarm " + sfarm['name']
        if vip_extra.get('backupServerFarm'):
            cmd += " backup " + vip_extra['backupServerFarm']
        cmd += "\nexit\nexit\nclass-map match-all " + vip['name'] + "\n" + \
               "description " + vip_extra['description'] + "\n" + \
               "match virtual-address " + vip['address'] + \
               " " + str(vip['mask']) + " " + vip_extra['proto'].lower()
        if vip_extra['proto'].lower() != "any":
            cmd += " eq " + str(vip['port'])
        cmd += "\nexit\npolicy-map multi-match " + pmap + "\nclass " + \
               vip['name']
        if vip.get('status'):
            cmd += "\nloadbalance vip " + vip['status'].lower()
        cmd += "\nloadbalance policy " + vip['name'] + "-l7slb"
        if vip_extra.get('ICMPreply'):
            cmd += "\nloadbalance vip icmp-reply"
        deployConfig(cmd)
        if vip_extra.get('allVLANs'):
            cmd = "service-policy input " + pmap
            try:
                deployConfig(cmd)
            except:
                logger.warning("Got exception on acl set")
        else:
            VLAN = vip_extra['VLAN']
            if is_sequence(VLAN):
                for i in VLAN:
                    cmd = "interface vlan " + str(i) + \
                          "\nservice-policy input " + pmap
                    deployConfig(cmd)
                    cmd = "interface vlan " + str(i) + \
                          "\naccess-group input vip-acl"
                    try:
                        deployConfig(cmd)
                    except:
                        logger.warning("Got exception on acl set")
            else:
                    cmd = "interface vlan " + str(VLAN) + \
                          "\nservice-policy input " + pmap
                    deployConfig(cmd)
                    cmd = "interface vlan " + str(VLAN) + \
                          "\naccess-group input vip-acl"
                    try:
                        deployConfig(cmd)
                    except:
                        logger.warning("Got exception on acl set")

    def deleteVIP(self, vip):
        vip_extra = vip['extra'] or {}
        if vip_extra.get('allVLANs'):
            pmap = "global"
        else:
            pmap = "int-" + str(md5.new(vip_extra['VLAN']).hexdigest())
        cmd = "policy-map multi-match " + pmap + "\nno class " + vip['name']
        deployConfig(cmd)
        cmd = "no class-map match-all " + vip['name'] + "\n"
        deployConfig(cmd)
        cmd = "no policy-map type loadbalance first-match " + \
              vip['name'] + "-l7slb"
        deployConfig(cmd)
        if (getConfig("policy-map %s" % pmap).find("class") <= 0):
            if vip_extra.get('allVLANs'):
                cmd = "no service-policy input " + pmap
                deployConfig(cmd)
            else:
                VLAN = vip_extra['VLAN']
                if is_sequence(VLAN):
                    for i in VLAN:
                        cmd = "interface vlan " + str(i) + \
                              "\nno service-policy input " + pmap
                        deployConfig(cmd)
                else:
                        cmd = "interface vlan " + str(VLAN) + \
                              "\nno service-policy input " + pmap
                        deployConfig(cmd)
            cmd = "no policy-map multi-match " + pmap
            deployConfig(cmd)
        cmd = "no access-list vip-acl extended permit ip any host " + \
              vip['address']
        deployConfig(cmd)
