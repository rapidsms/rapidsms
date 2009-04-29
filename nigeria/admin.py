#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.nigeria.models import *

class NetDistributionAdmin(admin.ModelAdmin):
    list_display = ['location', 'distributed', 'expected', 'actual', 'discrepancy',\
        'reporter', 'time']
    list_filter = ['reporter']
    date_hierarchy = 'time'


class CardDistributionAdmin(admin.ModelAdmin):
    list_display = ['location', 'settlements', 'people', 'distributed', 'reporter',\
        'time']
    list_filter = ['reporter']
    date_hierarchy = 'time'


admin.site.register(NetDistribution, NetDistributionAdmin)
admin.site.register(CardDistribution, CardDistributionAdmin)
