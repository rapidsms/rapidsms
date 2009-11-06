#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, threading
from rapidsms.router import Router
from rapidsms.backends.base import BackendBase
from rapidsms.tests.harness import MockApp, MockLogger


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router(prevent=False)

    def test_log(self):
        ### TODO
        pass

    def test_set_logger(self):
        ### TODO
        pass

    def test_build_component(self):
        ### TODO
        pass

    def test_add_backend(self):
        ### TODO
        pass

    def test_add_app(self):
        ### TODO
        pass

    def test_start_backend(self):
        ### TODO
        pass
                 
    def test_start_all_apps(self):
        ### TODO
        pass

    def test_start_all_backends(self):
        ### TODO
        pass

    def test_stop_all_backends(self):
        ### TODO
        pass

    def test_start_and_stop(self):
        pass

    def test_run(self):
        pass

    def test_incoming(self):
        pass
   
    def test_outgoing(self):
        pass
