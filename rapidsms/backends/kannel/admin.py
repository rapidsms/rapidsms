from django.contrib import admin
from rapidsms.backends.kannel.models import DeliveryReport


class DeliveryReportAdmin(admin.ModelAdmin):
    search_fields = ('text', 'sms_id', 'smsc')
    list_display = ('id', 'message_id', 'date', 'identity', 'status',
                    'status_text', 'smsc', 'date_sent')
    list_filter = ('smsc', 'status')
    ordering = ('-date',)


admin.site.register(DeliveryReport, DeliveryReportAdmin)
