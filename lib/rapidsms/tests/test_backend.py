#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, time
from rapidsms.backends.base import BackendBase
from rapidsms.messages.incoming import IncomingMessage


class MockRouter(object):
    def __init__(self):
        self.backends = []
        self.incoming = []

    def incoming_message(self, msg):
        self.incoming.append(msg)


class TestBackendBase(unittest.TestCase):
    def setUp(self):
        self.router = MockRouter()
        self.backend = BackendBase(self.router, "testing")
        self.router.backends.append(self.backend)

    def test__properties(self):
        self.assertEquals(self.backend.name, "testing")
        self.assertEquals(self.backend.title, "Testing")
        self.assertEquals(self.backend.router, self.router)
        self.assertFalse(self.backend.running)

    def test_message(self):
        msg = self.backend.message("0000", "Good morning!") 
        self.assertEquals(type(msg), IncomingMessage, "message() returns an incomingmessage")

    def test_route(self):
        msg = self.backend.message("0000", "Good morning!") 
        self.backend.route(msg)
        self.assertTrue(msg in self.router.incoming, "backend routes to router")
