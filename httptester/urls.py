#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.httptester.views as views

urlpatterns = patterns('',
    url(r'^http$', views.index),
    url(r'^http/proxy/(?P<number>\d+)/(?P<message>.*)$', views.proxy),
    #url(r'^httpbasic$', views.indexbasic),
    url(r'^httpbasic$', views.index_basic),
    url(r'^httpbasic/(?P<number>\d+)$', views.basic_ui, name='basic_ui'),
    
    
    # serve the static files for this HTTP app
    # TODO: this should be automatic, via WEBUI
    (r'^static/http/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"})
)
