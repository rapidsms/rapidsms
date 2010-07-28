#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import types
import threading
from functools import wraps
from django import template
from django.conf import settings
from django.core.urlresolvers import get_resolver, reverse, RegexURLPattern
from django.utils.importlib import import_module
from django.template import Variable

register = template.Library()


class Tab(object):
    def __init__(self, callback, caption=None):
        if isinstance(callback, basestring):
            module = '.'.join(callback.split('.')[:-1])
            view = callback.split('.')[-1]
            self.callback = getattr(import_module(module), view)
        else:
            self.callback = callback
        self._caption = caption
        self._view = None

    @staticmethod
    def _looks_like(a, b):
        return (a.__module__ == b.__module__) and\
               (a.__name__   == b.__name__)

    def _auto_caption(self):
        func_name = self.callback.__name__         # my_view
        return func_name.replace("_", " ").title() # My View

    @property
    def view(self):
        """
        Return the view of this tab.

        This is a little more complex than just returning the 'callback'
        attribute, since that is often wrapped (by decorators and the
        such). This iterates the project's urlpatterns, to find the
        real view function by name.
        """

        if not self._view:
            resolver = get_resolver(None)
            for pattern in resolver.url_patterns:
                if type(pattern) is RegexURLPattern:
                    if self._looks_like(self.callback, pattern.callback):
                        self._view = pattern.callback
                        break

        return self._view

    @property
    def url(self):
        """
        Return the URL of this tab.

        Warning: If this tab's view function cannot be reversed, Django
        will silently ignore the exception, and return the value of the
        TEMPLATE_STRING_IF_INVALID setting.
        """

        return reverse(self.view)

    @property
    def caption(self):
        return self._caption or self._auto_caption()


# adapted from ubernostrum's django-template-utils. it didn't seem
# substantial enough to add a dependency, so i've just pasted it.
class TabsNode(template.Node):
    def __init__(self, tabs, varname):
        self.tabs = tabs
        self.varname = varname
        
    def render(self, context):
        request = Variable("request").resolve(context)
        for tab in self.tabs:
            tab.is_active = tab.url == request.get_full_path()
        context[self.varname] = self.tabs
        return ""


@register.tag
def get_tabs(parser, token):
    """
    Retrive a list of the tabs for this project, and store them in a
    named context variable. Returns nothing, via `ContextUpdatingNode`.

    Syntax::
        {% get_tabs as [varname] %}

    Example::
        {% get_tabs as tabs %}
    """

    args = token.contents.split()
    tag_name = args.pop(0)

    if len(args) != 2:
        raise template.TemplateSyntaxError(
            "The {%% %s %%} tag requires two arguments" % (tag_name))

    if args[0] != "as":
        raise template.TemplateSyntaxError(
            'The second argument to the {%% %s %%} tag must be "as"' % (tag_name))

    tabs = [Tab(callback, caption) for callback, caption in settings.TABS]
    return TabsNode(tabs, str(args[1]))
