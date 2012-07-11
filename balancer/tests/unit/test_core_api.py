import mock
import unittest
import types
import balancer.core.api as api
from openstack.common import exception
from balancer import exception as exc


class TestDecorators(unittest.TestCase):

    def setUp(self):
        self.func = mock.MagicMock(__name__='Test func',
                return_value=mock.MagicMock(spec=types.FunctionType))

    def test_asynchronous_1(self):
        wrapped = api.asynchronous(self.func)
        wrapped(async=False)
        self.assertEquals(self.func.call_args_list, [mock.call()])

    @mock.patch("eventlet.spawn")
    def test_asynchronous_2(self, mock_event):
        wrapped = api.asynchronous(self.func)
        wrapped(async=True)
        self.assertTrue(mock_event.called)


class TestBalancer(unittest.TestCase):
    patch_balancer = mock.patch("balancer.loadbalancers.vserver.Balancer")
    patch_scheduller = mock.patch("balancer.core.scheduller.Scheduller")
    patch_logger = mock.patch("logging.getLogger")

    def setUp(self):
        self.conf = mock.MagicMock()
        value = mock.MagicMock
        self.dict_list = ({'id': 1, 'name': 'name', 'extra': {
            'stragearg': value, 'anotherarg': value}, },
            {'id': 2, 'name': 'name0', 'extra': {
                'stragearg': value, 'anotherarg': value}, })
        self.dictionary = {'id': 1, 'name': 'name', 'extra': {
            'stragearg': value, 'anotherarg': value}, }
        self.tenant_id = 1
        self.lb_id = 1
        self.lb_node = self.dictionary
        self.lb_nodes = self.dict_list
        self.lb_node_id = 1
        self.lb_body_0 = {'bubble': "bubble"}
        self.lb_body = {'algorithm': "bubble"}

    @mock.patch("balancer.db.api.loadbalancer_get_all_by_project")
    def test_lb_get_index(self, mock_api):
        api.lb_get_index(self.conf, self.tenant_id)
        self.assertTrue(mock_api.called)

    @mock.patch("balancer.db.api.loadbalancer_get_all_by_vm_id")
    def test_lb_find_for_vm(self, mock_api):
        vm_id = mock.Mock()
        api.lb_find_for_vm(self.conf, vm_id, self.tenant_id)
        self.assertTrue(mock_api.called)

    @mock.patch("balancer.db.api.loadbalancer_get")
    def test_get_data(self, mock_api):
        api.lb_get_data(self.conf, self.lb_id)
        self.assertTrue(mock_api.called)

    @patch_balancer
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_details(self, mock_api, mock_bal):
        api.lb_show_details(self.conf, self.lb_id)
        self.assertTrue(mock_api.called)

    @patch_balancer
    @patch_scheduller
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_0(self, mock_driver, mock_commands,
            mock_sched, mock_bal):
        """No exception"""
        api.create_lb(self.conf, async=False)
        self.assertTrue(mock_driver.called)
        self.assertTrue(mock_commands.called)

    @patch_balancer
    @patch_scheduller
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_1(self, mock_driver, mock_commands,
            mock_sched, mock_bal):
        """Exception"""
        mock_commands.side_effect = exception.Invalid
        api.create_lb(self.conf, async=False)
        mock_commands.called_once_with(exception.Invalid)

    @patch_balancer
    @mock.patch("balancer.db.api.predictor_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_update_lb_0(self, mock_driver, mock_api, mock_bal):
        """No exception, key.lower!='algorithm'"""
        api.update_lb(self.conf, self.lb_id, self.lb_body_0, async=False)
        self.assertFalse(mock_api.called)

    @patch_balancer
    @mock.patch("balancer.db.api.predictor_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_update_lb_1(self, mock_driver, mock_api, mock_bal):
        """No exception, key.lower='algorithm'"""
        api.update_lb(self.conf, self.lb_id, self.lb_body, async=False)
        self.assertTrue(mock_api.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    def test_update_lb_2(self, mock_driver, mock_bal):
        """exception"""
        mock_driver.return_value = None
        api.update_lb(self.conf, self.lb_id, self.lb_body, async=False)
        self.assertTrue(mock_driver.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.delete_loadbalancer")
    def test_delete_lb(self, mock_command, mock_driver, mock_bal):
        api.delete_lb(self.conf, self.lb_id)
        self.assertTrue(mock_command.called)
        self.assertTrue(mock_driver.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_node_to_loadbalancer")
    def test_lb_add_nodes(self, mock_command, mock_driver, mock_bal):
        api.lb_add_nodes(self.conf, self.lb_id, self.lb_nodes)
        self.assertTrue(mock_command.called)
        self.assertTrue(mock_command.call_count == 2)
        self.assertTrue(mock_driver.called)
        self.assertTrue(mock_driver.call_count == 2)

    @patch_balancer
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_nodes(self, mock_api, mock_bal):
        mock_bal.return_value.rs = self.dict_list
        api.lb_show_nodes(self.conf, 1)
        self.assertTrue(mock_api.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.remove_node_from_loadbalancer")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.server_destroy")
    def test_lb_delete_node(self, *mocks):
        api.lb_delete_node(self.conf, self.lb_id, self.lb_node_id)
        for mock in mocks:
            self.assertTrue(mock.called)

    @patch_balancer
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.activate_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_0(self, *mocks):
        """Activate server called"""
        lb_node_status = "inservice"
        api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
                    lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

    @patch_balancer
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.suspend_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_1(self, *mocks):
        """Suspend server called"""
        lb_node_status = ""
        api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
                    lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

    @patch_balancer
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.activate_rserver")
    @mock.patch("balancer.core.commands.suspend_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_2(self, mock_api_0, mock_commands1,
            mock_commands2, mock_driver, mock_api_1, patch_bal):
        """return ok"""
        mock_api_0.return_value = {'state': 'status'}
        api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
                'status')
        self.assertFalse(mock_commands1.called)
        self.assertFalse(mock_commands2.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.server_destroy")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    def test_lb_update_node_0(self, mock_com0, mock_com1, *mocks):
        """"""
        api.lb_update_node(self.conf, self.lb_id, self.lb_node_id,
                self.lb_node)
        self.assertTrue(mock_com0.called)
        self.assertTrue(mock_com1.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.db.api.server_destroy")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    def test_lb_update_node_1(self, mock_com0, mock_com1, mock_api0, *mocks):
        """"""
        mock_api0.return_value = self.dictionary
        api.lb_update_node(self.conf, self.lb_id, 1,
                self.lb_node)
        self.assertTrue(mock_com0.called)
        self.assertTrue(mock_com1.called)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    def test_lb_show_probes_0(self, db_api0, db_api1, db_api2):
        db_api0.return_value = self.dict_list
        api.lb_show_probes(self.conf, self.lb_id)
        self.assertTrue(db_api2.called)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    def test_lb_show_probes_1(self, db_api0, db_api1, db_api2):
        db_api0.return_value = self.dict_list
        db_api1.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_show_probes(self.conf, self.lb_id)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_probe_to_loadbalancer")
    def test_lb_add_probe_0(self, *mocks):
        """lb_probe['type']!=None"""
        lb_probe = {'type': 'Gvido'}
        api.lb_add_probe(self.conf, self.lb_id, lb_probe)
        for mok in mocks:
            self.assertTrue(mok.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_probe_to_loadbalancer")
    def test_lb_add_probe_1(self, *mocks):
        """lb_probe['type']=None"""
        lb_probe = {'type': None}
        api.lb_add_probe(self.conf, self.lb_id, lb_probe)
        for mok in mocks:
            self.assertFalse(mok.called)

    @patch_balancer
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.probe_get")
    @mock.patch("balancer.db.api.probe_destroy")
    def test_lb_delete_probe(self, *mocks):
        api.lb_delete_probe(self.conf, self.lb_id, self.lb_id)
        for mok in mocks:
            self.assertTrue(mok.called)

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_sticky0(self, db_api0, db_api1, db_api2):
        db_api1.return_value = self.dict_list
        api.lb_show_sticky(self.conf, self.lb_id)
        self.assertTrue(db_api0.called)

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_sticky1(self, db_api0, db_api1, db_api2):
        db_api1.return_value = self.dict_list
        db_api2.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_show_sticky(self.conf, self.lb_id)

    @patch_balancer
    @mock.patch("balancer.db.api.sticky_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_sticky_to_loadbalancer")
    def test_lb_add_sticky0(self, *mocks):
        sticky = mock.MagicMock()
        api.lb_add_sticky(self.conf, self.lb_id, sticky)
        for mok in mocks:
            self.assertTrue(mok.called)

    @patch_balancer
    @mock.patch("balancer.db.api.sticky_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_sticky_to_loadbalancer")
    def test_lb_add_sticky1(self, *mocks):
        sticky = {'persistenceType': None}
        api.lb_add_sticky(self.conf, self.lb_id, sticky)
        for mok in mocks:
            self.assertFalse(mok.called)

    @patch_balancer
    @mock.patch("balancer.db.api.sticky_get")
    @mock.patch("balancer.db.api.sticky_destroy")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.remove_sticky_from_loadbalancer")
    def test_lb_delete_sticky(self, *mocks):
        sticky = mock.MagicMock()
        api.lb_delete_sticky(self.conf, self.lb_id, sticky)
        for mok in mocks:
            self.assertTrue(mok.called)


class TestDevice(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock(register_group=mock.MagicMock)

    @mock.patch("balancer.db.api.device_get_all")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_device_get_index(self, mock_f1, mock_f2):
        mock_f2.__iter__.return_value = 1
        api.device_get_index(self.conf)
        self.assertTrue(mock_f2.called, "None")

    @mock.patch("balancer.core.scheduller.Scheduller.Instance")
    @mock.patch("balancer.db.api.device_pack_extra")
    @mock.patch("balancer.db.api.device_create")
    def test_device_create(self,  mock_f1, mock_f2, mock_f3):
        api.device_create(self.conf)
        self.assertTrue(mock_f2.called, "device_pack_extra not called")
        self.assertTrue(mock_f1.called, "device_create not called")
        self.assertTrue(mock_f3.called, "scheduller not called")

    def test_device_info(self):
        params = {'query_params': 2}
        res = 1
        res = api.device_info(params)
        self.assertEquals(res, None, "Alyarma!")
