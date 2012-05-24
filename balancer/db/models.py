# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
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
"""SQLAlchemy models for balancer data."""

import json
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import TypeDecorator
from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean, Text,
                        DateTime)


Base = declarative_base()


class JsonBlob(TypeDecorator):

    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Device(Base):
    """Represents a load balancer appliance."""

    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(255))
    version = Column(String(255))
    ip = Column(String(255))
    port = Column(Integer)
    user = Column(String(255))
    password = Column(String(255))
    interface = Column(String(255))
    supports_ipv6 = Column(Boolean, default=False) #SPEC UNUSED
    requires_vip_ip = Column(Boolean, default=True) #SPEC UNUSED
    has_acl = Column(Boolean, default=True) #SPEC UNUSED
    supports_vlan = Column(Boolean, default=True) #SPEC UNISED
    vip_vlan = Column(Integer, default=1) #SPEC UNUSED
    localpath = Column(String(255)) #SPEC HAPROXY
    configfilepath = Column(String(255)) #SPEC HAPROCE
    remotepath = Column(String(255)) #SPEC HAPROXY
    concurrent_deploys = Column(Integer, default=2) #SPEC MAYBEALL


class LoadBalancer(Base):
    """Represents an instance of load balancer applience for a tenant."""

    __tablename__ = 'loadbalancer'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device.id'))
    name = Column(String(255))
    algorithm = Column(String(255), default='LEAST_CONNECTIONS')
    protocol = Column(String(255), default='HTTP')
    transport = Column(String(255), default='TCP')
    status = Column(String(255), default='ACTIVE')
    project = Column(String(255))

    device = relationship(Device,
                          backref=backref('loadbalancers', order_by=id),
                          uselist=False)


class ServerFarm(Base):
    """Represents a server farm."""

    __tablename__ = 'serverfarm'
    id = Column(Integer, primary_key=True)
    loadbalancer_id = Column(Integer, ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    type = Column(String(255), default='host')
    status = Column(String(255), default='ACTIVE')
    description = Column(String(255))
    fail_action = Column(String(255)) #SPEC ACE
    inband_health_check = Column(String(255)) #SPEC ACE
    conn_failure_thresh_count = Column(Integer) #SPEC ACE
    reset_timeout = Column(Integer) #SPEC ACE
    resume_service = Column(String(255)) #SPEC ACE
    transparent = Column(Boolean, default=False) #SPEC ACE
    dynamic_workload_scale = Column(String(255)) #SPEC ACE
    vm_probe_name = Column(String(255)) #SPEC UNUSED
    fail_on_all = Column(Boolean, default=False) #SPEC ACE
    partial_thresh_percentage = Column(Integer) #SPEC ACE
    back_nservice = Column(Integer) #SPEC ACE
    retcode_map = Column(String(255)) #SPEC UNUSED

    loadbalancer = relationship(LoadBalancer,
                                backref=backref('serverfarms', order_by=id),
                                uselist=False)


class VirtualServer(Base):
    """Represents a Virtual IP."""

    __tablename__ = 'virtualserver'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    loadbalancer_id = Column(Integer, ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    ip_version = Column(String(255), default='IPv4')
    address = Column(String(255))
    mask = Column(String(255), default='255.255.255.255')
    proto = Column(String(255), default='TCP')
    app_proto = Column(String(255))
    port = Column(String(255), default='any')
    all_vlans = Column(Boolean, default=False)
    vlans = Column(String(255))
    icmp_reply = Column(Boolean, default=False)
    status = Column(String(255), default='inservice')

    serverfarm = relationship(ServerFarm,
                              backref=backref('virtualservers', order_by=id),
                              uselist=False)
    loadbalancer = relationship(LoadBalancer,
                                backref=backref('loadbalancers', order_by=id),
                                uselist=False)


class Server(Base):
    """Represents a real server."""

    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255), default='Host')
    description = Column(String(255))
    ip_version = Column(String(255), default='IPv4')
    address = Column(String(255))
    port = Column(String(255), default='any')
    min_conn = Column(Integer, default=40000)
    max_conn = Column(Integer, default=40000)
    weight = Column(Integer, default=8)
    rate_bandwidth = Column(Integer)
    rate_connection = Column(Integer)
    status = Column(String(255))
    webhost_redir = Column(String(255)) #SPEC ACE
    redir_code = Column(Integer) #SPEC ACE
    state = Column(String(255), default='inservice') #SPEC ACE,ANM
    opstate = Column(String(255), default='inservice') #SPEC UNUSED
    fail_on_all = Column(Boolean, default=False) #SPEC ACE
    backup_server = Column(String(255)) #SPEC ACE
    backup_port = Column(String(255)) #SPEC ACE
    cookie_str = Column(String(255)) #SPEC ACE
    parent_id = Column(Integer, ForeignKey('server.id')) #SPEC HACK

    serverfarm = relationship(ServerFarm,
                              backref=backref('servers', order_by=id),
                              uselist=False)

class Probe(Base):
    """Represents a health monitoring."""

    __tablename__ = 'probe'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    port = Column(Integer)
    probe_interval = Column(Integer, default=15) #SPEC ACE
    pass_detect_interval = Column(Integer, default=60) #SPEC ACE
    pass_detect_count = Column(Integer, default=3) #SPEC ACE
    fail_detect = Column(Integer, default=3) #SPEC ACE
    receive_timeout = Column(Integer, default=10) #SPEC ACE
    is_routed = Column(Boolean, default=False) #SPEC ACE
    delay = Column(Integer, default=15) #SPEC UNUSED
    deactivation_attempts = Column(Integer, default=3) #SPEC UNUSED
    timeout = Column(Integer, default=60) #SPEC UNUSED

    serverfarm = relationship(ServerFarm,
                              backref=backref('probes', order_by=id),
                              uselist=False)


class Sticky(Base):
    """Represents a persistent session."""

    __tablename__ = 'sticky'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    extra = Column(JsonBlob())
#    timeout = Column(Integer, default=1440) #SPEC ACE
#    replicate = Column(Boolean, default=False) #SPEC ACE

    serverfarm = relationship(ServerFarm,
                              backref=backref('stickies', order_by=id),
                              uselist=False)


    @classmethod
    def from_dict(cls, sticky_dict):
        sticky = {}
        extra = {}
        for key, value in sticky_dict.iteritems():
            if key not in ['id', 'serverfarm_id', 'name', 'type', 'extra']:
                extra[key] = value
            elif key != 'extra':
                sticky[key] = value
        sticky['extra'] = extra
        return sticky

    def to_dict(self):
        extra_copy = self.extra.copy()
        extra_copy['id'] = self.id
        extra_copy['name'] = self.name
        extra_copy['type'] = self.type
        extra_copy['serverfarm_id'] = self.serverfarm_id
        return extra_copy


class Predictor(Base):
    """Represents a algorithm of selecting server."""

    __tablename__ = 'predictor'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    type = Column(String(255))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('predictors', order_by=id),
                              uselist=False)

    @classmethod
    def from_dict(cls, predictor_dict):
        predictor = {}
        extra = {}
        for key, value in predictor_dict.copy().iteritems():
            if key not in ['id', 'serverfarm_id', 'type', 'extra']:
                extra[key] = value
            elif key != 'extra':
                predictor[key] = value
        predictor['extra'] = extra
        return predictor

    def to_dict(self):
        extra_copy = self.extra.copy()
        extra_copy['id'] = self.id
        extra_copy['type'] = self.type
        extra_copy['serverfarm_id'] = self.serverfarm_id
        return extra_copy


def register_models(engine):
    """Create tables for models."""

    Base.metadata.create_all(engine)
