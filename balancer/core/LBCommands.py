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


import logging
import sys
import threading
import Queue


class BaseCommand(object):
    def __init__(self,  driver):
        self._driver = driver

    @property
    def driver(self):
        return self._driver


class CreateSFCommand(BaseCommand):
    def __init__(self,  driver):
        super(CreateSFCommand,  self).__init__(driver)

    def execute(self, context,   sf):
        createSF(sf)
        self._sf = sf

    def undo(self, context,   params):
        deleteSF()


class CreateRServerCommand(BaseCommand):
    def __init__(self,  driver):
        super(CreateRServerCommand,  self).__init__(driver)

    def execute(self, context,   sf,  node):
        createRServer(sf, node)
        self._sf = sf
        self._node = node

    def undo(self, context,   params):
        deleteRServerFormSF(self._sf,  self._node)


class CreateProbeCommand(BaseCommand):
    def __init__(self,  driver):
        super(CreateProbeCommand,  self).__init__(driver)

    def execute(self, context,   probe):
        createProbe(probe)
        self._probe = probe

    def undo(self, context,   params):
        deleteProbe(self._probe)


class AttachProbeCommand(BaseCommand):
    def __init__(self,  driver):
        super(AttachProbeCommand,  self).__init__(driver)

    def execute(self, context,   sf,  probe):
        attachProbe(sf, probe)
        self._probe = probe
        self._sf = sf

    def undo(self, context,   params):
        deleteProbefromSF(self._sf, self._probe)


class CreateVServerCommand(BaseCommand):
    def __init__(self,  driver):
        super(CreateVServerCommand,  self).__init__(driver)

    def execute(self, context,   sf,  vip):
        createVS(sf, vip)
        self._vip = vip
        self._sf = sf

    def undo(self, context,   params):
        deleteVS(self._sf, self._vip)
