#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.urls import reverse
from django.test import TestCase
from mock import patch
from six import BytesIO

from rapidsms.backends.database.models import INCOMING
from rapidsms.contrib.httptester.forms import MessageForm
from rapidsms.tests.harness import RapidTest
from .storage import store_and_queue, store_message, get_messages, \
    clear_messages, clear_all_messages


class StorageTest(RapidTest):

    disable_phases = True

    def test_store_and_queue(self):
        """store_and_queue should use receive() API correctly"""
        store_and_queue("1112223333", "hi there!")
        self.assertEqual(self.inbound[0].text, "hi there!")

    def test_store_and_get(self):
        """If we store something, we can get it again"""
        direction, identity, text = u"I", u"identity", u"text"
        store_message(direction, identity, text)
        msgs = get_messages()
        msg = msgs[0]
        self.assertEqual(identity, msg.identity)
        self.assertEqual(direction, msg.direction)
        self.assertEqual(text, msg.text)

    def test_clear(self):
        """We can clear messages for a given identity"""
        direction, identity, text = u"I", u"identity1", u"text"
        store_message(direction, identity, text)
        direction, identity, text = u"I", u"identity2", u"text"
        store_message(direction, identity, text)
        direction, identity, text = u"I", u"identity3", u"text"
        store_message(direction, identity, text)
        clear_messages(u"identity2")
        msgs = get_messages()
        for msg in msgs:
            self.assertNotEqual(u"identity2", msg.identity)

    def test_clear_all(self):
        """We can clear all messages"""
        direction, identity, text = u"I", u"identity1", u"text"
        store_message(direction, identity, text)
        direction, identity, text = u"I", u"identity2", u"text"
        store_message(direction, identity, text)
        direction, identity, text = u"I", u"identity3", u"text"
        store_message(direction, identity, text)
        clear_all_messages()
        self.assertEqual(0, len(get_messages()))


class ViewTest(RapidTest):
    disable_phases = True
    phone = "12345"
    url = reverse('httptester', kwargs={'identity': phone})

    def test_send_through_form(self):
        # Submitting a message to the form adds it to storage
        phone2 = "67890"
        message = "RapidSMS FTW"

        self.login()
        rsp = self.client.get(self.url)
        self.assertEqual(200, rsp.status_code)
        data = {
            'identity': phone2,
            'text': message,
        }
        self.client.post(self.url, data)
        self.assertEqual(200, rsp.status_code)
        msg = get_messages()[0]
        self.assertEqual(phone2, msg.identity)
        self.assertEqual(INCOMING, msg.direction)
        self.assertEqual(message, msg.text)

    def test_bulk(self):
        messages = ["message 1", "message 2", "message 3"]
        file_content = "\n".join(messages) + "\n"
        fake_file = BytesIO(file_content.encode('utf-8'))
        setattr(fake_file, 'name', 'fake_file')
        data = {
            'identity': self.phone,
            'bulk': fake_file,
        }
        self.login()
        rsp = self.client.post(self.url, data)
        self.assertRedirects(rsp, self.url)
        self.assertEqual(302, rsp.status_code)
        self.assertEqual(3, len(get_messages()))
        for i, m in enumerate(messages):
            self.assertEqual(m, get_messages()[i].text)

    @patch('rapidsms.contrib.httptester.storage.clear_messages')
    def test_clear_identity_messages(self, clear_messages):
        # Selecting the 'clear' button calls clear_messages for that phone #
        data = {
            'identity': self.phone,
            'clear-btn': True,
        }
        self.login()
        rsp = self.client.post(self.url, data)
        self.assertEqual(302, rsp.status_code)
        self.assertTrue(clear_messages.called)
        self.assertEqual(self.phone, clear_messages.call_args[0][0])

    @patch('rapidsms.contrib.httptester.storage.clear_all_messages')
    def test_clear_all_identity_messages(self, clear_all_messages):
        # Selecting the 'clear all' button calls clear_all_messages
        data = {
            'identity': self.phone,
            'clear-all-btn': True,
        }
        self.login()
        rsp = self.client.post(self.url, data)
        self.assertEqual(302, rsp.status_code, msg=rsp.content)
        self.assertTrue(clear_all_messages.called, msg=rsp.content)

    @patch('rapidsms.contrib.httptester.views.randint')
    def test_generate_identity(self, randint):
        randint.return_value = self.phone
        url = reverse('httptester-index')
        self.login()
        rsp = self.client.get(url)
        new_url = reverse('httptester',
                          kwargs={'identity': self.phone})
        self.assertRedirects(rsp, new_url)


class FormTest(TestCase):
    def test_clean_identity(self):
        # The form strips whitespace from the phone number, and does not
        # accept non-numeric input
        form = MessageForm({'identity': ' 123 '})
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual('123', form.cleaned_data['identity'])
        form = MessageForm({'identity': ' 1a23 '})
        self.assertFalse(form.is_valid())
