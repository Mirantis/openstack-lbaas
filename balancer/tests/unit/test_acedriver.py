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
import unittest

from balancer.drivers.cisco_ace.ace_5x_driver import AceDriver
from balancer.drivers.cisco_ace.XmlSender import XmlSender
from balancer.loadbalancers.realserver import RealServer
from balancer.loadbalancers.serverfarm import ServerFarm
from balancer.loadbalancers.probe import *
from balancer.loadbalancers.sticky import *
from balancer.loadbalancers.virtualserver import VirtualServer

test_context = Context('10.4.15.21', '10443', 'admin', 'cisco123')
driver = AceDriver()

rs_host = RealServer()
rs_host.type = "Host"
rs_host.name = 'LB_test_rs01'
rs_host.address = '172.250.0.1'
rs_host.state = "inservice"
rs_host.description = "Created by test. RS type Host"
rs_host.minCon = 2000000
rs_host.maxCon = 3000000
rs_host.weight = 7
rs_host.rateBandwidth = 500000
rs_host.rateConnection = 5000
rs_host.failOnAll = True
#Next var for AddRStoSFarm
rs_host.port = "80"
rs_host.backupRS = ""
rs_host.backupRSport = ""
#rs_host.cookieStr = "stringcookie"
#rs_host.probes = ["icmp"]

rs_redirect = RealServer()
rs_redirect.type = "Redirect"
rs_redirect.name = 'LB_test_rs02'
rs_redirect.address = '172.250.0.2'
rs_redirect.state = "outofservice"
rs_redirect.description = "Created by test. RS type Redirect"
rs_redirect.minCon = 2000000
rs_redirect.maxCon = 3000000
rs_redirect.weight = 1
rs_redirect.rateBandwidth = 100000
rs_redirect.rateConnection = 999
rs_redirect.webHostRedir = "www.cisco.com"
rs_redirect.redirectionCode = 301

probe_dns = DNSprobe()
probe_dns.type = "DNS"
probe_dns.name = "LB_test_ProbeDNS"
probe_dns.description = "Created by test. Probe type DNS"
probe_dns.probeInterval = 2
probe_dns.passDetectInterval = 2
probe_dns.failDetect = 1
probe_dns.domainName = "test-org"
#more settings fields
probe_dns.passDetectCount = 1
probe_dns.receiveTimeout = 1
probe_dns.destIP = "1.1.1.1"
probe_dns.isRouted = None
probe_dns.port = 1

probe_echoUDP = ECHOUDPprobe()
probe_echoUDP.type = "ECHO-UDP"
probe_echoUDP.name = "LB_test_ProbeECHOUDP"
probe_echoUDP.description = "Created by test. Probe type ECHOUDP"
probe_echoUDP.probeInterval = 65535
probe_echoUDP.passDetectInterval = 65535
probe_echoUDP.failDetect = 65535
probe_echoUDP.sendData = "SendingData"
#more settings fields
probe_echoUDP.passDetectCount = 65535
probe_echoUDP.receiveTimeout = 65535
probe_echoUDP.destIP = "1.1.1.1"
probe_echoUDP.isRouted = True
probe_echoUDP.port = 65535

probe_echoTCP = ECHOTCPprobe()
probe_echoTCP.type = "ECHO-TCP"
probe_echoTCP.name = "LB_test_ProbeECHOTCP"
probe_echoTCP.description = "Created by test. Probe type ECHOTCP"
probe_echoTCP.probeInterval = 15
probe_echoTCP.passDetectInterval = 60
probe_echoTCP.failDetect = 3
probe_echoTCP.sendData = "SendingData"
#more settings fields
probe_echoTCP.passDetectCount = 3
probe_echoTCP.receiveTimeout = 10
probe_echoTCP.destIP = "1.1.1.1"
probe_echoTCP.isRouted = True
probe_echoTCP.port = "500"
probe_echoTCP.tcpConnTerm= True
probe_echoTCP.openTimeout = 10

