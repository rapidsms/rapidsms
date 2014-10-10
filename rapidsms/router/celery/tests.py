from mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from rapidsms.tests import harness
from rapidsms.router import get_router
from rapidsms.router.celery.tasks import receive_async, send_async


class CeleryRouterTest(harness.DatabaseBackendMixin, TestCase):
    """Tests for the CeleryRouter proxy class"""

    router_class = 'rapidsms.router.celery.CeleryRouter'

    def test_incoming(self):
        """Make sure the proper fields are passed to receive_async."""
        with patch.object(receive_async, 'delay') as mock_method:
            connections = self.lookup_connections(['1112223333'])
            msg = self.receive("test", connections[0], fields={'a': 'b'})
        mock_method.assert_called_once_with(msg.text, msg.connections[0].id,
                                            msg.id, msg.fields)

    def test_outgoing(self):
        """send() should preserve all message context."""
        connection = self.lookup_connections(['1112223333'])[0]
        msg = self.send("test", connection)
        backend_msg = self.sent_messages[0]
        self.assertEqual(msg.id, backend_msg.message_id)
        self.assertEqual(msg.text, backend_msg.text)
        self.assertEqual(msg.connections[0].identity, backend_msg.identity)

    def test_in_response_to_external_id(self):
        """CeleryRouter should maintain external_id through responses."""
        connection = self.lookup_connections([1112223333])[0]
        msg = self.receive("test", connection,
                           fields={'external_id': 'ABCD1234'})
        backend_msg = self.sent_messages[0]
        self.assertEqual(msg.fields['external_id'],
                         backend_msg.external_id)

    def test_send_async_catches_error(self):
        """send_async should capture sending exceptions properly."""
        backends = {'backend': {'ENGINE': harness.RaisesBackend}}
        with override_settings(INSTALLED_BACKENDS=backends):
            try:
                send_async("backend", "1234", "hello", ["1112223333"], {})
            except:
                self.fail("Sending exceptions should be caught within task")


class CeleryRouterConfigTest(harness.CustomRouterMixin, TestCase):

    router_class = 'rapidsms.router.celery.CeleryRouter'

    def test_eager_invalid_backend(self):
        """is_eager should return False if backend doesn't exist."""
        self.backends = {'mockbackend': {'ENGINE': harness.MockBackend}}
        self.set_backends()
        router = get_router()
        self.assertFalse(router.is_eager('foo'))

    def test_eager_not_set(self):
        """is_eager should return False if not set for specified backend."""
        self.backends = {'mockbackend': {'ENGINE': harness.MockBackend}}
        self.set_backends()
        router = get_router()
        self.assertFalse(router.is_eager('mockbackend'))

    def test_outgoing(self):
        """is_eager should return True if router.celery.eager is set."""
        self.backends = {'mockbackend': {'ENGINE': harness.MockBackend,
                                         'router.celery.eager': True}}
        self.set_backends()
        router = get_router()
        self.assertTrue(router.is_eager('mockbackend'))
