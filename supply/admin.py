#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from supply.models import *

class StockAdmin(admin.ModelAdmin):
    list_display = ['location', 'domain', 'balance']
    list_filter = ['domain', 'balance']


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['domain', 'issue', 'amount_sent', 'receipt', 'amount_received',\
        'flag']
    list_filter = ['domain', 'flag', 'amount_sent', 'amount_received']


class PartialTransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'amount', 'domain', 'reporter', 'origin', 'destination',\
        'status', 'flag']
    list_filter = ['date', 'type', 'domain', 'status', 'flag']
    date_hierarchy = 'date'


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['origin', 'sent', 'destination', 'received']
    list_filter = ['sent','received']
    date_hierarchy = 'received'


admin.site.register(Stock, StockAdmin)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Notification)
admin.site.register(PartialTransaction, PartialTransactionAdmin)
