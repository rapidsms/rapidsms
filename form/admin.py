#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from form.models import *

class DomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class FormEntryAdmin(admin.ModelAdmin):
    list_display = ['domain', 'reporter', 'form', 'date']
    list_filter = ['reporter', 'form', 'domain']
    date_hierarchy = 'date'


class TokenEntryAdmin(admin.ModelAdmin):
    list_display = ['form_entry', 'token', 'data']
    list_filter = ['token']


class TokenExistanceValidatorAdmin(admin.ModelAdmin):
    list_display = ['token', 'lookup_type', 'field_name']


class TokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']


admin.site.register(Form)
admin.site.register(Token, TokenAdmin)
admin.site.register(FormToken)
admin.site.register(DomainForm)
admin.site.register(Domain, DomainAdmin)
admin.site.register(FormEntry, FormEntryAdmin)
admin.site.register(TokenEntry, TokenEntryAdmin)
admin.site.register(TokenValidator)
admin.site.register(TokenExistanceValidator, TokenExistanceValidatorAdmin)
admin.site.register(RegexAlerter)
admin.site.register(App)
