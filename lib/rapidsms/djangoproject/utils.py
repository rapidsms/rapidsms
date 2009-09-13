#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, re, traceback
from rapidsms.djangoproject import settings
from rapidsms.utils.modules import try_import, get_module_path
from django.template import RequestContext
from django.shortcuts import render_to_response as django_r_to_r
from django.core.paginator import Paginator, EmptyPage, InvalidPage


def render_to_response(req, template_name, dictionary=None, **kwargs):
    """Proxies calls to django.shortcuts.render_to_response, to avoid having
       to include the global variables in every request. This is a giant hack,
       and there's probably a much better solution."""
    
    rs_dict = {
        "apps":  settings.RAPIDSMS_APPS.values(),
        "debug": settings.DEBUG,
        "javascripts": []
    }
    
    def __js_dir(fs_path, web_prefix):
        """Adds all of the .js files in a given directory to the javascripts array,
           to be included in the <head>. Also checks for a single file js with the
           same name as the directory. (dir_name/*.js and dir_name.js)"""
        
        if os.path.exists(fs_path):
            rs_dict["javascripts"].extend([
                "%s/%s" % (web_prefix, fn)
                for fn in os.listdir(fs_path)
                if fn[-3:] == ".js"])
        
        if os.path.exists("%s.js" % (fs_path)):
            rs_dict["javascripts"].append(
                "%s.js" % (web_prefix))
    
    # add all of the global javascript files for all running
    # apps. this is super handy for packaging functionality
    # which affects the whole webui without hard-coding it
    for module_name in settings.RAPIDSMS_APPS.keys():
        __js_dir(
            "%s/static/javascripts/global" % module_name,
            "/static/%s/javascripts/global" % get_module_path(module_name))
    
    # A NEW KIND OF LUNACY: inspect the stack to find out
    # which rapidsms app this function is being called from
    # --
    # TODO: we're assuming that this function was called
    # directly from the view, and looking for it at -2 in
    # the stack. this could be wrong, if something else is
    # further abstracting the call (which sounds fun).
    tb = traceback.extract_stack(limit=2)
    m = re.match(r'^.+/(.+?)/views\.py$', tb[-2][0])
    if m is not None:
        app_name = m.group(1)
        path = get_module_path(app_name)

        # since we're fetching the app conf, add it to the
        # template dict. it wouldn't be a very good idea to
        # use it, but sometimes, when time is short...
        rs_dict["app_conf"] = settings.RAPIDSMS_APPS[app_name]
        
        # note which app this func was called from, so the tmpl
        # can mark the tab (or some other type of nav) as active
        rs_dict["active_app"] = app_name
        
        # also note which "view" (function) this func was called
        # from, for a little introspection later in the rendering
        # process (the view name is added to the css class
        # of <body> to make per-view styling free)
        rs_dict["active_view"] = tb[-2][2]
        
        # find all of the javascript assets for
        # this app, and add them to the <head>
        __js_dir(
            "%s/static/javascripts/app" % path,
            "/static/%s/javascripts/app" % path)
        
        # check for a view-specific javascript,
        # to add LAST, after the dependencies
        __js_dir(
            "%s/static/javascripts/page/%s" % (path, rs_dict["active_view"]),
            "/static/%s/javascripts/page/%s.js" % (app_name, rs_dict["active_view"]))
        
        # attempt to import the "__global" function from
        # the views.py that this method was called from
        module = try_import("%s.views" % app_name)

        # if the views have a __global function, call it with the
        # request object, and add the output (a dictionary) to the
        # rs_dict. note that the 'dictionary' argument to _this_
        # method is merged AFTER this, overriding the global data.
        # also note that we do this here, rather than in the try
        # block above, to avoid masking exceptions raised within
        if module and hasattr(module, "__global"):
            global_data = module.__global(req)
            rs_dict.update(global_data)
    
    # allow the dict argument to
    # be omitted without blowing up
    if dictionary is not None:
        rs_dict.update(dictionary)
    
    # unless a context instance has been provided,
    # default to RequestContext, to get all of
    # the TEMPLATE_CONTEXT_PROCESSORS working
    if "context_instance" not in kwargs:
        kwargs["context_instance"] = RequestContext(req)
    
    # pass on the combined dicts to the original function
    return django_r_to_r(template_name, rs_dict, **kwargs)


def paginated(req, query_set, per_page=20, prefix="", wrapper=None):
    
    # since the behavior of this function depends on
    # the GET parameters, if there is more than one
    # paginated set per view, we'll need to prefix
    # the parameters to differentiate them
    prefix = ("%s-" % (prefix)) if prefix else ""
    
    # the per_page argument to this function provides
    # a default, but can be overridden per-request. no
    # interface for this yet, so it's... an easter egg?
    if (prefix + "per-page") in req.GET:
        try:
            per_page = int(req.GET[prefix+"per-page"])
        
        # if it was provided, it must be valid. we don't
        # want links containing extra useless junk like
        # invalid GET parameters floating around
        except ValueError:
            raise ValueError("Invalid per-page parameter: %r" %
                (req.GET[prefix + "per-page"]))
        
    try:
        page = int(req.GET.get(prefix+"page", "1"))
        paginator = Paginator(query_set, per_page)
        objects = paginator.page(page)
    
    # have no mercy if the page parameter is not valid. there
    # should be no links to an invalid page, so coercing it to
    # assume "page=xyz" means "page=1" would just mask bugs
    except (ValueError, EmptyPage, InvalidPage):
        raise ValueError("Invalid Page: %r" %
            (req.GET[prefix + "page"]))
    
    # if a wrapper function was provided, call it for each
    # object on the page, and replace the list with the result
    if wrapper is not None:
        objects.raw_object_list = objects.object_list
        objects.object_list = map(wrapper, objects.object_list)
    
    # attach the prefix (if provided; might be blank) to the
    # objects, where it can be found by the {% paginator %} tag
    objects.prefix = prefix
    
    return objects


def self_link(req, **kwargs):
    new_kwargs = req.GET.copy()
    
    # build a new querydict using the GET params from the
    # current request, with those passed to this function
    # overridden. we can't use QueryDict.update here, since
    # it APPENDS, rather than REPLACING keys. i hate CGI :|
    for k, v in kwargs.items():
        new_kwargs[k] = v
    
    # return the same path that we're currently
    # viewing, with the updated query string
    kwargs_enc = new_kwargs.urlencode()
    return "%s?%s" % (req.path, kwargs_enc)

