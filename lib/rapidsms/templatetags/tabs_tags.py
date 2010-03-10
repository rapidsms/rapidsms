#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import types
import threading
from functools import wraps
from django import template
from django.core.urlresolvers import get_resolver, reverse

register = template.Library()


# rather than messing around with middleware or context preprocessors
# for the sake of two values, we'll can store them as thread locals.
data = threading.local()
data._view = None
data._tabs = []


class Tab(object):
    def __init__(self, callback, caption=None):
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

    @property
    def is_active(self):
        return self._looks_like(self.view, data._view)


def register_tab(*args, **kwargs):
    """
    Decorate a view as a tab, which should be displayed globally in the
    WebUI via the {%% get_tabs %%} tag. Any keyword arguments are passed
    along to the `Tab` constructor.

    Example::

        @register_tab
        def dashboard(request):
            ...

        @register_tab(caption="Show all users")
        def users(request):
            ...

    WARNING: This only works when other decorators are well-behaved, and
    don't alter the signature (the __module__ and __name__ attributes)
    of their function. (This makes it very difficult to reverse the
    function.) Most Django decorators seem to work fine, but those
    bundled with contrib.auth do not. To work around this, attach the
    misbehaving decorators **before** @register_tab.
    """

    def decorator(func):
        def inner(*args, **kwargs):
            data._view = func
            response = func(*args, **kwargs)
            data._view = None
            return response

        data._tabs.append(
            Tab(func, **kwargs))

        return wraps(func)(inner)

    # here be dragons:
    # (or pythons, whatever.)
    #
    # i figured that `@decorate` was syntactic sugar for `@decorate()`.
    # but it's not. if this decorator was used without arguments, we
    # must return the decorated function. for example::
    #
    #   @register_tab
    #   def my_view(request):
    #      pass
    #
    if (len(kwargs) == 0) and (len(args) == 1) and\
    isinstance(args[0], types.FunctionType):
        return decorator(args[0])

    # otherwise, we must return a nested decorator, to pass along the
    # arguments. this python syntax is kind of funky, but consistent.
    # for example::
    #
    #  @register_tab(caption="My Lovely View")
    #  def my_view(request):
    #      pass
    #
    return decorator


# adapted from ubernostrum's django-template-utils. it didn't seem
# substantial enough to add a dependency, so i've just pasted it.
class ContextUpdatingNode(template.Node):
    def __init__(self, **kwargs):
        self.context = kwargs

    def render(self, context):
        context.update(self.context)
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

    kwargs = { str(args[1]): data._tabs }
    return ContextUpdatingNode(**kwargs)
