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

from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject

class Sticky(Serializeable,  UniqueObject):
    def __init__(self):
        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        self.sf_id = ""
        self.name = ""
        self.type = ""
        self.serverFarm = ""
        self.backupServerFarm = ""
        self.aggregateState = None
        self.enableStyckyOnBackupSF = None
        self.replicateOnHAPeer = None
        self.timeout = 1440
        self.timeoutActiveConn = None


class HTTPContentSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.offset = ""
        self.length = ""
        self.beginPattern = ""
        self.endPattern = ""


class HTTPCookieSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.cookieName = ""
        self.enableInsert = None
        self.browserExpire = None
        self.offset = ""
        self.length = ""
        self.secondaryName = ""


class HTTPHeaderSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.headerName = ""
        self.offset = ""
        self.length = ""


class IPNetmaskSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.netmask = ""
        self.ipv6PrefixLength = ""
        self.addressType = "Both"  # Destination, Source


class v6PrefixSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.prefixLength = ""
        self.netmask = ""
        self.addressType = "Both"  # Destination, Source


class L4PayloadSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.offset = ""
        self.length = ""
        self.beginPattern = ""
        self.endPattern = ""
        self.enableStickyForResponse = None


class RadiusSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.radiusTypes = ""  # Radius Calling Id, Radius User Name


class RTSPHeaderSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
        self.offset = ""
        self.length = ""


class SIPHeaderSticky(Sticky):
    def __init__(self):
        Sticky.__init__(self)
