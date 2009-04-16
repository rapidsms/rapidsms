#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.reporters.views as views

urlpatterns = patterns('',
    url(r'^reporters$',             views.index),
    url(r'^reporters/add$',         views.add_reporter),
    url(r'^reporters/(?P<pk>\d+)$', views.edit_reporter),
    
    url(r'^reporters/groups/$',            views.index_groups),
    url(r'^reporters/groups/add$',         views.add_group),
    url(r'^reporters/groups/(?P<pk>\d+)$', views.edit_group),
)
