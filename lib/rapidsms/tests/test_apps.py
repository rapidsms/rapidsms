#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equals
from ..apps.base import AppBase


# since AppBase introspects its name based upon the django app which it
# is located in, if the module name changes, the tests fail. this would
# be misleading, since it's the renamed tests at fault, not AppBase. to
# avoid confusion, explode early with a more detailed error.
if not __name__.startswith("rapidsms.tests"):
    raise Exception(
        "This module must be within the 'rapidsms.tests' package for " +
        "the unit tests to work, since AppBase introspects its name.")


class MockRouter(object):
    pass


class AppStub(AppBase):
    pass


def test_app_exposes_router():
    router = MockRouter()
    app = AppStub(router)

    assert_equals(app.router, router)


def test_app_has_name():
    router = MockRouter()
    app = AppStub(router)

    assert_equals(repr(app), "<app: tests>")
    assert_equals(unicode(app), "tests")
    assert_equals(app.name, "tests")


def test_app_logs():
    router = MockRouter()
    app = AppStub(router)

    from logging.handlers import MemoryHandler
    import logging

    log = logging.getLogger()
    handler = MemoryHandler(999)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    app.debug("This is a DEBUG message")
    app.info("This is an INFORMATIVE message")
    app.warning("This is a WARNING")
    app.error("This is an ERROR")
    app.critical("This is a CRITICAL error")

    assert_equals(len(handler.buffer), 5)
    assert_equals(handler.buffer[2].name, "app/tests")
    assert_equals(handler.buffer[2].msg, "This is a WARNING")


def test_app_finds_valid_app_classes():
    app = AppBase.find('rapidsms.contrib.default')
    from rapidsms.contrib.default.app import App
    assert_equals(app, App)


def test_app_ignores_missing_app_classes():
    app = AppBase.find('rapidsms.contrib.djangoadmin')
    assert_equals(app, None)


def test_app_ignores_invalid_modules():
    app = AppBase.find('not.a.valid.module')
    assert_equals(app, None)
