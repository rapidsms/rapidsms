from rapidsms.router import receive, send
from rapidsms.tests.harness import RapidTest


class RouterAPITest(RapidTest):
    """Tests for rapidsms.router.api"""

    disable_phases = True

    def test_send_with_connection(self):
        """Send accepts a single connection."""
        connection = self.create_connection()
        messages = send("echo hello", connection)
        self.assertEqual(messages[0].connection.identity, connection.identity)
        self.assertEqual(messages[0].connection.backend.name,
                         connection.backend.name)

    def test_send_with_connections(self):
        """Send accepts a list of connections."""
        connections = [self.create_connection(), self.create_connection()]
        messages = send("echo hello", connections)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].connection.identity,
                         connections[0].identity)
        self.assertEqual(messages[0].connection.backend.name,
                         connections[0].backend.name)

    def test_saved_message_fields_receive(self):
        """Extra data should persist through receive."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = receive('test incoming message',
                          connection=connection, fields=fields)
        self.assertTrue('extra-field' in message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])
