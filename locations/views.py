#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import *
from django.shortcuts import get_object_or_404
from rapidsms.webui.utils import render_to_response, paginated
from apps.locations.models import *


def __global(req):
    return {
        "location_types": LocationType.objects.all() }


@require_GET
def dashboard(req):
    return render_to_response(req,
        "locations/dashboard.html")


@require_GET
def location_type(req, location_type_pk):
    loc_type = get_object_or_404(
        LocationType, pk=location_type_pk)

    return render_to_response(req,
        "locations/location-type.html", {
            "active_location_type_tab": loc_type.pk,
            "locations": paginated(req, loc_type.locations.all(), prefix="loc"),
            "location_type": loc_type })


@require_GET
def location(req, location_type_pk, location_pk):
    loc_type = get_object_or_404(LocationType, pk=location_type_pk)
    location = get_object_or_404(Location, pk=location_pk)
    siblings = Location.objects.filter(type=loc_type)

    # is the map visible?
    # default to 0 (hidden)
    show_map = int(req.GET.get("map", 0))

    return render_to_response(req,
        "locations/location.html", {
            "active_location_type_tab": loc_type.pk,
            "sibling_locations": siblings,
            "location_type": loc_type,
            "location": location,
            "show_map": show_map })
