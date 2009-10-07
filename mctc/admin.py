from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models.general import Zone, Facility, Case, Provider, User 
from models.logs import MessageLog, EventLog, SystemErrorLog
from models.reports import ReportMalnutrition, ReportMalaria, ReportDiagnosis, Diagnosis, Observation, DiarrheaObservation, ReportDiarrhea
from django.utils.translation import ugettext_lazy as _

 
class ProviderInline (admin.TabularInline):
    """Allows editing Users in admin interface style"""
    model   = Provider
    fk_name = 'user'
    max_num = 1

class ProviderAdmin (UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    inlines     = (ProviderInline,)
    search_fields = ['first_name']
    #list_filter = ['is_active']

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
#admin.site.register(User, ProviderAdmin)

class CaseAdmin(admin.ModelAdmin):
    list_display = ("ref_id", "first_name", "last_name", "gender", "dob","zone","created_at","provider")
    search_fields = ['ref_id', 'first_name', 'last_name', 'provider__user__first_name', 'provider__user__last_name']
    list_filter = ("provider",)

class TheProviderAdmin(admin.ModelAdmin):
    list_display = ("get_name_display","clinic")
    list_filter = ("clinic",)
    search_fields = ['user__first_name', 'user__last_name']
    
admin.site.register(Case, CaseAdmin)
admin.site.register(Provider, TheProviderAdmin)
admin.site.register(Zone)
admin.site.register(Facility)
admin.site.register(Diagnosis)

class ReportMalnutritionAdmin(admin.ModelAdmin):
    list_display = ("case", "name","zone", "muac", "entered_at","provider","provider_number")

admin.site.register(ReportMalnutrition, ReportMalnutritionAdmin)

class ReportMalariaAdmin(admin.ModelAdmin):
    list_display = ("case","name","zone","result", "bednet","entered_at","provider","provider_number")
    verbose_name = "Malaria Report"
    verbose_name_plural = "Malaria Reports"

admin.site.register(ReportMalaria, ReportMalariaAdmin)

class ReportDiagnosisAdmin(admin.ModelAdmin):
    list_display = ("case", "entered_at")

admin.site.register(ReportDiagnosis, ReportDiagnosisAdmin)

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("sent_by_name","provider_clinic","mobile", "text", "created_at", "was_handled")
    list_filter = ("was_handled",)
    
admin.site.register(MessageLog, MessageLogAdmin)

class EventLogAdmin(admin.ModelAdmin):
    list_display = ("__unicode__",)
    list_filter = ("message", "content_type")
    
admin.site.register(EventLog, EventLogAdmin)

class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ("__unicode__",)
    list_filter = ("message", "created_at")
    
admin.site.register(SystemErrorLog, SystemErrorLogAdmin)

class ReportDiarrheaAdmin(admin.ModelAdmin):
    list_display = ("case", "ors", "days", "entered_at", "status")

admin.site.register(ReportDiarrhea, ReportDiarrheaAdmin)

admin.site.register(Observation)
admin.site.register(DiarrheaObservation)

