from django.conf import settings
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from rapidsms.backends.kannel import views
from rapidsms.tests.harness.base import CustomRouter


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
