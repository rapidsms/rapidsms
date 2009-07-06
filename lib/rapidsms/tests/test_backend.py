#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest, time
from rapidsms.backends.backend import Backend
from rapidsms.message import Message
from harness import MockRouter

class TestBackend(unittest.TestCase):
    def setUp (self):
        self.router = MockRouter()
        self.backend = Backend(self.router)
        self.router.add_backend(self.backend)

    def test__properties (self):
        self.assertEquals(self.backend.title, "backend")
        self.assertEquals(self.backend.router, self.router)
        self.assertFalse(self.backend.running)

    def test_start_stop (self):
        self.router.start()
        time.sleep(0.5)
        self.assertTrue(self.backend.running, "backend starts when router starts")
        self.router.stop()
        time.sleep(2.5)
        self.assertFalse(self.backend.running, "backend stops when router stops")
    
    def test_message (self):
        msg = self.backend.message("0000", "Good morning!") 
        self.assertEquals(type(msg), Message, "message() returns a message")

    def test_route (self):
        msg = self.backend.message("0000", "Good morning!") 
        self.backend.route(msg)
        self.assertTrue(self.router.message_waiting, "backend sends to router")

if __name__ == "__main__":
    unittest.main()
