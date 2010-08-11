from nose.tools import assert_equals, assert_true

from django.http import HttpRequest, HttpResponse

from rapidsms.tests.harness import MockRouter
from rapidsms.backends.http import RapidHttpBacked


class NewBackend(RapidHttpBacked):
    def configure(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(NewBackend, self).configure(*args, **kwargs)


def test_handle_request():
    """ handle_request must return a HttpResponse """
    router = MockRouter()
    backend = RapidHttpBacked(name='test', router=router)
    response = backend.handle_request(HttpRequest())
    assert_true(isinstance(response, HttpResponse))


def test_extra_config():
    """ Allow custom configuration """
    router = MockRouter()
    backend = NewBackend(name='test', router=router, username='rapidsms')
    assert_equals('rapidsms', backend.username)
