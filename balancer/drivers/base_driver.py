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
        raise NotImplementedError

    def create_ssl_proxy(self, ssl_proxy):
        raise NotImplementedError

    def delete_ssl_proxy(self, ssl_proxy):
        raise NotImplementedError

    def add_ssl_proxy_to_virtual_ip(self, vip, ssl_proxy):
        raise NotImplementedError

    def remove_ssl_proxy_from_virtual_ip(self, vip, ssl_proxy):
        raise NotImplementedError

    def create_real_server(self, rserver):
        raise NotImplementedError

    def delete_real_server(self, rserver):
        raise NotImplementedError

    def activate_real_server(self, serverfarm, rserver):
        raise NotImplementedError

    def activate_real_server_global(self, rserver):
        raise NotImplementedError

    def suspend_real_server(self, serverfarm, rserver):
        raise NotImplementedError

    def suspend_real_server_global(self, rserver):
        raise NotImplementedError

    def create_probe(self, probe):
        raise NotImplementedError

    def delete_probe(self, probe):
        raise NotImplementedError

    def create_server_farm(self, serverfarm, predictor):
        raise NotImplementedError

    def delete_server_farm(self, serverfarm):
        raise NotImplementedError

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        raise NotImplementedError

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        raise NotImplementedError

    def add_probe_to_server_farm(self, serverfarm, probe):
        raise NotImplementedError

    def delete_probe_from_server_farm(self, serverfarm, probe):
        raise NotImplementedError

    def create_stickiness(self, sticky):
        raise NotImplementedError

    def delete_stickiness(self, sticky):
        raise NotImplementedError

    def create_virtual_ip(self, vip, serverfarm):
        raise NotImplementedError

    def delete_virtual_ip(self, vip):
        raise NotImplementedError

    def get_statistics(self, serverfarm, rserver):
        raise NotImplementedError
    
    def get_capabilities(self):
        try:
            return self.device_ref['extra'].get('capabilities', [])
        except Exception:
            return []

def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
