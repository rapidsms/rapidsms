#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.reporters.models import *

class LocationInline(admin.TabularInline):
    model = Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ['name','type','code','latitude','longitude','parent']
    list_filter = ['type',]
    search_fields = ['name','code']
    inlines = [LocationInline,]

class ReporterAdmin(admin.ModelAdmin):
    list_display = ['alias', 'first_name', 'last_name', 'location','role']
    search_fields = ['alias','first_name','last_name','groups'] 

class RoleAdmin(admin.ModelAdmin):
    list_display = ['name','code']

class PersistantConnectionAdmin(admin.ModelAdmin):
    list_display = ['backend', 'identity', 'reporter', 'last_seen']
    date_hierarchy = 'last_seen'

admin.site.register(Role, RoleAdmin)
admin.site.register(LocationType)
admin.site.register(Location, LocationAdmin)
admin.site.register(Reporter, ReporterAdmin)
admin.site.register(ReporterGroup)
admin.site.register(PersistantBackend)
admin.site.register(PersistantConnection, PersistantConnectionAdmin)
