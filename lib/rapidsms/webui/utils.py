#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from rapidsms.config import Config
from django.template import loader
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response as django_r_to_r

def render_to_response(template_name, dictionary=None, **kwargs):
    """Proxies calls to django.shortcuts.render_to_response, to avoid having
       to include the global variables in every request. This is a giant hack,
       and there's probably a much better solution."""
    
    conf = Config(os.environ["RAPIDSMS_INI"])
    rs_dict = {"apps": conf["rapidsms"]["apps"] }
    
    # allow the dict argument to
    # be omitted without blowing up
    if dictionary is not None:
        rs_dict.update(dictionary)
    
    # pass on the combined dicts to the original function
    return django_r_to_r(template_name, rs_dict, **kwargs)
