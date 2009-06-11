#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
#from rapidsms.webui.utils import dashboard

from rapidsms.webui import settings

from django import template
register = template.Library()


@register.tag(name="element")
def get_dashboard_element(parser, token):
    try:
        tag_name, position = token.contents.split(None, 1)
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return DashboardElement(position[1:-1], parser, token)

class DashboardElement(template.Node):
    def __init__(self, position, parser, token):
        self.position = position 
        self.tag = None
        self.parser = parser
        self.token = token

        libraries = []
        for app in settings.RAPIDSMS_APPS.values():
            module = app["module"] + '.templatetags.' + app["type"]
            try:
                lib = template.get_library(module)
                libraries.append(lib)
            except Exception, e:
                continue

        for lib in libraries:
            if lib.tags.has_key(self.position):
                self.tag = lib.tags[position]

    def render(self, context):
        try:
            if self.tag is not None:
                return self.tag

            else:
                return ''

        except Exception, e: 
            print("render explosion")
            print(e)
            pass

