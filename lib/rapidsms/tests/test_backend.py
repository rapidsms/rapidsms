#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, time
from rapidsms.backends.base import BackendBase
from rapidsms.messages.incoming import IncomingMessage


class MockRouter(object):
    def __init__(self):
        self.backends = []


class TestBackendBase(unittest.TestCase):
    def setUp (self):
        self.router = MockRouter()
        self.backend = BackendBase(self.router, "testing")
        #self.router.add_backend(self.backend)
        self.router.backends.append(self.backend)

    def test__properties (self):
        self.assertEquals(self.backend.name, "testing")
        self.assertEquals(self.backend.router, self.router)
        self.assertFalse(self.backend.running)

    #def test_start_stop (self):
    #    self.router.start()
    #    time.sleep(0.5)
    #    self.assertTrue(self.backend.running, "backend starts when router starts")
    #    self.router.stop()
    #    time.sleep(2.5)
    #    self.assertFalse(self.backend.running, "backend stops when router stops")
    
    def test_message (self):
        msg = self.backend.message("0000", "Good morning!") 
        self.assertEquals(type(msg), IncomingMessage, "message() returns an incomingmessage")

    #def test_route (self):
    #    msg = self.backend.message("0000", "Good morning!") 
    #    self.backend.route(msg)
    #    self.assertTrue(self.router.message_waiting, "backend sends to router")
