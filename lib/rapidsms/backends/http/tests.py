from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import *

from rapidsms.tests.harness import CustomRouter

from . import views
from .forms import BaseHttpForm, GenericHttpForm

get_view_kwargs = {'params': {'identity_name': 'phone',
                              'text_name': 'message'},
                   'http_method_names': ['get']}
post_view_kwargs = {'params': {'identity_name': 'phone',
                               'text_name': 'message'},
                    'http_method_names': ['post']}
urlpatterns = patterns('',
    url(r"^(?P<backend_name>[\w-]+)/$", views.GenericHttpBackendView.as_view(),
        kwargs=get_view_kwargs, name='generic-http-get-view'),
    url(r"^(?P<backend_name>[\w-]+)/$", views.GenericHttpBackendView.as_view(),
        kwargs=post_view_kwargs, name='generic-http-post-view'),
)


class HttpTestMixin(object):

    urls = 'rapidsms.backends.http.tests'

    def setUp(self):
        self.rf = RequestFactory()
        self.post_url = reverse('generic-http-post-view',
                                args=['test-post-backend'])
        self.get_url = reverse('generic-http-get-view',
                               args=['test-get-backend'])
        self.view = views.GenericHttpBackendView.as_view(backend_name='http-backend')

    def _post(self, data={}):
        request = self.rf.post(self.post_url, data)
        return self.view(request)

    def _get(self, data={}):
        request = self.rf.get(self.get_url, data)
        return self.view(request)


class HttpFormTest(TestCase):

    def test_valid_default_post(self):
        """ Form should be valid if POST keys match default configuration """
        data = {'identity': '1112223333', 'text': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend')
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_get(self):
        """ Form should be valid if POST keys match configuration """
        data = {'phone': '1112223333', 'message': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend',
                               identity_name='phone', text_name='message')
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form_post(self):
        """ Form is invalid if POST keys don't match configuration """
        data = {'invalid-phone': '1112223333', 'invalid-message': 'hi there'}
        form = GenericHttpForm(data, backend_name='http-backend')
        self.assertFalse(form.is_valid())

    def test_get_incoming_data(self):
        """ Subclasses must implement get_incoming_data """
        form = BaseHttpForm(backend_name='http-backend')
        self.assertRaises(NotImplementedError, form.get_incoming_data)


class HttpViewTest(CustomRouter, HttpTestMixin, TestCase):

    router_class = 'rapidsms.router.test.NoOpTestRouter'

    def test_valid_response_post(self):
        """ HTTP 200 should return if form is valid """
        data = {'identity': '1112223333', 'text': 'hi there'}
        response = self._post(data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_response_post(self):
        """ HTTP 400 should return if form is invalid """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._post(data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_response_get(self):
        """ HTTP 400 should return if form is invalid """
        data = {'invalid-phone': '1112223333', 'message': 'hi there'}
        response = self._get(data)
        self.assertEqual(response.status_code, 400)
