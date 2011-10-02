import string
import random

from django.test import TestCase
from django.core.urlresolvers import reverse

from rapidsms.backends.base import BackendBase
from rapidsms.router.test import TestRouter
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.models import Backend, Contact, Connection
from rapidsms.tests.harness import CustomRouter

from rapidsms.contrib.messaging.forms import MessageForm


__all__ = ('OurgoingTest', 'MessagingTest')


class CreateDataTest(object):
    """
    Base test case that provides helper functions to create data
    """

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def create_backend(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Backend.objects.create(**defaults)

    def create_contact(self, data={}):
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def create_connection(self, data={}):
        defaults = {
            'identity': self.random_string(10),
        }
        defaults.update(data)
        if 'backend' not in defaults:
            defaults['backend'] = self.create_backend()
        return Connection.objects.create(**defaults)


class SimpleBackend(BackendBase):

	def __init__(self, *args, **kwargs):
		self._saved_message = None
		self.send_message = kwargs.pop('send_message', True)
		super(SimpleBackend, self).__init__(*args, **kwargs)

	def send(self, message):
		self._saved_message = message
		return self.send_message


class OurgoingTest(TestCase, CreateDataTest):

	def setUp(self):
		self.contact = self.create_contact()
		self.backend = self.create_backend({'name': 'simple'})
		self.connection = self.create_connection({'backend': self.backend,
		                                          'contact': self.contact})
		self.router = TestRouter()

	def test_outgoing(self):
		"""
		Router.outgoing should call backend.send() method
		and set message.sent flag respectively
		"""
		backend = SimpleBackend(self.router, self.backend.name)
		self.router.add_backend(self.backend.name, backend)
		msg = OutgoingMessage(self.connection, 'hello!')
		self.router.outgoing(msg)
		self.assertTrue(msg.sent)
		self.assertEqual(msg, backend._saved_message)

	def test_outgoing_failure(self):
		"""
		Message sent flag should be false if backend.send() fails
		"""
		backend = SimpleBackend(self.router, self.backend.name, send_message=False)
		self.router.add_backend(self.backend.name, backend)
		msg = OutgoingMessage(self.connection, 'hello!')
		self.router.outgoing(msg)
		self.assertFalse(msg.sent)

	def test_handle_outgoing_with_connection(self):
		"""
		Router.handle_outgoing with a connection
		"""
		backend = SimpleBackend(self.router, self.backend.name)
		self.router.add_backend(self.backend.name, backend)
		self.router.handle_outgoing('hello!', connection=self.connection)
		self.assertEqual('hello!', backend._saved_message.text)
		self.assertEqual(self.connection, backend._saved_message.connection)


class MessagingTest(CustomRouter, TestCase, CreateDataTest):
	"""
	Test rapidsms.contrib.messaging form and views
	"""

	router_backends = {'simple': SimpleBackend}

	def setUp(self):
		super(MessagingTest, self).setUp()
		self.contact = self.create_contact()
		self.backend = self.create_backend({'name': 'simple'})
		self.connection = self.create_connection({'backend': self.backend,
		                                          'contact': self.contact})

	def test_contacts_with_connection(self):
		"""
		Only contacts with connections are valid options
		"""
		connectionless_contact = self.create_contact()
		data = {'text': 'hello!',
		        'recipients': [self.contact.id, connectionless_contact.pk]}
		form = MessageForm(data)
		self.assertTrue('recipients' in form.errors)

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

	def test_ajax_send_view(self):
		"""
		Test AJAX send view with valid data
		"""
		data = {'text': 'hello!',
		        'recipients': [self.contact.id]}
		response = self.client.post(reverse('send_message'), data)
		self.assertEqual(response.status_code, 200)
