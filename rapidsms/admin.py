#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from .models import App, Backend, Connection, Contact


class ConnectionInline(admin.TabularInline):
    model = Connection
    extra = 1


class ContactAdmin(admin.ModelAdmin):
    inlines = (ConnectionInline,)


class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'backend', 'identity', 'contact')
    list_filter = ('backend',)
    search_fields = ('identity',)
    raw_id_fields = ('contact',)


admin.site.register(App)
admin.site.register(Backend)
admin.site.register(Connection, ConnectionAdmin)
admin.site.register(Contact, ContactAdmin)
