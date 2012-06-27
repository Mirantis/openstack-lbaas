# vim: tabstop=4 shiftwidth=4 softtabstop=4

import mock
import unittest
import types
#from balancer.core import commands
#from balancer.loadbalancers.vserver import Balancer
#from balancer.devices.DeviceMap import DeviceMap
#from balancer.core.scheduller import Scheduller
#from balancer.storage.storage import Storage
import balancer.core.api as api


@unittest.skip("fails")
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


@unittest.skip("requires balancer.storage module")
class TestBalancer(unittest.TestCase):

    def setUp(self):
        self.conf = mock.MagicMock()
        self.tenant_id = mock.MagicMock()
        self.store = mock.MagicMock(spec=Storage(self.conf))
        self.mock_lb = mock.MagicMock(autospec=True)
        self.patcher = mock.create_autospec('__main__.Balancer')
        #, autospec=True)

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

    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_details(self, mock_func):
        #, mock_obj):
        lb_id = mock.MagicMock(spec=int)
        #with mock.patch("balancer.loadbalancers.vserver.Balancer",
        #        autospec=True):
        api.lb_show_details(self.conf, lb_id)


@unittest.skip("fails")
class TestDevice(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock(register_group=mock.MagicMock)

    @mock.patch("balancer.db.api.device_get_all")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_device_get_index(self, mock_f1, mock_f2):
        mock_f2.__iter__.return_value = 1
        api.device_get_index(self.conf)
        self.assertTrue(mock_f2.called, "None")
#        self.assertTrue(mock_f1.called, "None")

    @mock.patch("balancer.db.api.device_pack_extra")
    @mock.patch("balancer.db.api.device_create")
    @mock.patch("balancer.core.scheduller.Scheduller")
    def test_device_create(self, mock_obj, mock_f1, mock_f2):
        api.device_create(self.conf)
        self.assertTrue(mock_f2.called, "device_pack_extra not called")
        self.assertTrue(mock_f1.called, "device_create not called")
        self.assertTrue(mock_obj.called, "scheduller not called")

    def test_device_info(self):
        params = {'query_params': 2}
        res = 1
        res = api.device_info(params)
        self.assertEquals(res, None, "Alyarma!")
