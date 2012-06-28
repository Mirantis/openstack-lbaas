# vim: tabstop=4 shiftwidth=4 softtabstop=4

import mock
import unittest
import types
#from balancer.core import commands
from balancer.loadbalancers.vserver import Balancer
#from balancer.devices.DeviceMap import DeviceMap
#from balancer.core.scheduller import Scheduller
#from balancer.storage.storage import Storage
import balancer.core.api as api


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
        self.patcher = mock.create_autospec(Balancer)
        self.lb_id = mock.MagicMock(spec=int)
        self.body = mock.MagicMock(keys=mock.MagicMock)
        self.body.keys.__iter__ = mock.MagicMock(return_value=iter([1, 2, 3]))
        self.lb_node = mock.MagicMock()
        self.lb_node_id = mock.MagicMock()

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
        lb_id = mock.Mock()
        lb_id.return_value = ""
        api.lb_get_data(self.conf, lb_id)
        self.assertTrue(mock_api.called)

#    @mock.patch("balancer.loadbalancers.vserver.Balancer.loadFromDB")
#    @mock.patch("balancer.db.api.unpack_extra")
#    def test_lb_show_details(self, mock_f1, mock_f2):
#        api.lb_show_details(self.conf, self.lb_id)
#        self.assertTrue(mock_f1.called)
#        self.assertTrue(mock_f2.called)
#
#    @mock.patch("balancer.core.scheduller.Scheduller.Instance.getDeviceByID")
#    @mock.patch("balancer.core.scheduller.Scheduller.Instance")
#    @mock.patch("balancer.loadbalancers.vserver.Balancer.parseParams")
#    @mock.patch("balancer.loadbalancers.vserver.Balancer.getLB")
#    @mock.patch("balancer.loadbalancers.vserver.Balancer.savetoDB")
#    @mock.patch("balancer.drivers.get_device_driver")
#    @mock.patch("balancer.core.scheduller.Scheduller.Instance")
#    @mock.patch("balancer.loadbalancers.vserver.Balancer")
#            #, autospec=True)
#    def test_create_lb_0(self, mock_obj1, mock_obj2):
#            #, mock_1, mock_2, mock_3,
#            #mock_4, mock_5, mock_6):
#        mock_obj1.parseParams = mock.MagicMock()
#        api.create_lb(self.conf, async=False)
#        self.assertTrue(mock_1.called)
#        self.assertTrue(mock_2.called)
#        self.assertTrue(mock_3.called)
#        self.assertTrue(mock_4.called)
#        self.assertTrue(mock_5.called)

    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.loadbalancers.vserver.Balancer", autospec=True)
    def test_update_lb(self, mock_f1, mock_2, mock_3, mock_4, mock_5, mock_6,
            mock_7, mock_8, mock_9, mock_10):
        api.update_lb(self.conf, self.lb_id, self.body, async=False)

    @mock.patch("balancer.db.api.sticky_destroy_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_destroy_by_sf_id")
    @mock.patch("balancer.db.api.probe_destroy_by_sf_id")
    @mock.patch("balancer.db.api.server_destroy_by_sf_id")
    @mock.patch("balancer.db.api.predictor_destroy_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_destroy")
    @mock.patch("balancer.db.api.loadbalancer_destroy")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.loadbalancers.vserver.Balancer", autospec=True)
    def test_delete_lb(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6,
            mock_7, mock_8, mock_9, mock_10, mock_11, mock_12, mock_13,
            mock_14, mock_15, mock_16):
        api.delete_lb(self.conf, self.lb_id)
        self.assertTrue(mock_3.called)

    @mock.patch("balancer.core.commands.add_node_to_loadbalancer")
    @mock.patch("balancer.db.api.predictor_update")
    @mock.patch("balancer.db.api.serverfarm_update")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.sticky_destroy_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_destroy_by_sf_id")
    @mock.patch("balancer.db.api.probe_destroy_by_sf_id")
    @mock.patch("balancer.db.api.server_destroy_by_sf_id")
    @mock.patch("balancer.db.api.predictor_destroy_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_destroy")
    @mock.patch("balancer.db.api.loadbalancer_destroy")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.loadbalancers.vserver.Balancer", autospec=True)
    def test_lb_add_node(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6,
            mock_7, mock_8, mock_9, mock_10, mock_11, mock_12, mock_13,
            mock_14, mock_15, mock_16, mock_17, mock_18, mock_19, mock_20):
        api.lb_add_node(self.conf, self.lb_id, self.lb_node)
        self.assertTrue(mock_20.called)
#   def lb_show_nodes(self):

    @mock.patch("balancer.core.commands.remove_node_from_loadbalancer")
    @mock.patch("balancer.db.api.server_destroy")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.predictor_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.loadbalancers.vserver.Balancer", autospec=True)
    def test_lb_delete_node(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6,
            mock_7, mock_8, mock_9, mock_10, mock_11, mock_12):
        api.lb_delete_node(self.conf, self.lb_id, self.lb_node_id)
        self.assertTrue(mock_12.called)


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
