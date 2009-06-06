#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from models import OutgoingMessage, IncomingMessage


class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display = ['identity', 'backend', 'text', 'sent']
    list_filter = ['identity', 'backend', 'text', 'sent']
    date_hierarchy = 'sent'

class IncomingMessageAdmin(admin.ModelAdmin):
    list_display = ['identity', 'backend', 'text', 'received']
    list_filter = ['identity', 'backend', 'text', 'received']
    date_hierarchy = 'received'


admin.site.register(OutgoingMessage, OutgoingMessageAdmin)
admin.site.register(IncomingMessage, IncomingMessageAdmin)