probe_finger = FINGERprobe()
probe_finger.type = "FINGER"
probe_finger.name = "LB_test_ProbeFinger"
probe_finger.description = "Created by test. Probe type Finger"
probe_finger.probeInterval = 20
probe_finger.passDetectInterval = 50
probe_finger.failDetect = 5
probe_finger.sendData = "SendingData"
#more settings fields
probe_finger.passDetectCount = 3
probe_finger.receiveTimeout = 10
probe_finger.destIP = "1.1.1.1"
probe_finger.isRouted = True
probe_finger.port = "501"
probe_finger.tcpConnTerm= None
probe_finger.openTimeout = 1

probe_ftp = FTPprobe()
probe_ftp.type = "FTP"
probe_ftp.name = "LB_test_ProbeFTP"
probe_ftp.description = "Created by test. Probe type FTP"
probe_ftp.probeInterval = 20
probe_ftp.passDetectInterval = 50
probe_ftp.failDetect = 5
#more settings fields
probe_ftp.passDetectCount = 5
probe_ftp.receiveTimeout = 15
probe_ftp.destIP = "1.1.1.1"
probe_ftp.isRouted = True
probe_ftp.port = "502"
probe_ftp.tcpConnTerm= True
probe_ftp.openTimeout = 65535

probe_http = HTTPprobe()
probe_http.type = "HTTP"
probe_http.name = "LB_test_ProbeHTTP"
probe_http.description = "Created by test. Probe type HTTP"
probe_http.probeInterval = 20
probe_http.passDetectInterval = 50
probe_http.failDetect = 5
probe_http.port = "80"
probe_http.requestMethodType = "GET"
probe_http.requestHTTPurl = "cisco.com"
#more settings fields
probe_http.passDetectCount = 5
probe_http.receiveTimeout = 15
probe_http.destIP = "1.1.1.1"
probe_http.isRouted = True
probe_http.tcpConnTerm = True
probe_http.appendPortHostTag = True
probe_http.openTimeout = 2
probe_http.userName = "user"
probe_http.password = "password"
probe_http.expectRegExp = ".*"
probe_http.expectRegExpOffset = 1
probe_http.hash = True
probe_http.hashString = "01020304010203040102030401020304"

probe_https = HTTPSprobe()
probe_https.type = "HTTPS"
probe_https.name = "LB_test_ProbeHTTPS"
probe_https.description = "Created by test. Probe type HTTPS"
probe_https.probeInterval = 20
probe_https.passDetectInterval = 50
probe_https.failDetect = 5
probe_https.port = "8080"
probe_https.requestMethodType = "HEAD"
probe_https.requestHTTPurl = "cisco.com"
probe_https.cipher = None
probe_https.SSLversion = "ALL"
#more settings fields
probe_https.passDetectCount = 5
probe_https.receiveTimeout = 15
probe_https.destIP = "1.1.1.1"
probe_https.isRouted = True
probe_https.tcpConnTerm = True
probe_https.appendPortHostTag = True
probe_https.openTimeout = 2
probe_https.userName = "user"
probe_https.password = "password"
probe_https.expectRegExp = ".*"
probe_https.expectRegExpOffset = 1
probe_https.hash = True
probe_https.hashString = "01020304010203040102030401020304"

probe_icmp = ICMPprobe()
probe_icmp.type = "ICMP"
probe_icmp.name = "LB_test_ProbeICMP"
probe_icmp.description = "Created by test. Probe type ICMP"
probe_icmp.probeInterval = 2
probe_icmp.passDetectInterval = 2
probe_icmp.failDetect = 1
#more settings fields
probe_icmp.passDetectCount = 1
probe_icmp.receiveTimeout = 1
probe_icmp.destIP = "1.1.1.1"
probe_icmp.isRouted = None

probe_imap = IMAPprobe()
probe_imap.type = "IMAP"
probe_imap.name = "LB_test_ProbeIMAP"
probe_imap.description = "Created by test. Probe type IMAP"
probe_imap.probeInterval = 20
probe_imap.passDetectInterval = 50
probe_imap.failDetect = 5
probe_imap.userName = "user"
probe_imap.password = "password"
probe_imap.maibox = "dhl.org"
probe_imap.requestCommand = "request"
#more settings fields
probe_imap.passDetectCount = 5
probe_imap.receiveTimeout = 15
probe_imap.destIP = "1.1.1.1"
probe_imap.isRouted = True
probe_imap.port = "503"
probe_imap.tcpConnTerm = True
probe_imap.openTimeout = 60

