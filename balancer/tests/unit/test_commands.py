import balancer.core.commands as cmd
from unittest import TestCase
from mock import patch, MagicMock as Mock
#from cmd import delete_rserver


class TestRollbackContext(TestCase):
    def setUp(self):
        self.rollback = Mock()
        self.rollback.return_value = "foo"
        self.obj = cmd.RollbackContext()
        self.stack = []

#    def test_init(self):
#        res = self.obj.__init__()
#        self.assertEquals(res, self.stack, "Not equal")
#    @patch("balancer.core.commands.RollbackContext")#, "__init__")
    def test_add_rollback(self):
        self.obj.add_rollback(self.rollback)
        self.assertFalse(self.obj.rollback_stack == [], 'Empty')


class TestRollbackContextManager(TestCase):
    def setUp(self):
        self.obj = cmd.RollbackContextManager()
        self.obj.context = Mock()
        self.obj.context.return_value = "foo"

    @patch("balancer.core.commands.RollbackContext")
    def test_init(self, mock_context):
        self.obj.__init__()
        self.assertTrue(mock_context.called, "Context not called")

    @patch("balancer.core.commands.RollbackContext")
    def test_enter(self, mock_context):
        res = self.obj.__enter__()
        self.assertEquals(res, self.obj.context, "Wrong context")

#    @patch("balancer.core.commands.RollbackContextManager")
#    def test_exit(self, mock_context):
#        res = self.obj.__exit__(Mock(), Mock(), Mock())
#        self.assertEquals(res, None)


class TestRserver(TestCase):
    def setUp(self):
        self.ctx = Mock(device=Mock(deleteRServer=Mock()))
        self.rs = Mock()
#    def test_create_rserver:

    @patch("balancer.db.api.server_get_all_by_parent_id")
    def test_delete_rserver(self, mock_func):
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertTrue(mock_func.called, "get not called")


