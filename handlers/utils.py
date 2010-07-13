#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.conf import settings
from rapidsms.utils.modules import find_python_files, get_class, try_import
from .handlers.base import BaseHandler


def get_handlers():
    """
    Return a list of ALL handlers defined in the current project. (Named
    after the django.db.models.loading.get_models function.)
    """

    handlers = []

    for module_name in _apps():
        handlers.extend(_handlers(module_name))

    return handlers


def _apps():
    """
    Return a list of the apps which may contain handlers. This is not
    quite as simple as returning settings.INSTALLED_APPS, since:

    1. This app (rapidsms.contrib.handlers) should be excluded, because
       although it contains handlers, they are intended to be abstract,
       not instantiated directly. (I think this is cleaner than marking
       them explicitly.)

    2. Django contrib apps should be excluded, because the "auth" app
       has an unrelated "handlers" module. (If I'd noticed that when I
       created this app, I may have named it differently. Sorry.)
    """

    return [
        module_name
        for module_name in settings.INSTALLED_APPS
        if module_name != "rapidsms.contrib.handlers"\
           and not module_name.startswith("django.contrib.")]


def _handlers(module_name):
    """
    Return a list of handlers (subclasses of app.handlers.HandlerBase)
    defined in the "handlers" directory of 'module_name'. Each Python
    file (*.py) is expected to contain a single new-style class, which
    can be named arbitrarily. (But probably shouldn't be.)

    Return an empty list if no handlers are defined, or the directory
    can't be opened. All exceptions raised while importing handlers are
    allowed to propagate, to avoid masking errors.
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
