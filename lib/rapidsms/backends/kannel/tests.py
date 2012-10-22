from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from rapidsms.backends.kannel import views
from rapidsms.tests.harness.base import CustomRouter
from rapidsms.tests.harness.base import CreateDataTest

from rapidsms.backends.kannel import KannelBackend


class KannelTestMixin(object):

    urls = 'rapidsms.backends.kannel.urls'

    def setUp(self):
        self.rf = RequestFactory()
        self.url = reverse('kannel-backend', args=['kannel-backend'])
        self.view = views.KannelBackendView.as_view(backend_name='kannel-backend')

    def _get(self, data={}):
        request = self.rf.get(self.url, data)
        return self.view(request)


class KannelTest(KannelTestMixin, TestCase):

    def test_valid_form(self):
        """ Form should be valid if GET keys match configuration """
        view = views.KannelBackendView()
        data = {'id': '1112223333', 'text': 'hi there'}
        view.request = self.rf.get(self.url, data)
        form = view.get_form(view.get_form_class())
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """ Form is invalid if POST keys don't match configuration """
        view = views.KannelBackendView()
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        view.request = self.rf.get(self.url, data)
        form = view.get_form(view.get_form_class())
        self.assertFalse(form.is_valid())


class KannelViewTest(CustomRouter, KannelTestMixin, TestCase):

    router_class = 'rapidsms.router.test.NoOpTestRouter'

    def test_valid_response_get(self):
        """ HTTP 200 should return if form is valid """
        data = {'id': '1112223333', 'text': 'hi there'}
        response = self._get(data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_response(self):
        """ HTTP 400 should return if form is invalid """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._get(data)
        self.assertEqual(response.status_code, 400)


class KannelSendTest(CreateDataTest, TestCase):

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
