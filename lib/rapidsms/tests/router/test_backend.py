"""
Test backend specific functionality of Router
"""

from nose.tools import assert_equals

from rapidsms.router.base import BaseRouter
from rapidsms.backends.base import BackendBase


def test_router_finds_backends():
    """
    Router should find backend with module path
    """
    router = BaseRouter()
    test_backend = "rapidsms.backends.base"
    backend = router.add_backend("mock", test_backend)

    assert_equals(router.backends["mock"], backend)
    assert_equals(len(router.backends), 1)


def test_router_downcases_backend_configs():
    """
    Backend configuration should automatically be lowercased
    """
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