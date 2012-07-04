import urllib

from nose.tools import assert_equals, assert_true, assert_raises

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from rapidsms.tests.harness import MockRouter
from rapidsms.backends.http import RapidHttpBackend

from django.utils import simplejson as json


class NewBackend(RapidHttpBackend):
    def configure(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(NewBackend, self).configure(*args, **kwargs)

def test_handle_good_request():
    """ handle_request must return a HttpResponse """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', 
                              router=router)
    http_request = HttpRequest()
    http_request.GET = {'id':'123','text':'message'}
    response = backend.handle_request(http_request)
    assert_true(isinstance(response, HttpResponse))

def test_handle_bad_request():
    """ handle_request must return a HttpResponse """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', 
                              router=router)
    response = backend.handle_request(HttpRequest())
    assert_true(isinstance(response, HttpResponseBadRequest))

def test_handle_json_missing_header():
    """ JSON requests will fail unless CONTENT_TYPE header is set """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', router=router)
    data = json.dumps({'id':'123','text':'message'})
    http_request = HttpRequest()
    http_request.POST = data
    response = backend.handle_request(HttpRequest())
    assert_true(isinstance(response, HttpResponseBadRequest))

def test_handle_json_with_header():
    """ JSON should be interpreted if request header is set """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', router=router)
    data = json.dumps({'id':'123','text':'message'})
    http_request = HttpRequest()
    http_request.POST = data
    http_request.META['CONTENT_TYPE'] = 'application/json'
    response = backend.handle_request(HttpRequest())
    assert_equals(response.status_code, 200)

def test_json_outbound_message():
    """ JSON-enabled backend should reply in JSON """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', router=router, format='JSON')
    data = {'message': 'foo', 'phone': '1112223333'}
    req = backend._build_request(data)
    assert_equals(req.get_data(), json.dumps(data))

def test_post_outbound_message():
    """ POST-enabled backend should reply as an HTTP POST """
    router = MockRouter()
    backend = RapidHttpBackend(name='test', router=router, format='POST')
    data = {'message': 'foo', 'phone': '1112223333'}
    req = backend._build_request(data)
    assert_equals(req.get_data(), urllib.urlencode(data))

def test_config():
    """ Allow custom configuration """
    router = MockRouter()
    backend = RapidHttpBackend(router=router, name="test_http_backend")
    backend.configure("localhost", 8080,
                      gateway_url='http://smsgateway.com',
                      params_outgoing = 'user=my_username&password=my_password&id=%(params_incoming)s&text=%(message)s',
                      params_incoming = "id=%(phone_number)s&text=%(message)s")
    assert_equals('http://smsgateway.com', backend.gateway_url)
    assert_equals('user=my_username&password=my_password&id=%(params_incoming)s&text=%(message)s', backend.http_params_outgoing)
    assert_equals('id', backend.incoming_phone_number_param)
    assert_equals('text', backend.incoming_message_param)

def test_bad_config():
    """ Test bad configuration """
    router = MockRouter()
    assert_raises(Exception, RapidHttpBackend, router=router, 
                                  username='rapidsms', 
                                  gateway_url = 'http://smsgateway.com',
                                  params_outgoing = "user=my_username&password=my_password&id=%(params_incoming)s&text=%(message)s",
                                  params_incoming = "id=%(foo)s&text=%(blargh)s")

def test_extra_config():
    """ Allow custom configuration """
    router = MockRouter()
    backend = NewBackend(name='test', router=router, username='rapidsms')
    assert_equals('rapidsms', backend.username)
