#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
import apps.locations.views as views


urlpatterns = patterns('',
    
    # mini dashboard for this app
    url(r'^locations$',
        views.dashboard,
        name="locations-home"),

    # view all locations of a location_type
    url(r'^location-types/(?P<location_type_pk>\d+)$',
        views.location_type,
        name="view-location-type"),

    # to view all of the data linked to a location,
    # which may have come from _any_ rapidsms app
    url(r'^location-types/(?P<location_type_pk>\d+)/locations/(?P<location_pk>\d+)$',
        views.location,
        name="view-location"),
)
