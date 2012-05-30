# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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

from balancer.loadbalancers.loadbalancer import *
from balancer.devices.device import LBDevice
from balancer.core.configuration import Configuration
from balancer.loadbalancers.probe import *
from balancer.loadbalancers.sticky import *
from balancer.loadbalancers.realserver import RealServer
from balancer.loadbalancers.predictor import *
from balancer.loadbalancers.serverfarm import ServerFarm
from balancer.loadbalancers.virtualserver import VirtualServer

from balancer import db
from balancer import exception


logger = logging.getLogger(__name__)


def load_to_old_model(object_ref, inst):
    inst.loadFromDict(object_ref)
    if 'extra' in object_ref and object_ref['extra'] is not None:
        inst.loadFromDict(object_ref['extra'])


def extract_extra(object_ref, inst_dict):
    extra_columns = set(inst_dict) - set(object_ref)
    extra = {}
    for col in extra_columns:
        extra[col] = inst_dict[col]
    return extra or None


def get_db_funcs(obj):
    if isinstance(obj, LoadBalancer):
        return (db.loadbalancer_get, db.loadbalancer_update)
    elif isinstance(obj, ServerFarm):
        return (db.serverfarm_get, db.serverfarm_update)
    elif isinstance(obj,  BasePredictor):
        return (db.predictor_get, db.predictor_update)
    elif isinstance(obj,  RealServer):
        return (db.server_get, db.server_update)
    elif isinstance(obj,  LBDevice):
        return (db.device_get, db.device_update)
    elif isinstance(obj,  VirtualServer):
        return (db.virtualserver_get, db.virtualserver_update)
    elif isinstance(obj, Probe):
        return (db.probe_get, db.probe_update)
    elif isinstance(obj, Sticky):
        return (db.sticky_get, db.sticky_update)


