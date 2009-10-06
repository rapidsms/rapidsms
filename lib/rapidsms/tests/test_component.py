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

    def test_name(self):
        c = Component()
        self.assertEquals(c.name, "Component", "Component.name has a default")
        c.name = "TestComponent"
        self.assertEquals(c.name, "TestComponent", "Component.name can be set")

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

if __name__ == "__main__":
    unittest.main()
