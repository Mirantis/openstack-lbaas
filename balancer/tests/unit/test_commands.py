import balancer.core.commands as cmd
import unittest
import mock


class TestRollbackContext(unittest.TestCase):
    def setUp(self):
        self.rollback = mock.MagicMock()
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


class TestRollbackContextManager(unittest.TestCase):
    def setUp(self):
        self.rollback_mock = mock.MagicMock()
        self.obj = cmd.RollbackContextManager(
                context=mock.MagicMock(rollback_stack=[self.rollback_mock]))

    @mock.patch("balancer.core.commands.RollbackContext")
    def test_init(self, mock_context):
        self.obj.__init__()
        self.assertTrue(mock_context.called, "Context not called")

    @mock.patch("balancer.core.commands.RollbackContext")
    def test_enter(self, mock_context):
        res = self.obj.__enter__()
        self.assertEquals(res, self.obj.context, "Wrong context")

    def test_exit_none(self):
        self.obj.__exit__(None, None, None)
        self.assertEquals([mock.call(True,)], self.rollback_mock.call_args_list)

    def test_exit_not_none(self):
        exc = Exception("Someone set up us the bomb")
        with self.assertRaises(type(exc)):
            self.obj.__exit__(type(exc), exc, None)
        self.assertEquals([mock.call(False,)], self.rollback_mock.call_args_list)


