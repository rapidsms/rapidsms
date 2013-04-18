from rapidsms.messages.base import MessageBase
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.tests.harness import RapidTest


class MessagesTest(RapidTest):

    disable_phases = True

    def test_message_id(self):
        """All message objects should have IDs."""
        connections = [self.create_connection()]
        msg = MessageBase(text="test", connections=connections)
        self.assertIsNotNone(msg.id)
        msg = IncomingMessage(text="test", connections=connections)
        self.assertIsNotNone(msg.id)
        msg = OutgoingMessage(text="test", connections=connections)
        self.assertIsNotNone(msg.id)

    def test_saved_message_fields(self):
        """Extra data should be attached to IncomingMessage."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        self.assertIn('extra-field', message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])

    def test_outgoing_message_link(self):
        """Extra data should be attached to response (OutgoingMessage)."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        response = message.respond('response')
        self.assertEqual(message, response['in_response_to'])
        self.assertIn('extra-field', response['in_response_to'].fields)

    def test_outgoing_message_send(self):
        """OutgoingMessage.send should use send() API correctly"""
        message = self.create_outgoing_message()
        message.send()
        self.assertEqual(self.outbound[0].text, message.text)

    def test_response_context(self):
        """
        InboundMessage responses should contain proper context for
        creating OutboundMessages by the router.
        """
        inbound_message = self.create_incoming_message()
        inbound_message.respond('test1')
        inbound_message.respond('test2')
        self.assertEqual(2, len(inbound_message.responses))
        response1 = inbound_message.responses[0]
        self.assertEqual("test1", response1['text'])
        self.assertEqual(inbound_message.connections, response1['connections'])
        # reply_to should reference original message
        self.assertEqual(inbound_message, response1['in_response_to'])
