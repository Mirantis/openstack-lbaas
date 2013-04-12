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

from balancer.drivers import base_driver
from remote_control import *
from config_manager import *


LOG = logging.getLogger(__name__)

ALGORITHMS_MAPPING = {
    'ROUND_ROBIN': 'roundrobin',
    'LEAST_CONNECTION': 'leastconn',
    'HASH_SOURCE': 'source',
    'HASH_URI': 'uri',
    'STATIC_RR': 'static-rr',
}


class HaproxyDriver(base_driver.BaseDriver):
    """
    This is the driver for HAProxy loadbalancer (http://haproxy.1wt.eu/)
    """

    algorithms = ALGORITHMS_MAPPING
    default_algorithm = ALGORITHMS_MAPPING['ROUND_ROBIN']

    def __init__(self, conf, device_ref):
        super(HaproxyDriver, self).__init__(conf, device_ref)

        self._remote_ctrl = RemoteControl(conf, device_ref)
        self.remote_socket = RemoteSocketOperation(device_ref,
                                                   self._remote_ctrl)
        self.remote_interface = RemoteInterface(device_ref, self._remote_ctrl)
        self.remote_service = RemoteService(self._remote_ctrl)
        self.config_manager = ConfigManager(device_ref, self._remote_ctrl)

    def request_context(self):
        mgr = super(HaproxyDriver, self).request_context()
        mgr.context.add_rollback(self.finalize_config)
        return mgr

    def add_probe_to_server_farm(self, serverfarm, probe):
        """
        Add a probe into server farm

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        """
        probe_type = probe['type'].lower()
        if probe_type not in ('http', 'https', 'tcp', 'connect'):
            LOG.debug('unsupported probe type %s, exit',
                         probe_type)
            return

        backend = HaproxyBackend(serverfarm['id'])

        new_lines = []
        if probe_type == 'http':
            option = 'option httpchk'
            method = (probe.get('extra') or {}).get('method')
            option = option + ' ' + (method if method else 'GET')

            HTTPurl = (probe.get('extra') or {}).get('path')
            option = option + ' ' + (HTTPurl if HTTPurl else '/')

            new_lines.append(option)

        # TODO: add handling of 'expected' field
        # from probe ('http-check expect ...')
        elif probe_type == 'tcp' or probe_type == 'connect':
            new_lines.append('option httpchk')
        elif probe_type == 'https':
            new_lines.append('option ssl-hello-chk')

        if new_lines:
            self.config_manager.add_lines_to_block(backend, new_lines)

    def delete_probe_from_server_farm(self, serverfarm, probe):
        """
        Delete probe from server farm

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        """
        backend = HaproxyBackend(serverfarm['id'])

        probe_type = probe['type'].lower()
        del_lines = []
        if probe_type in ('http', 'tcp', 'connect'):
            del_lines = ['option httpchk', 'http-check expect']
        elif probe_type == 'https':
            del_lines = ['option ssl-hello-chk', ]

        if del_lines:
            self.config_manager.del_lines_from_block(backend, del_lines)

    # For compatibility with drivers for other devices
    def create_real_server(self, rserver):
        pass

    def delete_real_server(self, rserver):
        pass

    def create_probe(self, probe):
        pass

    def delete_probe(self, probe):
        pass

    def create_stickiness(self, sticky):
        backend = HaproxyBackend(sticky['sf_id'])
        sticky_type = sticky['type'].lower()
        extra = sticky.get('extra') or {}
        new_lines = []
        if sticky_type == 'http-cookie':
            option = "appsession %s len %s timeout %s request-learn" % (
                    extra['cookie'],
                    extra.get('length', 16),
                    extra.get('timeout', '1h'))
            new_lines.append(option)
        else:
            LOG.error('Unsupported sticky type %s', sticky_type)
            return
        if new_lines:
            self.config_manager.add_lines_to_block(backend, new_lines)

    def delete_stickiness(self, sticky):
        backend = HaproxyBackend(sticky['sf_id'])
        sticky_type = sticky['type'].lower()
        del_lines = []
        if sticky_type == 'http-cookie':
            del_lines.append('appsession')

        if del_lines:
            self.config_manager.del_lines_from_block(backend, del_lines)

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        """
        Add a node (rserver) into load balancer (serverfarm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        haproxy_rserver = HaproxyRserver(rserver)
        LOG.debug('Creating rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, serverfarm['id']))

        self.config_manager.add_rserver(serverfarm['id'],
                                        haproxy_rserver)

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        """
        Delete node (rserver) from the specified loadbalancer (serverfarm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        haproxy_rserver = HaproxyRserver(rserver)
        #Modify remote config file, check and restart remote haproxy
        LOG.debug('Deleting rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, serverfarm['id']))

        self.config_manager.delete_rserver(serverfarm['id'],
                                           haproxy_rserver.name)

    def create_virtual_ip(self, virtualserver, serverfarm):
        """
        Create a new vip (virtual IP)

        :param virtualserver: VirtualServer \
        - see :py:class:`balancer.db.models.VirtualServer`
        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        """
        if not bool(virtualserver['id']):
            LOG.error('Virtualserver name is empty')
            return
        frontend = HaproxyFronted(virtualserver)
        backend = HaproxyBackend(serverfarm['id'])
        LOG.debug('Create VIP %s' % backend.name)
        self.remote_interface.add_ip(frontend)
        self.config_manager.add_frontend(frontend,
                                         backend)

    def delete_virtual_ip(self, virtualserver):
        """
        Delete vip from loadbalancer

        :param virtualserver: VirtualServer \
        - see :py:class:`balancer.db.models.VirtualServer`
        """
        LOG.debug('Delete VIP')
        if not bool(virtualserver['id']):
            LOG.error('Virtualserver name is empty')
            return
        frontend = HaproxyFronted(virtualserver)
        #Check ip for using in the another frontend
        if not (self.config_manager.
                find_string_in_any_block(frontend.bind_address,
                                         'frontend')):
            LOG.debug('ip %s is not used in any '
                         'frontend, deleting it from remote interface' %
                         frontend.bind_address)
            self.remote_interface.del_ip(frontend)
        self.config_manager.delete_block(frontend)

    def get_statistics(self, serverfarm, rserver):
        # TODO: Need to check work of this function with real device
        out = self.remote_socket.get_statistics(serverfarm['id'],
                                                rserver['id'])
        statistics = {}
        if out:
            status_line = out.split(",")
            stat_count = len(status_line)
            statistics['weight'] = status_line[18] if stat_count > 18 else ''
            statistics['state'] = status_line[17] if stat_count > 17 else ''
            statistics['connCurrent'] = (status_line[4] if stat_count > 4
                                         else '')
            statistics['connTotal'] = status_line[7] if stat_count > 7 else ''
            statistics['connFail'] = status_line[13] if stat_count > 13 else ''
            statistics['connMax'] = status_line[5] if stat_count > 5 else ''
            statistics['connRateLimit'] = (status_line[34] if stat_count > 34
                                           else '')
            statistics['bandwRateLimit'] = (status_line[35] if stat_count > 35
                                            else '')
        return statistics

    def suspend_real_server(self, serverfarm, rserver):
        """
        Put node into inactive state (suspend)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        self._operationWithRServer(serverfarm, rserver, 'suspend')

    def activate_real_server(self, serverfarm, rserver):
        """
        Put node into active state (activate)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        self._operationWithRServer(serverfarm, rserver, 'activate')

    def _operationWithRServer(self, serverfarm, rserver, type_of_operation):
        haproxy_rserver = HaproxyRserver(rserver)
        haproxy_serverfarm = HaproxyBackend(serverfarm['id'])

        if type_of_operation == 'suspend':
            self.config_manager.enable_rserver(haproxy_serverfarm.name,
                                               haproxy_rserver.name, False)
            self.remote_socket.suspend_server(haproxy_serverfarm, rserver)
        elif type_of_operation == 'activate':
            self.config_manager.enable_rserver(haproxy_serverfarm.name,
                                               haproxy_rserver.name, True)
            self.remote_socket.activate_server(haproxy_serverfarm, rserver)

    def create_server_farm(self, serverfarm, predictor):
        """
        Create a new loadbalancer (server farm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param predictor: Predictor \
        - see :py:class:`balancer.db.models.Predictor`
        """
        if not bool(serverfarm['id']):
            LOG.error('Serverfarm name is empty')
            return
        haproxy_serverfarm = HaproxyBackend(serverfarm['id'])

        if isinstance(predictor, list):
            predictor = predictor[0]

        predictor_type = predictor['type'].upper()
        algorithm = self.algorithms.get(predictor_type)
        if algorithm is not None:
            haproxy_serverfarm.balance = algorithm
        else:
            LOG.warning("Unknown algorithm %r, used default value %r.",
                           predictor_type, self.default_algorithm)
            haproxy_serverfarm.balance = self.default_algorithm

        self.config_manager.add_backend(haproxy_serverfarm)

    def delete_server_farm(self, serverfarm):
        """
        Delete a load balancer (server farm)
        """
        if not bool(serverfarm['id']):
            LOG.error('Serverfarm name is empty')
            return
        haproxy_serverfarm = HaproxyBackend(serverfarm['id'])

        self.config_manager.delete_block(haproxy_serverfarm)

    def finalize_config(self, good):
        """
           Store config on the haproxy VM
        """
        if good:
            if self.config_manager.deploy_config():
                if not self.remote_service.restart():
                    LOG.error("Failed to restart haproxy")

        self._remote_ctrl.close()
        return True

    def get_capabilities(self):
        capabilities = {}
        capabilities['algorithms'] = list(self.algorithms.keys())
        capabilities['protocols'] = ['HTTP', 'TCP']
        return capabilities
