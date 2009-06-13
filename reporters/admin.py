#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from apps.reporters.models import *

class ReporterAdmin(admin.ModelAdmin):
    list_display = ('identity','last_name')

admin.site.register(Role)
admin.site.register(Reporter, ReporterAdmin)
admin.site.register(ReporterGroup)
admin.site.register(PersistantBackend)
admin.site.register(PersistantConnection)
