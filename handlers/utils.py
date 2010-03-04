#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils.modules import find_python_files, get_class, try_import
from .handlers.base import BaseHandler


def find_handlers(module_name):
    """
    Returns a list of handlers (subclasses of app.handlers.HandlerBase)
    defined in the "handlers" directory of 'module_name'. Each Python
    file (*.py) is expected to contain a single new-style class, which
    can be named arbitrarily. (But probably shouldn't be.)

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
