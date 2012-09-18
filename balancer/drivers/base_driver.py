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
from balancer.core import commands


class DeviceRequestContext(commands.RollbackContext):
    def __init__(self, conf, device):
        super(DeviceRequestContext, self).__init__()
        self.conf = conf
        self.device = device


class BaseDriver(object):
    def __init__(self, conf, device_ref):
        self.conf = conf
        self.device_ref = device_ref

    def request_context(self):
        return commands.RollbackContextManager(
                DeviceRequestContext(self.conf, self))

    def checkNone(self, obj):
        if bool(obj):
            if obj != 'None':
                return True
        return False

    def import_certificate_or_key(self):
        """
        not used in API
        """
        raise NotImplementedError

    def create_ssl_proxy(self, ssl_proxy):
        """
        not used in API
        """
        raise NotImplementedError

    def delete_ssl_proxy(self, ssl_proxy):
        """
        not used in API
        """
        raise NotImplementedError

    def add_ssl_proxy_to_virtual_ip(self, vip, ssl_proxy):
        """
        not used in API
        """
        raise NotImplementedError

    def remove_ssl_proxy_from_virtual_ip(self, vip, ssl_proxy):
        """
        not used in API
        """
        raise NotImplementedError

    def create_real_server(self, rserver):
        """
        Create a new real server (node)

        :param rserver: Server \
         - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def delete_real_server(self, rserver):
        """
        Delete real server (node)

        :param rserver: Server \
         - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def activate_real_server(self, serverfarm, rserver):
        """
        Put node into active state (activate)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def activate_real_server_global(self, rserver):
        """
        not used in API. deprecated
        """
        raise NotImplementedError

    def suspend_real_server(self, serverfarm, rserver):
        """
        Put node into inactive state (suspend)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def suspend_real_server_global(self, rserver):
        """
        not used in API. deprecated
        """
        raise NotImplementedError

    def create_probe(self, probe):
        """
        Create probe for health monitoring

        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        :return:
        """
        raise NotImplementedError

    def delete_probe(self, probe):
        """
        Delete probe

        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        :return:
        """
        raise NotImplementedError

    def create_server_farm(self, serverfarm, predictor):
        """
        Create a new loadbalancer (server farm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param predictor: Predictor \
        - see :py:class:`balancer.db.models.Predictor`
        """
        raise NotImplementedError

    def delete_server_farm(self, serverfarm):
        """
        Delete a load balancer (server farm)
        """
        raise NotImplementedError

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        """
        Add a node (rserver) into load balancer (serverfarm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        """
        Delete node (rserver) from the specified loadbalancer (serverfarm)

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param rserver: Server \
        - see :py:class:`balancer.db.models.Server`
        """
        raise NotImplementedError

    def add_probe_to_server_farm(self, serverfarm, probe):
        """
        Add a probe into server farm

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        """
        raise NotImplementedError

    def delete_probe_from_server_farm(self, serverfarm, probe):
        """
        Delete probe from server farm

        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        :param probe: Probe \
        - see :py:class:`balancer.db.models.Probe`
        """
        raise NotImplementedError

    def create_stickiness(self, sticky):
        """
        Create a new stickiness object

        :param sticky: Sticky \
         - see :py:class:`balancer.db.models.Sticky`
        """
        raise NotImplementedError

    def delete_stickiness(self, sticky):
        """
        Delete a stickiness object

        :param sticky: Sticky \
         - see :py:class:`balancer.db.models.Sticky`
        """
        raise NotImplementedError

    def create_virtual_ip(self, vip, serverfarm):
        """
        Create a new vip (virtual IP)

        :param virtualserver: VirtualServer \
        - see :py:class:`balancer.db.models.VirtualServer`
        :param serverfarm: ServerFarm \
        - see :py:class:`balancer.db.models.ServerFarm`
        """
        raise NotImplementedError

    def delete_virtual_ip(self, vip):
        """
        Delete vip from loadbalancer

        :param virtualserver: VirtualServer \
        - see :py:class:`balancer.db.models.VirtualServer`
        """
        raise NotImplementedError

    def get_statistics(self, serverfarm, rserver):
        raise NotImplementedError

    def get_capabilities(self):
        return {}


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