probe_pop = POPprobe()
probe_pop.type = "POP"
probe_pop.name = "LB_test_ProbePOP"
probe_pop.description = "Created by test. Probe type POP"
probe_pop.probeInterval = 20
probe_pop.passDetectInterval = 50
probe_pop.failDetect = 5
probe_pop.userName = "user"
probe_pop.password = "password"
probe_pop.requestCommand = "request"
#more settings fields
probe_pop.passDetectCount = 5
probe_pop.receiveTimeout = 15
probe_pop.destIP = "1.1.1.1"
probe_pop.isRouted = True
probe_pop.port = "504"
probe_pop.tcpConnTerm = True
probe_pop.openTimeout = 60

probe_radius = RADIUSprobe()
probe_radius.type = "RADIUS"
probe_radius.name = "LB_test_ProbeRADIUS"
probe_radius.description = "Created by test. Probe type Radius"
probe_radius.probeInterval = 30
probe_radius.passDetectInterval = 100
probe_radius.failDetect = 5
probe_radius.userSecret = "topsecret"
probe_radius.userName = "user"
probe_radius.password = "password"
probe_radius.requestCommand = "request"
#more settings fields
probe_radius.passDetectCount = 5
probe_radius.receiveTimeout = 15
probe_radius.destIP = "1.1.1.1"
probe_radius.isRouted = True
probe_radius.port = "505"
probe_radius.NASIPaddr = "2.2.2.2"

probe_rtsp = RTSPprobe()
probe_rtsp.type = "RTSP"
probe_rtsp.name = "LB_test_ProbeRTSP"
probe_rtsp.description = "Created by test. Probe type RTSP"
probe_rtsp.probeInterval = 30
probe_rtsp.passDetectInterval = 100
probe_rtsp.failDetect = 5
probe_rtsp.requareHeaderValue = "headervalue"
probe_rtsp.proxyRequareHeaderValue = "requarevalue"
probe_rtsp.requestMethodType = True
probe_rtsp.requestURL = "cisco.com"
#more settings fields
probe_rtsp.passDetectCount = 5
probe_rtsp.receiveTimeout = 15
probe_rtsp.destIP = "1.1.1.1"
probe_rtsp.port = "506"
probe_rtsp.tcpConnTerm = True
probe_rtsp.openTimeout = 60

probe_scripted = SCRIPTEDprobe()
probe_scripted.type = "SCRIPTED"
probe_scripted.name = "LB_test_ProbeSCRIPTED"
probe_scripted.description = "Created by test. Probe type SCRIPTED"
probe_scripted.probeInterval = 30
probe_scripted.passDetectInterval = 100
probe_scripted.failDetect = 5
probe_scripted.port = "507"
probe_scripted.scriptName = "script.py"
probe_scripted.scriptArgv = "a1"
#more settings fields
probe_scripted.passDetectCount = 5
probe_scripted.receiveTimeout = 15
probe_scripted.copied = True
probe_scripted.proto = "FTP"
probe_scripted.userName = "user"
probe_scripted.password = "password"
probe_scripted.sourceFileName = "root/script.py"

probe_sipUDP = SIPUDPprobe()
probe_sipUDP.type = "SIP-UDP"
probe_sipUDP.name = "LB_test_ProbeSIPUDP"
probe_sipUDP.description = "Created by test. Probe type SIPUDP"
probe_sipUDP.probeInterval = 30
probe_sipUDP.passDetectInterval = 100
probe_sipUDP.failDetect = 5
#more settings fields
probe_sipUDP.passDetectCount = 5
probe_sipUDP.receiveTimeout = 15
probe_sipUDP.destIP = "1.1.1.1"
probe_sipUDP.port = "508"
probe_sipUDP.rport = True
probe_sipUDP.expectRegExp = ".*"
probe_sipUDP.expectRegExpOffset = 4000

