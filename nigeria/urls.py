#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.nigeria.views as views

urlpatterns = patterns('',
    url(r'^reports?$', views.index),
    url(r'^reports/bednets/summary/(?P<range(?P<locid>\d*)$', views.coupons_daily),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)$', views.coupons_weekly),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)$', views.coupons_weekly),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)$', views.coupons_weekly),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)$', views.coupons_weekly),
    url(r'^reports/coupons/monthly/(?P<locid>\d*)$', views.coupons_monthly),
    url(r'^reports/kano', views.kano),
    url(r'^reports/test', views.tests),
    url(r'^reports/test2', views.raw_tests),
    url(r'^reports/treetest', views.raw_tests),
    url(r'^reports/ajax', views.ajax),
    (r'^static/nigeria/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"}),
)
