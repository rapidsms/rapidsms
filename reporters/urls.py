#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
import reporters.views as views


urlpatterns = patterns('',
    url(r'^reporters$',             views.index),
    url(r'^reporters/add$',         views.add_reporter,  name="add-reporter"),
    url(r'^reporters/(?P<pk>\d+)$', views.edit_reporter, name="view-reporter"),
    
    url(r'^groups/$',            views.index),
    url(r'^groups/add$',         views.add_group),
    url(r'^groups/(?P<pk>\d+)$', views.edit_group),
)
