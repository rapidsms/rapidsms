#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, re, traceback
from rapidsms.config import conf, app_conf
from django.template import loader
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response as django_r_to_r

def render_to_response(req, template_name, dictionary=None, **kwargs):
    """Proxies calls to django.shortcuts.render_to_response, to avoid having
       to include the global variables in every request. This is a giant hack,
       and there's probably a much better solution."""
    
    rs_dict = {
        "apps":  conf("rapidsms", "apps"),
        "debug": conf("django", "debug"),
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
    for app in conf("rapidsms", "apps"):
        __js_dir(
            "%s/static/javascripts/global" % app["path"],
            "/static/%s/javascripts/global" % app["type"])
    
    # A NEW KIND OF LUNACY: inspect the stack to find out
    # which rapidsms app this function is being called from
    tb = traceback.extract_stack(limit=2)
    m = re.match(r'^.+/(.+?)/views\.py$', tb[-2][0])
    if m is not None:
        app_type = m.group(1)
        
        # since we're fetching the app conf, add it to the
        # template dict. it wouldn't be a very good idea to
        # use it, but sometimes, when time is short...
        rs_dict["app_conf"] = app_conf(app_type)
        
        # look up this app in the "apps" list that
        # we've already added, to make the tab (or
        # whatever other nav we're using) as active
        for app in rs_dict["apps"]:
            if app["type"] == app_type:
                app["active"] = True
        
        # find all of the javascript assets for
        # this app, and add them to the <head>
        __js_dir(
            "%s/static/javascripts/app" % rs_dict["app_conf"]["path"],
            "/static/%s/javascripts/app" % rs_dict["app_conf"]["type"])
        
        # check for a view-specific javascript,
        # to add LAST, after the dependencies
        view_name = tb[-2][2]
        __js_dir(
            "%s/static/javascripts/page/%s" % (rs_dict["app_conf"]["path"], view_name),
            "/static/%s/javascripts/page/%s.js" % (rs_dict["app_conf"]["type"], view_name))
    
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
