from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from rapidsms.backends.vumi import views


class HttpTest(TestCase):

    urls = 'rapidsms.backends.vumi.urls'

    def setUp(self):
        self.rf = RequestFactory()
        self.url = reverse('vumi-backend', args=['vumi-backend'])
        self.view = views.VumiBackendView.as_view(backend_name='vumi-backend')

    def _post(self, data={}):
        request = self.rf.post(self.url, json.dumps(data),
                               content_type='text/json')
        return self.view(request, backend_name='vumi-backend')

    def test_valid_form(self):
        """ Form should be valid if GET keys match configuration """
        view = views.VumiBackendView()
        data = {'id': '1112223333', 'text': 'hi there'}
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
