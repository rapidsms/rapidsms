#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import webapp.views as views

urlpatterns = patterns('',
    url(r'^$',     views.dashboard),
    url(r'^ping$', views.check_availability),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'webapp/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'webapp/loggedout.html'}),
)

