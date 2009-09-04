#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from training.models import *

admin.site.register(MessageInWaiting)
admin.site.register(ResponseInWaiting)
admin.site.register(Template)
