#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.messages import IncomingMessage, OutgoingMessage
from rapidsms.tests.harness import RapidTest
from ..app import MessageLogApp
from ..models import Message


__all__ = ['MessageLogAppTestBase', 'IncomingMessageLogAppTest',
           'OutgoingMessageLogAppTest']


class MessageLogAppTestBase(object):

    def setUp(self):
        self.contact = self.create_contact()
        self.connection = self.lookup_connections(['1112223333'])[0]
        self.connection.contact = self.contact
        self.app = MessageLogApp(self.router)

    def _check_message(self, msg, msg_obj):
        if isinstance(msg, IncomingMessage):
            self.assertEqual(msg_obj.direction, Message.INCOMING)
        else:
            self.assertEqual(msg_obj.direction, Message.OUTGOING)
        self.assertEqual(msg_obj, msg.logger_msg)
        self.assertEqual(msg_obj.contact, msg.connections[0].contact)
        self.assertEqual(msg_obj.connection, msg.connections[0])
        self.assertEqual(msg_obj.text, msg.text)

    def test_message(self):
        """Message should be logged & annotated."""
        msg = self.MessageType([self.connection], 'hello')
        self._send(msg)
        self.assertEqual(Message.objects.count(), 1)
        self._check_message(msg, Message.objects.get())

    def test_no_contact(self):
        """Message doesn't require a Contact if a Connection is present."""
        self.connection.contact = None
        msg = self.MessageType([self.connection], 'hello')
        self._send(msg)
        self.assertEqual(Message.objects.count(), 1)
        self._check_message(msg, Message.objects.get())


class IncomingMessageLogAppTest(MessageLogAppTestBase, RapidTest):
    MessageType = IncomingMessage

    def _send(self, msg):
        return self.app.parse(msg)


class OutgoingMessageLogAppTest(MessageLogAppTestBase, RapidTest):
    MessageType = OutgoingMessage

    def _send(self, msg):
        return self.app.outgoing(msg)
