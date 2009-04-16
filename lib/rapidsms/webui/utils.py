#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from rapidsms.config import Config
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
        "debug": conf("django", "debug")
    }
    
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


def conf(section, key):
    """Returns a value from the RapidSMS configuration file, as found in the
       RAPIDSMS_INI environment variable. This introduces mild coupling between
       the webui and backend, for the sake of convenience."""
    
    var = "RAPIDSMS_INI"
    if not var in os.environ:
        # "rapidsms.webui.utils.conf should only
        # be called from within a running django
        # server, where env[RAPIDSMS_INI] is defined"
        raise KeyError(var)
    
    try:
        return Config(os.environ[var])[section][key]
    
    # if the section or key (or both) were invalid,
    # just return none. as far as we're concerned,
    # absence is the same as False or None here
    except KeyError:
        return None
