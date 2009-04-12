#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest, threading
from rapidsms.router import Router
from rapidsms.backends.backend import Backend
from rapidsms.tests.harness import MockApp, MockLogger

class TestRouter(unittest.TestCase):
    def test_log(self):
        r = Router()
        r.logger = MockLogger()
        r.log("debug", "test message", 5)
        self.assertEquals(r.logger[0], (r,"debug","test message",5),
            "log() calls self.logger.write()")

    def test_set_logger(self):
        ### TODO
        pass

    def test_build_component (self):
        r = Router()
        r.logger = MockLogger()
        component = r.build_component("rapidsms.tests.%s.MockApp", 
                        {"type":"harness", "title":"test app"})
        self.assertEquals(type(component), MockApp, "component has right type")
        self.assertEquals(component.name, "test app", "component has right title")
        self.assertRaises(Exception, r.build_component, 
            ("rapidsms.tests.%s.MockApp", 
             {"type":"harness", "title":"test app", "argh": "no config"}),
            "build_component gracefully handles bad configuration options")

    def test_add_backend (self):
        r = Router()
        r.logger = MockLogger()
        r.add_backend({"type":"backend", "title":"test_backend"})
        self.assertEquals(len(r.backends), 1, "backends has 1 item")
        self.assertEquals(type(r.backends[0]), Backend, "backend has correct type")

    def test_add_app (self):
        ### TODO
        pass

    def test_start_backend (self):
        ### TODO
        pass
                 
    def test_start_all_apps (self):
        ### TODO
        pass

    def test_start_all_backends (self):
        ### TODO
        pass

    def test_stop_all_backends (self):
        ### TODO
        pass

    def test_start_and_stop (self):
        pass

    def test_run(self):
        pass

    def test_incoming(self):
        pass
   
    def test_outgoing(self):
        pass

if __name__ == "__main__":
    unittest.main()
