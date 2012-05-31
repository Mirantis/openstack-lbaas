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

import balancer.common.utils
import logging
import pdb
import openstack.common.exception
#from balancer.loadbalancers.command import BaseCommand
import balancer.storage.storage

import loadbalancer
import predictor
import probe
import realserver
import serverfarm
import virtualserver
import sticky

logger = logging.getLogger(__name__)


class Balancer():
    def __init__(self, conf):

        """ This member contains LoadBalancer object """
        self.lb = None
        self.sf = None
        self.rs = []
        self.probes = []
        self.vips = []
        self.conf = conf
        self.store = balancer.storage.storage.Storage(conf)

    def parseParams(self, params):

        #if (params.has_key('lb')):
        if 'lb' in params.keys():
            lb = params['lb']
        else:
            lb = loadbalancer.LoadBalancer()
        lb.loadFromDict(params)
        self.lb = lb
        self.lb.status = loadbalancer.LB_BUILD_STATUS
        nodes = params.get('nodes',  None)
        sf = serverfarm.ServerFarm()
        sf.lb_id = lb.id
        sf._predictor = createPredictor(lb.algorithm)
        
        sf._predictor.sf_id = sf.id
        
        sf.name = sf.id
        self.sf = sf
        device_id = params.get('device_id',  None)
        logger.debug("Device ID = %s" % device_id)
        if device_id != None:
            self.lb.device_id = device_id

        """ Parse RServer nodes and attach them to SF """
        if nodes != None:
            for node in nodes:
                rs = realserver.RealServer()
                rs.loadFromDict(node)
                # We need to check if there is already real server  with the same IP deployed
                rd = self.store.getReader()
                try:
                    parent_rs = rd.getRServerByIP(rs.address)
                except openstack.common.exception.NotFound:
                    parent_rs=None
                    pass
                if balancer.common.utils.checkNone(parent_rs):
                    if parent_rs.address != "":
                       rs.parent_id = parent_rs.id
                
                rs.sf_id = sf.id
                rs.name = rs.id
                self.rs.append(rs)
                self.sf._rservers.append(rs)

        probes = params.get("healthMonitor",  None)
        if probes != None:
            for pr in probes:
                prb = createProbe(pr['type'])
                prb.loadFromDict(pr)
                prb.sf_id = sf.id
                prb.name = prb.id
                self.probes.append(prb)
                self.sf._probes.append(prb)

        vips = params.get('virtualIps',  None)

        if vips != None:
            for vip in vips:
                vs = virtualserver.VirtualServer()
                vs.loadFromDict(vip)
                vs.proto = lb.transport
                vs.appProto = lb.protocol
                vs.sf_id = sf.id
                vs.lb_id = lb.id
                vs.name = vs.id
                self.vips.append(vs)

        stic = params.get("sessionPersistence",  None)
        
        if stic != None:
            for st in stic:
                st = createSticky(stic['type'])
                st.loadFromDict(stic)
                st.sf_id = sf.id
                st.name = st.id
                self.sf._sticky.append(st)

    def update(self):
        store = balancer.storage.storage.Storage(self.conf)
        wr = store.getWriter()
        wr.updateObjectInTable(self.lb)
        
        for st in self.sf._sticky:
            wr.updateObjectInTable(st)
        for rs in self.rs:
            wr.updateObjectInTable(rs)

        for pr in self.probes:
            wr.updateObjectInTable(pr)

        for vip in self.vips:
            wr.updateObjectInTable(vip)

    def getLB(self):
        return self.lb

    def savetoDB(self):
        store = balancer.storage.storage.Storage(self.conf)
        wr = store.getWriter()

        wr.writeLoadBalancer(self.lb)
        wr.writeServerFarm(self.sf)
        wr.writePredictor(self.sf._predictor)

        for rs in self.rs:
            wr.writeRServer(rs)

        for pr in self.probes:
            wr.writeProbe(pr)

        for vip in self.vips:
            wr.writeVirtualServer(vip)

        for st in self.sf._sticky:
            wr.writeSticky(st)

    def loadFromDB(self, lb_id):
        store = balancer.storage.storage.Storage(self.conf)
        rd = store.getReader()
        self.lb = rd.getLoadBalancerById(lb_id)
        self.sf = rd.getSFByLBid(lb_id)
        sf_id = self.sf.id
        predictor = rd.getPredictorBySFid(sf_id)
        self.sf._predictor = predictor
        self.rs = rd.getRServersBySFid(sf_id)
        sticks = rd.getStickiesBySFid(sf_id)

        for rs in self.rs:
            self.sf._rservers.append(rs)
        self.probes = rd.getProbesBySFid(sf_id)
        for prob in self.probes:
            self.sf._probes.append(prob)
        self.vips = rd.getVIPsBySFid(sf_id)
        for st in sticks:
            self.sf._sticky.append(st)

    def removeFromDB(self):
        store = balancer.storage.storage.Storage(self.conf)
        dl = store.getDeleter()
        lb_id = self.lb.id
        sf_id = self.sf.id
        dl.deleteLBbyID(lb_id)
        dl.deleteSFbyLBid(lb_id)
        dl.deletePredictorBySFid(sf_id)

        dl.deleteRSsBySFid(sf_id)
        dl.deleteProbesBySFid(sf_id)
        dl.deleteVSsBySFid(sf_id)
        dl.deleteStickiesBySFid(sf_id)

