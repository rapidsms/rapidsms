from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from datetime import datetime, date

from apps.mctc.models.general import Provider

# since there's only ever going to be a limited number of message
# on a strict one to one basis, lets just define them here,
# pushing the full text or setting up another model would work too
messages = {
    "provider_registered": _("Provider registered, awaiting confirmation"),
    "patient_created": _("Patient created"),
    "muac_taken": _("MUAC taken for the patient"),
    "diarrhea_taken": _("DIARRHEA taken for the patient"),
    "diarrhea_fu_taken": _("DIARRHEA follow-up received for the patient"),
    "mrdt_taken": _("MRDT taken for the patient"),
    "diagnosis_taken": _("Diagnosis taken for the patient"),    
    "user_logged_in": _("User logged into the user interface"),
    "confirmed_join": _("Provider confirmed"),
    "case_cancelled": _("Case was cancelled by the provider"),
    "case_transferred": _("Case was transferred to the current provider"),
    "note_added": _("Note added to the case by the provider")    
}

class EventLog(models.Model):
    """ This is a much more refined log, giving you nicer messages """
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    message = models.CharField(max_length=25, choices=tuple(messages.items()))
    created_at  = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "mctc"
        ordering = ("-created_at",)

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def __unicode__(self):
        return u"%(date)s - %(msg)s (%(type)s)" % {'date': self.created_at, 'msg': self.message, 'type': self.content_type}

class SystemErrorLog(models.Model):
    """ This is for exception errors """
    message = models.CharField(max_length=500)
    created_at  = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "mctc"
        ordering = ("-created_at",)

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def __unicode__(self):
        return u"%(date)s - %(msg)s (%(type)s)" % {'date': self.created_at, 'msg': self.message, 'type': self.content_type}

def elog(source, message):    
    ev = SystemErrorLog()    
    ev.message = message
    ev.created_at = datetime.now()
    ev.save()


def log(source, message):
    if not messages.has_key(message):
        raise ValueError, "No message: %s exists, please add to logs.py"
    if not source.id:
        print "* Cannot log until the object has been saved, id is None, %s" % message
    ev = EventLog()
    ev.content_object = source
    ev.message = message
    ev.created_at = datetime.now()
    ev.save()

class MessageLog(models.Model):
    """ This is the raw dirt message log, useful for some things """
    mobile      = models.CharField(max_length=255, db_index=True)
    sent_by     = models.ForeignKey(User, null=True)
    text        = models.TextField(max_length=255)
    was_handled = models.BooleanField(default=False, db_index=True)
    created_at  = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "mctc"
        ordering = ("-created_at",)        
        
    def provider_number(self):
        return self.provider.mobile
    
    def sent_by_name(self):
        return "%s %s" %(self.sent_by.first_name, self.sent_by.last_name)

    def provider_clinic(self):
	p = Provider.objects.get(user=self.sent_by)
	if p:
	    return "%s"%p.clinic
	return ""

    def save(self, *args):
        if not self.id:
            self.created_at = datetime.now()
        super(MessageLog, self).save(*args)
    
    @classmethod
    def count_by_provider(cls,provider, duration_end=None,duration_start=None):
        if provider is None:
            return None
        try:
            if duration_start is None or duration_end is None:
                return cls.objects.filter(provider=provider).count()
            return cls.objects.filter(created_at__lte=duration_end, created_at__gte=duration_start).filter(sent_by=provider.user_id).count()
        except models.ObjectDoesNotExist:
            return None
        
    @classmethod
    def count_processed_by_provider(cls,provider, duration_end=None,duration_start=None):
        if provider is None:
            return None
        try:
            if duration_start is None or duration_end is None:
                return cls.objects.filter(provider=provider.user_id).count()
            return cls.objects.filter(created_at__lte=duration_end, created_at__gte=duration_start).filter(sent_by=provider.user_id, was_handled=True).count()
        except models.ObjectDoesNotExist:
            return None
    
    @classmethod
    def count_refused_by_provider(cls,provider, duration_end=None,duration_start=None):
        if provider is None:
            return None
        try:
            if duration_start is None or duration_end is None:
                return cls.objects.filter(provider=provider).count()
            return cls.objects.filter(created_at__lte=duration_end, created_at__gte=duration_start).filter(sent_by=provider.user_id, was_handled=True).count()
        except models.ObjectDoesNotExist:
            return None
    
    @classmethod
    def days_since_last_activity(cls,provider):
        today = date.today()
        logs = MessageLog.objects.order_by("created_at").filter(created_at__lte=today,sent_by=provider.user_id).reverse()
        if not logs:
            return ""
        return (today - logs[0].created_at.date()).days
        