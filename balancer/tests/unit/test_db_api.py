import unittest
import mock
import tempfile
import os

from balancer.db import api as db_api
from balancer.db import session
from balancer import exception


device_fake1 = {'name': 'fake1',
                'type': 'FAKE',
                'version': '1',
                'ip': '10.0.0.10',
                'port': 1010,
                'user': 'user1',
                'password': 'secrete1',
                'extra': {'supports_vlan': False}}

device_fake2 = {'name': 'fake2',
                'type': 'FAKE',
                'version': '2',
                'ip': '10.0.0.20',
                'port': 2020,
                'user': 'user2',
                'password': 'secrete2',
                'extra': {'supports_vlan': True,
                          'vip_vlan': 10,
                          'requires_vip_ip': True}}


class TestExtra(unittest.TestCase):
    def test_pack_extra(self):
        model = mock.MagicMock()
        model_inst = model()
        model_inst.__iter__.return_value = ['name', 'type']
        values = {'name': 'fakename', 'type': 'faketype', 'other': 'fakeother'}
        obj_ref = db_api.pack_extra(model, values)
        expected = [mock.call('name', 'fakename'),
                    mock.call('type', 'faketype'),
                    mock.call('extra', {'other': 'fakeother'})]
        self.assertTrue(model_inst.__iter__.called)
        self.assertEqual(model_inst.__setitem__.mock_calls, expected)

    def test_unpack_extra(self):
        obj_ref = {'name': 'fakename',
                   'type': 'faketype',
                   'extra': {'other': 'fakeother'}}
        values = db_api.unpack_extra(obj_ref)
        expected = {'name': 'fakename',
                    'type': 'faketype',
                    'other': 'fakeother'}
        self.assertEqual(values, expected)


class TestDBAPI(unittest.TestCase):
    def setUp(self):
        _, filename = tempfile.mkstemp()
        self.filename = filename
        self.conf = mock.Mock()
        self.conf.sql.connection = "sqlite:///%s" % self.filename
        session.sync(self.conf)

    def tearDown(self):
        os.remove(self.filename)

    def test_device_create(self):
        device_ref = db_api.device_create(self.conf, device_fake1)
        self.assertIsNotNone(device_ref['id'])
        self.assertEqual(device_ref['name'], device_fake1['name'])
        self.assertEqual(device_ref['type'], device_fake1['type'])
        self.assertEqual(device_ref['version'], device_fake1['version'])
        self.assertEqual(device_ref['ip'], device_fake1['ip'])
        self.assertEqual(device_ref['port'], device_fake1['port'])
        self.assertEqual(device_ref['user'], device_fake1['user'])
        self.assertEqual(device_ref['password'], device_fake1['password'])
        self.assertEqual(device_ref['extra'], device_fake1['extra'])

    def test_device_update(self):
        device_ref = db_api.device_create(self.conf, device_fake1)
        self.assertIsNotNone(device_ref['id'])
        device_update = {'password': 'test',
                         'extra': {'supports_vlan': True,
                                   'vip_vlan': 100,
                                   'requires_vip_ip': True}}
        device_ref = db_api.device_update(self.conf, device_ref['id'],
                                          device_update)
        self.assertIsNotNone(device_ref['id'])
        self.assertEqual(device_ref['name'], device_fake1['name'])
        self.assertEqual(device_ref['type'], device_fake1['type'])
        self.assertEqual(device_ref['version'], device_fake1['version'])
        self.assertEqual(device_ref['ip'], device_fake1['ip'])
        self.assertEqual(device_ref['port'], device_fake1['port'])
        self.assertEqual(device_ref['user'], device_fake1['user'])
        self.assertEqual(device_ref['password'], device_update['password'])
        self.assertEqual(device_ref['extra'], device_update['extra'])

    def test_device_get_all(self):
        device_ref1 = db_api.device_create(self.conf, device_fake1)
        device_ref2 = db_api.device_create(self.conf, device_fake2)
        devices = db_api.device_get_all(self.conf)
        self.assertEqual(len(devices), 2)

    def test_device_get(self):
        device_ref1 = db_api.device_create(self.conf, device_fake1)
        device_ref2 = db_api.device_create(self.conf, device_fake2)
        dev1 = db_api.device_get(self.conf, device_ref1['id'])
        dev2 = db_api.device_get(self.conf, device_ref2['id'])
        self.assertEqual(dict(dev1.iteritems()), dict(device_ref1.iteritems()))
        self.assertEqual(dict(dev2.iteritems()), dict(device_ref2.iteritems()))

    def test_device_delete(self):
        device_ref = db_api.device_create(self.conf, device_fake1)
        db_api.device_destroy(self.conf, device_ref['id'])
        with self.assertRaises(exception.DeviceNotFound) as cm:
            db_api.device_get(self.conf, device_ref['id'])
        err = cm.exception
        self.assertEqual(err.kwargs, {'device_id': device_ref['id']})
