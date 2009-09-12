#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, sys
import rapidsms
from rapidsms.webui import settings
from handlers import BaseHandler


class App(rapidsms.App):
    def _find_python_files(self, path):
        """Returns a list of the Python files (*.py) in a directory. Note that
           the existance of a Python source file does not guarantee that it is
           a valid module, because the directory (or any number of its parents)
           may not contain an __init__.py, rendering it a non-module.

           This seems a bit of an oversimplification, given that Python modules
           can live inside eggs and zips and the such, but if it's good enough
           for django.core.management.find_commands, it's good enough for me.

           Returns an empty list if the directory doesn't exist, couldn't be
           iterated, or contains no relevant files."""

        try:
            return [
                # trim the extension
                file[:-3]

                # iterate all files in the path
                # (doesn't include . and .. links)
                for file in os.listdir(path)

                # ignore __magic__ files and those
                # not ending with the .py suffix
                if not file.startswith("_")
                and file.endswith('.py')]

        except OSError:
            return []


    def _try_import(self, module_name):
        """Attempts to import and return *module_name*, returning None if an
           ImportError was raised. Unlike the standard try/except approach to
           optional imports, this method jumps through some hoops to avoid
           catching ImportErrors raised from within *module_name*."""

        try:
            __import__(module_name)
            return sys.modules[module_name]

        except ImportError:

            # extract a backtrace, so we can find out where the exception was
            # raised from. if there is a NEXT frame, it means that the import
            # statement succeeded, but an ImportError was raised from _within_
            # the imported module. we must allow this error to propagate, to
            # avoid silently masking it with this optional import
            traceback = sys.exc_info()[2]
            if traceback.tb_next:
                raise

            # otherwise, the exception was raised
            # from this scope. *module_name* couldn't
            # be imported,which isn't such a big deal
            return None


    def _get_classes(self, module, superclass=None):
        """Returns a list of new-style classes defined in *module*, excluding
           _private and __magic__ names, and optionally filtering only those
           inheriting from *superclass*. Note that both of the arguments are
           actual modules, not names.

           This method only returns classes that were defined in *module*. Those
           imported from elsewhere are ignored."""

        objects = [
            getattr(module, name)
            for name in dir(module)
            if not name.startswith("_")]

        # filter out everything that isn't a new-style
        # class, or wasn't defined in *module* (ie, it
        # is imported from somewhere else)
        classes = [
            obj for obj in objects
            if isinstance(obj, type)
            and (obj.__module__ == module.__name__)]

        # if a superclass was given, filter the classes
        # again to remove those that aren't its subclass
        if superclass is not None:
            classes = [
                cls for cls in classes
                if issubclass(cls, superclass)]

        return classes


    def _get_class(self, module, superclass=None):
        """Returns the lone class contained by *module*, or raises a descriptive
           AttributeError if *module* contains zero or more than one class. This
           is useful when expecting a single class from a module without knowing
           its name, to avoid the usual constantly-named object in a module (eg.
           App, Backend, Command, Handler)."""

        classes = self._get_classes(
            module, superclass)

        if len(classes) == 1:
            return classes[0]

        # the error message includes *superclass*
        # if one was given, otherwise it's generic
        desc = "subclasses of %s" % (superclass.__name__)\
            if superclass else "new-style classes"

        if len(classes) > 1:
            names = ", ".join([cls.__name__ for cls in classes])
            raise(AttributeError("Module %s contains multiple %s (%s)." %
                (module.__name__, desc, names)))

        else: # len < 1
            raise(AttributeError("Module %s contains no %s." %
                (module.__name__, desc)))


    def _find_handlers(self, module):
        """Returns a list of handlers (subclasses of app.handlers.HandlerBase)
           defined in the "handlers" directory of *module*. Each Python file
           (*.py) is expected to contain a single new-style class, which can
           be named arbitrarily. (but probably shouldn't.)

           Returns an empty list if no handlers are defined, or the directory
           can't be opened. All exceptions raised while importing handlers are
           allowed to propagate."""

        files = self._find_python_files(
            os.path.join(module.__path__[0], "handlers"))

        module_names = [
            "%s.handlers.%s" % (module.__name__, file)
            for file in files]

        modules = [
            self._try_import(mod_name)
            for mod_name in module_names]

        return [
            self._get_class(mod, BaseHandler)
            for mod in filter(None, modules)]


    def __init__(self):
        self.handlers = []


    def start(self):
        """Spiders all RapidSMS apps, and registers all available handlers."""

        for conf in settings.RAPIDSMS_APPS.values():
            module = self._try_import(conf["module"])
            handlers = self._find_handlers(module)
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
