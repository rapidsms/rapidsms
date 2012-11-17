#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.utils.modules import try_import, get_class
from rapidsms.log.mixin import LoggerMixin


class BackendBase(object, LoggerMixin):
    """Base class for outbound backend functionality."""

    @classmethod
    def find(cls, module_name):
        module = try_import(module_name)
        if module is None:
            return None
        return get_class(module, cls)

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

    def start(self, legacy_behavior=False):
        pass

    def run(self):
        pass

    def stop(self):
        pass

    @property
    def model(self):
        """Return RapidSMS model object for this backend."""
        from rapidsms.models import Backend
        backend, _ = Backend.objects.get_or_create(name=self.name)
        return backend
