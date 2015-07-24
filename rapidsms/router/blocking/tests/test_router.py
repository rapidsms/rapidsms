from django.test import TestCase

from rapidsms.tests import harness
from rapidsms.router.blocking import BlockingRouter
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.models import Connection


class BlockingRouterTest(harness.CreateDataMixin, TestCase):
    """Test router phases and message classes."""

    def setUp(self):
        self.router = BlockingRouter(apps=[], backends={})

    def test_router_incoming_phases(self):
        """Incoming messages should trigger proper router phases."""
        self.router.add_app(harness.MockApp)
        self.router.receive_incoming(self.create_incoming_message())
        self.assertEqual(set(self.router.apps[0].calls),
                         set(self.router.incoming_phases))

    def test_router_outgoing_phases(self):
        """Outgoing messages should trigger proper router phases."""
        self.router.add_app(harness.MockApp)
        self.router.add_backend("mockbackend", harness.MockBackend)
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection(data={'backend': backend})
        msg = self.create_outgoing_message(data={'connections': [connection]})
        self.router.send_outgoing(msg)
        self.assertEqual(set(self.router.apps[0].calls),
                         set(self.router.outgoing_phases))

    def test_new_incoming_message(self):
        """BaseRouter should return a standard IncomingMessage by default."""
        fields = {'foo': 'bar'}
        connection = self.create_connection()
        msg = self.router.new_incoming_message(text="foo",
                                               connections=[connection],
                                               fields=fields)
        self.assertTrue(isinstance(msg, IncomingMessage))
        self.assertEqual("foo", msg.text)
        self.assertEqual(connection, msg.connections[0])
        self.assertEqual(fields['foo'], msg.fields['foo'])

    def test_new_incoming_message_class(self):
        """Make sure you can customize the incoming message class."""
        class TestIncomingMessage(IncomingMessage):
            pass
        connection = self.create_connection()
        msg = self.router.new_incoming_message(text="foo",
                                               connections=[connection],
                                               class_=TestIncomingMessage)
        self.assertTrue(isinstance(msg, TestIncomingMessage))

    def test_new_outgoing_message(self):
        """BaseRouter should return a standard OutgoingMessage by default."""
        fields = {'foo': 'bar'}
        connection = self.create_connection()
        incoming_message = self.create_incoming_message()
        msg = self.router.new_outgoing_message(text="foo",
                                               connections=[connection],
                                               fields=fields,
                                               in_response_to=incoming_message)
        self.assertTrue(isinstance(msg, OutgoingMessage))
        self.assertEqual("foo", msg.text)
        self.assertEqual(connection, msg.connections[0])
        self.assertEqual(fields['foo'], msg.fields['foo'])
        self.assertEqual(incoming_message, msg.in_response_to)

    def test_new_outgoing_message_class(self):
        """Make sure you can customize the outgoing message class."""
        class TestOutgoingMessage(OutgoingMessage):
            pass
        connection = self.create_connection()
        msg = self.router.new_outgoing_message(text="foo",
                                               connections=[connection],
                                               class_=TestOutgoingMessage)
        self.assertTrue(isinstance(msg, TestOutgoingMessage))


class RouterOutgoingPhases(harness.RapidTest):
    """Test router outgoing phases."""

    apps = (harness.MockApp,)

    def test_outgoing_phase(self):
        """App.outgoing should be called for sent messages."""
        self.send('test', self.lookup_connections('1112223333'))
        app = self.router.apps[0]
        self.assertIn('outgoing', app.calls)

    def test_process_outgoing_phases_return_value(self):
        """
        Returning False from App.outgoing should cause
        Router.process_outgoing_phases() to return False as well.
        """
        self.router.apps[0].return_values['outgoing'] = False
        msg = self.create_outgoing_message()
        continue_sending = self.router.process_outgoing_phases(msg)
        self.assertFalse(continue_sending)

    def test_processed_flag_set(self):
        """
        BaseMessage.processed should be set to True after
        outgoing phase processing.
        """
        msg = self.create_outgoing_message()
        self.router.process_outgoing_phases(msg)
        self.assertTrue(msg.processed)

    def test_return_value(self):
        """
        Returning False from App.outgoing should prevent messages
        being passed to the backends.
        """
        self.router.apps[0].return_values['outgoing'] = False
        self.send('test', self.lookup_connections('1112223333'))
        self.assertEqual(0, len(self.sent_messages))

    def test_outgoing_exception(self):
        """App exceptions shouldn't halt message processing."""
        def outgoing_exception(message):
            raise Exception("Error!")
        self.router.apps[0].outgoing = outgoing_exception
        self.send('test', self.lookup_connections('1112223333'))
        self.assertEqual(1, len(self.sent_messages))

    def test_single_connection_outgoing_message_count(self):
        """Single connection should only create 1 message."""
        identities = ['1112223333']
        self.send('test', self.lookup_connections(identities))
        self.assertEqual(1, len(self.sent_messages[0]['identities']))
        self.assertEqual(1, len(self.sent_messages))

    def test_multiple_connection_outgoing_message_count(self):
        """Multiple connections should only create 1 message."""
        identities = ['1112223333', '9998887777']
        self.send('test', self.lookup_connections(identities))
        self.assertEqual(2, len(self.sent_messages[0]['identities']))
        self.assertEqual(1, len(self.sent_messages))

    def test_group_outgoing_identities(self):
        """group_outgoing_identities() should group connections by backend."""
        mockbackend_connections = self.lookup_connections([1112223333])
        other_connections = self.lookup_connections([2223334444, 9998887777],
                                                    backend='other')
        connections = mockbackend_connections + other_connections
        msg = self.create_outgoing_message(data={'connections': connections})
        grouped_identities = self.router.group_outgoing_identities(msg)
        self.assertEqual(2, len(grouped_identities.keys()))
        self.assertEqual(1, len(grouped_identities['mockbackend']))
        self.assertEqual(2, len(grouped_identities['other']))


class OutgoingQuerysetTest(harness.RapidTest):

    apps = (harness.MockApp,)

    def setUp(self):
        self.conn1 = self.create_connection(data={'identity': '1112223333'})
        self.conn2 = self.create_connection(data={'identity': '9998887777'})
        self.conns = Connection.objects.all()

    def test_group_does_not_contain_embedded_lists(self):
        """Using QuerySets should return a flat list of identities."""

        msg = self.create_outgoing_message(data={'connections': self.conns})
        grouped_identities = self.router.group_outgoing_identities(msg)
        backend_name = self.conn1.backend.name
        self.assertEqual(grouped_identities[backend_name][0],
                         self.conn1.identity)

    def test_distinct_grouping(self):
        """Connections should be grouped by backend name only once."""

        # create second connection using the same backend
        self.create_connection(data={'identity': '77766655555',
                                     'backend': self.conn1.backend})
        self.conns = Connection.objects.all()
        msg = self.create_outgoing_message(data={'connections': self.conns})
        grouped_identities = self.router.group_outgoing_identities(msg)
        backend_name = self.conn1.backend.name
        self.assertEqual(len(grouped_identities[backend_name]), 2)


class ExternalIDTest(harness.DatabaseBackendMixin, TestCase):

    def test_in_response_to_external_id(self):
        """BlockingRouter should maintain external_id through responses."""
        connection = self.lookup_connections(['1112223333'])[0]
        msg = self.receive("test", connection,
                           fields={'external_id': 'ABCD1234'})
        backend_msg = self.sent_messages[0]
        self.assertEqual(msg.fields['external_id'],
                         backend_msg.external_id)
