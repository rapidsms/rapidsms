#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import export.views as views

urlpatterns = patterns('',
    url(r'^export/database', views.database),
    url(r'^export/str$', views.str_to_excel),
    url(r'^export/(?P<app_label>.+?)/(?P<model_name>.+?)$', views.model_to_excel),
)
