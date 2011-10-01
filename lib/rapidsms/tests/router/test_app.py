"""
Test app specific functionality of Router
"""

from nose.tools import assert_equals, assert_raises, assert_true

from django.core.exceptions import ImproperlyConfigured

from rapidsms.apps.base import AppBase
from rapidsms.router.legacy import BaseRouter


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


def test_add_instantiated_app():
    """
    Router.add_app should also accept an instantiated AppBase
    """
    router = BaseRouter()
    app = AppBase(router)
    router.add_app(app)
    assert_equals(len(router.apps), 1)
    assert_true(app in router.apps)