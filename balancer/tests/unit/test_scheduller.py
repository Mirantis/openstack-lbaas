import mock
import unittest

import balancer.core.scheduller as schedull
from balancer.exception import NoValidDevice, DeviceNotFound


def fake_filter(lb_ref, dev_ref):
    return True if dev_ref > 3 else False


def fake_cost(lb_ref, dev_ref):
    return 1.


class TestScheduller(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()
        self.lb_ref = mock.Mock()

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_without_filters(self, mocks):
        try:
            schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        except NoValidDevice:
            pass
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_with_filters(self, dev_get_all):
        attrs = {'device_filters':
                 ['balancer.tests.unit.test_scheduller.fake_filter'],
                 'device_cost_functions':
                 ['balancer.tests.unit.test_scheduller.fake_cost'],
                 'device_cost_fake_cost_weight': 1.}
        self.conf.configure_mock(**attrs)
        dev_get_all.return_value = [1, 2, 3, 4, 5]
        schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        self.assertTrue(dev_get_all.called)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_without_devices(self, dev_get_all):
        dev_get_all.return_value = []
        try:
            schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        except DeviceNotFound:
            pass
        self.assertTrue(dev_get_all.called)
