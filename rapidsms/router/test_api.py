from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured

from rapidsms.router import get_router, receive, send
from rapidsms.tests import harness
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage


class MockRouter(object):
    """Dummy class used to test importing with get_router()"""
    pass


class RouterAPITest(harness.RapidTest):
    """Tests for rapidsms.router.api"""

    disable_phases = True

    def test_get_router(self):
        """Test exceptions for bad input given to get_router()"""
        bad_module_router = 'rapidsms.tests.router.bad_module.MockRouter'
        bad_class_router = 'rapidsms.tests.router.test_base.BadClassName'
        good_mock_router = 'rapidsms.router.test_api.MockRouter'
        with override_settings(RAPIDSMS_ROUTER=bad_module_router):
            self.assertRaises(ImproperlyConfigured, get_router)
        with override_settings(RAPIDSMS_ROUTER=bad_class_router):
            self.assertRaises(ImproperlyConfigured, get_router)
        with override_settings(RAPIDSMS_ROUTER=good_mock_router):
            self.assertTrue(isinstance(get_router(), MockRouter))

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
