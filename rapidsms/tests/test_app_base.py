#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase

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


class AppBaseTest(TestCase):

    def test_app_exposes_router(self):
        router = MockRouter()
        app = AppStub(router)
        self.assertEqual(app.router, router)

    def test_app_has_name(self):
        router = MockRouter()
        app = AppStub(router)
        self.assertEqual(repr(app), "<app: tests>")
        self.assertEqual(unicode(app), "tests")
        self.assertEqual(app.name, "tests")

    def test_app_finds_valid_app_classes(self):
        app = AppBase.find('rapidsms.contrib.default')
        from rapidsms.contrib.default.app import App
        self.assertEqual(app, App)

    def test_app_ignores_invalid_modules(self):
        app = AppBase.find('not.a.valid.module')
        self.assertEqual(app, None)
