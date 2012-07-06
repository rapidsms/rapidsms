from django.test import TestCase

from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.router_api import handle_incoming

from rapidsms.router.test import BlockingRouter
from rapidsms.tests.harness.base import MockBackendRouter


class OutgoingTest(MockBackendRouter, TestCase):

    router_class = 'rapidsms.router.test.TestRouter'

    def test_saved_message_fields(self):
        """ Extra data should be attached to IncomingMessage """
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        self.assertTrue('extra-field' in message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])

    def test_saved_message_fields_handle_incoming(self):
        """ Extra data should preserve through handle_incoming """
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = handle_incoming('test incoming message',
                                  connection=connection, fields=fields)
        self.assertTrue('extra-field' in message.fields)
        self.assertEqual(message.fields['extra-field'], fields['extra-field'])

    def test_outgoing_message_link(self):
        """ Extra data should be attached to response (OutgoingMessage) """
        connection = self.create_connection()
        fields = {'extra-field': 'extra-value'}
        message = IncomingMessage(connection, 'test incoming message',
                                  fields=fields)
        response = message.respond('response')
        self.assertEqual(message, response.in_reply_to)
        self.assertTrue('extra-field' in response.in_reply_to.fields)
