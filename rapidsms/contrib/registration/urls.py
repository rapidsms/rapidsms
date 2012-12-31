#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from . import views


urlpatterns = patterns('',
   url(r'^$', views.registration, name="registration"),
   url(r'^(?P<pk>\d+)/edit/$', views.registration, name="registration_edit"),
)
