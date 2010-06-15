#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from . import views


urlpatterns = patterns('',
    url(r'^locations(?:/(?P<location_type_slug>[a-z\-]+):(?P<location_pk>\d+))?$',
        views.dashboard,
        name="locations")
)
