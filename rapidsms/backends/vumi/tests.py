import json
from mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url

from rapidsms.backends.vumi import views
from rapidsms.backends.vumi.outgoing import VumiBackend
from rapidsms.backends.vumi.forms import VumiForm
from rapidsms.tests.harness import RapidTest, CreateDataMixin


urlpatterns = patterns('',
    url(r"^backend/vumi/$",
        views.VumiBackendView.as_view(backend_name='vumi-backend'),
        name='vumi-backend'),
)


class VumiFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "transport_name": "transport",
            "in_reply_to": None,
            "group": None,
            "from_addr": "127.0.0.1:38634",
            "message_type": "user_message",
            "helper_metadata": {},
            "to_addr": "0.0.0.0:8005",
            "content": "ping",
            "message_version": "20110921",
            "transport_type": "telnet",
            "timestamp": "2012-07-06 14:08:20.845715",
            "transport_metadata": {},
            "session_event": "resume",
            "message_id": "56047985ceec40da908ca064f2fd59d3"
        }

    def test_valid_form(self):
        """Form should be valid if GET keys match configuration."""
        form = VumiForm(self.valid_data, backend_name='vumi-backend')
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Form is invalid if POST keys don't match configuration."""
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        form = VumiForm(data, backend_name='vumi-backend')
        self.assertFalse(form.is_valid())

    def test_get_incoming_data(self):
        """get_incoming_data should return matching text and connection."""
        form = VumiForm(self.valid_data, backend_name='vumi-backend')
        form.is_valid()
        incoming_data = form.get_incoming_data()
        self.assertEqual(self.valid_data['content'], incoming_data['text'])
        self.assertEqual(self.valid_data['from_addr'],
                         incoming_data['connection'].identity)
        self.assertEqual('vumi-backend',
                         incoming_data['connection'].backend.name)


class VumiViewTest(RapidTest):

    urls = 'rapidsms.backends.vumi.tests'
    disable_phases = True

    def setUp(self):
        self.valid_data = {
            "transport_name": "transport",
            "in_reply_to": None,
            "group": None,
            "from_addr": "127.0.0.1:38634",
            "message_type": "user_message",
            "helper_metadata": {},
            "to_addr": "0.0.0.0:8005",
            "content": "ping",
            "message_version": "20110921",
            "transport_type": "telnet",
            "timestamp": "2012-07-06 14:08:20.845715",
            "transport_metadata": {},
            "session_event": "resume",
            "message_id": "56047985ceec40da908ca064f2fd59d3"
        }

    def test_valid_response_post(self):
        """HTTP 200 should return if data is valid."""
        response = self.client.post(reverse('vumi-backend'),
                                    json.dumps(self.valid_data),
                                    content_type='text/json')
        self.assertEqual(response.status_code, 200)

    def test_invalid_response(self):
        """HTTP 400 should return if data is invalid."""
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self.client.post(reverse('vumi-backend'), json.dumps(data),
                                    content_type='text/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_json(self):
        """HTTP 400 should return if JSON is invalid."""
        data = "{bad json, , lala}"
        response = self.client.post(reverse('vumi-backend'), data,
                                    content_type='text/json')
        self.assertEqual(response.status_code, 400)

    def test_valid_post_message(self):
        """Valid POSTs should pass message object to router."""
        self.client.post(reverse('vumi-backend'), json.dumps(self.valid_data),
                         content_type='text/json')
        message = self.inbound[0]
        self.assertEqual(self.valid_data['content'], message.text)
        self.assertEqual(self.valid_data['from_addr'],
                         message.connection.identity)
        self.assertEqual('vumi-backend',
                         message.connection.backend.name)

    def test_blank_message_is_valid(self):
        """Blank messages should be considered valid."""
        empty = self.valid_data.copy()
        empty.update({'content': ''})
        null = self.valid_data.copy()
        null.update({'content': None})
        no_content = self.valid_data.copy()
        del no_content['content']
        for blank_msg in [empty, null, no_content]:
            self.client.post(reverse('vumi-backend'), json.dumps(blank_msg),
                             content_type='text/json')
            message = self.inbound[0]
            self.assertEqual('', message.text)


class VumiSendTest(CreateDataMixin, TestCase):

    def test_required_fields(self):
        """Vumi backend requires Gateway URL and credentials."""
        self.assertRaises(TypeError, VumiBackend, None, "vumi")

    def test_outgoing_keys(self):
        """Vumi requires JSON to include to_addr and content."""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity], {})
        self.assertEqual(kwargs['url'], config['sendsms_url'])
        data = json.loads(kwargs['data'])
        self.assertEqual(data['to_addr'], [message.connections[0].identity])
        self.assertEqual(data['content'], message.text)

    def test_response_external_id(self):
        """Make sure external_id context is sent to Vumi."""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity],
                                         {'external_id': 'ASDF1234'})
        data = json.loads(kwargs['data'])
        self.assertEqual("ASDF1234", data['in_reply_to'])

    def test_bulk_response_external_id(self):
        """Only single messages should include in_response_to."""
        conn1 = self.create_connection()
        conn2 = self.create_connection()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request("1234", "foo",
                                         [conn1.identity, conn2.identity],
                                         {'external_id': 'ASDF1234'})
        data = json.loads(kwargs['data'])
        self.assertTrue('in_reply_to' not in data)

    def test_message_id_in_metadata(self):
        """Make sure our uuid is sent to Vumi."""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity], {})
        data = json.loads(kwargs['data'])
        self.assertIn(message.id, data.get('metadata', {}).values())

    def test_from_addr_and_endpoint_in_payload(self):
        """Make sure that we include from_addr or endpoint if provided, but only those keys"""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        context = {'from_addr': '5551212',
                   'endpoint': '12345',
                   'other': 'not included'}
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity], context)
        data = json.loads(kwargs['data'])
        self.assertEqual(context['from_addr'], data['from_addr'])
        self.assertEqual(context['endpoint'], data['endpoint'])
        self.assertNotIn('other', data)

    def test_send(self):
        """Test successful send."""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity], {})
        with patch('rapidsms.backends.vumi.outgoing.requests.post') as mock_post:
            backend.send(message.id, message.text,
                         [message.connections[0].identity], {})
        mock_post.assert_called_once_with(**kwargs)

    def test_auth(self):
        """Vumi backend shold use basic authentication if given user/pass."""
        message = self.create_outgoing_message()
        config = {"sendsms_url": "http://example.com",
                  "sendsms_user": "username",
                  "sendsms_pass": "password"}
        backend = VumiBackend(None, "vumi", **config)
        kwargs = backend.prepare_request(message.id, message.text,
                                         [message.connections[0].identity], {})
        self.assertTrue('auth' in kwargs)
