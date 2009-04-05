#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.webui.views as views

urlpatterns = patterns('',
    
    url(r'^$', views.dashboard),
    
    (r'^static/webui/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"})
)

