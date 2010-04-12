#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
import sys
import inspect


def render_to_response(req, template_name, dictionary=None, **kwargs):
    """
    Wrap django.shortcuts.render_to_response, to avoid having to include
    the same stuff in every view. TODO: moar.
    """

    # delay imports until this function is called, so this module can be
    # imported before django is finished being configured
    import django.shortcuts
    import django.template

    # find the view which this function was called from
    view = _extract_callback()
    module = sys.modules[view.__module__]

    # if the module containing 'view' contains a __context__ function,
    # call it and add the output (a dict or None) to the view context
    if hasattr(module, "__context__"):
        app_dict = module.__context__(req, view)
        if app_dict is not None:
            
            # merge backwards, so the view can overwrite values from the
            # app without iterating and checking them individually
            tmp = dictionary or {}
            dictionary = app_dict
            dictionary.update(tmp)

    # unless a context instance was specified, default to RequestContext
    # to get all of the TEMPLATE_CONTEXT_PROCESSORS working. (this is a
    # really crappy part of django, which makes app reuse difficult.)
    if "context_instance" not in kwargs:
        kwargs["context_instance"] =\
            django.template.RequestContext(req)

    # pass along the combined dicts to the original function
    return django.shortcuts.render_to_response(
        template_name, dictionary, **kwargs)


def _extract_callback():
    """
    Extract and return the view function which is handling this request
    (by inspecting the stack!), or Raise Exception if called outside of
    a request.
    """

    # find the filename of the django.core.handlers.base module, which
    # calls the view (in get_response:92 (of django 1.1)). split the
    # filename, since it's always the source (.py file) the stack, but
    # module (.pyc file) in sys.modules
    handler_module = sys.modules["django.core.handlers.base"]
    root, ext = os.path.splitext(handler_module.__file__)

    # iterate the stack, searching for django.core.handlers.base. when
    # we find it, extract the 'callback' variable, which contains the
    # original view function that this request was dispatched to
    for tpl in inspect.stack(0):
        try:
            frame, filename = tpl[0:2]
            if os.path.normcase(os.path.splitext(filename)[0]) == os.path.normcase(root):
                return frame.f_locals['callback']

        # release the frame object to avoid gc cycles, as advised by:
        # http://docs.python.org/library/inspect.html#the-interpreter-stack
        finally:
            del frame

    # if we haven't returned yet, we're probably being called from
    # somewhere other than a request. this makes no sense, so explode
    raise Exception("Couldn't find django.core.handlers.base in the stack.")
