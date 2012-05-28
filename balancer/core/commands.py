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

import functools
import logging

from balancer.common import utils
from balancer.storage import storage

LOG = logging.getLogger(__name__)


class RollbackContext(object):
    def __init__(self):
        self.rollback_stack = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        good = exc_type is None
        if not good:
            LOG.error("Rollback because of: %s", exc_value)
        while self.rollback_stack:
            self.rollback_stack.pop()(good)

    def add_rollback(self, rollback):
        try:
            self.rollback_stack.append(rollback)
        except Rollback:
            pass
        except Exception:
            LOG.exception("Exception during rollback.")


class Rollback(Exception):
    pass


def with_rollback(func):
    @functools.wraps(func)
    def __inner(ctx, *args, **kwargs):
        gen = func(ctx, *args, **kwargs)
        res = gen.next()

        def fin(good):
            if good:
                gen.close()
            else:
                gen.throw(Rollback)
        ctx.add_rollback(fin)
        return res
    return __inner


@with_rollback
def create_rserver(ctx, conf, driver, rs):
    try:
        # We can't create multiple RS with the same IP. So parent_id points to
        # RS which already deployed and has this IP
        LOG.debug("Creating rserver command execution with rserver: %s", rs)
        LOG.debug("RServer parent_id: %s", rs.parent_id)
        if rs.parent_id == "":
            driver.createRServer(ctx, rs)
            rs.deployed = 'True'
            stor = storage.Storage(conf)
            wr = stor.getWriter()
            wr.updateDeployed(rs, 'True')
        yield
    except Exception:
        driver.deleteRServer(ctx, rs)
        rs.deployed = 'False'
        stor = storage.Storage(conf)
        wr = stor.getWriter()
        wr.updateDeployed(rs, 'False')
        raise


def delete_rserver(ctx, conf, driver, rs):
    store = storage.Storage(conf)
    reader = store.getReader()
    rss = []
    LOG.debug("Got delete RS request")
    if rs.parent_id != "" and utils.checkNone(rs.parent_id):
        rss = reader.getRServersByParentID(rs.parent_id)
        LOG.debug("List servers %s", rss)
        if len(rss) == 1:
            parent_rs = reader.getRServerById(rs.parent_id)
            driver.deleteRServer(ctx, parent_rs)
    else:
        # rs1
        # We need to check if there are reals who reference this rs as a parent
        rss = reader.getRServersByParentID(rs.id)
        LOG.debug("List servers %s", rss)
        if len(rss) == 0:
            driver.deleteRServer(ctx, rs)


def create_sticky(ctx, conf, driver, sticky):
    driver.createStickiness(ctx,  sticky)
    sticky.deployed = 'True'
    stor = storage.Storage(conf)
    wr = stor.getWriter()
    wr.updateDeployed(sticky, 'True')


def delete_sticky(ctx, conf, driver, sticky):
    driver.deleteStickiness(ctx,  sticky)
    sticky.deployed = 'False'
    stor = storage.Storage(conf)
    wr = stor.getWriter()
    wr.updateDeployed(sticky,  'False')
