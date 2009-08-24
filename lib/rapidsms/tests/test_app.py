#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
from rapidsms.app import App
from harness import MockRouter

class TestApp(unittest.TestCase):

    def setUp(self):
        self.router = MockRouter()

    def test___init__(self):
        app = App(self.router)
        self.assertEqual(self.router, app.router,
            "failed to set router")

    def test_api(self):
        app = App(self.router)
        api_methods = (
            'start',
            'parse',
            'handle',
            'cleanup',
            'outgoing',
            'stop')
        for method in api_methods:
            self.assertTrue(hasattr(app, method), 
                "app does not have attribute '%s'" % method)
            self.assertTrue(callable(getattr(app, method)),
                "attribute '%s' is not callable" % method)


if __name__ == "__main__":
    unittest.main()
