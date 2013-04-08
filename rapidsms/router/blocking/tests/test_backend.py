from django.test import TestCase
from rapidsms.router.blocking import BlockingRouter
from rapidsms.backends.base import BackendBase


class RouterBackendTest(TestCase):
    """BlockingRouter backend tests."""

    def setUp(self):
        self.router = BlockingRouter(apps=[], backends={})

    def test_valid_backend_path(self):
        """Valid RapidSMS backend modules should load properly."""
        backend = self.router.add_backend("backend",
                                          "rapidsms.backends.base.BackendBase")
        self.assertEquals(1, len(self.router.backends.keys()))
        self.assertEquals(backend, self.router.backends["backend"])

    def test_router_downcases_backend_configs(self):
        """Backend configuration should automatically be lowercased."""
        test_backend = "rapidsms.backends.base.BackendBase"
        test_conf = {"a": 1, "B": 2, "Cc": 3}
        backend = self.router.add_backend("backend", test_backend, test_conf)
        self.assertEquals(len(backend._config), 3)
        self.assertIn("a", backend._config)
        self.assertIn("b", backend._config)
        self.assertIn("cc", backend._config)
        self.assertNotIn("B", backend._config)
        self.assertNotIn("Cc", backend._config)

    def test_add_backend_class(self):
        """Router.add_backend should also accept a class."""
        self.router.add_backend("backend", BackendBase)
        self.assertEquals(1, len(self.router.backends.keys()))
        self.assertIn("backend", self.router.backends.keys())
        self.assertEquals("backend", self.router.backends['backend'].name)
