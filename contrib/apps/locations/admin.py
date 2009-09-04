#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from locations.models import *


admin.site.register(LocationType)
admin.site.register(Location)