#    def deploy(self,  driver,  context):
#        #Step 1. Deploy server farm
#        if  driver.createServerFarm(context,  self.sf) != "OK":
#            raise exception.OpenstackException
#
#        #Step 2. Create RServers and attach them to SF
#
#        for rs in self.rs:
#            driver.createRServer(context,  rs)
#            driver.addRServerToSF(context,  self.sf,  rs)
#
#        #Step 3. Create probes and attache them to SF
#        for pr in self.probes:
#            driver.createProbe(context,  pr)
#            driver.addProbeToSF(context,  self.sf,  pr)
#        #Step 4. Deploy vip
#        for vip in self.vips:
#            driver.createVIP(context,  vip,  self.sf)


def createProbe(probe_type):
    probeDict = {'DNS': probe.DNSprobe(), 'ECHO TCP': probe.ECHOTCPprobe(),
                'ECHO UDP': probe.ECHOUDPprobe(), 'FINGER': probe.FINGERprobe(),
                'FTP': probe.FTPprobe(), 'HTTPS': probe.HTTPSprobe(),
                'HTTP': probe.HTTPprobe(), 'ICMP': probe.ICMPprobe(),
                'IMAP': probe.IMAPprobe(), 'POP': probe.POPprobe(),
                'RADIUS': probe.RADIUSprobe(), 'RTSP': probe.RTSPprobe(),
                'SCRIPTED': probe.SCRIPTEDprobe(),
                'SIP TCP': probe.SIPTCPprobe(),
                'SIP UDP': probe.SIPUDPprobe(), 'SMTP': probe.SMTPprobe(),
                'SNMP': probe.SNMPprobe(), 'CONNECT': probe.TCPprobe(),
                'TELNET': probe.TELNETprobe(), 'UDP': probe.UDPprobe(),
                'VM': probe.VMprobe()}
    obj = probeDict.get(probe_type,  None)
    if obj == None:
        raise openstack.common.exception.Invalid("Can't create health \
			   monitoring probe of type %s" % probe_type)
    return obj.createSame()


def createPredictor(pr_type):
    predictDict = {'HashAddr': predictor.HashAddrPredictor(),
                  'HashContent': predictor.HashContent(),
                  'HashCookie': predictor.HashCookie(),
                  'HashHeader': predictor.HashHeader(),
                  'HashLayer4': predictor.HashLayer4(),
                  'HashURL': predictor.HashURL(),
                  'LeastBandwidth': predictor.LeastBandwidth(),
                  'LeastConnections': predictor.LeastConn(),
                  'LeastLoaded': predictor.LeastLoaded(),
                  'Response': predictor.Response(),
                  'RoundRobin': predictor.RoundRobin()}

    obj = predictDict.get(pr_type,  None)
    if obj == None:
        raise openstack.common.exception.Invalid("Can't find load balancing \
                                           algorithm with type %s" % pr_type)
    return obj.createSame()


def createSticky(st_type):
    stickyDict = {'http-content': sticky.HTTPContentSticky(), \
                        'http-cookie': sticky.HTTPCookieSticky(), \
                        'http-header': sticky.HTTPHeaderSticky(), \
                        'ip-netmask': sticky.IPNetmaskSticky(), \
                        'layer4-payload': sticky.L4PayloadSticky(), \
                        'rtsp-header': sticky.RTSPHeaderSticky(), \
                        'radius': sticky.RadiusSticky(), \
                        'sip-header': sticky.SIPHeaderSticky(), \
                        'v6prefix': sticky.v6PrefixSticky()}

    obj = stickyDict.get(st_type,  None)
    if obj == None:
        raise openstack.common.exception.Invalid("Can't find load balancing \
                                           algorithm with type %s" % st_type)
    return obj.createSame()
