from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url

from rapidsms.backends.kannel import views
from rapidsms.backends.kannel import KannelBackend
from rapidsms.backends.kannel.forms import KannelForm
from rapidsms.tests.harness import RapidTest, CreateDataMixin


urlpatterns = patterns('',
                       url(r"^backend/kannel/$",
                           views.KannelBackendView.as_view(
                               backend_name='kannel-backend'),
                           name='kannel-backend'),
                       )


class KannelFormTest(TestCase):

    def test_valid_form(self):
        """Form should be valid if GET keys match configuration."""
        data = {'id': '1112223333', 'text': 'hi there'}
        form = KannelForm(data, backend_name='kannel-backend')
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Form is invalid if POST keys don't match configuration."""
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        form = KannelForm(data, backend_name='kannel-backend')
        self.assertFalse(form.is_valid())

    def test_get_incoming_data(self):
        """get_incoming_data should return matching text and connection."""
        data = {'id': '1112223333', 'text': 'hi there'}
        form = KannelForm(data, backend_name='kannel-backend')
        form.is_valid()
        incoming_data = form.get_incoming_data()
        self.assertEqual(data['text'], incoming_data['text'])
        self.assertEqual(data['id'],
                         incoming_data['connection'].identity)
        self.assertEqual('kannel-backend',
                         incoming_data['connection'].backend.name)


class KannelViewTest(RapidTest):

    urls = 'rapidsms.backends.kannel.tests'
    disable_phases = True

    def test_valid_response_get(self):
        """HTTP 200 should return if data is valid."""
        data = {'id': '1112223333', 'text': 'hi there'}
        response = self.client.get(reverse('kannel-backend'), data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_response(self):
        """HTTP 400 should return if data is invalid."""
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self.client.get(reverse('kannel-backend'), data)
        self.assertEqual(response.status_code, 400)

    def test_valid_post_message(self):
        """Valid POSTs should pass message object to router."""
        data = {'id': '1112223333', 'text': 'hi there'}
        self.client.get(reverse('kannel-backend'), data)
        message = self.inbound[0]
        self.assertEqual(data['text'], message.text)
        self.assertEqual(data['id'],
                         message.connection.identity)
        self.assertEqual('kannel-backend',
                         message.connection.backend.name)


class KannelSendTest(CreateDataMixin, TestCase):

    def test_outgoing_keys(self):
        """Outgoing POST data should contain the proper keys."""
        message = self.create_outgoing_message()
        config = {
            "sendsms_url": "http://127.0.0.1:13013/cgi-bin/sendsms",
            "sendsms_params": {"smsc": "usb0-modem",
                               "from": "+SIMphonenumber",
                               "username": "rapidsms",
                               "password": "CHANGE-ME"},
            "coding": 0,
            "charset": "ascii",
            "encode_errors": "ignore",
        }
        backend = KannelBackend(None, "kannel", **config)
        data = backend.prepare_message(message)
        self.assertEqual(config['sendsms_params']['smsc'], data['smsc'])
        self.assertEqual(config['sendsms_params']['from'], data['from'])
        self.assertEqual(config['sendsms_params']['username'],
                         data['username'])
        self.assertEqual(config['sendsms_params']['password'],
                         data['password'])
        self.assertEqual(message.connection.identity, data['to'])
        self.assertEqual(message.text, data['text'])
        self.assertEqual(config['coding'], data['coding'])
        self.assertEqual(config['charset'], data['charset'])

    def test_outgoing_unicode_characters(self):
        """Ensure outgoing messages are encoded properly."""
        message = self.create_outgoing_message()
        config = {
            "sendsms_url": "http://127.0.0.1:13013/cgi-bin/sendsms",
            "sendsms_params": {"smsc": "usb0-modem",
                               "from": "+SIMphonenumber",
                               "username": "rapidsms",
                               "password": "CHANGE-ME"},
            "coding": 0,
            "charset": "UTF-8",
            "encode_errors": "ignore",
        }
        backend = KannelBackend(None, "kannel", **config)
        data = backend.prepare_message(message)
        self.assertEqual(data['text'].decode('UTF-8'), message.text)
