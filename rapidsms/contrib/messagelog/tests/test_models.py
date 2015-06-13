#!/usr/bin/env python
# vim: aui ts=4 sts=4 et sw=4

from django.core.exceptions import ValidationError
from django.utils.timezone import now
from rapidsms.tests.harness import RapidTest
from ..models import Message


__all__ = ['MessageLogModelTest']


class MessageLogModelTest(RapidTest):

    def setUp(self):
        self.contact = self.create_contact()
        self.connection = self.lookup_connections(['1112223333'])[0]
        self.connection.contact = self.contact
        self.data = {
            'contact': self.contact,
            'connection': self.connection,
            'direction': Message.INCOMING,
            'date': now(),
            'text': 'hello',
        }

    def test_no_contact_or_connection(self):
        """Message requires a Contact or a Connection."""
        self.data.pop('contact')
        self.data.pop('connection')
        with self.assertRaises(ValidationError):
            Message.objects.create(**self.data)

    def test_no_contact(self):
        """Message does not require a Contact if a Connection is available."""
        self.data.pop('contact')
        msg = Message.objects.create(**self.data)
        self.assertEqual(msg.contact, self.contact)

        self.connection.contact = None
        msg = Message.objects.create(**self.data)
        self.assertEqual(msg.contact, None)

    def test_no_connection(self):
        """Message does not require a Connection if a Contact is available."""
        self.data.pop('connection')
        msg = Message.objects.create(**self.data)
        self.assertEqual(msg.connection, None)

    def test_contact_mismatch(self):
        """If both present, Contact and Connection Contact must match."""
        self.data['contact'] = self.create_contact()
        with self.assertRaises(ValidationError):
            Message.objects.create(**self.data)
