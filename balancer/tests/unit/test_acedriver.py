# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

from balancer.drivers.cisco_ace.ace_driver import AceDriver

def deployConfig(s):
    W += s
    return 'OK'

def getConfig(s):
    return 'test'

class TestDriver(AceDriver):
    pass


dev = {'ip':'10.4.15.21', 'port':'10443', \
       'login':'admin', 'password':'cisco123'}

conf = []
driver = TestDriver(conf, dev)

rs_host = { 'type': 'host', 'name': 'LB_test_rs01', \
           'address': '172.250.0.1', 'state': 'inservice' }
rs_host['extra'] = { 'description': 'Created by test. RS type Host', \
                     'minCon': '2000000', 'maxCon': '3000000', \
                     'weight': '7', 'rateBandwidth': '500000', \
                     'rateConnection': '5000', 'failOnAll': 'True', \
                     'port': '80', 'cookieStr': 'stringcookie' }

rs_redirect = { 'type': 'redirect', 'name': 'LB_test_rs02', \
                'address': '172.250.0.2', 'state': 'outofservice' }
rs_redirect['extra'] = { 'description': 'Created by test. RS type Redirect', \
                         'minCon': '2000000', 'maxCon': '3000000', \
                         'weight': '1', 'rateBandwidth': '100000', \
                         'rateConnection': '999', 'redirectionCode': '301', \
                         'webHostRedir': 'www.cisco.com' }

rs_test3 = { 'type': 'host', 'name': 'LB_test_rs03', \
           'address': '10.4.15.231', 'state': 'outofservice' }
rs_test3['extra'] = { 'description': 'Created by test. RS type Host', \
                     'weight': '70', 'rateBandwidth': '5000', \
                     'rateConnection': '5000', \
                     'port': '809', 'cookieStr': 'stringcookie' }

rs_test4 = { 'type': 'redirect', 'name': 'LB_test_rs02', \
                'address': '172.250.0.2', 'state': 'inservice' }
rs_test4['extra'] = { 'description': 'Created by test. RS type Redirect', \
                         'weight': '100', 'redirectionCode': '301', \
                         'webHostRedir': 'www.cisco.com' }

probe_dns = { 'type': 'DNS', 'name': 'LB_test_ProbeDNS' }
probe_dns['extra'] = { 'description': 'Created by test. Probe type DNS', \
                       'probeInterval': '2', 'passDetectInterval': '2', \
                       'failDetect': '1', 'domainName': 'test-org', \
                       'passDetectCount': '1', 'receiveTimeout': '1', \
                       'destIP': '1.1.1.1', 'port': '1' }

probe_echoUDP = { 'type': 'ECHO-UDP', 'name': 'LB_test_ProbeECHOUDP' }
probe_echoUDP['extra'] = { 'description': 'Created by test. ', \
                           'probeInterval': '65535', \
                           'passDetectInterval': '65535', \
                           'failDetect': '65535', 'sendData': 'SendingData', \
                           'passDetectCount': '65535', \
                           'receiveTimeout': '65535', 'destIP': '1.1.1.1', \
                           'isRouted': 'True', 'port': '65535' }

probe_echoTCP = { 'type': 'ECHO-TCP', 'name': 'LB_test_ProbeECHOTCP' }
probe_echoTCP['extra'] = { 'description': 'Probe type ECHOTCP', \
                           'probeInterval': '15', 'passDetectInterval': '60', \
                           'failDetect': '3', 'sendData': 'SendingData', \
                           'passDetectCount': '3', 'receiveTimeout': '10', \
                           'destIP': '1.1.1.1', 'isRouted': 'True', \
                           'port': '500', 'tcpConnTerm': 'True', \
                           'openTimeout': '10' }

probe_finger = { 'type': 'FINGER', 'name': 'LB_test_ProbeFinger' }
probe_finger['extra'] = { 'description': 'Probe type Finger', \
                          'probeInterval': '20', \
                          'passDetectInterval': '50', \
                          'failDetect': '5', 'sendData': 'SendingData', \
                          'passDetectCount': '3', 'receiveTimeout': '10', \
                          'destIP': '1.1.1.1', 'isRouted': 'True', \
                          'port': '501', 'openTimeout': '1' }

