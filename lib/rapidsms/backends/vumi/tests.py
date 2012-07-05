from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from rapidsms.router.test import TestRouter
from rapidsms.backends.vumi import views
from rapidsms.backends.vumi.outgoing import VumiBackend
from rapidsms.tests.harness.base import CreateDataTest
from rapidsms.messages.outgoing import OutgoingMessage


class ReceiveTest(TestCase):

    urls = 'rapidsms.backends.vumi.urls'

    def setUp(self):
        self.rf = RequestFactory()
        self.url = reverse('vumi-backend', args=['vumi-backend'])
        self.view = views.VumiBackendView.as_view(backend_name='vumi-backend')

    def _post(self, data={}):
        request = self.rf.post(self.url, json.dumps(data),
                               content_type='text/json')
        return self.view(request)

    def test_valid_form(self):
        """ Form should be valid if GET keys match configuration """
        view = views.VumiBackendView()
        data = {'from_adr': '1112223333', 'content': 'hi there'}
        view.request = self.rf.post(self.url, json.dumps(data),
                                    content_type='text/json')
        form = view.get_form(view.get_form_class())
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """ Form is invalid if POST keys don't match configuration """
        view = views.VumiBackendView()
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        view.request = self.rf.post(self.url, json.dumps(data),
                                    content_type='text/json')
        form = view.get_form(view.get_form_class())
        self.assertFalse(form.is_valid())

    def test_invalid_response(self):
        """ HTTP 400 should return if form is invalid """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._post(data)
        self.assertEqual(response.status_code, 400)

    def test_outgoing_context(self):
        """ Make sure outgoing JSON contains correct keys """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._post(data)
        self.assertEqual(response.status_code, 400)


class SendTest(CreateDataTest, TestCase):

    def test_required_fields(self):
        """ Vumi backend requires Gateway URL and credentials """
        router = TestRouter()
        self.assertRaises(TypeError, VumiBackend, router, "vumi")

    def test_outgoing_keys(self):
        """ Vumi requires JSON to include to_adr and content """
        connection = self.create_connection()
        message = OutgoingMessage(connection, 'hello!')
        router = TestRouter()
        backend = VumiBackend(router, "vumi",
                              vumi_url="http://example.com",
                              vumi_credentials={'username': 'user',
                                                'password': 'pass'})
        request = backend._build_request(message)
        self.assertEqual(request.get_full_url(), "http://example.com")
        self.assertTrue('to_adr' in request.get_data())
        self.assertTrue('content' in request.get_data())