probe_sipTCP = SIPTCPprobe()
probe_sipTCP.type = "SIP-TCP"
probe_sipTCP.name = "LB_test_ProbeSIPTCP"
probe_sipTCP.description = "Created by test. Probe type SIPTCP"
probe_sipTCP.probeInterval = 30
probe_sipTCP.passDetectInterval = 100
probe_sipTCP.failDetect = 5
#more settings fields
probe_sipTCP.passDetectCount = 5
probe_sipTCP.receiveTimeout = 15
probe_sipTCP.destIP = "1.1.1.1"
probe_sipTCP.port = "509"
probe_sipTCP.tcpConnTerm = True
probe_sipTCP.openTimeout = 60
probe_sipTCP.expectRegExp = ".*"
probe_sipTCP.expectRegExpOffset = 4000

probe_smtp = SMTPprobe()
probe_smtp.type = "SMTP"
probe_smtp.name = "LB_test_ProbeSMTP"
probe_smtp.description = "Created by test. Probe type SMTP"
probe_smtp.probeInterval = 30
probe_smtp.passDetectInterval = 100
probe_smtp.failDetect = 5
#more settings fields
probe_smtp.passDetectCount = 5
probe_smtp.receiveTimeout = 15
probe_smtp.destIP = "1.1.1.1"
probe_smtp.isRouted = True
probe_smtp.port = "510"
probe_smtp.tcpConnTerm = True
probe_smtp.openTimeout = 60

probe_snmp = SNMPprobe()
probe_snmp.type = "SNMP"
probe_snmp.name = "LB_test_ProbeSNMP"
probe_snmp.description = "Created by test. Probe type SNMP"
probe_snmp.probeInterval = 30
probe_snmp.passDetectInterval = 100
probe_snmp.failDetect = 5
probe_snmp.SNMPComm = "public"
probe_snmp.SNMPver = None
#more settings fields
probe_snmp.passDetectCount = 5
probe_snmp.receiveTimeout = 15
probe_snmp.destIP = "1.1.1.1"
probe_snmp.isRouted = True
probe_snmp.port = "511"
probe_snmp.tcpConnTerm = True
probe_snmp.openTimeout = 60

probe_tcp = TCPprobe()
probe_tcp.type = "TCP"
probe_tcp.name = "LB_test_ProbeTCP"
probe_tcp.description = "Created by test. Probe type TCP"
probe_tcp.probeInterval = 20
probe_tcp.passDetectInterval = 50
probe_tcp.failDetect = 5
probe_tcp.port = "512"
probe_tcp.sendData = "SendingData"
#more settings fields
probe_tcp.passDetectCount = 5
probe_tcp.receiveTimeout = 15
probe_tcp.destIP = "1.1.1.1"
probe_tcp.isRouted = True
probe_tcp.tcpConnTerm= True
probe_tcp.openTimeout = 60
probe_tcp.expectRegExp = ".*"
probe_tcp.expectRegExpOffset = 500

probe_telnet = TELNETprobe()
probe_telnet.type = "TELNET"
probe_telnet.name = "LB_test_ProbeTELNET"
probe_telnet.description = "Created by test. Probe type TELNET"
probe_telnet.probeInterval = 20
probe_telnet.passDetectInterval = 50
probe_telnet.failDetect = 5
#more settings fields
probe_telnet.passDetectCount = 5
probe_telnet.receiveTimeout = 15
probe_telnet.destIP = "1.1.1.1"
probe_telnet.isRouted = True
probe_telnet.port = "513"
probe_telnet.tcpConnTerm= True
probe_telnet.openTimeout = 60

probe_udp = UDPprobe()
probe_udp.type = "UDP"
probe_udp.name = "LB_test_ProbeUDP"
probe_udp.description = "Created by test. Probe type UDP"
probe_udp.probeInterval = 20
probe_udp.passDetectInterval = 50
probe_udp.failDetect = 5
probe_udp.port = "514"
probe_udp.sendData = "SendingData"
#more settings fields
probe_udp.passDetectCount = 5
probe_udp.receiveTimeout = 15
probe_udp.destIP = "1.1.1.1"
probe_udp.isRouted = True
probe_udp.expectRegExp = ".*"
probe_udp.expectRegExpOffset = 500