class TestSticky(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.sticky = Mock()
        self.sticky[1] = 'id'
        self.sticky[2] = 'deployed'

    @patch("balancer.db.api.sticky_update")
    def test_create_sticky(self, mock_upd):
        cmd.create_sticky(self.ctx, self.sticky)
        self.assertTrue(mock_upd.called, "upd not called")

    @patch("balancer.db.api.sticky_update")
    def test_delete_sticky(self, mock_upd):
        cmd.delete_sticky(self.ctx, self.sticky)
        self.assertTrue(mock_upd.called, "upd not called")


class TestProbe(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.probe = Mock()
#    def test_create_probe(self):

    @patch("balancer.db.api.probe_update")
    def test_delete_probe(self, mock_upd):
        cmd.delete_probe(self.ctx, self.probe)
        self.assertTrue(mock_upd.called, "upd not called")


class TestVip(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.vip = Mock()
        self.server_farm = Mock()
#    def test_create_vip(self):

    @patch("balancer.db.api.virtualserver_update")
    def test_delete_vip(self, mock_upd):
        cmd.delete_vip(self.ctx, self.vip)
        self.assertTrue(mock_upd.called, "upd not called")


class TestServerFarm(TestCase):
    def setUp(self):
        self.ctx = Mock(device=Mock(deleteRServerFromSF=Mock(),
            deleteProbeFromSF=Mock(), activateRServer=Mock(),
            suspendRServer=Mock()))
        self.server_farm = Mock()
        self.rserver = Mock()
        self.probe = Mock()

#    def test_create_server_farm(self):
    @patch("balancer.db.api.serverfarm_update")
    def test_delete_server_farm(self, mock_upd):
        cmd.delete_server_farm(self.ctx, self.server_farm)
        self.assertTrue(mock_upd.called, "upd not called")

#    def test_add_rserver_to_server_farm(self):
    def test_delete_rserver_from_server_farm(self):
        cmd.delete_rserver_from_server_farm(self.ctx, self.server_farm,\
                                            self.rserver)
        self.assertTrue(self.ctx.device.deleteRServerFromSF.called,\
                "method not called")

#    def test_add_probe_to_server_farm(self):
#    @patch()
    def test_remove_probe_from_server_farm(self):
        cmd.remove_probe_from_server_farm(self.ctx, self.server_farm,\
                                          self.probe)
        self.assertTrue(self.ctx.device.deleteProbeFromSF.called,\
                "method not called")

    def test_activate_rserver(self):
        cmd.activate_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(self.ctx.device.activateRServer.called,\
                "method not called")

    def test_suspend_rserver(self):
        cmd.suspend_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(self.ctx.device.suspendRServer.called,\
                "method not called")


class TestLoadbalancer(TestCase):
    def setUp(self):
        self.ctx = Mock()
        self.balancer = Mock(probes=Mock(), rs=Mock(), vips=Mock())
        self.rserver = Mock()
        self.probe = Mock()
        self.sticky = Mock()

    @patch("balancer.core.commands.create_probe")
    @patch("balancer.core.commands.create_server_farm")
    @patch("balancer.core.commands.create_rserver")
    @patch("balancer.core.commands.add_rserver_to_server_farm")
    @patch("balancer.core.commands.create_vip")
    def test_create_loadbalancer(self, mf1, mf2, mf3, mf4, mf5):
        cmd.create_loadbalancer(self.ctx, self.balancer)
        #self.assertTrue(self.balancer.probes.called, "create_probe not called")
        self.assertTrue(mf4.called, "create_server_farm not called")
        #self.assertTrue(mf3.called, "create_rserver not called")
        #self.assertTrue(mf4.called, "add_rserver_to_server_farm not called")
        #self.assertTrue(mf5.called, "create_vip not called")

    @patch("balancer.core.commands.delete_probe")
    @patch("balancer.core.commands.delete_server_farm")
    @patch("balancer.core.commands.delete_rserver")
    @patch("balancer.core.commands.delete_rserver_from_server_farm")
    @patch("balancer.core.commands.delete_vip")
    def test_delete_loadbalancer(self, mf1, mf2, mf3, mf4, mf5):
        cmd.delete_loadbalancer(self.ctx, self.balancer)
        self.assertTrue(mf4.called, "delete_server_farm not called")
        #self.assertTrue(self.balancer.called, "balancer not called")

    @patch("balancer.core.commands.create_server_farm")
    def test_update_loadbalancer(self, mock_func):
        self.lb0 = Mock()
        cmd.update_loadbalancer(self.ctx, self.balancer, self.lb0)
        self.assertTrue(mock_func.called, "function not called")

    @patch("balancer.core.commands.create_rserver")
    @patch("balancer.core.commands.add_rserver_to_server_farm")
    def test_add_node_to_loadbalancer(self, mock_f1, mock_f2):
        cmd.add_node_to_loadbalancer(self.ctx, self.balancer, self.rserver)
        self.assertTrue(mock_f2.called, "create_rserver not called")
        self.assertTrue(mock_f1.called, "add_rserver not called")

    @patch("balancer.core.commands.delete_rserver")
    @patch("balancer.core.commands.delete_rserver_from_server_farm")
    def test_remove_node_from_loadbalancer(self, mock_f1, mock_f2):
        cmd.remove_node_from_loadbalancer(self.ctx, self.balancer, self.rserver)
        self.assertTrue(mock_f1.called, "delete_rserver_from_farm not called")
        self.assertTrue(mock_f2.called, "delete_rserver called")

    @patch("balancer.core.commands.create_probe")
    @patch("balancer.core.commands.add_probe_to_server_farm")
    def test_add_probe_to_loadbalancer(self, mock_f1, mock_f2):
        cmd.add_probe_to_loadbalancer(self.ctx, self.balancer, self.probe)
        self.assertTrue(mock_f1.called, "add_probe not called")
        self.assertTrue(mock_f2.called, "create_probe not called")

    @patch("balancer.core.commands.remove_probe_from_server_farm")
    @patch("balancer.core.commands.delete_probe")
    def test_makeDeleteProbeFromLBChain(self, mock_f1, mock_f2):
        cmd.makeDeleteProbeFromLBChain(self.ctx, self.balancer, self.probe)
        self.assertTrue(mock_f1.called, "delete_probe not called")
        self.assertTrue(mock_f2.called, "remove_probe_from_server_farm not called")

    @patch("balancer.core.commands.create_sticky")
    def test_add_sticky_to_loadbalancer(self, mock_func):
        cmd.add_sticky_to_loadbalancer(self.ctx, self.balancer, self.sticky)
        self.assertTrue(mock_func.called, "create_sticky not called")

    @patch("balancer.core.commands.delete_sticky")
    def test_remove_sticky_from_loadbalancer(self, mock_func):
        cmd.remove_sticky_from_loadbalancer(self.ctx, self.balancer, self.sticky)
        self.assertTrue(mock_func.called, "delete_sticky not called")
