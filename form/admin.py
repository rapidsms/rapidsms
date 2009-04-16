#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.form.models import *

admin.site.register(Reporter)
admin.site.register(Form)
admin.site.register(Token)
admin.site.register(Domain)
admin.site.register(FormEntry)
admin.site.register(TokenEntry)
admin.site.register(TokenValidator)
admin.site.register(TokenExistanceValidator)
admin.site.register(RegexAlerter)
admin.site.register(App)
