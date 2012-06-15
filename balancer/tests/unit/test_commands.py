#import functools
#import logging
#import types

#from balancer.common import utils
#from balancer.db import api as db_api
import balancer.core.commands as cmd
from unittest import TestCase
from mock import Mock


class TestRollbackContext(TestCase):
    def setUp(self):
        self.rollback = Mock()
        self.rollback.return_value = "foo"
        self.obj = cmd.RollbackContext()

    def test_add_rollback(self):
        res = self.obj.add_rollback(self.rollback)
        self.assertEquals(res, "foo", "Something wrong")


class TestRollbackContextManager(TestCase):
    def setUp(self):
        self.obj = cmd.RollbackContextManager()
        self.obj.context = Mock()
        self.obj.context.return_value = "foo"
#don' really know how to test __init__ func
#    def test_init(self):
#       res = self.obj.__init__(context=Mock())
#       self

    def test_enter(self):
        res = self.obj.__enter__()
        self.assertEquals(res, "foo", "Something wrong")

    def test_exit(self):
        res = self.obj.__exit__(None, None, None)
        self.assertEquals(res, None, "Something wrong")
        exc_type = Mock()
        exc_value = Mock()
        exc_tb = Mock()
        exc_value.return_value = "foo"
        exc_type.return_value = "foo"
        exc_tb.return_value = "foo"
        res = self.obj.__exit__(exc_type, exc_value, exc_tb)
        self.assertEquals(res, "foo foo foo", "Something wrong")


class TestRserver(TestCase):
    def setUp_(self):
        self.ctx = Mock()
        self.rs = Mock()
#    def test_create_rserver:

    def test_delete_rserver(self):
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.rs.called, "rs not called")


class TestSticky(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.sticky = Mock()

    def test_create_sticky(self):
        cmd.create_sticky(self.ctx, self.sticky)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.sticky.called, "sticky not called")

    def test_delete_sticky(self):
        cmd.delete_sticky(self.ctx, self.sticky)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.sticky.called, "sticky not called")


class TestProbe(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.probe = Mock()
#    def test_create_probe(self):

    def test_delete_probe(self):
        cmd.delete_probe(self.ctx, self.probe)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.probe.ocalled, "probe not called")


class TestVip(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.vip = Mock()
        self.server_farm = Mock()
#    def test_create_vip(self):

    def test_delete_vip(self):
        cmd.delete_vip(self.ctx, self.vip)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.vip.called, "vip not called")


class TestServerFarm(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.server_farm = Mock()
        self.rserver = Mock()
        self.probe = Mock()

#    def test_create_server_farm(self):
    def test_delete_server_farm(self):
        cmd.delete_server_farm(self.ctx, self.server_farm)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.server_farm.called, "server farm not called")

#    def test_add_rserver_to_server_farm(self):
    def test_delete_rserver_from_server_farm(self):
        cmd.delete_rserver_from_server_farm(self.ctx, self.server_farm,\
                                            self.rserver)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.server_farm.called, "server farm not called")
        self.assertTrue(self.rserver.called, "rserver not called")
#    def test_add_probe_to_server_farm(self):

    def test_remove_probe_from_server_farm(self):
        cmd.remove_probe_from_server_farm(self.ctx, self.server_farm,\
                                          self.probe)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.server_farm.called, "server farm not called")
        self.assertTrue(self.probe.called, "probe not called")

    def test_activate_rserver(self):
        cmd.activate_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.server_farm.called, "server farm not called")
        self.assertTrue(self.rserver.called, "rserver not called")

    def test_suspend_rserver(self):
        cmd.suspend_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.server_farm.called, "server farm not called")
        self.assertTrue(self.rserver.called, "rserver not called")


class TestLoadbalancer(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.balancer = Mock()
        self.rserver = Mock()
        self.probe = Mock()

    def test_create_loadbalancer(self):
        cmd.create_loadbalancer(self.ctx, self.balancer)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")

    def test_delete_loadbalancer(self):
        cmd.delete_loadbalancer(self.ctx, self.balancer)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")

    def test_update_loadbalancer(self):
        self.lb0 = Mock()
        cmd.update_loadbalancer(self.ctx, self.balancer, self.lb0)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.lb0.called, "lb0 not called")

    def test_add_node_to_loadbalancer(self):
        cmd.add_node_to_loadbalancer(self.ctx, self.balancer, self.rserver)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.rserver.called, "rserver not called")

    def test_remove_node_from_loadbalancer(self):
        cmd.remove_node_from_loadbalancer(self.ctx, self.balancer, self.rserver)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.rserver.called, "rserver not called")

    def test_add_probe_to_loadbalancer(self):
        cmd.add_probe_to_loadbalancer(self.ctx, self.balancer, self.probe)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.probe.called, "probe not called")

    def test_makeDeleteProbeFromLBChain(self):
        cmd.makeDeleteProbeFromLBChain(self.ctx, self.balancer, self.probe)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.probe.called, "probe not called")

    def test_add_sticky_to_loadbalancer(self):
        cmd.add_sticky_to_loadbalancer(self.ctx, self.balancer, self.sticky)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.sticky.called, "sticky not called")

    def test_remove_sticky_from_loadbalancer(self):
        cmd.remove_sticky_from_loadbalancer(self.ctx, self.balancer, self.sticky)
        self.assertTrue(self.ctx.called, "ctx not called")
        self.assertTrue(self.balancer.called, "balancer not called")
        self.assertTrue(self.sticky.called, "sticky not called")
