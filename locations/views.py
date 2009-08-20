#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import require_GET, require_http_methods
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from rapidsms.webui.utils import render_to_response, paginated
from apps.reporters.utils import insert_via_querydict, update_via_querydict
from apps.locations.models import *


def __global(req):
    return {
        "location_types": LocationType.objects.all() }


def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })


@require_GET
def dashboard(req):
    return render_to_response(req,
        "locations/dashboard.html", {
            "all_locations": Location.objects.all() })


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
            "locations": paginated(req, all_locations, prefix="loc"),
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
