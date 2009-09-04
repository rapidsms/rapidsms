#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from i18n.models import *

admin.site.register(Language)
admin.site.register(Translation)
