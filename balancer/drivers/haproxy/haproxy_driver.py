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
}


class HaproxyDriver(base_driver.BaseDriver):
    """
    This is the driver for HAProxy loadbalancer (http://haproxy.1wt.eu/)
    """

    algorithms = ALGORITHMS_MAPPING
    default_algorithm = ALGORITHMS_MAPPING['ROUND_ROBIN']

    def __init__(self, conf, device_ref):
        super(HaproxyDriver, self).__init__(conf, device_ref)

        self._remote_ctrl = RemoteControl(device_ref)
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

        :param serverfarm: ServerFarm
        :param probe: Probe
        """
        probe_type = probe['type'].lower()
        if probe_type not in ('http', 'https', 'tcp', 'connect'):
            LOG.debug('unsupported probe type %s, exit',
                         probe_type)
            return

        backend = HaproxyBackend()
        backend.name = serverfarm['id']

        new_lines = []
        if probe_type == 'http':
            option = 'option httpchk'
            method = probe.get('method')
            option = option + ' ' + (method if method else 'GET')

            HTTPurl = probe.get('path', '')
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

        :param serverfarm: ServerFarm
        :param probe: Probe
        """
        backend = HaproxyBackend()
        backend.name = serverfarm['id']

        probe_type = probe['type'].lower()
        del_lines = []
        if probe_type in ('http', 'tcp', 'connect'):
            del_lines = ['option httpchk', 'http-check expect']
        elif probe_type == 'https':
            del_lines = ['option ssl-hello-chk', ]

        if del_lines:
            self.config_manager.del_lines_from_block(backend, del_lines)

    '''
        For compatibility with drivers for other devices
    '''
    def create_real_server(self, rserver):
        pass

    def delete_real_server(self, rserver):
        pass

    def create_probe(self, probe):
        pass

    def delete_probe(self, probe):
        pass

    def create_stickiness(self, sticky):
        pass

    def delete_stickiness(self, sticky):
        pass

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        """
        Add a node (rserver) into load balancer (serverfarm)

        :param serverfarm: ServerFarm
        :param rserver: Server
        """
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        haproxy_rserver.weight = rserver.get('weight') or 1
        haproxy_rserver.address = rserver['address']
        haproxy_rserver.port = rserver.get('port') or 0
        if rserver.get('extra'):
            haproxy_rserver.maxconn = rserver['extra'].get('maxCon') or 10000
        #Modify remote config file, check and restart remote haproxy
        LOG.debug('Creating rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, haproxy_serverfarm.name))

        self.config_manager.add_rserver(haproxy_serverfarm.name,
                                        haproxy_rserver)

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        """
        Delete node (rserver) from the specified loadbalancer (serverfarm)

        :param serverfarm: ServerFram
        :param rserver: Server
        """
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        #Modify remote config file, check and restart remote haproxy
        LOG.debug('Deleting rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, haproxy_serverfarm.name))

        self.config_manager.delete_rserver(haproxy_serverfarm.name,
                                           haproxy_rserver.name)

    def create_virtual_ip(self, virtualserver, serverfarm):
        """
        Create a new vip (virtual IP).

        :param virtualserver: VirtualServer
        :param serverfarm: ServerFarm
        """
        if not bool(virtualserver['id']):
            LOG.error('Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver['id']
        haproxy_virtualserver.bind_address = virtualserver['address']
        haproxy_virtualserver.bind_port = virtualserver.get('port') or 0
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        LOG.debug('Create VIP %s' % haproxy_serverfarm.name)
        self.remote_interface.add_ip(haproxy_virtualserver)

        self.config_manager.add_frontend(haproxy_virtualserver,
                                         haproxy_serverfarm)

    def delete_virtual_ip(self, virtualserver):
        """
        Delete vip from loadbalancer

        :param virtualserver: VirtualServer
        """
        LOG.debug('Delete VIP')
        if not bool(virtualserver['id']):
            LOG.error('Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver['id']
        haproxy_virtualserver.bind_address = virtualserver['address']
        #Check ip for using in the another frontend
        if not (self.config_manager.
                find_string_in_any_block(haproxy_virtualserver.bind_address,
                                         'frontend')):
            LOG.debug('ip %s is not used in any '
                         'frontend, deleting it from remote interface' %
                         haproxy_virtualserver.bind_address)
            self.remote_interface.del_ip(haproxy_virtualserver)
        self.config_manager.delete_block(haproxy_virtualserver)

    def get_statistics(self, serverfarm):
        # TODO: Need to check work of this function with real device
        out = self.remote_socket.get_statistics(self.remote_socket,\
                                    serverfarm['id'])
        statistics = {}
        if out:
            status_line = out.split(",")
            stat_count = len(status_line)
            statistics['weight'] = status_line[18] if stat_count > 18 else ''
            statistics['state'] = status_line[17] if stat_count > 17 else ''
            statistics['connCurrent'] = [4] if stat_count > 4 else ''
            statistics['connTotal'] = [7] if stat_count > 7 else ''
            statistics['connFail'] = [13] if stat_count > 13 else ''
            statistics['connMax'] = [5] if stat_count > 5 else ''
            statistics['connRateLimit'] = [34] if stat_count > 34 else ''
            statistics['bandwRateLimit'] = [35] if stat_count > 35 else ''
        return statistics

    def suspend_real_server(self, serverfarm, rserver):
        """
        Put node into inactive state (suspend)

        :param serverfarm: ServerFarm
        :param rserver: Server
        """
        self.operationWithRServer(serverfarm, rserver, 'suspend')

    def activate_real_server(self, serverfarm, rserver):
        """
        Put node into active state (activate)

        :param serverfarm: ServerFarm
        :param rserver: Server
        """
        self.operationWithRServer(serverfarm, rserver, 'activate')

    def operationWithRServer(self, serverfarm, rserver, type_of_operation):
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']

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
        :param serverfarm: ServerFarm
        :param predictor: Predictor
        """
        if not bool(serverfarm['id']):
            LOG.error('Serverfarm name is empty')
            return 'SERVERFARM FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']

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
            return 'SERVER FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']

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