class Reader(object):
    """ Reader class is used for db read opreations"""
    def __init__(self, conf):
        self.conf = conf
        self._probeDict = {'DNS': DNSprobe(), 'ECHO TCP': ECHOTCPprobe(), \
                        'ECHO-UDP': ECHOUDPprobe(), 'FINGER': FINGERprobe(), \
                        'FTP': FTPprobe(), 'HTTPS': HTTPSprobe(), \
                        'HTTP': HTTPprobe(), 'ICMP': ICMPprobe(), \
                        'IMAP': IMAPprobe(), 'POP': POPprobe(), \
                        'RADIUS': RADIUSprobe(), 'RTSP': RTSPprobe(), \
                        'SCRIPTED': SCRIPTEDprobe(), 'SIP TCP': SIPTCPprobe(), \
                        'SIP UDP': SIPUDPprobe(), 'SMTP': SMTPprobe(), \
                        'SNMP': SNMPprobe(), 'CONNECT': TCPprobe(), \
                        'TELNET': TELNETprobe(), 'UDP': UDPprobe(), \
                        'VM': VMprobe()}
        self._predictDict = {'HashAddrPredictor': HashAddrPredictor(), \
                          'HashContent': HashContent(), \
                          'HashCookie': HashCookie(), \
                          'HashHeader': HashHeader(),
                          'HashLayer4': HashLayer4(), 'HashURL': HashURL(), \
                          'LeastBandwidth': LeastBandwidth(), \
                          'LeastConnections': LeastConn(), \
                          'LeastLoaded': LeastLoaded(), \
                          'Response': Response(), 'RoundRobin': RoundRobin()}
        self._stickyDict = {'http-content': HTTPContentSticky(), \
                                    'http-cookie': HTTPCookieSticky(), \
                                    'http-header': HTTPHeaderSticky(), \
                                    'ip-netmask': IPNetmaskSticky(), \
                                    'layer4-payload': L4PayloadSticky(), \
                                    'rtsp-header': RTSPHeaderSticky(), \
                                    'radius': RadiusSticky(), \
                                    'sip-header': SIPHeaderSticky(), \
                                    'v6prefix': v6PrefixSticky()}

    def getLoadBalancers(self, tenant_id):
        lbalancers = []
        lb_refs = db.loadbalancer_get_all_by_project(self.conf, tenant_id)
        for lb_ref in lb_refs:
            lb = LoadBalancer()
            load_to_old_model(lb_ref, lb)
            lbalancers.append(lb)
        return lbalancers

    def getLoadBalancerById(self, id):
        lb_ref = db.loadbalancer_get(self.conf, id)
        lb = LoadBalancer()
        load_to_old_model(lb_ref, lb)
        return lb

    def getDeviceById(self, id):
        device_ref = db.device_get(self.conf, id)
        device = LBDevice()
        load_to_old_model(device_ref, device)
        return device

    def getDeviceByLBid(self, id):
        lb = self.getLoadBalancerById(id)
        device = self.getDeviceById(lb.device_id)
        return device

    def getDevices(self):
        devices = []
        device_refs = db.device_get_all(self.conf)
        for device_ref in device_refs:
            device = LBDevice()
            load_to_old_model(device_ref, device)
            devices.append(device)
        return devices

    def getProbeById(self, id):
        probe_ref = db.probe_get(self.conf, id)
        prb = self._probeDict[probe_ref['type']].createSame()
        load_to_old_model(probe_ref, prb)
        return prb

    def getProbes(self):
        probes = []
        probe_refs = db.probe_get_all(self.conf)
        for probe_ref in probe_refs:
            prb = self._probeDict[probe_ref['type']].createSame()
            load_to_old_model(probe_ref, prb)
            probes.append(prb)
        return probes


    def getStickyById(self, id):
        sticky_ref = db.sticky_get(self.conf, id)
        st = self._stickyDict[sticky_ref['type']].createSame()
        load_to_old_model(sticky_ref, st)
        return st

    def getStickies(self):
        stickies = []
        sticky_refs = db.sticky_get_all(self.conf)
        for sticky_ref in sticky_refs:
            st = self._stickyDict[sticky_ref['type']].createSame()
            load_to_old_model(sticky_ref, st)
            stickies.append(st)
        return stickies

    def getRServerById(self, id):
        server_ref = db.server_get_by_uuid(self.conf, id)
        rs = RealServer()
        load_to_old_model(server_ref, rs)
        return rs

    def getRServerByIP(self, ip):
        server_address = ip
        if server_address is None:
            raise exception.NotFound("Empty device ip.")
        server_ref = db.server_get_by_address(self.conf, server_address)
        rs = RealServer()
        load_to_old_model(server_ref, rs)
        return rs

    def getRServersByParentID(self, id):
        if id is None:
            raise exception.NotFound("Empty rservers parent id.")
        parent_ref = db.server_get(self.conf, id)
        server_refs = db.server_get_all_by_parent_id(self.conf,
                                                     parent_ref['id'])
        servers = []
        for server_ref in server_refs:
            rs = RealServer()
            load_to_old_model(server_ref, rs)
            servers.append(rs)
        return servers

    def getRServers(self):
        servers = []
        server_refs = db.server_get_all(self.conf)
        for server_ref in server_refs:
            rs = RealServer()
            load_to_old_model(server_ref, rs)
            servers.append(rs)
        return servers

    def getLoadBalancersByVMid(self, vm_id, tenant_id):
        lbalancers = []
        lb_refs = db.loadbalancer_get_all_by_vm_id(self.conf, vm_id, tenant_id)
        for lb_ref in lb_refs:
            lb = LoadBalancer()
            load_to_old_model(lb_ref, lb)
            lbalancers.append(lb)
        return lbalancers

    def getSFByLBid(self,  id):
        lb_ref = db.loadbalancer_get(self.conf, id)
        sf_refs = db.serverfarm_get_all_by_lb_id(self.conf, lb_ref['id'])
        sf = ServerFarm()
        if sf_refs:
            load_to_old_model(sf_refs[0], sf)
        return sf

    def getRServersBySFid(self, id):
        servers = []
        server_refs = db.server_get_all_by_sf_id(self.conf, id)
        for server_ref in server_refs:
            rs = RealServer()
            load_to_old_model(server_ref, rs)
            servers.append(rs)
        return servers

    def getStickiesBySFid(self, id):
        sticky_refs = db.sticky_get_all_by_sf_id(self.conf, id)
        stickies = []
        for sticky_ref in sticky_refs:
            st = self._stickyDict[sticky_ref['type']].createSame()
            load_to_old_model(sticky_ref, st)
            stickies.append(st)
        return stickies

    def getProbesBySFid(self, id):
        probes = []
        probe_refs = db.probe_get_all_by_sf_id(self.conf, id)
        for probe_ref in probe_refs:
            prb = self._probeDict[probe_ref['type']].createSame()
            load_to_old_model(probe_ref, prb)
            probes.append(prb)
        return probes

    def getPredictorBySFid(self, id):
        predictors = []
        predictor_refs = db.predictor_get_all_by_sf_id(self.conf, id)
        for predictor_ref in predictor_refs:
            pred = self._probeDict[predictor_ref['type']].createSame()
            load_to_old_model(predictor_ref, pred)
            predictors.append(pred)
        return predictors


    def getVIPsBySFid(self, id):
        vservers = []
        vserver_refs = db.virtualverser_get_all_by_sf_id(self.conf, id)
        for vserver_ref in vserver_refs:
            vs = VirtualServer()
            load_to_old_model(vserver_ref, vs)
            vservers.append(vs)
        return vservers


