#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from .models import *


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "full_name")


admin.site.register(Point)
admin.site.register(LocationType)
admin.site.register(Location, LocationAdmin)
