import mock
import unittest
import balancer.core.scheduller as schedull


def fake_filter(*args):
    return True


def fake_cost(*args):
    return 1.


class TestScheduller(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()
        self.lb_ref = mock.Mock()

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_without_filters(self, *mocks):
        schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch('balancer.db.api.device_get_all')
    def test_scheduler_with_filters(self, *mocks):
        attrs = {'device_filters':
                 ['balancer.tests.unit.test_scheduller.fake_filter'],
                 'device_cost_functions':
                 ['balancer.tests.unit.test_scheduller.fake_cost'],
                 'device_cost_fake_cost_weight': 1.}
        self.conf.configure_mock(**attrs)
        schedull.schedule_loadbalancer(self.conf, self.lb_ref)
        for mock in mocks:
            self.assertTrue(mock.called)