probe_ftp = { 'type': 'FTP', 'name': 'LB_test_ProbeFTP' }
probe_ftp['extra'] = { 'description': 'Created by test. Probe type FTP', \
                       'probeInterval': '20', 'passDetectInterval': '50', \
                       'failDetect': '5', 'passDetectCount': '5', \
                       'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                       'isRouted': 'True', 'port': '502', \
                       'tcpConnTerm': 'True', 'openTimeout': '65535' }

probe_http = { 'type': 'HTTP', 'name': 'LB_test_ProbeHTTP' }
probe_http['extra'] = { 'description': 'Created by test. Probe type HTTP', \
                        'probeInterval': '20', 'passDetectInterval': '50', \
                        'failDetect': '5', 'port': '80', \
                        'requestMethodType': 'GET', 'destIP': '1.1.1.1', \
                        'requestHTTPurl': 'cisco.com', 'isRouted': 'True', \
                        'passDetectCount': '5', 'tcpConnTerm': 'True', \
                        'probe_http.receiveTimeout': '15', \
                        'appendPortHostTag': 'True', 'openTimeout': '2', \
                        'userName': 'user', 'password': 'password', \
                        'expectRegExp': '.*', 'expectRegExpOffset': '1', \
                        'hash': 'True', \
                        'hashString': '01020304010203040102030401020304' }

probe_https = { 'type': 'HTTPS', 'name': 'LB_test_ProbeHTTPS' }
probe_https['extra'] = { 'description': 'Created by test. Probe type HTTPS', \
                         'probeInterval': '20', 'passDetectInterval': '50', \
                         'failDetect': '5', 'port': '8080', \
                         'requestMethodType': 'HEAD', \
                         'requestHTTPurl': 'cisco.com', 'SSLversion': 'ALL', \
                         'passDetectCount': '5', 'receiveTimeout': '15', \
                         'destIP': '1.1.1.1', 'isRouted': 'True', \
                         'tcpConnTerm': 'True', 'appendPortHostTag': 'True', \
                         'openTimeout': '2', 'userName': 'user', \
                         'password': 'password', 'expectRegExp': '.*', \
                         'expectRegExpOffset': '1', 'hash': 'True', \
                         'hashString': '01020304010203040102030401020304' }

probe_icmp = { 'type': 'ICMP', 'name': 'LB_test_ProbeICMP' }
probe_icmp['extra'] = { 'description': 'Created by test. Probe type ICMP', \
                        'probeInterval': '2', 'passDetectInterval': '2', \
                        'failDetect': '1', 'passDetectCount': '1', \
                        'receiveTimeout': '1', 'destIP': '1.1.1.1' }

probe_imap = { 'type': 'IMAP', 'name': 'LB_test_ProbeIMAP' }
probe_imap['extra'] = { 'description': 'Created by test. Probe type IMAP', \
                        'probeInterval': '20', 'passDetectInterval': '50', \
                        'failDetect': '5', 'userName': 'user', \
                        'password': 'password', 'maibox': 'dhl.org',
                        'requestCommand': 'request', 'passDetectCount': '5', \
                        'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                        'isRouted': 'True', 'port': '503', \
                        'tcpConnTerm': 'True', 'openTimeout': '60' }

probe_pop = { 'type': 'POP', 'name': 'LB_test_ProbePOP' }
probe_pop['extra'] = { 'description': 'Created by test. Probe type POP', \
                       'probeInterval': '20', 'passDetectInterval': '50', \
                       'failDetect': '5', 'userName': 'user', \
                       'password': 'password', 'requestCommand': 'request', \
                       'passDetectCount': '5', 'receiveTimeout': '15', \
                       'destIP': '1.1.1.1', 'isRouted': 'True', \
                       'port': '504', 'tcpConnTerm': 'True', \
                       'openTimeout': '60' }

probe_radius = { 'type': 'RADIUS', 'name': 'LB_test_ProbeRADIUS' }
probe_radius['extra'] = { 'description': 'Probe type Radius', \
                          'probeInterval': '30', 'passDetectInterval': '100', \
                          'failDetect': '5', 'userSecret': 'topsecret', \
                          'userName': 'user', 'password': 'password', \
                          'requestCommand': 'request', \
                          'passDetectCount': '5', 'receiveTimeout': '15', \
                          'destIP': '1.1.1.1', 'isRouted': 'True', \
                          'port': '505', 'NASIPaddr': '2.2.2.2' }

probe_rtsp = { 'type': 'RTSP', 'name': 'LB_test_ProbeRTSP' }
probe_rtsp['extra'] = { 'description': 'Created by test. Probe type RTSP', \
                        'probeInterval': '30', 'passDetectInterval': '100', \
                        'failDetect': '5', 'requestURL': 'cisco.com', \
                        'requareHeaderValue': 'headervalue', \
                        'proxyRequareHeaderValue': 'requarevalue', \
                        'requestMethodType': 'True', \
                        'passDetectCount': '5', 'receiveTimeout': '15', \
                        'destIP': '1.1.1.1', 'port': '506' , \
                        'tcpConnTerm': 'True', 'openTimeout': '60' }

probe_scripted =  { 'type': 'SCRIPTED', 'name': 'LB_test_ProbeSCRIPTED' }
probe_scripted['extra'] = { 'description': 'Probe type SCRIPTED', \
                            'probeInterval': '30', \
                            'passDetectInterval': '100', \
                            'failDetect': '5', 'port': '507', \
                            'scriptName': 'script.py', 'scriptArgv': 'a1', \
                            'passDetectCount': '5', 'receiveTimeout': '15', \
                            'copied': 'True', 'proto': 'FTP' , \
                            'userName': 'user', 'password': 'password', \
                            'sourceFileName': 'root/script.py' }

probe_sipUDP = { 'type': 'SIP-UDP', 'name': 'LB_test_ProbeSIPUDP' }
probe_sipUDP['extra'] = { 'description': 'Probe type SIPUDP', \
                          'probeInterval': '30', \
                          'passDetectInterval': '100', 'failDetect': '5', \
                          'passDetectCount': '5', 'receiveTimeout': '15', \
                          'destIP': '1.1.1.1', 'port': '508', \
                          'rport': 'True', 'expectRegExp': '.*', \
                          'expectRegExpOffset': '4000' }

probe_sipTCP = { 'type': 'SIP-TCP', 'name': 'LB_test_ProbeSIPTCP' }
probe_sipTCP['extra'] = { 'description': 'Probe type SIPTCP', \
                          'probeInterval': '30', 'passDetectInterval': '100', \
                          'failDetect': '5', 'passDetectCount': '5', \
                          'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                          'port': '509', 'tcpConnTerm': 'True', \
                          'openTimeout': '60', 'expectRegExp': '.*', \
                          'expectRegExpOffset': '4000' }

probe_smtp = { 'type': 'SMTP', 'name': 'LB_test_ProbeSMTP' }
probe_smtp['extra'] = { 'description': 'Created by test. Probe type SMTP', \
                        'probeInterval': '30', 'passDetectInterval': '100', \
                        'failDetect': '5', 'passDetectCount': '5', \
                        'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                        'isRouted': 'True', 'port': '510', \
                        'tcpConnTerm': 'True', 'openTimeout': '60' }

probe_snmp = { 'type': 'SNMP', 'name': 'LB_test_ProbeSNMP' }
probe_snmp['extra'] = { 'description': 'Created by test. Probe type SNMP', \
                        'probeInterval': '30', 'passDetectInterval': '100', \
                        'failDetect': '5', 'SNMPComm': 'public', \
                        'passDetectCount': '5', 'receiveTimeout': '15', \
                        'destIP': '1.1.1.1', 'isRouted': 'True', \
                        'port': '511', 'tcpConnTerm': 'True', \
                        'openTimeout': '60' }

probe_tcp = { 'type': 'TCP', 'name': 'LB_test_ProbeTCP' }
probe_tcp['extra'] = { 'description': 'Created by test. Probe type TCP', \
                       'probeInterval': '20', 'passDetectInterval': '50', \
                       'failDetect': '5', 'port': '512', \
                       'sendData': 'SendingData', 'passDetectCount': '5', \
                       'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                       'isRouted': 'True', 'tcpConnTerm': 'True', \
                       'openTimeout': '60', 'expectRegExp': '.*', \
                       'expectRegExpOffset': '500' }

probe_telnet =  { 'type': 'TELNET', 'name': 'LB_test_ProbeTELNET' }
probe_telnet['extra'] = { 'description': 'Probe type TELNET', \
                          'probeInterval': '20', 'passDetectInterval': '50', \
                          'failDetect': '5', 'passDetectCount': '5', \
                          'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                          'isRouted': 'True', 'port': '513', \
                          'tcpConnTerm': 'True', 'openTimeout': '60' }

probe_udp = { 'type': 'UDP', 'name': 'LB_test_ProbeUDP' }
probe_udp['extra'] = { 'description': 'Created by test. Probe type UDP', \
                       'probeInterval': '20', 'passDetectInterval': '50', \
                       'failDetect': '5', 'port': '514', \
                       'sendData': 'SendingData', 'passDetectCount': '5', \
                       'receiveTimeout': '15', 'destIP': '1.1.1.1', \
                       'isRouted': 'True', 'expectRegExp': '.*', \
                       'expectRegExpOffset': '500' }

probe_vm = { 'type': 'VM', 'name': 'LB_test_ProbeVM' }
probe_vm['extra'] = { 'description': 'Created by test. Probe type VM', \
                      'probeInterval': '600', 'maxCPUburstThresh': '97', \
                      'minCPUburstThresh': '97', 'maxMemBurstThresh': '97', \
                      'minMemBurstThresh': '97' }

sf_host = { 'type': 'Host', 'name': 'LB_test_sfarm01' }
sf_host['extra'] = { 'description': 'Created by test. Sfarm type Host', \
                     'failAction': 'reassign', 'failOnAll': 'True', \
                     'inbandHealthCheck': 'Remove', \
                     'connFailureThreshCount': '5', 'resetTimeout': '200', \
                     'resumeService': '40', 'transparent': 'True', \
                     'dynamicWorkloadScale': 'Local', \
                     'partialThreshPercentage': '11', 'backInservice': '22' }

sf_redirect = { 'type': 'Redirect', 'name': 'LB_test_sfarm02' }
sf_redirect['extra'] = { 'description': 'SFarm type Redirect' , \
                         'failAction': 'purge' }

sticky_httpContent = { 'type': 'HTTPContent', \
                       'name': 'LB_test_stickyHTTPContent' }
sticky_httpContent['extra'] = { 'offset': '0', \
                                'beginPattern': 'beginpaternnn', \
                                'endPattern': 'endpaternnnn', \
                                'serverFarm': 'LB_test_sfarm01',\
                                'backupServerFarm': 'LB_test_sfarm02', \
                                'replicateOnHAPeer': 'True', \
                                'timeout': '2880', \
                                'timeoutActiveConn': 'True' }

sticky_httpCookie = { 'type': 'HTTPCookie', 'name': 'LB_test_stickyHTTPCookie' }
sticky_httpCookie['extra'] = { 'cookieName': 'cookieshmuki', \
                               'enableInsert': 'True', \
                               'browserExpire': 'True', 'offset': '999', \
                               'length': '1000', \
                               'secondaryName': 'stickysecname', \
                               'serverFarm': 'LB_test_sfarm01', \
                               'backupServerFarm': 'LB_test_sfarm02', \
                               'replicateOnHAPeer': 'True', \
                               'timeout': '2880', 'timeoutActiveConn': 'True' }

sticky_httpHeader = { 'type': 'HTTPHeader', \
                      'name': 'LB_test_stickyHTTPHeader' }
sticky_httpHeader['extra'] = { 'headerName': 'authorization', 'offset': '50', \
                               'length': '150', \
                               'serverFarm': 'LB_test_sfarm01', \
                               'backupServerFarm': 'LB_test_sfarm02', \
                               'replicateOnHAPeer': 'True', \
                               'timeout': '2880', 'timeoutActiveConn': 'True' }

sticky_ipnetmask = { 'type': 'IPNetmask', 'name': 'LB_test_stickyIPNetmask' }
sticky_ipnetmask['extra'] = { 'netmask': '255.255.255.128', 'timeout': '1', \
                              'ipv6PrefixLength': '96', \
                              'addressType': 'Both', \
                              'serverFarm': 'LB_test_sfarm01', \
                              'backupServerFarm': 'LB_test_sfarm02', \
                              'replicateOnHAPeer': 'True', \
                              'timeoutActiveConn': 'True' }

sticky_v6prefix = { 'type': 'v6prefix', 'name': 'LB_test_stickyV6prefix' }
sticky_v6prefix['extra'] = { 'prefixLength': '96', \
                             'netmask': '255.255.255.128', \
                             'addressType': 'destination', \
                             'serverFarm': 'LB_test_sfarm01', \
                             'backupServerFarm': 'LB_test_sfarm02', \
                             'replicateOnHAPeer': 'True', \
                             'timeout': '65535', 'timeoutActiveConn': 'True' }

sticky_l4payload = { 'type': 'l4payload', 'name': 'LB_test_stickyL4payload' }
sticky_l4payload['extra'] = { 'offset': '50', 'length': '200', \
                              'beginPattern': 'beginpaternnn', \
                              'enableStickyForResponse': 'True', \
                              'serverFarm': 'LB_test_sfarm01', \
                              'backupServerFarm': 'LB_test_sfarm02', \
                              'replicateOnHAPeer': 'True', \
                              'timeout': '2880', 'timeoutActiveConn': 'True' }

sticky_radius = { 'type': 'radius', 'name': 'LB_test_stickyRadius' }
sticky_radius['extra'] = { 'serverFarm': 'LB_test_sfarm01', \
                           'backupServerFarm': 'LB_test_sfarm02', \
                           'replicateOnHAPeer': 'True', 'timeout': '2880', \
                           'timeoutActiveConn': 'True' }

sticky_rtspHeader = { 'type': 'RTSPHeader', \
                      'name': 'LB_test_stickyRTSPHeader' }
sticky_rtspHeader['extra'] = { 'offset': '50', 'length': '200', \
                               'serverFarm': 'LB_test_sfarm01', \
                               'backupServerFarm': 'LB_test_sfarm02', \
                               'replicateOnHAPeer': 'True', \
                               'timeout': '2880', \
                               'timeoutActiveConn': 'True' }

sticky_sipHeader = { 'type': 'SIPHeader', 'name': 'LB_test_stickySIPHeader' }
sticky_sipHeader['extra'] = { 'serverFarm': 'LB_test_sfarm01', \
                              'backupServerFarm': 'LB_test_sfarm02', \
                              'replicateOnHAPeer': 'True', 'timeout': '2880', \
                              'timeoutActiveConn': 'True' }

vip_loadbalance = { 'name': 'LB_test_VIP1', 'ipVersion': 'IPv4', \
                    'address': '10.250.250.250', 'mask': '255.255.255.0', \
                    'proto': 'TCP', 'appProto': 'HTTP', 'port': '20', \
                    'VLAN': "2" }

vip_sticky = { 'name': 'LB_test_VIP2', 'ipVersion': 'IPv4', \
               'address': '10.250.250.251', 'mask': '255.255.255.0', \
               'proto': 'TCP', 'appProto': 'HTTPS', 'port': '5077', \
               'VLAN': '2' }

vip_test3 = { 'name': 'test3', 'ipVersion': 'IPv4', \
               'address': '10.250.250.253', 'mask': '255.255.255.0', \
               'proto': 'TCP', 'appProto': 'RTSP', 'port': '507', \
               'allVLANs': 'True' }

class Ace_DriverTestCase(unittest.TestCase):
    def test_01a_createRServer_typeHost(self):
        print driver.create_real_server(rs_host)

    def test_01b_createRServer_typeRedirect(self):
        print driver.create_real_server(rs_redirect)

    def test_01c_createRServer_typeHost(self):
        print driver.create_real_server(rs_test3)

    def test_01d_createRServer_typeRedirect(self):
        print driver.create_real_server(rs_test4)

    def test_02a_createDNSProbe(self):
        driver.create_probe(probe_dns)

    def test_02b_createECHOUDPprobe(self):
        driver.create_probe(probe_echoUDP)

    def test_02c_createECHOTCPprobe(self):
        driver.create_probe(probe_echoTCP)

    def test_02d_createFINGERprobe(self):
        driver.create_probe(probe_finger)

    def test_02e_createFTPprobe(self):
        driver.create_probe(probe_ftp)

    def test_02f_createHTTPprobe(self):
        driver.create_probe(probe_http)

    def test_02g_createHTTPSprobe(self):
        driver.create_probe(probe_https)

    def test_02h_createICMPprobe(self):
        driver.create_probe(probe_icmp)

    def test_02i_createIMAPprobe(self):
        driver.create_probe(probe_imap)

    def test_02j_createPOPprobe(self):
        driver.create_probe(probe_pop)

    def test_02k_createRADIUSprobe(self):
        driver.create_probe(probe_radius)

    def test_02l_createRTSPprobe(self):
        driver.create_probe(probe_rtsp)

    def test_02m_createSCRIPTEDprobe(self):
        driver.create_probe(probe_scripted)

    def test_02n_createSIPUDPprobe(self):
        driver.create_probe(probe_sipUDP)

    def test_02o_createSMTPprobe(self):
        driver.create_probe(probe_smtp)

    def test_02p_createSNMPprobe(self):
        driver.create_probe(probe_snmp)

    def test_02r_createTCPprobe(self):
        driver.create_probe(probe_tcp)

    def test_02s_createTELNETprobe(self):
        driver.create_probe(probe_telnet)

    def test_02t_createUDPprobe(self):
        driver.create_probe(probe_udp)

    def test_02u_createVMprobe(self):
        driver.create_probe(probe_vm)

    def test_03a_createServerFarm_typeHost(self):
        driver.create_server_farm(sf_host)

    def test_03b_createServerFarm_typeRedirect(self):
        driver.create_server_farm(sf_redirect)

    def test_04_addRServerToSF(self):
        driver.add_real_server_to_server_farm(sf_host,  rs_host)

    def test_05_addProbeToSF(self):
        driver.add_probe_to_server_farm(sf_host,  probe_http)

    def test_06a_createHTTPContentStickiness(self):
        driver.create_stickiness(sticky_httpContent)

    def test_06b_createHTTPCookieStickiness(self):
        driver.create_stickiness(sticky_httpCookie)

    def test_06c_createHTTPHeaderStickiness(self):
        driver.create_stickiness(sticky_httpHeader)

    def test_06d_createIPNetmaskStickiness(self):
        driver.create_stickiness(sticky_ipnetmask)

    def test_06e_createV6prefixStickiness(self):
        driver.create_stickiness(sticky_v6prefix)

    def test_06f_createL4payloadStickiness(self):
        driver.create_stickiness(sticky_l4payload)

    def test_06g_createRadiusStickiness(self):
        driver.create_stickiness(sticky_radius)

    def test_06h_createRTSPHeaderStickiness(self):
        driver.create_stickiness(sticky_rtspHeader)

    def test_06i_createSIPHeaderStickiness(self):
        driver.create_stickiness(sticky_sipHeader)

    def test_07a_createVIP_loadbalncer(self):
        driver.create_virtual_ip(vip_loadbalance,  sf_host)

    def test_07b_createVIP_sticky(self):
        driver.create_virtual_ip(vip_sticky,  sf_redirect)

    def test_07c_createVIP_loadbalncer(self):
        driver.create_virtual_ip(vip_test,  sf_host)

    def test_08_suspendRServer(self):
        driver.suspend_real_server(sf_host, rs_host)

    def test_08a_suspendRServerGlobal(self):
        driver.suspend_real_server_global(rs_redirect)

    def test_09_activateRServer(self):
        driver.activate_real_server(sf_host, rs_host)

    def test_09a_activateRServerGlobal(self):
        driver.activate_real_server_global(rs_redirect)

    def test_10a_deleteVIP_loadbalance(self):
        driver.delete_virtual_ip(vip_loadbalance)

    def test_10b_deleteVIP_sticky(self):
        driver.delete_virtual_ip(vip_sticky)

    def test_11a_deleteHTTPContentStickiness(self):
        driver.delete_stickiness(sticky_httpContent)

    def test_11b_deleteHTTPCookieStickiness(self):
        driver.delete_stickiness(sticky_httpCookie)

    def test_11c_deleteHTTPHeaderStickiness(self):
        driver.delete_stickiness(sticky_httpHeader)

    def test_11d_deleteIPNetmaskStickiness(self):
        driver.delete_stickiness(sticky_ipnetmask)

    def test_11e_deleteV6prefixStickiness(self):
        driver.delete_stickiness(sticky_v6prefix)

    def test_11f_deleteL4payloadStickiness(self):
        driver.delete_stickiness(sticky_l4payload)

    def test_11g_deleteRadiusStickiness(self):
        driver.delete_stickiness(sticky_radius)

    def test_11h_deleteRTSPHeaderStickiness(self):
        driver.delete_stickiness(sticky_rtspHeader)

    def test_11i_deleteSIPHeaderStickiness(self):
        driver.delete_stickiness(sticky_sipHeader)

    def test_12_deleteProbeFromSF(self):
        driver.delete_probe_from__server_farm(sf_host, probe_http)

    def test_13_deleteRServerFromSF(self):
        driver.delete_real_server_from_server_farm(sf_host, rs_host)

    def test_14a_deleteServerFarm_typeHost(self):
        driver.delete_server_farm(sf_host)

    def test_14b_deleteServerFarm_typeRedirect(self):
        driver.delete_server_farm(sf_redirect)

    def test_15a_deleteDNSProbe(self):
        driver.delete_probe(probe_dns)

    def test_15b_deleteECHOUDPprobe(self):
        driver.delete_probe(probe_echoUDP)

    def test_15c_deleteECHOTCPprobe(self):
        driver.delete_probe(probe_echoTCP)

    def test_15d_deleteFINGERprobe(self):
        driver.delete_probe(probe_finger)

    def test_15e_deleteFTPprobe(self):
        driver.delete_probe(probe_ftp)

    def test_15f_deleteHTTPprobe(self):
        driver.delete_probe(probe_http)

    def test_15g_deleteHTTPSprobe(self):
        driver.delete_probe(probe_https)

    def test_15h_deleteICMPprobe(self):
        driver.delete_probe(probe_icmp)

    def test_15i_deleteIMAPprobe(self):
        driver.delete_probe(probe_imap)

    def test_15j_deletePOPprobe(self):
        driver.delete_probe(probe_pop)

    def test_15k_deleteRADIUSprobe(self):
        driver.delete_probe(probe_radius)

    def test_15l_deleteRTSPprobe(self):
        driver.delete_probe(probe_rtsp)

    def test_15m_deleteSCRIPTEDprobe(self):
        driver.delete_probe(probe_scripted)

    def test_15n_deleteSIPUDPprobe(self):
        driver.delete_probe(probe_sipUDP)

    def test_15o_deleteSMTPprobe(self):
        driver.delete_probe(probe_smtp)

    def test_15p_deleteSNMPprobe(self):
        driver.delete_probe(probe_snmp)

    def test_15r_deleteTCPprobe(self):
        driver.delete_probe(probe_tcp)

    def test_15s_deleteTELNETprobe(self):
        driver.delete_probe(probe_telnet)

    def test_15t_deleteUDPprobe(self):
        driver.delete_probe(probe_udp)

    def test_15u_deleteVMprobe(self):
        driver.delete_probe(probe_vm)

    def test_16a_deleteRServer_typeHost(self):
        driver.delete_real_server(rs)

    def test_16b_deleteRServer_typeRedirect(self):
        driver.delete_real_server(rs)
