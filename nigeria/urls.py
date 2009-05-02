#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.nigeria.views as views

urlpatterns = patterns('',
    url(r'^locgen/?$', views.generate),
    url(r'^reports/?$', views.index),
    url(r'^reports/summary/(?P<locid>\d*)/?$', views.index),
    url(r'^reports/logistics/summary/(?P<locid>\d*)/?$', views.logistics_summary),
    url(r'^reports/bednets/summary/(?P<range>.*)/?(?P<from>.*)/?(?P<to>.*)/?$', views.bednets_summary),
    url(r'^reports/coupons/summary/(?P<locid>.*)/?$', views.coupons_summary),
    url(r'^reports/supply/summary/(?P<range>.*)/?(?P<from>.*)/?(?P<to>.*)/?$', views.supply_summary),
    url(r'^reports/bednets/daily/(?P<locid>\d*)/?$', views.bednets_daily),
    url(r'^reports/bednets/weekly/(?P<locid>\d*)/?$', views.bednets_weekly),
    url(r'^reports/bednet/monthly/(?P<locid>\d*)/?$', views.bednets_monthly),
    url(r'^reports/coupons/daily/(?P<locid>\d*)/?$', views.coupons_daily),
    url(r'^reports/coupons/weekly/(?P<locid>\d*)/?$', views.coupons_weekly),
    url(r'^reports/coupons/monthly/(?P<locid>\d*)/?$', views.coupons_monthly),
    url(r'^reports/supply/daily/(?P<locid>\d*)/?$', views.supply_daily),
    url(r'^reports/supply/weekly/(?P<locid>\d*)/?$', views.supply_weekly),
    url(r'^reports/supply/monthly/(?P<locid>\d*)/?$', views.supply_monthly),
    url(r'^reports/test/?$', views.index),
    (r'^static/nigeria/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"}),
)