probe_vm = VMprobe()
probe_vm.type = "VM"
probe_vm.name = "LB_test_ProbeVM"
probe_vm.description = "Created by test. Probe type VM"
probe_vm.probeInterval = 600
probe_vm.maxCPUburstThresh = 97
probe_vm.minCPUburstThresh = 97
probe_vm.maxMemBurstThresh = 97
probe_vm.minMemBurstThresh = 97
probe_vm.VMControllerName = None

sf_host = ServerFarm()
sf_host.type = "Host"
sf_host.name = "LB_test_sfarm01"
sf_host.description = "Created by test. Sfarm type Host"
sf_host.failAction = "reassign"
#sf_host.Failaction Reassign Across Vlans - variable not define
sf_host.failOnAll = True
sf_host.inbandHealthCheck = "Remove"
sf_host.connFailureThreshCount = 5
sf_host.resetTimeout = 200
sf_host.resumeService = 40
sf_host.transparent = True
sf_host.dynamicWorkloadScale = "Local"
sf_host.partialThreshPercentage = 11
sf_host.backInservice = 22
# Adding probes in another function

sf_redirect = ServerFarm()
sf_redirect.type = "Redirect"
sf_redirect.name = "LB_test_sfarm02"
sf_redirect.description = "Created by test. SFarm type Redirect"
sf_redirect.failAction = "purge"

sticky_httpContent = HTTPContentSticky()
sticky_httpContent.type = "HTTPContent"
sticky_httpContent.name = "LB_test_stickyHTTPContent"
sticky_httpContent.offset = 0
sticky_httpContent.length = None
sticky_httpContent.beginPattern = "beginpaternnn"
sticky_httpContent.endPattern = "endpaternnnn"
sticky_httpContent.serverFarm = "LB_test_sfarm01"
sticky_httpContent.backupServerFarm = "LB_test_sfarm02"
# Aggregate State - var not define
# Enable Sticky On Backup Server Farm - var not define
sticky_httpContent.replicateOnHAPeer = True
sticky_httpContent.timeout = 2880
sticky_httpContent.timeoutActiveConn = True

sticky_httpCookie = HTTPCookieSticky()
sticky_httpCookie.type = "HTTPCookie"
sticky_httpCookie.name = "LB_test_stickyHTTPCookie"
sticky_httpCookie.cookieName = "cookieshmuki"
sticky_httpCookie.enableInsert = True
sticky_httpCookie.browserExpire = True
sticky_httpCookie.offset = 999
sticky_httpCookie.length = 1000
sticky_httpCookie.secondaryName = "stickysecname"
sticky_httpCookie.serverFarm = "LB_test_sfarm01"
sticky_httpCookie.backupServerFarm = "LB_test_sfarm02"
sticky_httpCookie.replicateOnHAPeer = True
sticky_httpCookie.timeout = 2880
sticky_httpCookie.timeoutActiveConn = True

sticky_httpHeader = HTTPHeaderSticky()
sticky_httpHeader.type = "HTTPHeader"
sticky_httpHeader.name = "LB_test_stickyHTTPHeader"
sticky_httpHeader.headerName = "authorization"
sticky_httpHeader.offset = 50
sticky_httpHeader.length = 150
sticky_httpHeader.serverFarm = "LB_test_sfarm01"
sticky_httpHeader.backupServerFarm = "LB_test_sfarm02"
sticky_httpHeader.replicateOnHAPeer = True
sticky_httpHeader.timeout = 2880
sticky_httpHeader.timeoutActiveConn = True

sticky_ipnetmask = IPNetmaskSticky()
sticky_ipnetmask.type = "IPNetmask"
sticky_ipnetmask.name = "LB_test_stickyIPNetmask"
sticky_ipnetmask.netmask = "255.255.255.128"
sticky_ipnetmask.ipv6PrefixLength = "96"
sticky_ipnetmask.addressType = "Both"
sticky_ipnetmask.serverFarm = "LB_test_sfarm01"
sticky_ipnetmask.backupServerFarm = "LB_test_sfarm02"
sticky_ipnetmask.replicateOnHAPeer = True
sticky_ipnetmask.timeout = 1
sticky_ipnetmask.timeoutActiveConn = True

