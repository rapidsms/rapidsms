#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils.modules import try_import
from .forms import LocationForm
from .models import Location


def get_model(name):
    """
    """

    for type in Location.subclasses():
        if type._meta.module_name == name:
            return type

    raise StandardError("There is no Location subclass named '%s'" % name)


def form_for_model(model):
    """
    Return the Form which should be used to add/edit ``model`` in the
    WebUI, by importing the class named ``"%sForm" % model.__name__``
    from the sibling ``forms`` module. For example::

        app1.models.Alpha     -> myapp.forms.SchoolForm
        app2.models.beta.Beta -> app2.forms.beta.BetaForm

    If no such form is defined, an appropriately-patched copy of the
    rapidsms.contrib.locations.forms.LocationForm form is returned.
    """

    parts = model.__module__.split(".")
    parts[parts.index("models")] = "forms"

    module_name = ".".join(parts)
    form_name = model.__name__ + "Form"

    module = try_import(module_name)
    if module is not None:

        form = getattr(module, form_name, None)
        if form is not None:
            return form

    meta_dict = LocationForm.Meta.__dict__
    meta_dict["model"] = model

    return type(
        form_name,
        (LocationForm,), {
            "Meta": type("Meta", (), meta_dict)
        }
    )
