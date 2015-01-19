from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf.urls import url

from rapidsms.tests.harness import RapidTest
from rapidsms.backends.http import views
from rapidsms.backends.http.forms import BaseHttpForm, GenericHttpForm


class CustomHttpBackend(views.GenericHttpBackendView):
    """Generic HTTP backend with custom parameters."""

    backend_name = 'custom-http-backend'
    params = {'identity_name': 'phone', 'text_name': 'message'}


urlpatterns = (
    url(r"^backend/http/$",
        views.GenericHttpBackendView.as_view(backend_name='http-backend'),
        name='http-backend'),
    url(r"^backend/http-custom/$",
        CustomHttpBackend.as_view(),
        name='custom-http-backend'),
)


class HttpFormTest(TestCase):

    def test_valid_default_post(self):
        """Form should be valid if POST keys match default configuration."""
        data = {'identity': '1112223333', 'text': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend')
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_get(self):
        """Form should be valid if POST keys match configuration."""
        data = {'phone': '1112223333', 'message': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend',
                               identity_name='phone', text_name='message')
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form_post(self):
        """Form is invalid if POST keys don't match configuration."""
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend')
        self.assertFalse(form.is_valid())

    def test_not_implemented_get_incoming_data(self):
        """Subclasses must implement get_incoming_data."""
        form = BaseHttpForm(backend_name='http-backend')
        self.assertRaises(NotImplementedError, form.get_incoming_data)

    def test_get_incoming_data(self):
        """get_incoming_data should return matching text and connection."""
        data = {'identity': '1112223333', 'text': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend')
        form.is_valid()
        incoming_data = form.get_incoming_data()
        self.assertEqual(data['text'], incoming_data['text'])
        self.assertEqual(data['identity'],
                         incoming_data['connection'].identity)
        self.assertEqual('http-backend',
                         incoming_data['connection'].backend.name)


class HttpViewTest(RapidTest):

    urls = 'rapidsms.backends.http.tests'
    disable_phases = True

    def setUp(self):
        self.http_backend_url = reverse('http-backend')
        self.custom_http_backend_url = reverse('custom-http-backend')

    def test_valid_response_get(self):
        """HTTP 200 should return with valid GET data."""
        data = {'identity': '1112223333', 'text': 'hi there'}
        response = self.client.get(self.http_backend_url, data)
        self.assertEqual(response.status_code, 200)

    def test_valid_response_post(self):
        """HTTP 200 should return with valid POST data."""
        data = {'identity': '1112223333', 'text': 'hi there'}
        response = self.client.post(self.http_backend_url, data)
        self.assertEqual(response.status_code, 200)

    def test_custom_valid_response_post(self):
        """HTTP 200 should return with custom valid POST data."""
        data = {'phone': '1112223333', 'message': 'hi there'}
        response = self.client.post(self.custom_http_backend_url, data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_response_get(self):
        """HTTP 400 should return with invalid GET data."""
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self.client.get(self.http_backend_url, data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_response_post(self):
        """HTTP 400 should return with invalid POST data."""
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self.client.post(self.http_backend_url, data)
        self.assertEqual(response.status_code, 400)

    def test_custom_invalid_response_post(self):
        """HTTP 400 should return with custom valid POST data."""
        data = {'bad-phone': '1112223333', 'bad-message': 'hi there'}
        response = self.client.post(self.custom_http_backend_url, data)
        self.assertEqual(response.status_code, 400)

    def test_valid_post_message(self):
        """Valid POSTs should pass message object to router."""
        data = {'identity': '1112223333', 'text': 'hi there'}
        self.client.post(self.http_backend_url, data)
        message = self.inbound[0]
        self.assertEqual(data['text'], message.text)
        self.assertEqual(data['identity'],
                         message.connection.identity)
        self.assertEqual('http-backend',
                         message.connection.backend.name)

    def test_valid_post_message_backend_name(self):
        """Created message/connection should be from custom http backend"""
        data = {'phone': '1112223333', 'message': 'hi there'}
        self.client.post(self.custom_http_backend_url, data)
        message = self.inbound[0]
        self.assertEqual('custom-http-backend',
                         message.connection.backend.name)
