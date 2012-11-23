#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from rapidsms.contrib.httptester import views


urlpatterns = patterns('',
    url(r"^$", views.generate_identity, name='httptester-new'),
    url(r"^(?P<identity>\d+)/$", views.message_tester, name='httptester')
)
