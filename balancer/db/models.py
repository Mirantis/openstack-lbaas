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

import datetime
import uuid

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean,
                        DateTime)

from balancer.db.base import Base, DictBase, JsonBlob


def create_uuid():
    return uuid.uuid4().hex


class Device(DictBase, Base):
    """
    Represents a load balancer appliance - a physical device (like F5 BigIP) or
    a software system (such as HAProxy) that can perform load balancing
    functions
    """

    __tablename__ = 'device'
    id = Column(String(32), primary_key=True, default=create_uuid)
    name = Column(String(255))
    type = Column(String(255))
    version = Column(String(255))
    ip = Column(String(255))
    port = Column(Integer)
    user = Column(String(255))
    password = Column(String(255))
    extra = Column(JsonBlob())


class LoadBalancer(DictBase, Base):
    """
    Represents an instance of load balancer appliance for a tenant.
    This is a subsystem behind a virtual IP, i.e. the VIP itself,
    the load balancer instance serving this particular VIP,
    the server farm behind it, and the health probes.

    :var name: string
    :var algorithm: string - load balancing algorithm (e.g. RoundRobin)
    :var protocol: string - load balancing protocol (e.g. TCP, HTTP)
    :var tenant_id: string - OpenStack tenant ID
    :var extra: dictionary - additional attributes
    """

    __tablename__ = 'loadbalancer'
    id = Column(String(32), primary_key=True, default=create_uuid)
    device_id = Column(String(32), ForeignKey('device.id'))
    name = Column(String(255))
    algorithm = Column(String(255))
    protocol = Column(String(255))
    status = Column(String(255))
    tenant_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow,
                        nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow,
                        nullable=False)
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    device = relationship(Device,
                          backref=backref('loadbalancers', order_by=id),
                          uselist=False)


class ServerFarm(DictBase, Base):
    """
    Represents a server farm - a set of servers providing the same backend
    application, managed by a single LB pool.

    :var name: string
    :var extra: dictionary - additional attributes
    """

    __tablename__ = 'serverfarm'
    id = Column(String(32), primary_key=True, default=create_uuid)
    lb_id = Column(String(32), ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    type = Column(String(255))
    status = Column(String(255))
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    loadbalancer = relationship(LoadBalancer,
                                backref=backref('serverfarms', order_by=id),
                                uselist=False)


class VirtualServer(DictBase, Base):
    """
    Represents a Virtual IP - an IP address on which the LB Appliance listens
    to traffic from clients. This is the address seen by the clients.
    Client requests to this IP are routed by the load balancer to backend
    application instances.

    :var name: string
    :var address: string - IP address of VIP to accept traffic
    :var mask: string - network mask
    :var port: string - tcp port
    :var extra: dictionary - additional attributes
    """

    __tablename__ = 'virtualserver'
    id = Column(String(32), primary_key=True, default=create_uuid)
    sf_id = Column(String(32), ForeignKey('serverfarm.id'))
    lb_id = Column(String(32), ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    address = Column(String(255))
    mask = Column(String(255))
    port = Column(String(255))
    status = Column(String(255))
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('virtualservers', order_by=id),
                              uselist=False)
    loadbalancer = relationship(LoadBalancer,
                                backref=backref('loadbalancers', order_by=id),
                                uselist=False)


class Server(DictBase, Base):
    """
    Represents a real server (Node) - a single server providing a single
    backend application instance.

    :var name: string
    :var type: string (not used!)
    :var address: string - IPv4 or IPv6 Address of the node
    :var port: string - application port on which the node listens
    :var weight: integer - weight of the node with respect to other nodes in \
    the same SF. Semantics of weight depends on the particular balancer \
    algorithm
    :var status: string - current health status of the node
    :var extra: dictionary - additional attributes
    """

    __tablename__ = 'server'
    id = Column(String(32), primary_key=True, default=create_uuid)
    sf_id = Column(String(32), ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    address = Column(String(255))
    port = Column(String(255))
    weight = Column(Integer)
    status = Column(String(255))
    parent_id = Column(Integer)
    deployed = Column(String(40))
    vm_id = Column(Integer)
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('servers', order_by=id),
                              uselist=False)


class Probe(DictBase, Base):
    """
    Represents a health monitoring. The probe can be implemented by ICMP ping,
    or more sophisticated way, like sending HTTP GET to specified URL

    :var type: string - type of probe (HTTP, HTTPS, ICMP, CONNECT, etc.) \
    - real set depends on driver support
    :var extra: dictionary - additional attributes
    """

    __tablename__ = 'probe'
    id = Column(String(32), primary_key=True, default=create_uuid)
    sf_id = Column(String(32), ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('probes', order_by=id),
                              uselist=False)


class Sticky(DictBase, Base):
    """
    Represents a persistent session.
    """

    __tablename__ = 'sticky'
    id = Column(String(32), primary_key=True, default=create_uuid)
    sf_id = Column(String(32), ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('stickies', order_by=id),
                              uselist=False)


class Predictor(DictBase, Base):
    """
    Represents an algorithm of selecting server by load balancer.

    :var type: string - the algorithm, e.g. RoundRobin
    """

    __tablename__ = 'predictor'
    id = Column(String(32), primary_key=True, default=create_uuid)
    sf_id = Column(String(32), ForeignKey('serverfarm.id'))
    type = Column(String(255))
    deployed = Column(String(40))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('predictors', order_by=id),
                              uselist=False)


def register_models(engine):
    """Create tables for models."""

    Base.metadata.create_all(engine)
