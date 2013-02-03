from django.contrib import admin
from rapidsms.router.db.models import Message, Transmission


class MessageAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_display = ('id', 'date', 'direction', 'text', 'status', 'updated',
                    'sent', 'delivered')
    list_filter = ('direction', 'status',)
    ordering = ('-updated',)


class TransmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'status', 'connection', 'updated', 'sent',
                    'delivered')
    ordering = ('-updated',)
    list_filter = ('status',)
    raw_id_fields = ('message', 'connection',)


admin.site.register(Message, MessageAdmin)
admin.site.register(Transmission, TransmissionAdmin)
