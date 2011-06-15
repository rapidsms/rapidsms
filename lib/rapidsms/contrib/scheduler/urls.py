#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
from django.conf.urls.defaults import *
import rapidsms.contrib.scheduler.views as views

urlpatterns = patterns('',
    url(r'^$', views.index, name="scheduler"),
    url(r'^(?P<pk>\d+)/$', views.edit),
    url(r'^(?P<schedule_pk>\d+)/test/?$', views.test_schedule, name='test_schedule'),
)
