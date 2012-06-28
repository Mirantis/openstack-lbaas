import balancer.core.commands as cmd
import unittest
import mock
import types


class TestDecorators(unittest.TestCase):
    """Need help with def fin coverage"""
    def setUp(self):
        self.obj0 = mock.MagicMock(__name__='GenTypeObj',
                return_value=mock.MagicMock(spec=types.GeneratorType))
        self.obj1 = mock.MagicMock(__name__='NonGenTypeObj',
                return_value=mock.MagicMock(spec=types.FunctionType))
        self.ctx_mock = mock.MagicMock()
        self.exc = Exception("Someone doing something wrong")

    def test_with_rollback_gen_type_0(self):
        """Don't get any exception"""
        wrapped = cmd.with_rollback(self.obj0)
        wrapped(self.ctx_mock, "arg1", "arg2")
        self.assertEquals([mock.call(self.ctx_mock, "arg1", "arg2")],
                self.obj0.call_args_list)
        rollback_fn = self.ctx_mock.add_rollback.call_args[0][0]
        rollback_fn(True)
        self.assertTrue(self.ctx_mock.add_rollback.called)
        self.assertTrue(self.obj0.return_value.close.called)

    def test_with_rollback_gen_type_1(self):
        """Get Rollback exception"""
        self.obj0.return_value.throw.side_effect = cmd.Rollback
        wrapped = cmd.with_rollback(self.obj0)
        wrapped(self.ctx_mock, "arg1", "arg2")
        self.assertEquals([mock.call(self.ctx_mock, "arg1", "arg2")],
                self.obj0.call_args_list)
        rollback_fn = self.ctx_mock.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(self.ctx_mock.add_rollback.called)
        self.assertEquals(self.obj0.return_value.throw.call_args_list,
                [mock.call(cmd.Rollback)])

    def test_with_rollback_gen_type_2(self):
        """Get exception during rollback"""
        self.obj0.return_value.throw.side_effect = Exception()
        wrapped = cmd.with_rollback(self.obj0)
        wrapped(self.ctx_mock, "arg1", "arg2")
        self.assertEquals([mock.call(self.ctx_mock, "arg1", "arg2")],
                self.obj0.call_args_list)
        rollback_fn = self.ctx_mock.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(self.ctx_mock.add_rollback.called)
        self.assertEquals(self.obj0.return_value.throw.call_args_list,
                [mock.call(cmd.Rollback)])

    def test_with_rollback_gen_type_3(self):
        """Get StopIteration exception"""
        self.obj0.return_value.next.side_effect = StopIteration
        with self.assertRaises(type(self.exc)):
            wrapped = cmd.with_rollback(self.obj0)
            wrapped(self.ctx_mock, "arg1", "arg2")
        self.assertEquals([mock.call(self.ctx_mock, "arg1", "arg2")],
                self.obj0.call_args_list)
        self.assertFalse(self.ctx_mock.add_rollback.called)

    def test_with_rollback_non_gen_type(self):
        with self.assertRaises(type(self.exc)):
            wrapped = cmd.with_rollback(self.obj1)
            wrapped(self.ctx_mock, "arg1", "arg2")

    def test_ignore_exceptions0(self):
        """Don't get exception"""
        wrapped = cmd.ignore_exceptions(self.obj1)
        wrapped("arg1", "arg2")
        self.assertEquals([mock.call("arg1", "arg2")],
                self.obj1.call_args_list)

    def test_ignore_exceptions1(self):
        """Get exception"""
        self.obj1.side_effect = Exception()
        wrapped = cmd.ignore_exceptions(self.obj1)
        wrapped()
        self.assertTrue(self.obj1.call_args_list, Exception)


class TestRollbackContext(unittest.TestCase):
    def setUp(self):
        self.rollback = mock.MagicMock()
        self.rollback.return_value = "foo"
        self.obj = cmd.RollbackContext()
        self.stack = []

    def test_init(self):
        self.obj.__init__()
        self.assertEquals(self.obj.rollback_stack, [], "Not equal")

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
        self.assertEquals([mock.call(True,)],
                self.rollback_mock.call_args_list)

    def test_exit_not_none(self):
        exc = Exception("Someone set up us the bomb")
        with self.assertRaises(type(exc)):
            self.obj.__exit__(type(exc), exc, None)
        self.assertEquals([mock.call(False,)],
                self.rollback_mock.call_args_list)


