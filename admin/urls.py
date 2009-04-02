#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
 
urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
)
