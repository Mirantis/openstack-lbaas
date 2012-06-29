# vim: tabstop=4 shiftwidth=4 softtabstop=4

import mock
import unittest
import types
#from balancer.core import commands
#from balancer.loadbalancers import vserver
#from balancer.devices.DeviceMap import DeviceMap
#from balancer.core.scheduller import Scheduller
#from balancer.storage.storage import Storage
import balancer.core.api as api
from openstack.common import exception


@unittest.skip
class TestDecoratos(unittest.TestCase):

    def setUp(self):
        self.func = mock.MagicMock(__name__='Test func',
                return_value=mock.MagicMock(spec=types.FunctionType))

    def test_asynchronous_1(self):
        wrapped = api.asynchronous(self.func)
        wrapped()
        self.assertEquals(self.func.call_args_list, [mock.call()])

    def test_asynchronous_2(self):
        wrapped = api.asynchronous(self.func)
        wrapped(False)
        self.assertEquals(self.func.call_args_list, [mock.call()])


class TestBalancer(unittest.TestCase):

    def setUp(self):
        self.conf = mock.MagicMock()
        self.tenant_id = mock.MagicMock()
        self.mock_lb = mock.MagicMock(autospec=True)
        self.lb_id = mock.MagicMock(spec=int)
        self.lb_node = mock.MagicMock()
        self.lb_node_id = mock.MagicMock()
        self.lb_body = mock.MagicMock()
        self.patch_balancer = mock.patch("balancer.loadbalancers.vserver.Balancer")
        self.patch_scheduller = mock.patch("balancer.core.scheduller.Scheduller")
        self.lb_node_status = mock.MagicMock()

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

    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_details(self, mock_api):
        with self.patch_balancer:
            api.lb_show_details(self.conf, self.lb_id)
        self.assertTrue(mock_api.called)

    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_0(self, mock_driver, mock_commands):
        """No exception"""
        with self.patch_scheduller, self.patch_balancer:
            api.create_lb(self.conf, async=False)
        self.assertTrue(mock_driver.called)
        self.assertTrue(mock_commands.called)

    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_1(self, mock_driver, mock_commands):
        """Exception"""
        mock_driver.side_effect = exception.Error
        with self.patch_scheduller, self.patch_balancer:
            with self.assertRaises(exception.Error):
                api.create_lb(self.conf, async=False)
        self.assertTrue(mock_driver.called)
        self.assertFalse(mock_commands.called)

#    @mock.patch("balancer.drivers.get_device_driver")
#    def test_update_lb(self, mock_driver):
#        """No exception"""
#        with self.patch_balancer:
#            api.update_lb(self.conf, self.lb_id, self.lb_body, async=False)
#        self.assert

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.delete_loadbalancer")
    def test_delete_lb(self, mock_command, mock_driver):
        with self.patch_balancer:
            api.delete_lb(self.conf, self.lb_id)
        self.assertTrue(mock_command.called)
        self.assertTrue(mock_driver.called)

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_node_to_loadbalancer")
    def test_lb_add_node(self, mock_command, mock_driver):
        with self.patch_balancer:
            api.lb_add_node(self.conf, self.lb_id, self.lb_node)
        self.assertTrue(mock_command.called)
        self.assertTrue(mock_driver.called)

#    @mock.patch("balancer.db.api.unpack_extra")
#    def test_lb_show_nodes(self, mock_api):
#        with self.patch_balancer:
#            api.lb_show_nodes(self.conf, self.lb_id)
#        self.assertTrue(mock_api.called)

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.remove_node_from_loadbalancer")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.server_destroy")
    def test_lb_delete_node(self, *mocks):
        with self.patch_balancer:
            api.lb_delete_node(self.conf, self.lb_id, self.lb_node_id)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.activate_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_0(self, *mocks):
        """Activate server called"""
        self.lb_node_status = "inservice"
        with self.patch_balancer:
            api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
                    self.lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.suspend_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_1(self, *mocks):
        """Suspend server called"""
        self.lb_node_status = ""
        with self.patch_balancer:
            api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
                    self.lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

#    @mock.patch("balancer.db.api.server_update")
#    @mock.patch("balancer.drivers.get_device_driver")
#    @mock.patch("balancer.core.commands.suspend_rserver")
#    @mock.patch("balancer.db.api.server_get")
#    def test_lb_change_node_status_2(self, *mocks):
#        """return ok"""
#        for mok in mocks:
#            self.lb_node_status = mok[2]
#        with self.patch_balancer:
#            api.lb_change_node_status(self.conf, self.lb_id, self.lb_node_id,
#                    self.lb_node_status)
#        for mok in mocks:
#            self.assertEquals(self.lb_node_status, mok[2])


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
