from django.test import TestCase

from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.router import receive, send

from rapidsms.router.test import BlockingRouter
from rapidsms.tests.harness.base import MockBackendRouter


class RouterAPITest(MockBackendRouter, TestCase):
    """Tests for rapidsms.router.api"""

    router_class = 'rapidsms.router.test.NoOpTestRouter'

    def test_receive_with_identity(self):
        """Receive accepts an identity/backend_name combo"""

        message = receive(text="echo hello", identity="12223334444",
                          backend_name="mockbackend")
        self.assertEqual(message.connection.identity, "12223334444")
        self.assertEqual(message.connection.backend.name, "mockbackend")

    def test_receive_with_connection(self):
        """Receive accepts an identity/backend_name combo"""

        connection = self.create_connection()
        message = receive(text="echo hello", connection=connection)
        self.assertEqual(message.connection.identity, connection.identity)
        self.assertEqual(message.connection.backend.name,
                         connection.backend.name)

    def test_send_with_identity(self):
        """Send accepts an identity/backend_name combo"""

        message = send(text="echo hello", identity="12223334444",
                       backend_name="mockbackend")
        self.assertEqual(message.connection.identity, "12223334444")
        self.assertEqual(message.connection.backend.name, "mockbackend")

    def test_send_with_connection(self):
        """Send accepts an identity/backend_name combo"""

        connection = self.create_connection()
        message = send(text="echo hello", connection=connection)
        self.assertEqual(message.connection.identity, connection.identity)
        self.assertEqual(message.connection.backend.name,
                         connection.backend.name)
