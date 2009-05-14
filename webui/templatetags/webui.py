#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import template
register = template.Library()

@register.tag(name="ifhasperm")
def do_perm_check(parser, token):
    nodelist = parser.parse(('endifhasperm',))
    parser.delete_first_token()

    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user, app_name, perm_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    if not (perm_string[0] == perm_string[-1] and perm_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return PermCheck(user, app_name, perm_string[1:-1], nodelist)

class PermCheck(template.Node):
    def __init__(self, user, app_name, perm_string, nodelist):
        self.app_name = template.Variable(app_name)
        self.user = template.Variable(user)
        self.perm_string = perm_string
        self.nodelist = nodelist

    def render(self, context):
        try:
            app = self.app_name.resolve(context)
            user = self.user.resolve(context)
            permission = app['type'] + '.' + self.perm_string
            if user.has_perm(permission): 
                return self.nodelist.render(context)
            else:
                return ''

        except template.VariableDoesNotExist:
            return ''
