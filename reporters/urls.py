#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.reporters.views as views

urlpatterns = patterns('',
    url(r'^reporters$',     views.index),
    url(r'^reporters/add$', views.add_reporter),
)
