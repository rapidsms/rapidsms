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
    module = try_import(".".join(parts))

    form_name = model.__name__ + "Form"
    form = getattr(module, form_name)

    return form
