#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from rapidsms.models import Backend
from rapidsms.backends.base import BackendBase


class TestBackend(BackendBase):
    pass


class BackendBaseTest(TestCase):

    def test_backend_has_name(self):
        backend = BackendBase(None, "mock")
        self.assertEquals(repr(backend), "<backend: mock>")
        self.assertEquals(unicode(backend), "mock")
        self.assertEquals(backend.name, "mock")

    def test_backend_has_model(self):
        backend = BackendBase(None, "mock")
        # the row should be created when .model is called.
        self.assertEquals(backend.model.__class__, Backend)
        self.assertEquals(backend.model.name, "mock")
        # check that the backend stub was committed to the db.
        self.assertEquals(Backend.objects.filter(name="mock").count(), 1)

    def test_backend_passes_kwargs_to_configure(self):
        class ConfigurableBackend(BackendBase):
            def configure(self, **kwargs):
                self.conf = kwargs
        conf_backend = ConfigurableBackend(None, "mock", a=1, b=2)
        self.assertEquals(conf_backend.conf, {"a": 1, "b": 2})

    def test_backend_finds_valid_backend_class(self):
        """Class should be returned if valid."""
        backend = BackendBase.find('rapidsms.backends.test_base.TestBackend')
        self.assertEquals(TestBackend, backend)
