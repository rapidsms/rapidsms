#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.tests.harness import RapidTest

from ..forms import MessageForm


__all__ = ['TestMessagingForm']


class TestMessagingForm(RapidTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend({'name': 'mockbackend'})
        self.connection = self.create_connection({
            'backend': self.backend,
            'contact': self.contact,
        })
        self.message = 'hello'
        self.data = {
            'message': self.message,
            'connections_1': [self.connection.pk],
        }

    def test_no_message(self):
        """Form should require the message field."""
        self.data.pop('message')
        form = MessageForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('message' in form.errors)

    def test_no_recipients(self):
        """Form should require at least one recipient."""
        self.data.pop('connections_1')
        form = MessageForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('connections' in form.errors)

    def test_valid_data(self):
        form = MessageForm(self.data)
        self.assertTrue(form.is_valid())

    def test_send(self):
        form = MessageForm(self.data)
        self.assertTrue(form.is_valid())
        message = form.send()
        self.assertEqual(message.text, self.message)
        self.assertEqual(message.connection, self.connection)
