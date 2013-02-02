from django.contrib import admin
from rapidsms.router.db.models import Message, Transmission


class MessageAdmin(admin.ModelAdmin):
    pass


class TransmissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(Transmission, TransmissionAdmin)
