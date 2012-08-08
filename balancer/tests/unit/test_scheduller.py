import mock
import unittest
import balancer.core.scheduller as schedull


class TestScheduller(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock()

    @mock.patch('balancer.db.api.device_get_all')
    def test_schedule_loadbalancer(self, *mocs):
        lb_ref = {}
        schedull.schedule_loadbalancer(self.conf, lb_ref)
        for mock in mocs:
            self.assertTrue(mock.called)
