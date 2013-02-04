from rapidsms.router import receive, send
from rapidsms.tests.harness import RapidTest
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage


class RouterAPITest(RapidTest):
    """Tests for rapidsms.router.api"""

    disable_phases = True

    def test_send_with_connection(self):
        """Send accepts a single connection."""
        connection = self.create_connection()
        message = send("echo hello", connection)
        self.assertEqual(message.connection.identity, connection.identity)
        self.assertEqual(message.connection.backend.name,
                         connection.backend.name)

    def test_send_with_connections(self):
        """Send accepts a list of connections."""
        connections = [self.create_connection(), self.create_connection()]
        message = send("echo hello", connections)
        self.assertEqual(len(message.connections), 2)
        self.assertEqual(message.connection.identity,
                         connections[0].identity)
        self.assertEqual(message.connection.backend.name,
                         connections[0].backend.name)

    def test_saved_message_fields_receive(self):
        """Extra data should persist through receive."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = receive('test incoming message',
                          connection=connection, fields=fields)
        self.assertTrue('extra-field' in message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])

    def test_receive_message_class(self):
        """receive() should let you customize the incoming message class."""
        class TestIncomingMessage(IncomingMessage):
            pass
        msg = self.receive("echo hello", self.create_connection(),
                           class_=TestIncomingMessage)
        self.assertTrue(isinstance(msg, TestIncomingMessage))

    def test_send_message_class(self):
        """send() should let you customize the outgoing message class."""
        class TestIncomingMessage(OutgoingMessage):
            pass
        msg = self.send("hello", self.create_connection(),
                        class_=TestIncomingMessage)
        self.assertTrue(isinstance(msg, TestIncomingMessage))
