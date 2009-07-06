#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest, time
from rapidsms.message import Message
from rapidsms.backends.backend import Backend
from rapidsms.connection import Connection
from rapidsms.person import Person
from harness import MockRouter

class TestMessage(unittest.TestCase):
    def setUp (self):
        self.router = MockRouter()
        self.backend = Backend(self.router)
        self.connection = Connection(self.backend, "12345")
        self.person = Person()
        self.person.add_connection(self.connection)
        self.router.add_backend(self.backend)

    def test__init__ (self): 
        msg = Message(self.connection, "this is a test")
        self.assertEquals(msg.connection, self.connection, "connection is right (connection)")
        msg = Message(None, "this is a test", self.person)
        self.assertEquals(msg.connection, self.connection, "connection is right (person)")
        self.assertEquals(msg.text, "this is a test", "text is right")
        self.assertEquals(msg.responses, [], "responses is empty")
        self.assertRaises(Exception, Message)

    def test__unicode__ (self):
        msg = Message(self.connection, "this is a test")
        self.assertEquals(unicode(msg), "this is a test", "unicode is right")
    
    def test_peer (self):
        msg = Message(self.connection, "this is a test")
        self.assertEquals(msg.peer, "12345", "peer identifier is right")

    def test_send (self):
        self.router.start()
        msg = Message(self.connection, "this is a test")
        self.assertTrue(msg.send(), "message was sent")
        waiting = self.backend.next_message()
        self.assertEquals(msg, waiting, "the backend got the message")
        self.router.stop()

    def test_respond (self):
        msg = Message(self.connection, "this is a test")
        msg.respond("how did it go?")
        msg.respond("okay?")
        self.assertEquals(len(msg.responses), 2, "message queues responses")
        self.assertEquals(msg.responses[0].text, "how did it go?", "it went well")
        self.assertEquals(msg.responses[1].text, "okay?", "sure enough")

    def test_flush_responses (self):
        msg = Message(self.connection, "this is a test")
        self.router.start()
        msg.respond("how did it go?")
        msg.flush_responses()
        
        waiting = self.backend.next_message()
        self.assertEquals(waiting.text, "how did it go?", "the backend got the message (1)")
        msg.respond("again?")
        msg.respond("and again?")
        msg.flush_responses()

        waiting = self.backend.next_message()
        self.assertEquals(waiting.text, "again?", "the backend got the message (2)")
        waiting = self.backend.next_message()
        self.assertEquals(waiting.text, "and again?", "the backend got the message (3)")
        self.router.stop()

if __name__ == "__main__":
    unittest.main()
