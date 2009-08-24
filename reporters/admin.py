#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from reporters.models import *


admin.site.register(Role)
admin.site.register(Reporter)
admin.site.register(ReporterGroup)
admin.site.register(PersistantBackend)
admin.site.register(PersistantConnection)
