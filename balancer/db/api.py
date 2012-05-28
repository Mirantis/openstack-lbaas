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
"""Database storage API."""

from balancer.db import models
from balancer.db.session import get_session
from balancer import exception


def device_create(conf, values):
    session = get_session(conf)
    with session.begin():
        device_ref = models.Device()
        device_ref.update(values)
        session.add(device_ref)
        return device_ref


def device_get(conf, device_id, session=None):
    session = session or get_session(conf)
    device_ref = session.query(models.Device).filter_by(id=device_id).first()
    if not device_ref:
        raise exception.DeviceNotFound(device_id=device_id)
    return device_ref


def device_destroy(conf, device_id):
    session = get_session(conf)
    with session.begin():
        device_ref = device_get(conf, device_id, session=session)
        session.delete(device_ref)


def device_update(conf, device_id, values):
    session = get_session(conf)
    with session.begin():
        device_ref = device_get(conf, device_id, session=session)
        device_ref.update(values)
        session.add(device_ref)