class Writer(object):
    def __init__(self, conf):
        self.conf = conf

    def writeLoadBalancer(self,  lb):
        logger.debug("Saving LoadBalancer instance in DB.")
        lb_dict = lb.convertToDict()
        lb_ref = db.loadbalancer_create(self.conf, lb_dict)
        lb_ref['extra'] = extract_extra(lb_ref, lb_dict)
        db.loadbalancer_update(self.conf, lb_ref['id'], lb_ref)

    def writeDevice(self,  device):
        logger.debug("Saving Device instance in DB.")
        device_dict = device.convertToDict()
        device_ref = db.device_create(self.conf, device_dict)
        device_ref['extra'] = extract_extra(device_ref, device_dict)
        db.device_update(self.conf, device_ref['id'], device_ref)

    def writeProbe(self, prb):
        logger.debug("Saving Probe instance in DB.")
        probe_dict = prb.convertToDict()
        probe_ref = db.probe_create(self.conf, probe_dict)
        probe_ref['extra'] = extract_extra(probe_ref, probe_dict)
        db.probe_update(self.conf, probe_ref['id'], probe_ref)

    def writeSticky(self, st):
        if st == None:
            return
        logger.debug("Saving Sticky instance in DB.")
        sticky_dict = st.convertToDict()
        sticky_ref = db.sticky_create(self.conf, sticky_dict)
        sticky_ref['extra'] = extract_extra(sticky_ref, sticky_dict)
        db.sticky_update(self.conf, sticky_ref['id'], sticky_ref)

    def writeRServer(self, rs):
        logger.debug("Saving RServer instance in DB.")
        server_dict = rs.convertToDict()
        server_ref = db.server_create(self.conf, server_dict)
        server_ref['extra'] = extract_extra(server_ref, server_dict)
        db.server_update(self.conf, server_ref['id'], server_ref)

    def writePredictor(self, prd):
        logger.debug("Saving Predictor instance in DB.")
        predictor_dict = prd.convertToDict()
        predictor_ref = db.predictor_create(self.conf, predictor_dict)
        predictor_ref['extra'] = extract_extra(predictor_ref, predictor_dict)
        db.predictor_update(self.conf, predictor_ref['id'], predictor_ref)

    def writeServerFarm(self, sf):
        logger.debug("Saving ServerFarm instance in DB.")
        serverfarm_dict = sf.convertToDict()
        serverfarm_ref = db.serverfarm_create(self.conf, serverfarm_dict)
        serverfarm_ref['extra'] = extract_extra(serverfarm_ref, serverfarm_dict)
        db.serverfarm_update(self.conf, serverfarm_ref['id'], serverfarm_ref)

    def writeVirtualServer(self, vs):
        logger.debug("Saving VirtualServer instance in DB.")
        virtualserver_dict = vs.convertToDict()
        virtualserver_ref = db.virtualserver_create(self.conf, virtualserver_dict)
        virtualserver_ref['extra'] = extract_extra(virtualserver_ref, virtualserver_dict)
        db.virtualserver_update(self.conf, virtualserver_ref['id'], virtualserver_ref)

    def updateObjectInTable(self, obj):
        (db_get_func, db_update_func) = get_db_funcs(obj)

        obj_dict = obj.convertToDict()
        obj_ref = db_get_func(self.conf, obj_dict['id'])
        obj_ref.update(obj_dict)
        obj_ref['extra'] = extract_extra(obj_ref, obj_dict)
        db_update_func(self.conf, obj_ref['id'], obj_ref)

    def updateDeployed(self, obj, status):
        obj['deployed'] = status
        self.updateObjectInTable(obj)


