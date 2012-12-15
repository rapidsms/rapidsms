from rapidsms.messages.incoming import IncomingMessage
from rapidsms.tests.harness import RapidTest


class MessagesTest(RapidTest):

    disable_phases = True

    def test_saved_message_fields(self):
        """Extra data should be attached to IncomingMessage."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        self.assertTrue('extra-field' in message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])

    def test_outgoing_message_link(self):
        """Extra data should be attached to response (OutgoingMessage)."""
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        response = message.respond('response')
        self.assertEqual(message, response.in_reply_to)
        self.assertTrue('extra-field' in response.in_reply_to.fields)

    def test_outgoing_message_send(self):
        """OutgoingMessage.send should use send() API correctly"""
        message = self.create_outgoing_message()
        message.send()
        self.assertEqual(self.outbound[0].text, message.text)
