#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import require_GET, require_http_methods
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.templatetags.tabs_tags import register_tab
from django.conf import settings

from rapidsms.utils import render_to_response
from .models import *


def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })


@register_tab(caption="Map")
@require_GET
def dashboard(req, location_pk=None):

    # to avoid the breadcrumb trail being empty browsing the entire
    # world, hard-code the first item. TODO: configure via settings.
    breadcrumbs = [("Planet Earth", reverse(dashboard))]

    # if a location was given, we will display its sub-locations via its
    # sub-locationtypes.
    if location_pk is not None:
        location = get_object_or_404(Location, pk=location_pk)

        # add each ancestor to the breadcrumbs.
        for loc in location.path:
            url = reverse(dashboard, args=(loc.pk,))
            breadcrumbs.append((loc.name, url))

    # no location is fine; we're browing the entire world. the top-level
    # location types will be returned by filter(exists_in=None).
    else: location = None

    # build a list of [sub-]locationtypes with their locations, to avoid
    # having to invoke the ORM from the template (which is foul).
    locations_data = [
        (x, Location.objects.filter(type=x))
        for x in LocationType.objects.filter(exists_in=location)
    ]

    return render_to_response(req,
        "locations/dashboard.html", {
            "breadcrumbs": breadcrumbs,
            "locations_data": locations_data,
            "location": location
         }
     )


@require_GET
def view_location(req, location_code, location_type_slug):
    location = get_object_or_404(Location, slug=location_code)
    loc_type = get_object_or_404(LocationType, exists_in=location)
    locations = loc_type.location_set.all().order_by("slug")

    return render_to_response(req,
        "locations/dashboard.html", {
            "locations": locations })


@require_GET
def view_location_type(req, location_type_slug):

    # look up the location type by the slug
    # (maybe not as concise as the 
    loc_type = get_object_or_404(
        LocationType,
        slug=location_type_slug)

    # prefetch all locations in this loc_type,
    # since we're going to plot them ALL on the
    # google map whether or not they're visible
    all_locations = list(loc_type.locations.all().order_by("code"))

    return render_to_response(req,
        "locations/view_location_type.html", {
            "active_location_type_tab": loc_type.pk,
            "locations": paginated(req, all_locations, prefix="loc", wrapper=with_related_objects),
            "relations": related_objects(Location),
            "all_locations": all_locations,
            "location_type": loc_type })


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

            return message(req,
                "Location %d deleted" % (pk),
                link=reverse("locations_dashboard"))

        # otherwise, just update the object
        # and display the success message
        else:
            location = update_via_querydict(location, req.POST)
            location.save()

            return message(req,
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
        
        return message(req,
            "Location %d saved" % (location.pk),
            link=reverse("locations_dashboard"))
