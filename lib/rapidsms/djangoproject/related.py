#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.utils.text import capfirst


def _related(object):
    return object._meta.get_all_related_objects()


def _verbose_name(related_object):

    # find the relationship itself (a django.db.models.fields.related.*
    # object), and check if it has a verbose_name attribute explicity set
    rel = getattr(related_object.model, related_object.field.name).field.rel
    if hasattr(rel, "verbose_name"):
        return getattr(rel, "verbose_name")

    # otherwise, we'll take a guess based on the related_name
    return capfirst(related_object.get_accessor_name())


def related_objects(model):
    return [
        (_verbose_name(rel), rel)
        for rel in _related(model)]


def with_related_objects(object):
    object.related_objects = [
        getattr(object, rel.get_accessor_name()).all()
        for rel in _related(object)]
    return object
