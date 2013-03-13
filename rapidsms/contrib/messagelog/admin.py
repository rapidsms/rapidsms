#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from .models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ("text", "direction", "who", "date")
    list_filter = ("direction", "date")


admin.site.register(Message, MessageAdmin)
