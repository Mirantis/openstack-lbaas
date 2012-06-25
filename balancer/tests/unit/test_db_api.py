import unittest
import mock
import tempfile
import os

from balancer.db import api as db_api
from balancer.db import session
from balancer import exception


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
        values = {'name': 'fake1',
                  'type': 'FAKE',
                  'version': '1',
                  'ip': '10.0.0.10',
                  'port': 2020,
                  'user': 'user',
                  'password': 'secrete',
                  'extra': {'vip_vlan': 75}}
        device_ref = db_api.device_create(self.conf, values)
        self.assertIsNotNone(device_ref['id'])
        self.assertEqual(device_ref['name'], values['name'])
        self.assertEqual(device_ref['type'], values['type'])
        self.assertEqual(device_ref['version'], values['version'])
        self.assertEqual(device_ref['ip'], values['ip'])
        self.assertEqual(device_ref['port'], values['port'])
        self.assertEqual(device_ref['user'], values['user'])
        self.assertEqual(device_ref['password'], values['password'])
        self.assertEqual(device_ref['extra'], values['extra'])

    def test_device_update(self):
        values = {'name': 'fake1',
                  'type': 'FAKE',
                  'version': '1',
                  'ip': '10.0.0.10',
                  'port': 2020,
                  'user': 'user',
                  'password': 'secrete',
                  'extra': {'vip_vlan': 75}}
        device_ref = db_api.device_create(self.conf, values)
        self.assertIsNotNone(device_ref['id'])
        self.assertEqual(device_ref['password'], values['password'])
        update_values = {'password': 'test',
                         'extra': {'vip_vlan': 75,
                                   'requires_vip_ip': 1}}
        device_ref = db_api.device_update(self.conf, device_ref['id'],
                                          update_values)
        self.assertIsNotNone(device_ref['id'])
        self.assertEqual(device_ref['name'], values['name'])
        self.assertEqual(device_ref['type'], values['type'])
        self.assertEqual(device_ref['version'], values['version'])
        self.assertEqual(device_ref['ip'], values['ip'])
        self.assertEqual(device_ref['port'], values['port'])
        self.assertEqual(device_ref['user'], values['user'])
        self.assertEqual(device_ref['password'], update_values['password'])
        self.assertEqual(device_ref['extra'], update_values['extra'])
