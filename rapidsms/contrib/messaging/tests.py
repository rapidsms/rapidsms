#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest

from nose.tools import nottest

from .forms import MessageForm


class MessagingTest(RapidTest):
    """
    Test rapidsms.contrib.messaging form and views
    """

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend({'name': 'mockbackend'})
        self.connection = self.create_connection({'backend': self.backend,
                                                  'contact': self.contact})

    @nottest
    def test_messaging_list(self):
        """
        The messaging index page should return a 200
        """
        response = self.client.get(reverse('messaging'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_with_connection(self):
        """
        Only contacts with connections are valid options
        """
        connectionless_contact = self.create_contact()
        data = {'text': 'hello!',
                'recipients': [self.contact.id, connectionless_contact.pk]}
        form = MessageForm(data)
        self.assertTrue('recipients' in form.errors)
        self.assertEqual(len(self.outbound), 0)

    def test_valid_send_data(self):
        """
        MessageForm.send should return successfully with valid data
        """
        data = {'text': 'hello!',
                'recipients': [self.contact.id]}
        form = MessageForm(data)
        self.assertTrue(form.is_valid())
        recipients = form.send()
        self.assertTrue(self.contact in recipients)
        self.assertEqual(self.outbound[0].text, data['text'])
