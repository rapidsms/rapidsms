#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^(?:(?P<location_uid>[a-z\-]+:\d+)/)?$',
        views.locations,
        name="locations")
)
