import time
import threading

from nose.tools import assert_equals

from rapidsms.apps.base import AppBase
from rapidsms.backends.base import BackendBase
from rapidsms.router.legacy import LegacyRouter


def test_legacy_router_starts_and_stops_apps_and_backends():
    class MockApp(AppBase):
        start_called = False
        stop_called = False

        def start(self):
            self.start_called = True

        def stop(self):
            self.stop_called = True

    class MockBackend(BackendBase):
        start_called = False
        stop_called = False

        def start(self, *args, **kwargs):
            self.start_called = True
            BackendBase.start(self, *args, **kwargs)

        def stop(self):
            self.stop_called = True
            BackendBase.stop(self)

    router = LegacyRouter()
    app = MockApp(router)
    router.apps.append(app)
    backend = MockBackend(router, "mock")
    router.backends["mock"] = backend

    assert_equals(app.start_called, False)
    assert_equals(app.stop_called, False)
    assert_equals(backend.start_called, False)
    assert_equals(backend.stop_called, False)

    # start in a separate thread, so we can test it asynchronously.
    worker = threading.Thread(target=router.start)
    worker.daemon = True
    worker.start()

    # wait until the router has started.
    while not router.running:
        time.sleep(0.3)

    assert_equals(app.start_called, True)
    assert_equals(backend.start_called, True)
    assert_equals(app.stop_called, False)
    assert_equals(backend.stop_called, False)

    # wait until the router has stopped.
    router.stop()
    worker.join()

    assert_equals(app.start_called, True)
    assert_equals(app.stop_called, True, 'App not stopped')
    assert_equals(backend.start_called, True)
    assert_equals(backend.stop_called, True, 'Backend not stopped')
