#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import template
register = template.Library()

from apps.webui.app import App as webui_app
from rapidsms.webui.settings import RAPIDSMS_APPS as app_conf

@register.tag(name="ifhasperm")
def do_perm_check(parser, token):
    # save everything between the beginning and ending tags
    nodelist = parser.parse(('endifhasperm',))
    # according to django documentation:
    # "After parser.parse() is called, the parser hasn't yet "consumed" the 
    # {% endifhasperm %} tag, so the code needs to explicitly call 
    # parser.delete_first_token()." Hmm
    parser.delete_first_token()

    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user, app_name, perm_string = token.split_contents()
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    if not (perm_string[0] == perm_string[-1] and perm_string[0] in ('"', "'")):
        # make sure our perm_string is in quotes
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return PermCheck(user, app_name, perm_string[1:-1], nodelist)

class PermCheck(template.Node):
    def __init__(self, user, app_name, perm_string, nodelist):
        # tell django that app and user are variables
        self.app_name = template.Variable(app_name)
        self.user = template.Variable(user)
        # keep these around
        self.perm_string = perm_string
        self.nodelist = nodelist

    def render(self, context):
        try:
            # get the values of app and user variables
            app = self.app_name.resolve(context)
            user = self.user.resolve(context)
            # construct the permission we will check for
            permission = app['type'] + '.' + self.perm_string
            # return an empty string unless there is content to display. 
            # otherwise 'None' will show up rather than a tab or nothing
            display = ''
            if user.has_perm(permission): 
                # return the stuff between the tags
                display = self.nodelist.render(context)
            elif user.is_anonymous():
                # for anonymous users, check against anon_perms
                # defined in the webui section of rapidsms.ini 
                print app_conf['webui']
                if app_conf['webui']:
                    if permission in app_conf['webui']['anon_perms']:
                        display =  self.nodelist.render(context)
            return display

        except template.VariableDoesNotExist:
            return ''

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
        tag_name, user, position = token.contents.split(None, 2)
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return DashboardElement(position[1:-1], user)

class DashboardElement(template.Node):
    def __init__(self, position, user):
        self.position = position 
        self.tag = None
        self.user = template.Variable(user)

        possible_tags = []
        for app in app_conf.values():
            module = app["module"] + '.templatetags.' + app["type"]
            try:
                lib = template.get_library(module)
                for key in lib.tags.keys():
                    if key.startswith(self.position):
                        possible_tags.append(key)
            except Exception, e:
                # don't worry about apps that don't have templatetags
                continue

        # see what tags are registered in this position
        self.register = template.get_library("apps.webui.templatetags.webui")
        self.tags = []
        for tag in possible_tags:
            if self.register.tags.has_key(tag):
                self.tags.append(tag)

    def render(self, context):
        user = self.user.resolve(context)
        rendered = ''
        try:
            for tag in self.tags:
                try:
                    position, perm = tag.split('-')
                except Exception, e:
                    perm = None
                if perm is not None:
                    if user.has_perm(perm):
                        rendered = rendered + self.register.tags[tag]
                    else:
                        rendered = rendered + "You are not allowed!!"
            return rendered
        except Exception, e:
            print(e)
            return rendered 
