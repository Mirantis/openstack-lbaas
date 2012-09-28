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

from balancer.drivers.base_driver import BaseDriver

logger = logging.getLogger(__name__)


class DummyDriver(BaseDriver):
    def import_certificate_or_key(self):
        logger.debug("Called DummyDriver(%r).import_certificate_or_key().",
                     self.device_ref['id'])

    def create_ssl_proxy(self, ssl_proxy):
        logger.debug("Called DummyDriver(%r).create_ssl_proxy(%r).",
                     self.device_ref['id'], ssl_proxy)

    def delete_ssl_proxy(self, ssl_proxy):
        logger.debug("Called DummyDriver(%r).delete_ssl_proxy(%r).",
                     self.device_ref['id'], ssl_proxy)

    def add_ssl_proxy_to_virtual_ip(self, vip, ssl_proxy):
        logger.debug("Called DummyDriver(%r)."
                     "add_ssl_proxy_to_virtual_ip(%r, %r).",
                     self.device_ref['id'], vip, ssl_proxy)

    def remove_ssl_proxy_from_virtual_ip(self, vip, ssl_proxy):
        logger.debug("Called DummyDriver(%r)."
                     "remove_ssl_proxy_from_virtual_ip(%r, %r).",
                     self.device_ref['id'], vip, ssl_proxy)

    def create_real_server(self, rserver):
        logger.debug("Called DummyDriver(%r).create_real_server(%r).",
                     self.device_ref['id'], rserver)

    def delete_real_server(self, rserver):
        logger.debug("Called DummyDriver(%r).delete_real_server(%r).",
                     self.device_ref['id'], rserver)

    def activate_real_server(self, serverfarm, rserver):
        logger.debug("Called DummyDriver(%r).activate_real_server(%r, %r).",
                     self.device_ref['id'], serverfarm, rserver)

    def activate_real_server_global(self, rserver):
        logger.debug("Called DummyDriver(%r).activate_real_server_global(%r).",
                     self.device_ref['id'], rserver)

    def suspend_real_server(self, serverfarm, rserver):
        logger.debug("Called DummyDriver(%r).suspend_real_server(%r, %r).",
                     self.device_ref['id'], serverfarm, rserver)

    def suspend_real_server_global(self, rserver):
        logger.debug("Called DummyDriver(%r).suspend_real_server_global(%r).",
                     self.device_ref['id'], rserver)

    def create_probe(self, probe):
        logger.debug("Called DummyDriver(%r).create_probe(%r).",
                     self.device_ref['id'], probe)

    def delete_probe(self, probe):
        logger.debug("Called DummyDriver(%r).delete_probe(%r).",
                     self.device_ref['id'], probe)

    def create_server_farm(self, serverfarm, predictor):
        logger.debug("Called DummyDriver(%r).create_server_farm(%r).",
                     self.device_ref['id'], serverfarm)

    def delete_server_farm(self, serverfarm):
        logger.debug("Called DummyDriver(%r).delete_server_farm(%r).",
                     self.device_ref['id'], serverfarm)

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        logger.debug("Called DummyDriver(%r)."
                     "add_real_server_to_server_farm(%r, %r).",
                     self.device_ref['id'], serverfarm, rserver)

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        logger.debug("Called DummyDriver(%r)."
                     "delete_real_server_from_server_farm(%r, %r).",
                     self.device_ref['id'], serverfarm, rserver)

    def add_probe_to_server_farm(self, serverfarm, probe):
        logger.debug("Called DummyDriver(%r)."
                     "add_probe_to_server_farm(%r, %r).",
                     self.device_ref['id'], serverfarm, probe)

    def delete_probe_from_server_farm(self, serverfarm, probe):
        logger.debug("Called DummyDriver(%r)."
                     "delete_probe_from_server_farm(%r, %r).",
                     self.device_ref['id'], serverfarm, probe)

    def create_stickiness(self, sticky):
        logger.debug("Called DummyDriver(%r).create_stickiness(%r).",
                     self.device_ref['id'], sticky)

    def delete_stickiness(self, sticky):
        logger.debug("Called DummyDriver(%r).delete_stickiness(%r).",
                     self.device_ref['id'], sticky)

    def create_virtual_ip(self, vip, serverfarm):
        logger.debug("Called DummyDriver(%r).create_virtual_ip(%r, %r).",
                     self.device_ref['id'], vip, serverfarm)

    def delete_virtual_ip(self, vip):
        logger.debug("Called DummyDriver(%r).delete_virtual_ip(%r).",
                     self.device_ref['id'], vip)

    def get_statistics(self, serverfarm, rserver):
        logger.debug("Called DummyDriver(%r).get_statistics(%r, %r).",
                     self.device_ref['id'], serverfarm, rserver)
