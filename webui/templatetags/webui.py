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
                #print app_conf['webui']
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
        dashboard template. AND the dashboard can magically change based on the
        permissions of the user!

        In an app's templatetags file, import the dashboard utility:

            from rapidsms.webui.utils import dashboard 

        Then, for templatetags we'd like to appear on the dashboard,
        add the dashboard decorator, passing it (1) the position on the dashboard
        where the templatetag should appear, (2) the template file, and
        (3) permission the user needs to see the element: 

            @register.inclusion_tag("myapp/partials/mytag.html")
            @dashboard("my_position", "myapp/partials/mytag.html", "myapp.permission")
            def my_tag():
                ...
                return {"stuff" : stuff, "things", things}
                
        We can have whatever positions we want, as long as there is a 
        corresponding {% element user "my_position" %} tag on the dashboard
        (avoid hyphens in position names).

        We can also decorate a tag with several dashboard tags so it can
        appear in different positions based on different permissions.

            @register.inclusion_tag("myapp/partials/mytag.html")
            @dashboard("my_position", "myapp/partials/mytag.html", "myapp.permission")
            @dashboard("another_position", "myapp/partials/mytag.html", "myapp.another_permission")
            def my_tag():
                ...
                return {"stuff" : stuff, "things", things}

        This could get confusing if a user has both permissions, so use 
        groups and permisisons wisely.'''

    try:
        tag_name, user, position = token.contents.split(None, 2)
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return DashboardElement(position[1:-1], user)

class DashboardElement(template.Node):
    def __init__(self, position, user):
        self.position = position 
        self.user = template.Variable(user)
        self.register = template.get_library("apps.webui.templatetags.webui")
        self.possible_tags = []

        # we have to hit all apps' templatetags so our dashboard versions
        # get created. also gather all the possible tags for this position
        #
        # FIXME the first element is not shown the first time the dashboard
        # is displayed after runserver begins (because our fake tags haven't
        # been added to library yet. chicken or egg situation). A workaround
        # is putting a dummy element tag with a position that is never used
        # by a real templatetag
        for app in app_conf.values():
            module = app["module"] + '.templatetags.' + app["type"]
            try:
                lib = template.get_library(module)
                #print lib.tags.keys()
                for key in lib.tags.keys():
                    if key.startswith(self.position):
                        #print self.position + ' possibility: ' + key 
                        self.possible_tags.append(key)
            except Exception, e:
                # don't worry about apps that don't have templatetags
                continue

    def render(self, context):
        user = self.user.resolve(context)
        rendered = ''
        try:
            for tag in self.possible_tags:
                try:
                    # break apart tags ('position_name-app.perm_name')
                    position, perm = tag.split('-')
                except ValueError:
                    perm = None
                    rendered = "Oops. The dashboard decorator requires a permisison."

                if perm is not None:
                    if user.has_perm(perm):
                        rendered = self.register.tags[tag]
                    elif user.is_anonymous():
                        # lookup default permissions for anonymous users
                        if app_conf['webui']:
                            if perm in app_conf['webui']['anon_perms']:
                                rendered = self.register.tags[tag]
                    else:
                        rendered = "You do not have permission to view this information. Please login or contact webmaster."
            return rendered
        except Exception, e:
            return e
