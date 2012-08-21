#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import mptt

from rapidsms.contrib.locations.models import Location

# This registers the Location model with the mptt library
# (`pip install django-mptt`), adding all the necessary internals for using
# nested sets, and registering the `tree_parent` field as the parent used
# within the nested set tree
mptt.register(Location, parent_attr='tree_parent')
