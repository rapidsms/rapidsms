#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from apps.reporters.models import PersistantConnection, Reporter


class IncomingMessage(models.Model):
    reporter   = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    received   = models.DateTimeField()
    text = models.TextField()

    def __unicode__(self):
        sender = self.reporter if self.reporter else self.connection
        return u"Message from %s: %s" % (sender, self.text)


class OutgoingMessage(models.Model):
    sent = models.DateTimeField()
    text = models.TextField()

    def __unicode__(self):
        to = ", ".join(map(unicode, self.recipients.all()))
        return u"Message to %s: %s" % (to, self.text)


class Recipient(models.Model):
    reporter         = models.ForeignKey(Reporter, null=True, blank=True)
    connection       = models.ForeignKey(PersistantConnection, null=True, blank=True)
    outgoing_message = models.ForeignKey(OutgoingMessage, related_name="recipients")
    
    def __unicode__(self):
        if   self.reporter:   return unicode(self.reporter)
        elif self.connection: return unicode(self.connection)
        else:                 return u"Unknown"
