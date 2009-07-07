#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
from harness import MockRouter
from rapidsms.backends.spomc import Backend
from spomsky import Client

class TestBackendSpomc(unittest.TestCase):
    def test_backend_spomc (self):
        router = MockRouter()
        backend = Backend(router)
        backend.configure(host="localhost",port=65000)
        self.assertEquals(type(backend), Backend, "SPOMC backend loads")
        self.assertEquals(type(backend.client), Client, "SPOMC backend has Spomsky client")

if __name__ == "__main__":
    unittest.main()
