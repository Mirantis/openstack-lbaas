import mock
import unittest

import balancer.core.scheduller as schedull
from balancer import exception as exp


def fake_filter(conf, lb_ref, dev_ref):
    return True if ord(dev_ref) > 98 else False


def fake_cost(conf, lb_ref, dev_ref):
    return 1. * ord(dev_ref)


class TestScheduller(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()
        self.lb_ref = mock.Mock()
        self.attrs = {'device_filters':
                 ['%s.fake_filter' % __name__],
                 'device_cost_functions':
                 ['%s.fake_cost' % __name__],
                 'device_cost_fake_cost_weight': 1.}
        self.conf.configure_mock(**self.attrs)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_no_proper_devs(self, dev_get_all):
        dev_get_all.return_value = ['a', 'b']
        with self.assertRaises(exp.NoValidDevice):
            schedull.schedule_loadbalancer(self.conf, self.lb_ref)
            self.assertTrue(dev_get_all.called)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_with_proper_devs(self, dev_get_all):
        dev_get_all.return_value = ['a', 'b', 'c', 'd']
        res = schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        self.assertTrue(dev_get_all.called)
        self.assertEqual('c', res)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_without_devices(self, dev_get_all):
        dev_get_all.return_value = []
        with self.assertRaises(exp.DeviceNotFound):
            schedull.schedule_loadbalancer(self.conf, self.lb_ref)
            self.assertTrue(dev_get_all.called)


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()
        self.lb_ref = {}
        self.dev_ref = {}

    def tearDown(self):
        self.lb_ref.clear()
        self.dev_ref.clear()

    def test_filter_capabilities_proper(self):
        self.conf.device_filter_capabilities = []
        self.lb_ref['algorithm'] = 'test'
        self.dev_ref.update({'extra': {'capabilities': {'algorithm': 'test'}}})
        res = schedull.filter_capabilities(self.conf, self.lb_ref,
                                           self.dev_ref)
        self.assertTrue(res)

    def test_filter_capabilities_not_proper(self):
        self.conf.device_filter_capabilities = []
        res = schedull.filter_capabilities(self.conf, self.lb_ref,
                                           self.dev_ref)
        self.assertFalse(res)


class TestWeigthsFunctions(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()
        self.lb_ref = {}
        self.dev_ref = {}

    @mock.patch('balancer.db.api.lb_count_active_by_device')
    def test_lbs_on(self, lb_count):
        lb_count.return_value = 3.
        self.dev_ref['id'] = '1'
        res = schedull.lbs_on(self.conf, self.lb_ref, self.dev_ref)
        self.assertEqual(res, 3.)