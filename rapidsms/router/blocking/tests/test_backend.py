from django.test import TestCase
from rapidsms.router.blocking import BlockingRouter
from rapidsms.backends.base import BackendBase
from rapidsms.tests.harness import RaisesBackend, CreateDataMixin
from rapidsms.errors import MessageSendingError


class RouterBackendTest(CreateDataMixin, TestCase):
    """BlockingRouter backend tests."""

    def setUp(self):
        self.router = BlockingRouter(apps=[], backends={})

    def test_valid_backend_path(self):
        """Valid RapidSMS backend modules should load properly."""
        backend = self.router.add_backend("backend",
                                          "rapidsms.backends.base.BackendBase")
        self.assertEqual(1, len(self.router.backends.keys()))
        self.assertEqual(backend, self.router.backends["backend"])

    def test_router_downcases_backend_configs(self):
        """Backend configuration should automatically be lowercased."""
        test_backend = "rapidsms.backends.base.BackendBase"
        test_conf = {"a": 1, "B": 2, "Cc": 3}
        backend = self.router.add_backend("backend", test_backend, test_conf)
        self.assertEqual(len(backend._config), 3)
        self.assertIn("a", backend._config)
        self.assertIn("b", backend._config)
        self.assertIn("cc", backend._config)
        self.assertNotIn("B", backend._config)
        self.assertNotIn("Cc", backend._config)

    def test_add_backend_class(self):
        """Router.add_backend should also accept a class."""
        self.router.add_backend("backend", BackendBase)
        self.assertEqual(1, len(self.router.backends.keys()))
        self.assertIn("backend", self.router.backends.keys())
        self.assertEqual("backend", self.router.backends['backend'].name)

    def test_router_not_configured_with_backend(self):
        """
        send_to_backend should raise MessageSendingError if backend
        hasn't been configured with the router.
        """
        args = ("missing-backend", "1234", "hello", ["1112223333"], {})
        self.assertRaises(MessageSendingError, self.router.send_to_backend,
                          *args)

    def test_backend_send_raises_error(self):
        """
        send_to_backend should capture all backend exceptions and raise the
        standard MessageSendingError.
        """
        backend = self.router.add_backend("backend", RaisesBackend)
        args = (backend.model.name, "1234", "hello", ["1112223333"], {})
        self.assertRaises(MessageSendingError, self.router.send_to_backend,
                          *args)

    def test_send_captures_exception(self):
        """BlockingRouter should catch exceptions during sending."""
        backend = self.router.add_backend("backend", RaisesBackend)
        msg = self.create_outgoing_message(backend=backend.model)
        try:
            self.router.send_outgoing(msg)
        except Exception:
            self.fail("send_outgoing should capture all excetpions.")
