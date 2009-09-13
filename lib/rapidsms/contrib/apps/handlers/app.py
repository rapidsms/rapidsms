#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from rapidsms.djangoproject import settings
from rapidsms.utils.modules import find_python_files, get_class, try_import
from rapidsms.contrib.apps.handlers import BaseHandler


class App(rapidsms.App):
    def _find_handlers(self, module_name):
        """
            Returns a list of handlers (subclasses of app.handlers.HandlerBase)
            defined in the "handlers" directory of *module_name*. Each Python
            file (*.py) is expected to contain a single new-style class, which
            can be named arbitrarily. (but probably shouldn't be.)

            Returns an empty list if no handlers are defined, or the directory
            can't be opened. All exceptions raised while importing handlers are
            allowed to propagate.
        """

        handlers_module = try_import(
            "%s.handlers" % module_name)

        if handlers_module is None:
            return []

        if not hasattr(handlers_module, "__path__"):
            raise Exception(
                "Module %s must be a directory." %
                    (handlers_module.__name__))

        files = find_python_files(
            handlers_module.__path__[0])

        module_names = [
            "%s.%s" % (handlers_module.__name__, file)
            for file in files]

        modules = [
            try_import(mod_name)
            for mod_name in module_names]

        return [
            get_class(mod, BaseHandler)
            for mod in filter(None, modules)]


    def start(self):
        """Spiders all RapidSMS apps, and registers all available handlers."""

        self.handlers = []

        for module_name in settings.RAPIDSMS_APPS.keys():
            handlers = self._find_handlers(module_name)
            self.handlers.extend(handlers)

        class_names = [cls.__name__ for cls in self.handlers]
        self.info("Registered handlers: %s" % (", ".join(class_names)))


    def handle(self, msg):
        """Forwards the *msg* to every handler, and short-circuits the phase if
           any of them accept it. The first to accept it will block the others,
           and there's (deliberately) no way to predict the order that they're
           called in, so handlers should be as reluctant as possible."""

        for handler in self.handlers:
            if handler.dispatch(self.router, msg):
                self.info("Incoming message handled by %s" % handler.__name__)
                return True
