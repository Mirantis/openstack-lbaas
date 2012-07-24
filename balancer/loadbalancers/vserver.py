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
import openstack.common.exception

from balancer.db import api as db_api
from balancer import exception
from balancer.core import lb_status


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

    def parseParams(self, params):
        obj_dict = params.copy()
        nodes_list = obj_dict.pop('nodes', [])
        probes_list = obj_dict.get('healthMonitor', [])
        vips_list = obj_dict.get('virtualIps', [])
        stic = obj_dict.get('sessionPersistence', [])

        try:
            lb = obj_dict.pop('lb')
        except KeyError:
            lb_ref = db_api.loadbalancer_pack_extra(obj_dict)
        else:
            lb_ref = db_api.loadbalancer_pack_extra(obj_dict)
            lb_ref['id'] = lb['id']
            lb_ref['tenant_id'] = lb['tenant_id']
            lb_ref['created_at'] = lb['created_at']
            lb_ref['updated_at'] = lb['updated_at']

        lb_ref['status'] = lb_status.BUILD
        self.lb = lb_ref

        sf_ref = db_api.serverfarm_pack_extra({})
        self.sf = sf_ref
        self.sf._rservers = []
        self.sf._probes = []
        self.sf._sticky = []

        predictor_ref = db_api.predictor_pack_extra({})
        self.sf._predictor = predictor_ref

        """ Parse RServer nodes and attach them to SF """
        for node in nodes_list:
            rs_ref = db_api.server_pack_extra(node)
            # We need to check if there is already real server with the
            # same IP deployed
            try:
                parent_ref = db_api.server_get_by_address_on_device(self.conf,
                                                        rs_ref['address'],
                                                        lb_ref['device_id'])
            except exception.ServerNotFound:
                pass
            else:
                if parent_ref.get('address') != '':
                    rs_ref['parent_id'] = parent_ref['id']

            self.rs.append(rs_ref)
            self.sf._rservers.append(rs_ref)

        for pr in probes_list:
            probe_ref = db_api.probe_pack_extra(pr)
            self.probes.append(probe_ref)
            self.sf._probes.append(probe_ref)

        for vip in vips_list:
            vs_ref = db_api.virtualserver_pack_extra(vip)
            vs_ref['transport'] = lb_ref['extra'].get('transport')
            vs_ref['appProto'] = lb_ref['protocol']
            self.vips.append(vs_ref)
            self.vips.append(vs_ref)

# NOTE(ash): broken
#        if stic != None:
#            for st in stic:
#                st = createSticky(stic['type'])
#                st.loadFromDict(stic)
#                st.sf_id = sf.id
#                st.name = st.id
#                self.sf._sticky.append(st)

    def update(self):
        db_api.loadbalancer_update(self.conf, self.lb['id'], self.lb)
        for st in self.sf._sticky:
            db_api.sticky_update(self.conf, st['id'], st)
        for rs in self.rs:
            db_api.server_update(self.conf, rs['id'], rs)
        for pr in self.probes:
            db_api.probe_update(self.conf, pr['id'], pr)
        for vip in self.vips:
            db_api.virtualserver_update(self.conf, vip['id'], vip)

    def getLB(self):
        return self.lb

    def savetoDB(self):
        try:
            lb_ref = db_api.loadbalancer_update(self.conf, self.lb['id'],
                                                self.lb)
        except exception.LoadBalancerNotFound:
            lb_ref = db_api.loadbalancer_create(self.conf, self.lb)

        self.sf['lb_id'] = lb_ref['id']
        try:
            sf_ref = db_api.serverfarm_update(self.conf, self.sf['id'],
                                              self.sf)
        except exception.ServerFarmNotFound:
            sf_ref = db_api.serverfarm_create(self.conf, self.sf)

        self.sf._predictor['sf_id'] = sf_ref['id']
        try:
            db_api.predictor_update(self.conf, self.sf._predictor['id'],
                                    self.sf._predictor)
        except exception.PredictorNotFound:
            db_api.predictor_create(self.conf, self.sf._predictor)

        stickies = self.sf._sticky
        vips = []

        self.sf = sf_ref
        self.sf._rservers = []
        self.sf._probes = []
        self.sf._sticky = []

        for rs in self.rs:
            rs['sf_id'] = sf_ref['id']
            try:
                rs_ref = db_api.server_update(self.conf, rs['id'], rs)
            except exception.ServerNotFound:
                rs_ref = db_api.server_create(self.conf, rs)
            self.sf._rservers.append(rs_ref)

        for pr in self.probes:
            pr['sf_id'] = sf_ref['id']
            try:
                pr_ref = db_api.probe_update(self.conf, pr['id'], pr)
            except exception.ProbeNotFound:
                pr_ref = db_api.probe_create(self.conf, pr)
            self.sf._probes.append(pr_ref)

        for vip in self.vips:
            vip['sf_id'] = sf_ref['id']
            vip['lb_id'] = lb_ref['id']
            try:
                vip_ref = db_api.virtualserver_update(self.conf, vip['id'],
                                                      vip)
            except exception.VirtualServerNotFound:
                vip_ref = db_api.virtualserver_create(self.conf, vip)
            vips.append(vip_ref)

        for st in stickies:
            st['sf_id'] = sf_ref['id']
            try:
                st_ref = db_api.sticky_update(self.conf, st['id'], st)
            except exception.StickyNotFound:
                st_ref = db_api.sticky_create(self.conf, st)
            self.sf._sticky.append(st_ref)

        self.rs = self.sf._rservers
        self.probes = self.sf._probes
        self.vips = vips

    def loadFromDB(self, lb_id):
        self.lb = db_api.loadbalancer_get(self.conf, lb_id)
        self.sf = db_api.serverfarm_get_all_by_lb_id(self.conf, lb_id)[0]
        sf_id = self.sf['id']

        self.vips = db_api.virtualserver_get_all_by_sf_id(self.conf, sf_id)

        predictor = db_api.predictor_get_all_by_sf_id(self.conf, sf_id)[0]
        self.sf._predictor = predictor

        self.rs = db_api.server_get_all_by_sf_id(self.conf, sf_id)
        self.sf._rservers = []
        for rs in self.rs:
            self.sf._rservers.append(rs)

        self.probes = db_api.probe_get_all_by_sf_id(self.conf, sf_id)
        self.sf._probes = []
        for prob in self.probes:
            self.sf._probes.append(prob)

        sticks = db_api.sticky_get_all_by_sf_id(self.conf, sf_id)
        self.sf._sticky = []
        for st in sticks:
            self.sf._sticky.append(st)

    def removeFromDB(self):
        lb_id = self.lb['id']
        sf_id = self.sf['id']
        db_api.loadbalancer_destroy(self.conf, lb_id)
        db_api.serverfarm_destroy(self.conf, sf_id)
        db_api.predictor_destroy_by_sf_id(self.conf, sf_id)
        db_api.server_destroy_by_sf_id(self.conf, sf_id)
        db_api.probe_destroy_by_sf_id(self.conf, sf_id)
        db_api.virtualserver_destroy_by_sf_id(self.conf, sf_id)
        db_api.sticky_destroy_by_sf_id(self.conf, sf_id)


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
