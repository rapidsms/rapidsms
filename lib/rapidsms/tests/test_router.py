#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest, threading, time, datetime
from rapidsms.router import Router
from rapidsms.connection import Connection
from rapidsms.message import Message
from rapidsms.backends.backend import Backend
from rapidsms.tests.harness import MockApp, MockLogger

class TestRouter(unittest.TestCase):
    def test_log(self):
        r = Router()
        r.logger = MockLogger()
        r.log("debug", "test message %d", 5)
        self.assertEquals(r.logger[0], (r,"debug","test message %d",5),
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
        self.assertEquals(component.title, "test app", "component has right title")
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
        r = Router()
        r.logger = MockLogger()
        threading.Thread(target=r.start).start()
        self.assertTrue(r.running)
        r.stop()
        self.assertTrue(not r.running) 
        # not waiting for the router to shutdown causes exceptions
        # on global destruction. (race condition)
        time.sleep(1.0)

    def test_run(self):
        r = Router()
        r.logger = MockLogger()
        app = r.build_component("rapidsms.tests.%s.MockApp", 
                        {"type":"harness", "title":"test app"})
        r.apps.append(app)
        r.add_backend({"type":"backend", "title":"test_backend"})
        backend = r.get_backend("test-backend") # NOTE the dash; FIXME
        msg = backend.message("test user", "test message")
        r.send(msg)
        r.run()
        received = app.calls[-1][1]
        self.assertEquals(msg, received, "message is identical")
        self.assertEquals(msg.connection, received.connection, "same connection")
        self.assertEquals(msg.text, received.text, "same text")

    def test_call_at (self):
        def callback(stash, arg1, **argv):
            stash["arg1"]=arg1
            if "try_again" in argv and "try_again" not in stash:
                stash["try_again"] = False
                return 1.0
            else:
                stash.update(argv)
        r = Router()
        r.logger = MockLogger()
        stash = {}
        r.call_at(0.5, callback, stash, 1, arg2="a")
        r.call_at(datetime.datetime.now() + datetime.timedelta(seconds=0.5), callback, stash, 1, arg3="b")
        r.call_at(datetime.timedelta(seconds=1.0), callback, stash, 1, try_again=True)
        r.call_at(3, callback, stash, 2)
        threading.Thread(target=r.start).start()
        time.sleep(1.0)
        self.assertEquals(stash["arg1"], 1, "*args ok")
        self.assertEquals(stash["arg2"], "a", "**kargs ok")
        self.assertEquals(stash["arg3"], "b", "datetime works")
        self.assertEquals(stash["try_again"], False, "timedelta works")
        time.sleep(3.0)
        self.assertEquals(stash["try_again"], True, "repeated callback")
        self.assertEquals(stash["arg1"], 2, "int works")
        r.stop()

    def test_incoming(self):
        pass
   
    def test_outgoing(self):
        pass

if __name__ == "__main__":
    unittest.main()
