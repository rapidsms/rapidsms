#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.logger.views as views

urlpatterns = patterns('',
    url(r'^logger/?$',  views.index),
    url(r'^logger/csv/in?$',     views.csv_in),
    url(r'^logger/csv/out?$',     views.csv_out),
)
