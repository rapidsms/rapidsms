#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from rapidsms.utils import render_to_response, web_message
from rapidsms.conf import settings
from .forms import *
from .models import *
from .tables import *


def _breadcrumbs(location=None, first_caption="Planet Earth"):
    """
    Return the breadcrumb trail leading to ``location``. To avoid the
    trail being empty when browsing the entire world, the caption of the
    first crumb is hard coded.
    """

    breadcrumbs = [(first_caption, reverse(dashboard))]

    if location is not None:
        for loc in location.path:
            url = reverse(dashboard, args=(loc.pk,))
            breadcrumbs.append((loc.name, url))

    return breadcrumbs


def _type(location_type, request):
    """
    Return a tuple of ``location_type`` and a LocationTable populated
    with any Location objects of the type. Pass along ``request``, so
    the table can build its own URLs (for sorting, pagination, etc).
    """

    return (
        location_type,
        LocationTable(
            Location.objects.filter(type=location_type),
            prefix=location_type.slug + "-",
            request=request
        )
    )


@require_GET
def dashboard(req, location_pk=None):

    if location_pk is not None:
        location = get_object_or_404(Location, pk=location_pk)
        location_form = LocationForm(instance=location)

    else:
        location = None
        location_form = None

    location_types = LocationType.objects.filter(exists_in=location)
    all_locations = Location.objects.filter(type__in=location_types)

    return render_to_response(req,
        "locations/dashboard.html", {
            "breadcrumbs": _breadcrumbs(location),
            "all_locations": all_locations,

            # build a list of [sub-]locationtypes with their locations,
            # to avoid having to invoke the ORM from the template.
            "location_type_tables": map(lambda lt: _type(lt, req), location_types),

            # from rapidsms.contrib.locations.settings
            "default_latitude":  settings.MAP_DEFAULT_LATITUDE,
            "default_longitude": settings.MAP_DEFAULT_LONGITUDE,

            # if there are no locationtypes, then we should display a
            # big error, since this app is useless without them.
            "no_location_types": (LocationType.objects.count() == 0)
         }
     )


@require_http_methods(["GET", "POST"])
def edit_location(req, location_type_slug, location_pk):
    loc_type = get_object_or_404(LocationType, slug=location_type_slug)
    location = get_object_or_404(Location, pk=location_pk)

    if req.method == "GET":
        return render_to_response(req,
            "locations/location_form.html", {
                "active_location_type_tab": loc_type.pk,
                "location": location,

                # redirect back to this view to save (below)
                "save_url": reverse("edit_location", kwargs={
                    "location_type_slug": location_type_slug,
                    "location_pk": location_pk }),

            # is the map visible? default to 0 (hidden)
            # since the map makes everything very slow
            "show_map": int(req.GET.get("map", 0)) })

    elif req.method == "POST":
        # if DELETE was clicked... delete
        # the object, then and redirect
        if req.POST.get("delete", ""):
            pk = location.pk
            location.delete()

            return web_message(req,
                "Location %d deleted" % (pk),
                link=reverse("locations_dashboard"))

        # otherwise, just update the object
        # and display the success message
        else:
            
            location = update_via_querydict(location, req.POST)
            location.save()

            return web_message(req,
                "Location %d saved" % (location.pk),
                link=reverse("locations_dashboard"))


@require_http_methods(["GET", "POST"])
def add_location(req, location_type_slug):
    loc_type = get_object_or_404(LocationType, slug=location_type_slug)

    if req.method == "GET":
        return render_to_response(req,
            "locations/location_form.html", {
                "active_location_type_tab": loc_type.pk,

                # redirect back to this view to save (below)
                "save_url": reverse("add_location", kwargs={
                    "location_type_slug": location_type_slug}),

                # is the map visible? default to 1 (visible),
                # since i almost always want to set the location
                "show_map": int(req.GET.get("map", 1)) })

    elif req.method == "POST":
        location = insert_via_querydict(Location, req.POST, { "type": loc_type })
        location.save()
        
        return web_message(req,
            "Location %d saved" % (location.pk),
            link=reverse("locations_dashboard"))
