#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import component


class App(component.Component):
    """
    """

    NAMED_PRIORITIES = {
        "first":   1,
        "highest": 1,
        "high":   10,
        "normal": 50,
        "low":    90,
        "lowest": 99,
        "last":   99 }


    def __init__(self, router=None):
        self._router = router


    def __str__(self):
        return self.title


    def __repr__(self):
        return "<%s.%s>" %\
            (type(self).__module__, type(self).__name__)


    @staticmethod
    def _name(module_name):
        """
        Returns the last interesting part of *module_name* (which can also be a
        class name), to uniquely identify it without leaving variations of "app"
        all over the place. This method attempts to handle all of the various
        ways that RapidSMS apps can be named. For example:

          >>> App._name("apps.alpha.app")
          'alpha'

          >>> App._name("rapidsms.contrib.apps.beta")
          'beta'

          >>> App._name("somewhere.else.gamma.App")
          'gamma'
        """

        parts = filter(
            lambda x: x not in ["App", "app", "apps"],
            module_name.split("."))

        return parts[-1]


    @property
    def name(self):
        """
        Returns the name of the module which this app was defined within. To be
        findable by Router.add_app, this module name will be importable as-is,
        making it unambiguous within this project, and usable as an identifier.

        # pretend we're in myproject/whatever/app.py
        >>> __name__ = "myproject.whatever.app"

        >>> class MockApp(App): pass
        >>> MockApp(None).name
        'whatever'
        """

        return App._name(self.__module__)


    @property
    def title(self):
        """
        Returns the title of this app, which isn't guaranteed to be unique,
        consistant between calls, or in any particular format -- it should be
        used for display purposes only.

        >>> __name__ = "myproject.whatever.app"
        >>> class MockApp(App):
        ...     pass

        >>> MockApp().title
        'Whatever'
        """

        if hasattr(self, "_title"):
            return self._title

        module_name = type(self).__module__
        return self._name(module_name).title()


    def priority(self):
        """Returns the numeric "priority" of this RapidSMS App object,
           which dictates the order in which the app will be notified
           of incoming and outgoing messages, relative to other apps.
           The best way to set the priority of an app is to include a
           PRIORITY constant in the class definition."""

        named = App.NAMED_PRIORITIES
        if hasattr(self, "PRIORITY"):
            p = getattr(self, "PRIORITY")
            pt = type(p)
            
            # if the PRIORITY is a string, we can assume that it's a named
            # priority. these should almost always be used over integers,
            # so we can re-jig them in future, if necessary
            if pt == str:
                if p in named:
                    return named[p]
                
                else:
                    self.warning("Invalid PRIORITY name: %s" % p)
            
            # an integer is fine, even if it *is*
            # a little lower-level than most app
            # authors need to be
            elif pt == int:
                if p >= 1 and p <= 99:
                    return p
                
                else:
                    # we enforce the range here, to prevent hackery. because
                    # hackery, in the brave new rapidsms world, is BAD
                    self.warning("Invalid numeric PRIORITY: %d (keep it between 1 and 99)")
             
            # TODO: is there a use-case for non int/string
            # priorities? I can't think of one...
            else:
                self.warning("Invalid PRIORITY type: %s (use str or int)" % tp)
        
        # if the app doesn't have a priority of its own, or it
        # was invalid (and warned) above, default to "normal"
        return named["normal"]


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

    def pre_send (self, message):
        pass

    def stop (self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
