#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from ..log.mixin import LoggerMixin
from ..utils.modules import try_import, get_class


class AppBase(object, LoggerMixin):
    """
    """


    @classmethod
    def find(cls, app_name):
        module_name = "%s.app" % app_name
        module = try_import(module_name)
        if module is None: return None
        return get_class(module, cls)


    def __init__(self, router=None):
        self._router = router


    @property
    def router (self):
        if hasattr(self, "_router"):
            return self._router


    def _logger_name(self):
        return "app/%s" % self.name


    @property
    def name(self):
        """
        Return the name of the module which this app was defined within.
        This can be considered a unique identifier with the project.
        """

        return self.__module__.split(".")[-2]


    def __unicode__(self):
        return self.name


    def __repr__(self):
        return "<app: %s>" %\
            self.name


    def start (self):
        pass

    def filter (self, message):
        pass

    def parse (self, message):
        pass

    def handle (self, message):
        pass

    def catch (self, message):
        pass

    def cleanup (self, message):
        pass

    def outgoing (self, message):
        pass

    def stop (self):
        pass
