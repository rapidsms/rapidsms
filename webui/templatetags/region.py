#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from rapidsms.djangoproject import settings
from rapidsms.utils.modules import try_import

from django import template
register = template.Library()


@register.inclusion_tag("webui/partials/region.html", takes_context=True)
def region(context, name):
    def __path(module_name):
        module = try_import(module_name)
        return "%s/templates/regions/%s.html" %\
            (module.__path__[0], name)

    # start with the current context, which is passed on
    # to all of the included templates by {% include %},
    # and override just the bits that we need
    context.update({
        "name": name,
        "request": context["request"],
        "includes": [
            __path(module_name)
             for module_name in settings.RAPIDSMS_APPS.keys()
             if os.path.exists(__path(module_name)) ]})
    
    return context
