#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equals
from rapidsms.backends.base import BackendBase


def test_backend_has_name():
    backend = BackendBase(None, "mock")

    assert_equals(repr(backend), "<backend: mock>")
    assert_equals(unicode(backend), "mock")
    assert_equals(backend.name, "mock")


def test_backend_has_model():
    backend = BackendBase(None, "mock")
    from ...models import Backend as B

    # before fetching the model via BackendBase, check that it does not
    # already exist in the db. (if it does, this test checks nothing.)
    assert_equals(B.objects.filter(name="mock").count(), 0)

    # the row should be created when .model is called.
    assert_equals(backend.model.__class__, B)
    assert_equals(backend.model.name, "mock")

    # check that the backend stub was committed to the db.
    assert_equals(B.objects.filter(name="mock").count(), 1)

    # tidy up the db.
    B.objects.filter(name="mock").delete()


def test_backend_passes_kwargs_to_configure():
    class ConfigurableBackend(BackendBase):
        def configure(self, **kwargs):
            self.conf = kwargs

    conf_backend = ConfigurableBackend(None, "mock", a=1, b=2)
    assert_equals(conf_backend.conf, {"a": 1, "b": 2})


def test_backend_finds_valid_backend_classes():
    backend = BackendBase.find('rapidsms.backends.kannel.outgoing')
    from rapidsms.backends.kannel.outgoing import KannelBackend
    assert_equals(backend, KannelBackend)
