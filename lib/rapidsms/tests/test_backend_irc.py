#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
from harness import MockRouter

class TestBackendIRC(unittest.TestCase):
    def test_backend_irc (self):
        router = MockRouter()
        try:
            import irclib
            from rapidsms.backends.irc import Backend
            backend = Backend(router)
            backend.configure(host="localhost",nick="test",channels="#test1,#test2")
            self.assertEquals(type(backend), Backend, "IRC backend loads")
            self.assertEquals(backend.nick, "test", "IRC backend has nick set")
            self.assertEquals(backend.host, "localhost", "IRC backend has host set")
            self.assertEquals(backend.channels, ["#test1","#test2"],
                              "IRC backend has channels correctly set")
        except ImportError:
            pass

if __name__ == "__main__":
    unittest.main()
