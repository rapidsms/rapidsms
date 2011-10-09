from django.test import TestCase
from django.core.urlresolvers import reverse

from rapidsms.backends.base import BackendBase
from rapidsms.router.test import TestRouter
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.tests.harness.base import MockBackendRouter, CreateDataTest
from rapidsms.tests.harness import backend

from rapidsms.contrib.messaging.forms import MessageForm


__all__ = ('OurgoingTest', 'MessagingTest')


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
        self.router.backends[self.backend.name] = backend
        msg = OutgoingMessage(self.connection, 'hello!')
        self.router.outgoing(msg)
        self.assertTrue(msg.sent)
        self.assertEqual(msg, backend._saved_message)

    def test_outgoing_failure(self):
        """
        Message sent flag should be false if backend.send() fails
        """
        backend = SimpleBackend(self.router, self.backend.name, send_message=False)
        self.router.backends[self.backend.name] = backend
        msg = OutgoingMessage(self.connection, 'hello!')
        self.router.outgoing(msg)
        self.assertFalse(msg.sent)

    def test_handle_outgoing_with_connection(self):
        """
        Router.handle_outgoing with a connection
        """
        backend = SimpleBackend(self.router, self.backend.name)
        self.router.backends[self.backend.name] = backend
        self.router.handle_outgoing('hello!', connection=self.connection)
        self.assertEqual('hello!', backend._saved_message.text)
        self.assertEqual(self.connection, backend._saved_message.connection)


class MessagingTest(MockBackendRouter, CreateDataTest, TestCase):
    """
    Test rapidsms.contrib.messaging form and views
    """

    def setUp(self):
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
        self.assertEqual(len(backend.outbox), 0)

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
        self.assertEqual(backend.outbox[0].text, data['text'])

    def test_ajax_send_view(self):
        """
        Test AJAX send view with valid data
        """
        data = {'text': 'hello!',
                'recipients': [self.contact.id]}
        response = self.client.post(reverse('send_message'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(backend.outbox[0].text, data['text'])
