#import functools
#import logging
#import types

#from balancer.common import utils
#from balancer.db import api as db_api
import balancer.core.commands as cmd
from unittest import TestCase
from mock import Mock


class TestRollbackContext(TestCase):
    def __init__(self):
        self.rollback = Mock()
        self.rollback.return_value = "foo"
        self.obj = cmd.RollbackContext()

    def test_add_rollback(self):
        res = self.obj.add_rollback(self.rollback)
        self.assertEquals(res, "foo", "Something wrong")


class TestRollbackContextManager(TestCase):
    def __init__(self):
        self.obj = cmd.RollbackContextManager()
        self.obj.context = Mock()
        self.obj.context.return_value = "foo"
#don' really know how to test __init__ func
#    def test_init(self):
#       res = self.obj.__init__(context=Mock())
#      self

    def test_enter(self):
        res = self.obj.__enter__()
        self.assertEquals(res, "foo", "Something wrong")

    def test_exit(self):
        res = self.obj.__exit__(None, None, None)
        self.assertEquals(res, None, "Something wrong")
        exc_type = Mock()
        exc_value = Mock()
        exc_tb = Mock()
        exc_value.return_value = "foo"
        exc_type.return_value = "foo"
        exc_tb.return_value = "foo"
        res = self.obj.__exit__(exc_type, exc_value, exc_tb)
        self.assertEquals(res, "foo foo foo", "Something wrong")