sticky_v6prefix = v6PrefixSticky()
sticky_v6prefix.type = "v6prefix"
sticky_v6prefix.name = "LB_test_stickyV6prefix"
sticky_v6prefix.prefixLength = "96"
sticky_v6prefix.netmask = "255.255.255.128"
sticky_v6prefix.addressType = "destination"
sticky_v6prefix.serverFarm = "LB_test_sfarm01"
sticky_v6prefix.backupServerFarm = "LB_test_sfarm02"
sticky_v6prefix.replicateOnHAPeer = True
sticky_v6prefix.timeout = 65535
sticky_v6prefix.timeoutActiveConn = True

sticky_l4payload = L4PayloadSticky()
sticky_l4payload.type = "l4payload"
sticky_l4payload.name = "LB_test_stickyL4payload"
sticky_l4payload.offset = 50
sticky_l4payload.length = 200
sticky_l4payload.beginPattern = "beginpaternnn"
sticky_l4payload.enableStickyForResponse = True
sticky_l4payload.serverFarm = "LB_test_sfarm01"
sticky_l4payload.backupServerFarm = "LB_test_sfarm02"
sticky_l4payload.replicateOnHAPeer = True
sticky_l4payload.timeout = 2880
sticky_l4payload.timeoutActiveConn = True

sticky_radius = RadiusSticky()
sticky_radius.type = "radius"
sticky_radius.name = "LB_test_stickyRadius"
#sticky_radius.radiusTypes = "Radius Calling Id" - var not processed
sticky_radius.serverFarm = "LB_test_sfarm01"
sticky_radius.backupServerFarm = "LB_test_sfarm02"
sticky_radius.replicateOnHAPeer = True
sticky_radius.timeout = 2880
sticky_radius.timeoutActiveConn = True

sticky_rtspHeader = RTSPHeaderSticky()
sticky_rtspHeader.type = "RTSPHeader"
sticky_rtspHeader.name = "LB_test_stickyRTSPHeader"
sticky_rtspHeader.offset = 50
sticky_rtspHeader.length = 200
sticky_rtspHeader.serverFarm = "LB_test_sfarm01"
sticky_rtspHeader.backupServerFarm = "LB_test_sfarm02"
sticky_rtspHeader.replicateOnHAPeer = True
sticky_rtspHeader.timeout = 2880
sticky_rtspHeader.timeoutActiveConn = True

sticky_sipHeader = SIPHeaderSticky
sticky_sipHeader.type = "SIPHeader"
sticky_sipHeader.name = "LB_test_stickySIPHeader"
sticky_sipHeader.serverFarm = "LB_test_sfarm01"
sticky_sipHeader.backupServerFarm = "LB_test_sfarm02"
sticky_sipHeader.replicateOnHAPeer = True
sticky_sipHeader.timeout = 2880
sticky_sipHeader.timeoutActiveConn = True

vip_loadbalance = VirtualServer()
vip_loadbalance.name = "LB_test_VIP1"
vip_loadbalance.ipVersion = "IPv4"
vip_loadbalance.address = "10.250.250.250"
vip_loadbalance.mask = "255.255.255.255"
vip_loadbalance.proto = "TCP"
vip_loadbalance.appProto = "HTTP"
vip_loadbalance.port = "80"
vip_loadbalance.VLAN = [2]
# vip_loadbalance.ICMPreply = True - not processed

vip_sticky = VirtualServer()
vip_sticky.name = "LB_test_VIP2"
vip_sticky.ipVersion = "IPv4"
vip_sticky.address = "10.250.250.251"
vip_sticky.mask = "255.255.255.255"
vip_sticky.proto = "TCP"
vip_sticky.appProto = "HTTP"
vip_sticky.port = "80"
vip_sticky.VLAN = [2]


