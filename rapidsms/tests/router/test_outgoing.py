from rapidsms.models import Connection
from rapidsms.tests.harness import RapidTest, MockApp


class RouterOutgoingPhases(RapidTest):

    apps = (MockApp,)

    def test_outgoing_phase(self):
        """App.outgoing should be called for sent messages."""
        self.send('test', self.lookup_connections('1112223333'))
        app = self.router.apps[0]
        self.assertTrue('outgoing' in app.calls)

    def test_process_outgoing_phases_return_value(self):
        """
        Returning False from App.outgoing should cause
        Router.process_outgoing_phases() to return False as well.
        """
        self.router.apps[0].return_values['outgoing'] = False
        msg = self.create_outgoing_message()
        continue_sending = self.router.process_outgoing_phases(msg)
        self.assertFalse(continue_sending)

    def test_proccessed_flag_set(self):
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
        """App exceptions shouldn't hault message processing."""
        def outgoing_exception(message):
            raise Exception("Error!")
        self.router.apps[0].outgoing = outgoing_exception
        self.send('test', self.lookup_connections('1112223333'))
        self.assertEqual(1, len(self.sent_messages))


class OutgoingTest(RapidTest):

    apps = (MockApp,)

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

    def test_group_outgoing_identities_with_queryset(self):
        """group_outgoing_identities() should accept a QuerySet."""
        connection1 = self.create_connection(data={'identity': '1112223333'})
        connection2 = self.create_connection(data={'identity': '9998887777'})
        connections = Connection.objects.all()
        msg = self.create_outgoing_message(data={'connections': connections})
        grouped_identities = self.router.group_outgoing_identities(msg)
        self.assertTrue(connection1.backend.name in grouped_identities)
        self.assertTrue(connection2.backend.name in grouped_identities)
