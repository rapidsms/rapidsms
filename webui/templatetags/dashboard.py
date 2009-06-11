#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rapidsms.webui import settings

from django import template
register = template.Library()


@register.tag(name="element")
def get_dashboard_element(parser, token):
    ''' A templatetag for returning other templatetags! Why? So templatetags
        used in other apps can be marked for inclusion on the project dashboard
        without explicitly loading or including those templatetags in the 
        dashboard template.

        In an app's templatetags file, import the dashboard utility:

            from rapidsms.webui.utils import dashboard 

        Then, for templatetags we'd like to appear on the dashboard,
        add the dashboard decorator, passing it (1) the position on the dashboard
        where the templatetag should appear and (2) the template file: 

            @register.inclusion_tag("myapp/partials/mytag.html")
            @dashboard("my_position", "myapp/partials/mytag.html")
            def my_tag():
                ...
                return {"stuff" : stuff, "things", things}
                
        We can have whatever positions we want, as long as there is a 
        corresponding {% element "my_position" %} tag on the dashboard

    '''
    try:
        tag_name, position = token.contents.split(None, 1)
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return DashboardElement(position[1:-1])

class DashboardElement(template.Node):
    def __init__(self, position):
        self.position = position 
        self.tag = None

        # we have to hit all the templatetags files in order to create
        # the dashboard versions of the needed templatetags
        # TODO technically, this only needs to happen once -- so they are there
        # the first time the dashboard is accessed after runserver is started
        for app in settings.RAPIDSMS_APPS.values():
            module = app["module"] + '.templatetags.' + app["type"]
            try:
                lib = template.get_library(module)
            except Exception, e:
                # don't worry about apps that don't have templatetags
                continue

        # see if there is a tag registered in this position
        register = template.get_library("apps.webui.templatetags.dashboard")
        if register.tags.has_key(self.position):
            self.tag = register.tags[position]

    def render(self, context):
        try:
            if self.tag is not None:
                # our fake templatetag is already rendered, so just return
                return self.tag
            else:
                # if theres not a tag registered for this position, return
                # an empty string (otherwise None will show up)
                return ''

        except Exception, e: 
            print("render explosion!")
            print(e)
            pass

