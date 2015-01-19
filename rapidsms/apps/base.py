#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils.encoding import python_2_unicode_compatible

from ..utils.modules import try_import, get_class


@python_2_unicode_compatible
class AppBase(object):
    """
    """

    @classmethod
    def find(cls, app_name):
        """
        Return the RapidSMS app class from *app_name* (a standard Django
        app name), or None if it does not exist. Import errors raised
        *within* the module are allowed to propagate.
        """

        module_name = "%s.app" % app_name
        module = try_import(module_name)
        if module is None:
            return None
        try:
            app_class = get_class(module, cls)
        except AttributeError:
            app_class = None
        return app_class

    def __init__(self, router):
        self.router = router

    @property
    def name(self):
        """
        Return the name of the module which this app was defined within.
        This can be considered a unique identifier with the project.
        """

        return self.__module__.split(".")[-2]

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<app: %s>" %\
            self.name

    # incoming phases
    def filter(self, msg):
        pass

    def parse(self, msg):
        pass

    def handle(self, msg):
        pass

    def default(self, msg):
        pass

    def catch(self, msg):
        pass

    def cleanup(self, msg):
        pass

    # outgoing phases:
    def outgoing(self, msg):
        pass
