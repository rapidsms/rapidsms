import time
import threading

from nose.tools import assert_equals

from rapidsms.apps.base import AppBase
from rapidsms.backends.base import BackendBase
from rapidsms.router.legacy import LegacyRouter


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
