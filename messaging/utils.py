#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import django


def messagable_models():
    """Returns an array of every messagable model in the current project. Models
       contained by apps which are present but not running are ignored. To make
       a model messagable, add a "__message__" method which accepts a router."""

    return filter(
        lambda o: getattr(o, "__message__", False),
        django.db.models.loading.get_models())
