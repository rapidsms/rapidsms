from django.test import TestCase

from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.router import receive, send

from rapidsms.router.test import BlockingRouter
from rapidsms.tests.harness.base import MockBackendRouter


class RouterAPITest(MockBackendRouter, TestCase):
    """Tests for rapidsms.router.api"""

    router_class = 'rapidsms.router.test.NoOpTestRouter'

    def test_receive_with_connection(self):
        """Receive accepts an identity/backend_name combo"""

        connection = self.create_connection()
        message = receive("echo hello", connection)
        self.assertEqual(message.connection.identity, connection.identity)
        self.assertEqual(message.connection.backend.name,
                         connection.backend.name)

    def test_send_with_connection(self):
        """Send accepts a single connection"""

        connection = self.create_connection()
        messages = send("echo hello", connection)
        self.assertEqual(messages[0].connection.identity, connection.identity)
        self.assertEqual(messages[0].connection.backend.name,
                         connection.backend.name)

    def test_send_with_connections(self):
        """Send accepts a list of connections"""

        connections = [self.create_connection(), self.create_connection()]
        messages = send("echo hello", connections)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].connection.identity,
                         connections[0].identity)
        self.assertEqual(messages[0].connection.backend.name,
                         connections[0].backend.name)
