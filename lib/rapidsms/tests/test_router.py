#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import threading
from nose.tools import assert_equals, assert_raises
from django.utils.functional import curry
from django.core.exceptions import ImproperlyConfigured
from ..backends.base import BackendBase
from ..apps.base import AppBase
from ..router import get_router
from ..router.base import BaseRouter
from ..router.legacy import LegacyRouter


class MockRouter(object):
    pass


def test_get_router():
    assert_raises(ImproperlyConfigured, get_router,
                  'rapidsms.tests.test_router.BadClassName')
    assert_raises(ImproperlyConfigured, get_router,
                  'rapidsms.tests.bad_module.MockRouter')
    assert_equals(get_router('rapidsms.tests.test_router.MockRouter'),
                  MockRouter)

def test_router_finds_apps():
    router = BaseRouter()
    router.add_app("rapidsms.contrib.default")
    from rapidsms.contrib.default.app import App

    assert_equals(len(router.apps), 1)
    app = router.get_app("rapidsms.contrib.default")

    assert_equals(type(app), App)


def test_router_returns_none_on_invalid_apps():
    assert_equals(BaseRouter().get_app("not.a.valid.app"), None)


def test_router_raises_on_uninstalled_apps():
    assert_raises(KeyError, BaseRouter().get_app, "rapidsms.contrib.default")


def test_legacy_router_starts_and_stops_apps_and_backends():
    class MockApp(AppBase):
        def start(self):
            self.started = True

        def stop(self):
            self.stopped = True

    class MockBackend(BackendBase):
        def start(self):
            self.started = True
            BackendBase.start(self)

        def stop(self):
            self.stopped = True
            BackendBase.stop(self)

    router = LegacyRouter()
    app = MockApp(router)
    router.apps.append(app)
    backend = MockBackend(router, "mock")
    router.backends["mock"] = backend

    assert hasattr(app, 'started') == False
    assert hasattr(app, 'stopped') == False
    assert hasattr(backend, 'started') == False
    assert hasattr(backend, 'stopped') == False

    # start in a separate thread, so we can test it asynchronously.
    worker = threading.Thread(target=router.start)
    worker.daemon = True
    worker.start()

    # wait until the router has started.
    while not router.running:
        time.sleep(0.1)

    assert_equals(app.started, True)
    assert_equals(backend.started, True)
    assert hasattr(app, 'stopped') == False
    assert hasattr(backend, 'stopped') == False

    # wait until the router has stopped.
    router.stop()
    worker.join()

    assert_equals(app.started, True)
    assert_equals(app.stopped, True)
    assert_equals(backend.started, True)
    assert_equals(backend.stopped, True)


def test_router_finds_backends():
    router = BaseRouter()
    test_backend = "rapidsms.backends.base"
    backend = router.add_backend("mock", test_backend)

    assert_equals(router.backends["mock"], backend)
    assert_equals(len(router.backends), 1)


def test_router_downcases_backend_configs():
    router = BaseRouter()
    test_backend = "rapidsms.backends.base"
    test_conf = { "a": 1, "B": 2, "Cc": 3 }

    backend = router.add_backend("mock", test_backend, test_conf)

    assert_equals(len(backend._config), 3)
    assert_equals("a"  in backend._config, True)
    assert_equals("b"  in backend._config, True)
    assert_equals("cc" in backend._config, True)
    assert_equals("B"  in backend._config, False)
    assert_equals("Cc" in backend._config, False)


def test_router_calls_all_app_phases():
    class MockMsg(object):
        connection = None
        text = ''
        handled = False

    class MockApp(AppBase):
        start_phases = ["start"]
        incoming_phases = ["filter", "parse", "handle", "default", "cleanup"]
        outgoing_phases = ["outgoing"]
        stop_phases = ["stop"]
        called_phases = []
        
        def _append_phase(self, phase, *args, **kwargs):
            self.called_phases.append(phase)
            return False

        def __init__(self, router):
            phases = self.start_phases + self.incoming_phases +\
                     self.outgoing_phases + self.stop_phases
            for phase in phases:
                setattr(self, phase, curry(self._append_phase, phase))
            super(MockApp, self).__init__(router)
            
    router = BaseRouter()
    app = MockApp(router)
    router.apps.append(app)
    router.incoming(MockMsg())
    assert_equals(app.called_phases, app.incoming_phases)
    app.called_phases = []
    router.outgoing(MockMsg())
    assert_equals(app.called_phases, app.outgoing_phases)
    app.called_phases = []
    router.start()
    assert_equals(app.called_phases, app.start_phases)
    app.called_phases = []
    router.stop()
    assert_equals(app.called_phases, app.stop_phases)

