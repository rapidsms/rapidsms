#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.utils.modules import import_class
from rapidsms.log.mixin import LoggerMixin


class BackendBase(object, LoggerMixin):
    """Base class for outbound backend functionality."""

    @classmethod
    def find(cls, module_name):
        return import_class(module_name, cls)

    def __init__(self, router, name, **kwargs):
        self.router = router
        self.name = name

        self._config = kwargs
        if hasattr(self, "configure"):
            self.configure(**kwargs)

    def _logger_name(self):  # pragma: no cover
        return "backend/%s" % self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<backend: %s>" % self.name

    def send(self, id_, text, identities, context={}):
        """
        Send a message.
        """
        # subclasses should override this
        raise NotImplementedError()

    @property
    def model(self):
        """Return RapidSMS model object for this backend."""
        from rapidsms.models import Backend
        backend, _ = Backend.objects.get_or_create(name=self.name)
        return backend
