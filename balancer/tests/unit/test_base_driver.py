import unittest
import mock

from .test_db_api import device_fake1
from balancer.drivers.base_driver import BaseDriver


class TestBaseDriver(unittest.TestCase):
    def setUp(self):
        super(TestBaseDriver, self).setUp()
        self.conf = mock.Mock()

    def test_get_capabilities(self):
        """Test without capabilities"""
        base_driver = BaseDriver(self.conf, device_fake1)
        self.assertEqual(base_driver.get_capabilities(), None)

    def test_get_capabilities1(self):
        """Test with capabilities"""
        capabilities = {'capabilities': {
                        'algorithms': ['algo1', 'algo2'],
                        'protocols': ['udp', 'tcp']}}
        device_fake1['extra'] = capabilities
        base_driver = BaseDriver(self.conf, device_fake1)
        self.assertDictEqual(base_driver.get_capabilities(),
                             capabilities['capabilities'])
