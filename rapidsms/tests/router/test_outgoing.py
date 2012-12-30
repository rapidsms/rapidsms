from rapidsms.router.test import BlockingRouter
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.tests.harness import RapidTest, MockApp


class OutgoingTest(RapidTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend({'name': 'mockbackend'})
        self.connection = self.create_connection({'backend': self.backend,
                                                  'contact': self.contact})
        self.router = BlockingRouter()

    # def test_outgoing(self):
    #     """
    #     Router.outgoing should call backend.send() method
    #     and set message.sent flag respectively
    #     """
    #     self.send('test', self.lookup_connections('1112223333')[0])
    #     self.router.send_outgoing(msg)
    #     self.assertTrue(msg.sent)
    #     self.assertEqual(msg, self.sent_messages[0])


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


class PhaseTest(RapidTest):

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
