#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.nigeria.views as views

urlpatterns = patterns('',
    url(r'^reports/coupons/daily/(?P<locid>\d*)$', views.coupons_daily),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)$', views.coupons_weekly),
)