class Ace_5x_DriverTestCase(unittest.TestCase):
    def test_01a_createRServer_typeHost(self):
        print driver.createRServer(test_context, rs_host)
    
    def test_01b_createRServer_typeRedirect(self):
        print driver.createRServer(test_context, rs_redirect)

    def test_02a_createDNSProbe(self):
        driver.createProbe(test_context, probe_dns)

    def test_02b_createECHOUDPprobe(self):
        driver.createProbe(test_context, probe_echoUDP)

    def test_02c_createECHOTCPprobe(self):
        driver.createProbe(test_context, probe_echoTCP)

    def test_02d_createFINGERprobe(self):
        driver.createProbe(test_context, probe_finger)

    def test_02e_createFTPprobe(self):
        driver.createProbe(test_context, probe_ftp)

    def test_02f_createHTTPprobe(self):
        driver.createProbe(test_context, probe_http)

    def test_02g_createHTTPSprobe(self):
        driver.createProbe(test_context, probe_https)

    def test_02h_createICMPprobe(self):
        driver.createProbe(test_context, probe_icmp)

    def test_02i_createIMAPprobe(self):
        driver.createProbe(test_context, probe_imap)

    def test_02j_createPOPprobe(self):
        driver.createProbe(test_context, probe_pop)

    def test_02k_createRADIUSprobe(self):
        driver.createProbe(test_context, probe_radius)

    def test_02l_createRTSPprobe(self):
        driver.createProbe(test_context, probe_rtsp)

    def test_02m_createSCRIPTEDprobe(self):
        driver.createProbe(test_context, probe_scripted)

    def test_02n_createSIPUDPprobe(self):
        driver.createProbe(test_context, probe_sipUDP)

    def test_02o_createSMTPprobe(self):
        driver.createProbe(test_context, probe_smtp)

    def test_02p_createSNMPprobe(self):
        driver.createProbe(test_context, probe_snmp)

    def test_02r_createTCPprobe(self):
        driver.createProbe(test_context, probe_tcp)

    def test_02s_createTELNETprobe(self):
        driver.createProbe(test_context, probe_telnet)

    def test_02t_createUDPprobe(self):
        driver.createProbe(test_context, probe_udp)

    def test_02u_createVMprobe(self):
        driver.createProbe(test_context, probe_vm)

    def test_03a_createServerFarm_typeHost(self):
        driver.createServerFarm(test_context, sf_host)

    def test_03b_createServerFarm_typeRedirect(self):
        driver.createServerFarm(test_context, sf_redirect)

    def test_04_addRServerToSF(self):
        driver.addRServerToSF(test_context, sf_host,  rs_host)

    def test_05_addProbeToSF(self):
        driver.addProbeToSF(test_context, sf_host,  probe_http)

    def test_06a_createHTTPContentStickiness(self):
        driver.createStickiness(test_context, sticky_httpContent)

    def test_06b_createHTTPCookieStickiness(self):
        driver.createStickiness(test_context, sticky_httpCookie)

    def test_06c_createHTTPHeaderStickiness(self):
        driver.createStickiness(test_context, sticky_httpHeader)

    def test_06d_createIPNetmaskStickiness(self):
        driver.createStickiness(test_context, sticky_ipnetmask)

    def test_06e_createV6prefixStickiness(self):
        driver.createStickiness(test_context, sticky_v6prefix)

    def test_06f_createL4payloadStickiness(self):
        driver.createStickiness(test_context, sticky_l4payload)

    def test_06g_createRadiusStickiness(self):
        driver.createStickiness(test_context, sticky_radius)

    def test_06h_createRTSPHeaderStickiness(self):
        driver.createStickiness(test_context, sticky_rtspHeader)

    def test_06i_createSIPHeaderStickiness(self):
        driver.createStickiness(test_context, sticky_sipHeader)

    def test_07a_createVIP_loadbalncer(self):
        driver.createVIP(test_context, vip_loadbalance,  sf_host)

    def test_07b_createVIP_sticky(self):
        driver.createVIP(test_context, vip_sticky,  sf_redirect)

    def test_08_suspendRServer(self):
        driver.suspendRServer(test_context, sf_host, rs_host)

    def test_08a_suspendRServerGlobal(self):
        driver.suspendRServerGlobal(test_context, rs_redirect)

    def test_09_activateRServer(self):
        driver.activateRServer(test_context, sf_host, rs_host)

    def test_09a_activateRServerGlobal(self):
        driver.activateRServerGlobal(test_context, rs_redirect)

    def test_10a_deleteVIP_loadbalance(self):
        driver.deleteVIP(test_context, vip_loadbalance)

    def test_10b_deleteVIP_sticky(self):
        driver.deleteVIP(test_context, vip_sticky)

    def test_11a_deleteHTTPContentStickiness(self):
        driver.deleteStickiness(test_context, sticky_httpContent)

    def test_11b_deleteHTTPCookieStickiness(self):
        driver.deleteStickiness(test_context, sticky_httpCookie)

    def test_11c_deleteHTTPHeaderStickiness(self):
        driver.deleteStickiness(test_context, sticky_httpHeader)

    def test_11d_deleteIPNetmaskStickiness(self):
        driver.deleteStickiness(test_context, sticky_ipnetmask)

    def test_11e_deleteV6prefixStickiness(self):
        driver.deleteStickiness(test_context, sticky_v6prefix)

    def test_11f_deleteL4payloadStickiness(self):
        driver.deleteStickiness(test_context, sticky_l4payload)

    def test_11g_deleteRadiusStickiness(self):
        driver.deleteStickiness(test_context, sticky_radius)

    def test_11h_deleteRTSPHeaderStickiness(self):
        driver.deleteStickiness(test_context, sticky_rtspHeader)

    def test_11i_deleteSIPHeaderStickiness(self):
        driver.deleteStickiness(test_context, sticky_sipHeader)

    def test_12_deleteProbeFromSF(self):
        driver.deleteProbeFromSF(test_context, sf_host,  probe_http)

    def test_13_deleteRServerFromSF(self):
        driver.deleteRServerFromSF(test_context, sf_host,  rs_host)

    def test_14a_deleteServerFarm_typeHost(self):
        driver.deleteServerFarm(test_context, sf_host)

    def test_14b_deleteServerFarm_typeRedirect(self):
        driver.deleteServerFarm(test_context, sf_redirect)

    def test_15a_deleteDNSProbe(self):
        driver.deleteProbe(test_context, probe_dns)

    def test_15b_deleteECHOUDPprobe(self):
        driver.deleteProbe(test_context, probe_echoUDP)

    def test_15c_deleteECHOTCPprobe(self):
        driver.deleteProbe(test_context, probe_echoTCP)

    def test_15d_deleteFINGERprobe(self):
        driver.deleteProbe(test_context, probe_finger)

    def test_15e_deleteFTPprobe(self):
        driver.deleteProbe(test_context, probe_ftp)

    def test_15f_deleteHTTPprobe(self):
        driver.deleteProbe(test_context, probe_http)

    def test_15g_deleteHTTPSprobe(self):
        driver.deleteProbe(test_context, probe_https)

    def test_15h_deleteICMPprobe(self):
        driver.deleteProbe(test_context, probe_icmp)

    def test_15i_deleteIMAPprobe(self):
        driver.deleteProbe(test_context, probe_imap)

    def test_15j_deletePOPprobe(self):
        driver.deleteProbe(test_context, probe_pop)

    def test_15k_deleteRADIUSprobe(self):
        driver.deleteProbe(test_context, probe_radius)

    def test_15l_deleteRTSPprobe(self):
        driver.deleteProbe(test_context, probe_rtsp)

    def test_15m_deleteSCRIPTEDprobe(self):
        driver.deleteProbe(test_context, probe_scripted)

    def test_15n_deleteSIPUDPprobe(self):
        driver.deleteProbe(test_context, probe_sipUDP)

    def test_15o_deleteSMTPprobe(self):
        driver.deleteProbe(test_context, probe_smtp)

    def test_15p_deleteSNMPprobe(self):
        driver.deleteProbe(test_context, probe_snmp)

    def test_15r_deleteTCPprobe(self):
        driver.deleteProbe(test_context, probe_tcp)

    def test_15s_deleteTELNETprobe(self):
        driver.deleteProbe(test_context, probe_telnet)

    def test_15t_deleteUDPprobe(self):
        driver.deleteProbe(test_context, probe_udp)

    def test_15u_deleteVMprobe(self):
        driver.deleteProbe(test_context, probe_vm)

    def test_16a_deleteRServer_typeHost(self):
        driver.deleteRServer(test_context, rs)

    def test_16b_deleteRServer_typeRedirect(self):
        driver.deleteRServer(test_context, rs)