class TestRserver(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock(device=mock.MagicMock(
            delete_real_server=mock.MagicMock(),
            create_real_server=mock.MagicMock()))
        self.rs = {'parent_id': "", 'id': mock.MagicMock(spec=int),
                'deployed': ""}
        self.exc = Exception()

    @mock.patch("balancer.db.api.server_update")
    def test_create_rserver_1(self, mock_func):
        """ parent_id == "" """
        cmd.create_rserver(self.ctx, self.rs)
        self.assertTrue(self.ctx.device.create_real_server.called)
        self.assertTrue(mock_func.called)

    @mock.patch("balancer.db.api.server_update")
    def test_create_rserver_2(self, mock_func):
        """ parent_id != "", no exception """
        self.rs['parent_id'] = 0
        cmd.create_rserver(self.ctx, self.rs)
        self.assertFalse(self.ctx.device.create_real_server.called)
        self.assertFalse(mock_func.called)

    @mock.patch("balancer.db.api.server_update")
    def test_create_rserver_3(self, mock_func):
        """Exception"""
        self.rs['parent_id'] = ""
        cmd.create_rserver(self.ctx, self.rs)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(self.ctx.device.delete_real_server.called)
        self.assertTrue(mock_func.called)

    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    def test_delete_rserver_1(self, mock_f1, mock_f2):
        """rs empty, len rss > 0"""
        mock_f1.return_value = ({'id': 2}, {'id': 3})
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertTrue(self.ctx.device.delete_real_server.called,
                "ctx_delete_rs not called")
        self.assertTrue(mock_f2.called, "server_upd not called")
        self.assertTrue(self.ctx.device.create_real_server.called,
                "ctx_create_rs not called")
        self.assertNotEquals(len(mock_f1.return_value), 0)

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    @mock.patch("balancer.db.api.server_get")
    def test_delete_rserver_2(self, mock_f1, mock_f2):
        """rs not empty, rss not empty"""
        self.rs['parent_id'] = 1
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertFalse(self.ctx.device.delete_real_server.called,\
                "delete_rserver called")

    @mock.patch("balancer.db.api.server_get_all_by_parent_id")
    @mock.patch("balancer.db.api.server_update")
    def test_delete_rserver_3(self, mock_f1, mock_f2):
        """rs empty, rss empty"""
        mock_f2.return_value = ()
        cmd.delete_rserver(self.ctx, self.rs)
        self.assertFalse(mock_f1.called,\
                "server_update called")


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

    @mock.patch("balancer.core.commands")
    @mock.patch("balancer.db.api.probe_update")
    def test_create_probe_0(self, mock_f1, mock_f2):
        cmd.create_probe(self.ctx, self.probe)
        self.assertTrue(self.ctx.device.create_probe.called)
        self.assertTrue(mock_f1.called)

    @mock.patch("balancer.core.commands.delete_probe")
    @mock.patch("balancer.db.api.probe_update")
    def test_create_probe_1(self, mock_f1, mock_f2):
        cmd.create_probe(self.ctx, self.probe)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(mock_f2.called)

    @mock.patch("balancer.db.api.probe_update")
    def test_delete_probe(self, mock_upd):
        cmd.delete_probe(self.ctx, self.probe)
        self.assertTrue(mock_upd.called, "upd not called")


class TestVip(unittest.TestCase):
    def setUp(self):
        self.ctx = mock.MagicMock()
        self.vip = mock.MagicMock()
        self.server_farm = mock.MagicMock()

    @mock.patch("balancer.core.commands.delete_vip")
    @mock.patch("balancer.db.api.virtualserver_update")
    def test_create_vip_0(self, mock_f1, mock_f2):
        """No exception"""
        cmd.create_vip(self.ctx, self.vip, self.server_farm)
        self.assertTrue(self.ctx.device.create_virtual_ip.called)
        self.assertTrue(mock_f1.called)

    @mock.patch("balancer.core.commands.delete_vip")
    @mock.patch("balancer.db.api.virtualserver_update")
    def test_create_vip_1(self, mock_f1, mock_f2):
        """Exception"""
        cmd.create_vip(self.ctx, self.vip, self.server_farm)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(mock_f2.called)

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
            uspend_real_server=mock.MagicMock(),
            add_real_server_to_server_farm=mock.MagicMock(),
            create_server_farm=mock.MagicMock(),
            add_probe_to_server_farm=mock.MagicMock()),
            conf=mock.MagicMock())
        self.server_farm = mock.MagicMock()
        self.rserver = mock.MagicMock()
        self.probe = mock.MagicMock()

    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_update")
    @mock.patch("balancer.core.commands.delete_server_farm")
    def test_create_server_farm_0(self, mock_f1, mock_f2, mock_f3):
        """No exception"""
        cmd.create_server_farm(self.ctx, self.server_farm)
        self.assertTrue(self.ctx.device.create_server_farm.called)
        self.assertTrue(mock_f2.called)
        self.assertFalse(mock_f1.called)
        self.assertTrue(mock_f3.called)

    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_update")
    @mock.patch("balancer.core.commands.delete_server_farm")
    def test_create_server_farm_1(self, mock_f1, mock_f2, mock_f3):
        """Exception"""
        cmd.create_server_farm(self.ctx, self.server_farm)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(mock_f1.called)

    @mock.patch("balancer.db.api.serverfarm_update")
    def test_delete_server_farm(self, mock_upd):
        cmd.delete_server_farm(self.ctx, self.server_farm)
        self.assertTrue(mock_upd.called, "upd not called")

    def test_add_rserver_to_server_farm_0(self):
        "No exception, if statement = True"
        cmd.add_rserver_to_server_farm(self.ctx, self.server_farm,
                self.rserver)
        self.assertTrue(self.ctx.device.add_real_server_to_server_farm.called)
        self.assertEquals(self.rserver['name'], self.rserver['parent_id'])

    def test_add_rserver_to_server_farm_1(self):
        "Exception"
        cmd.add_rserver_to_server_farm(self.ctx, self.server_farm,
                self.rserver)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(
            self.ctx.device.delete_real_server_from_server_farm.called)

    def test_delete_rserver_from_server_farm(self):
        cmd.delete_rserver_from_server_farm(self.ctx, self.server_farm,\
                                            self.rserver)
        self.assertTrue(
                self.ctx.device.delete_real_server_from_server_farm.called,\
                "method not called")

    def test_add_probe_to_server_farm_0(self):
        "No exception"
        cmd.add_probe_to_server_farm(self.ctx, self.server_farm, self.probe)
        self.assertTrue(self.ctx.device.add_probe_to_server_farm.called)

    def test_add_probe_to_server_farm_1(self):
        "Exception"
        cmd.add_probe_to_server_farm(self.ctx, self.server_farm, self.probe)
        rollback_fn = self.ctx.add_rollback.call_args[0][0]
        rollback_fn(False)
        self.assertTrue(self.ctx.device.delete_probe_from_server_farm.called)

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
