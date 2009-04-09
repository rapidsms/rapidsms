#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.supply.models import *

admin.site.register(Reporter)
admin.site.register(Role)
admin.site.register(Report)
admin.site.register(Token)
admin.site.register(Supply)
admin.site.register(LocationType)
admin.site.register(Location)
admin.site.register(Stock)
admin.site.register(Shipment)
admin.site.register(Transaction)
admin.site.register(Notification)
admin.site.register(TokenValidator)
admin.site.register(TokenExistanceValidator)