class Deleter(object):
    def __init__(self, conf):
        self.conf = conf

    def deleteRSbyID(self, id):
        db.server_destroy(self.conf, id)

    def deleteRSsBySFid(self, id):
        server_refs in db.server_get_all_by_sf_id(self.conf, id)
        for server_ref in server_refs:
            self.deleteRSbyID(server_ref['id'])

    def deleteVSbyID(self, id):
        db.virtualserver_destroy(self.conf, id)

    def deleteVSsBySFid(self,  id):
        vserver_refs = db.virtualserver_get_all_by_sf_id(self.conf, id)
        for vserver_ref in vserver_refs:
            self.deleteVSbyID(vserver_ref['id'])

    def deleteProbeByID(self,  id):
        db.probe_destroy(self.conf, id)


    def deleteProbesBySFid(self, id):
        probe_refs = db.probe_get_all_by_sf_id(self.conf, id)
        for probe_ref in probe_refs:
            self.deleteProbeByID(probe_ref['id'])

    def deleteStickyByID(self,  id):
        db.sticky_destroy(self.conf, id)

    def deleteStickiesBySFid(self, id):
        sticky_refs = db.sticky_get_all_by_sf_id(self.conf, id)
        for sticky_ref in sticky_refs:
            self.deleteStickyByID(sticky_ref['id'])


    def deleteLBbyID(self,  id):
        db.loadbalancer_destroy(self.conf, id)

    def deleteDeviceByID(self, id):
        db.device_destroy(self.conf, id)

    def deletePredictorByID(self, id):
        db.predictor_destroy(self.conf, id)

    def deletePredictorBySFid(self, id):
        predictor_refs = db.predictor_get_all_by_sf_id(self.conf, id)
        for predictor_ref in predictor_refs:
            self.deletePredictorByID(predictor_ref['id'])

    def deleteSFbyID(self, id):
        db.serverfarm_destroy(self.conf, id)

    def deleteSFbyLBid(self, id):
        sf_refs = db.serverfarm_get_all_by_lb_id(self.conf, id)
        for sf_ref in sf_refs:
            self.deleteSFbyID(sf_ref['id'])


class Storage(object):
    def __init__(self,  conf):
        self.conf = conf
        self._writer = Writer(self.conf)

    def getReader(self):
        return Reader(self.conf)

    def getWriter(self):
        return self._writer

    def getDeleter(self):
        return Deleter(self.conf)
