#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from models import *


class IncomingMessageAdmin(admin.ModelAdmin):
    list_display=("text", "who", "received")
    list_filter=("received", "reporter")


class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display=("text", "who", "sent")
    list_filter=("sent", "reporter")


admin.site.register(IncomingMessage, IncomingMessageAdmin)
admin.site.register(OutgoingMessage, OutgoingMessageAdmin)