class TestRserver(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock(device=mock.MagicMock(
            delete_real_server=mock.MagicMock()))
        self.rs = mock.MagicMock()
#    def test_create_rserver:

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    def test_delete_rserver_1(self, mock_func):
        """rs not empty, rss not 1"""
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertTrue(mock_func.called, "get not called")

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    @mock.patch("balancer.db.api.server_get")
    def test_delete_rserver_2(self, mock_f1, mock_f2):
        """rs not empty, rss length = 1"""
        mock_f2.return_value = '1'
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertTrue(mock_f1.called, "server_get not called")
        self.assertTrue(self.ctx.device.delete_real_server.called,\
                "delete_rserver not called")

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    @mock.patch("balancer.db.api.server_get")
    def test_delete_rserver_3(self, mock_f1, mock_f2):
        """rs empty, rss length != 0"""
        mock_f2.return_value = '1'
        rs = mock.MagicMock(get=mock.MagicMock(return_value=None))
        cmd.delete_rserver(self.ctx, rs)
        self.assertTrue(mock_f2.called, "server_get_parent not called")
        self.assertFalse(self.ctx.device.delete_real_server.called,\
                "delete_rserver called")

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    @mock.patch("balancer.db.api.server_get")
    def test_delete_rserver_4(self, mock_f1, mock_f2):
        """rs empty, rss length = 0"""
        mock_f2.return_value = ''
        rs = mock.MagicMock(get=mock.MagicMock(return_value=None))
        cmd.delete_rserver(self.ctx, rs)
        self.assertTrue(mock_f2.called, "server_get_parent not called")
        self.assertTrue(self.ctx.device.delete_real_server.called,\
                "delete_rserver not called")


class TestSticky(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock()
        self.sticky = mock.MagicMock()
        self.sticky[1] = 'id'
        self.sticky[2] = 'deployed'

    @mock.patch("balancer.db.api.sticky_update")
    def test_create_sticky(self, mock_upd):
        cmd.create_sticky(self.ctx, self.sticky)
        self.assertTrue(mock_upd.called, "upd not called")

    @mock.patch("balancer.db.api.sticky_update")
    def test_delete_sticky(self, mock_upd):
        cmd.delete_sticky(self.ctx, self.sticky)
        self.assertTrue(mock_upd.called, "upd not called")


class TestProbe(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock()
        self.probe = mock.MagicMock()
#    def test_create_probe(self):

    @mock.patch("balancer.db.api.probe_update")
    def test_delete_probe(self, mock_upd):
        cmd.delete_probe(self.ctx, self.probe)
        self.assertTrue(mock_upd.called, "upd not called")


class TestVip(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock()
        self.vip = mock.MagicMock()
        self.server_farm = mock.MagicMock()
#    def test_create_vip(self):

    @mock.patch("balancer.db.api.virtualserver_update")
    def test_delete_vip(self, mock_upd):
        cmd.delete_vip(self.ctx, self.vip)
        self.assertTrue(mock_upd.called, "upd not called")


class TestServerFarm(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock(device=mock.MagicMock(
            delete_real_server_from_server_farm=mock.MagicMock(),
            delete_probe_from_server_farm=mock.MagicMock(),
            activate_real_server=mock.MagicMock(),
            suspend_real_server=mock.MagicMock()))
        self.server_farm = mock.MagicMock()
        self.rserver = mock.MagicMock()
        self.probe = mock.MagicMock()

#    def test_create_server_farm(self):
    @mock.patch("balancer.db.api.serverfarm_update")
    def test_delete_server_farm(self, mock_upd):
        cmd.delete_server_farm(self.ctx, self.server_farm)
        self.assertTrue(mock_upd.called, "upd not called")

#    def test_add_rserver_to_server_farm(self):
    def test_delete_rserver_from_server_farm(self):
        cmd.delete_rserver_from_server_farm(self.ctx, self.server_farm,\
                                            self.rserver)
        self.assertTrue(
                self.ctx.device.delete_real_server_from_server_farm.called,\
                "method not called")

#    def test_add_probe_to_server_farm(self):
    def test_remove_probe_from_server_farm(self):
        cmd.remove_probe_from_server_farm(self.ctx, self.server_farm,\
                                          self.probe)
        self.assertTrue(
                self.ctx.device.delete_probe_from_server_farm.called,\
                "method not called")

    def test_activate_rserver(self):
        cmd.activate_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(
                self.ctx.device.activate_real_server.called,\
                "method not called")

    def test_suspend_rserver(self):
        cmd.suspend_rserver(self.ctx, self.server_farm, self.rserver)
        self.assertTrue(
                self.ctx.device.suspend_real_server.called,\
                "method not called")


class TestLoadbalancer(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock()
        self.rserver = mock.MagicMock()
        self.probe = mock.MagicMock()
        self.sticky = mock.MagicMock()
        self.call_list = mock.MagicMock(spec=list)
        self.call_list.__iter__.return_value = [mock.MagicMock(
            get=mock.MagicMock())]
        self.balancer = mock.MagicMock(probes=self.call_list,
               rs=self.call_list, vips=self.call_list,
               sf=mock.MagicMock(_sticky=self.call_list))
        #self.balancer = Mock()

    @mock.patch("balancer.core.commands.add_probe_to_server_farm")
    @mock.patch("balancer.core.commands.create_probe")
    @mock.patch("balancer.core.commands.create_server_farm")
    @mock.patch("balancer.core.commands.create_rserver")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    @mock.patch("balancer.core.commands.create_vip")
    def test_create_loadbalancer(self, mf1, mf2, mf3, mf4, mf5, mf6):
        cmd.create_loadbalancer(self.ctx, self.balancer)
        self.assertTrue(mf5.called, "create_probe not called")
        self.assertTrue(mf4.called, "create_server_farm not called")
        self.assertTrue(mf3.called, "create_rserver not called")
        self.assertTrue(mf2.called, "add_rserver_server_farm not called")
        self.assertTrue(mf6.called, "add_probe_to_server_farm not called")
        self.assertTrue(mf1.called, "create_vip not called")

    @mock.patch("balancer.core.commands.delete_sticky")
    @mock.patch("balancer.core.commands.remove_probe_from_server_farm")
    @mock.patch("balancer.core.commands.delete_probe")
    @mock.patch("balancer.core.commands.delete_server_farm")
    @mock.patch("balancer.core.commands.delete_rserver")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    @mock.patch("balancer.core.commands.delete_vip")
    def test_delete_loadbalancer(self, mf1, mf2, mf3, mf4, mf5, mf6, mf7):
        cmd.delete_loadbalancer(self.ctx, self.balancer)
        self.assertTrue(mf1.called, "delete_vip not called")
        self.assertTrue(mf2.called, "delete_rserver_from_sf not called")
        self.assertTrue(mf3.called, "delete_rserver")
        self.assertTrue(mf5.called, "delete_probe not called")
        self.assertTrue(mf6.called, "remove_probe_from_server_farm not called")
        self.assertTrue(mf7.called, "delete_sticky not called")
        self.assertTrue(mf4.called, "delete_server_farm not called")

    @mock.patch("balancer.core.commands.create_server_farm")
    def test_update_loadbalancer(self, mock_func):
        self.lb0 = mock.MagicMock()
        cmd.update_loadbalancer(self.ctx, self.balancer, self.lb0)
        self.assertTrue(mock_func.called, "function not called")

    @mock.patch("balancer.core.commands.create_rserver")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    def test_add_node_to_loadbalancer(self, mock_f1, mock_f2):
        cmd.add_node_to_loadbalancer(self.ctx, self.balancer, self.rserver)
        self.assertTrue(mock_f2.called, "create_rserver not called")
        self.assertTrue(mock_f1.called, "add_rserver not called")

    @mock.patch("balancer.core.commands.delete_rserver")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    def test_remove_node_from_loadbalancer(self, mock_f1, mock_f2):
        cmd.remove_node_from_loadbalancer(
                self.ctx, self.balancer, self.rserver)
        self.assertTrue(mock_f1.called, "delete_rserver_from_farm not called")
        self.assertTrue(mock_f2.called, "delete_rserver called")

    @mock.patch("balancer.core.commands.create_probe")
    @mock.patch("balancer.core.commands.add_probe_to_server_farm")
    def test_add_probe_to_loadbalancer(self, mock_f1, mock_f2):
        cmd.add_probe_to_loadbalancer(self.ctx, self.balancer, self.probe)
        self.assertTrue(mock_f1.called, "add_probe not called")
        self.assertTrue(mock_f2.called, "create_probe not called")

    @mock.patch("balancer.core.commands.remove_probe_from_server_farm")
    @mock.patch("balancer.core.commands.delete_probe")
    def test_makeDeleteProbeFromLBChain(self, mock_f1, mock_f2):
        cmd.makeDeleteProbeFromLBChain(self.ctx, self.balancer, self.probe)
        self.assertTrue(mock_f1.called, "delete_probe not called")
        self.assertTrue(mock_f2.called,\
                "remove_probe_from_server_farm not called")

    @mock.patch("balancer.core.commands.create_sticky")
    def test_add_sticky_to_loadbalancer(self, mock_func):
        cmd.add_sticky_to_loadbalancer(self.ctx, self.balancer, self.sticky)
        self.assertTrue(mock_func.called, "create_sticky not called")

    @mock.patch("balancer.core.commands.delete_sticky")
    def test_remove_sticky_from_loadbalancer(self, mock_func):
        cmd.remove_sticky_from_loadbalancer(
                self.ctx, self.balancer, self.sticky)
        self.assertTrue(mock_func.called, "delete_sticky not called")
