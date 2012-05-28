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

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean,
                        DateTime)

from balancer.db.base import Base, DictBase, JsonBlob


class Device(DictBase, Base):
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
    extra = Column(JsonBlob())


class LoadBalancer(DictBase, Base):
    """Represents an instance of load balancer applience for a tenant."""

    __tablename__ = 'loadbalancer'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device.id'))
    name = Column(String(255))
    algorithm = Column(String(255))
    protocol = Column(String(255))
    status = Column(String(255))
    project_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow,
                        nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        nullable=False)
    extra = Column(JsonBlob())

    device = relationship(Device,
                          backref=backref('loadbalancers', order_by=id),
                          uselist=False)


class ServerFarm(DictBase, Base):
    """Represents a server farm."""

    __tablename__ = 'serverfarm'
    id = Column(Integer, primary_key=True)
    loadbalancer_id = Column(Integer, ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    type = Column(String(255))
    status = Column(String(255))
    extra = Column(JsonBlob())

    loadbalancer = relationship(LoadBalancer,
                                backref=backref('serverfarms', order_by=id),
                                uselist=False)


class VirtualServer(DictBase, Base):
    """Represents a Virtual IP."""

    __tablename__ = 'virtualserver'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    loadbalancer_id = Column(Integer, ForeignKey('loadbalancer.id'))
    name = Column(String(255))
    ip_version = Column(String(255))
    address = Column(String(255))
    mask = Column(String(255))
    port = Column(String(255))
    status = Column(String(255))

    serverfarm = relationship(ServerFarm,
                              backref=backref('virtualservers', order_by=id),
                              uselist=False)
    loadbalancer = relationship(LoadBalancer,
                                backref=backref('loadbalancers', order_by=id),
                                uselist=False)


class Server(DictBase, Base):
    """Represents a real server."""

    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    ip_version = Column(String(255))
    address = Column(String(255))
    port = Column(String(255))
    weight = Column(Integer)
    status = Column(String(255))
    # NOTE(ash): parent_id keep compatibility because it is searchable field
    parent_id = Column(Integer)
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('servers', order_by=id),
                              uselist=False)

class Probe(DictBase, Base):
    """Represents a health monitoring."""

    __tablename__ = 'probe'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('probes', order_by=id),
                              uselist=False)


class Sticky(DictBase, Base):
    """Represents a persistent session."""

    __tablename__ = 'sticky'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    name = Column(String(255))
    type = Column(String(255))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('stickies', order_by=id),
                              uselist=False)


class Predictor(DictBase, Base):
    """Represents a algorithm of selecting server."""

    __tablename__ = 'predictor'
    id = Column(Integer, primary_key=True)
    serverfarm_id = Column(Integer, ForeignKey('serverfarm.id'))
    type = Column(String(255))
    extra = Column(JsonBlob())

    serverfarm = relationship(ServerFarm,
                              backref=backref('predictors', order_by=id),
                              uselist=False)


def register_models(engine):
    """Create tables for models."""

    Base.metadata.create_all(engine)
