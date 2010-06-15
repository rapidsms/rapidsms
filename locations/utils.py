#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db.models import loading
from django.contrib.contenttypes.models import ContentType
from .models import LocationTypeStub, Location


def get_location_types():
    return [
        LocationTypeStub(cls)
        for cls in loading.get_models()
        if issubclass(cls, Location) and\
            (cls is not Location)]


def get_locations(parent=None):
    if parent is not None:
        kwargs = {
            "parent_type": ContentType.objects.get_for_model(parent),
            "parent_id": parent.pk }

    else:
        kwargs = {
            "parent_type": None,
            "parent_id": None }

    return [
        (type, type.model.objects.filter(**kwargs))
        for type in get_location_types()]
