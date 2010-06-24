#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils.modules import try_import
from .models import Location


def get_model(name):
    """
    """

    for type in Location.subclasses():
        if type._meta.module_name == name:
            return type

    raise StandardError("There is no Location subclass named '%s'"  % name)


def form_for_model(model):
    """
    """

    parts = model.__module__.split(".")
    parts[parts.index("models")] = "forms"
    module_name = ".".join(parts)
    module = try_import(module_name)
    
    if module is None:
        raise StandardError(
            "No such module as '%s'." %
            module_name)

    form_name = model.__name__ + "Form"
    form = getattr(module, form_name, None)

    if form is None:
        raise StandardError(
            "No such form as '%s' in '%s'." %
            (form_name, module_name))

    return form
