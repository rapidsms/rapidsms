#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
from rapidsms.component import Component, Receiver
import threading, time

class TestComponent(unittest.TestCase):
    def test_router (self):
        c = Component()
        self.assertEquals(c.router, None, "no router set yet")
        c._router = "(router)"
        self.assertEquals(c.router, "(router)", "router can be set")

    def test_title(self):
        c = Component()
        self.assertEquals(c.title, "component", "Component.title has a default")
        c._title = "TestComponent"
        self.assertEquals(c.title, "TestComponent", "Component.title can be set")

    def test_config_requires(self):
        c = Component()
        self.assertEquals(c.config_requires("example", "hello"), "hello",
            "config_requires returns value if not None")
        self.assertRaises(Exception, c.config_requires, "example", None,
            "config_requires raises an Exception if value is None")

    def test_config_bool (self):
        c = Component()
        self.assertTrue(c.config_bool("true"), "config_bool accepts true")
        self.assertTrue(c.config_bool("True"), "config_bool accepts True")
        self.assertTrue(c.config_bool("yes"), "config_bool accepts yes")
        self.assertTrue(c.config_bool("YES"), "config_bool accepts YES")
        self.assertFalse(c.config_bool("false"), "config_bool accepts false")
        self.assertFalse(c.config_bool("no"), "config_bool accepts no")

    def test_config_list (self):
        c = Component()
        self.assertEquals(c.config_list("a,b,c"),["a","b","c"], "config_list parses str")
        self.assertEquals(c.config_list(["a","b"]),["a","b"], "config_list copies list")
        self.assertEquals(c.config_list("a"),["a"], "config_list creates len-1 list")

    def test__logging_method(self):
        self.assertTrue(callable(Component.debug), "Component has debug log method")
        self.assertTrue(callable(Component.info), "Component has info log method")
        self.assertTrue(callable(Component.warning), "Component has warning log method")
        self.assertTrue(callable(Component.error), "Component has error log method")
        self.assertTrue(callable(Component.critical), "Component has critical log method")

class TestReceiver(unittest.TestCase):
    def test_message_waiting(self):
        r = Receiver()
        r.send("message 1")
        self.assertEquals(r.message_waiting, 1, "1 message is waiting")

    def test_next_message (self):
        r = Receiver()
        self.assertEquals(r.next_message(), None, "no message waiting")
        r.send("message 2")
        self.assertEquals(r.next_message(), "message 2", "got a message")
        self.assertEquals(r.next_message(), None, "message was removed")

        def send_a_message_later (secs):
            time.sleep(secs)
            r.send("message 3")
        
        thread = threading.Thread(target=send_a_message_later, args=(0.5,))
        thread.start()
        self.assertEquals(r.next_message(5.0), "message 3", "block and wait")        

        thread = threading.Thread(target=send_a_message_later, args=(5.0,))
        thread.start()
        self.assertEquals(r.next_message(0.5), None, "next_msg doesn't block too long")        
if __name__ == "__main__":
    unittest.main()
