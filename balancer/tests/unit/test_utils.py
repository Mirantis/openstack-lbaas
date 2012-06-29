import unittest
import balancer.api.utils as utils


class TestHttpCode(unittest.TestCase):

    def test_http_code_decorator(self):

        @utils.http_success_code(202)
        def test_function():
            return

        self.assertTrue(hasattr(test_function, "wsgi_code") and
                        test_function.wsgi_code == 202,
                        "http_code_decorator doesn't work")
