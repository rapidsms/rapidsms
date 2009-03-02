#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django
from django.db import models


class MessageBase(models.Model):
    text = models.CharField(max_length=140)
    caller = models.CharField(max_length=15)
    
    def __unicode__(self):
        return "[%s] %s" % (self.caller, self.text)
    
    class Meta:
        abstract = True
    
    
class IncomingMessage(MessageBase):
    received = models.DateTimeField(auto_now_add=True)
    

class OutgoingMessage(MessageBase):
    sent = models.DateTimeField(auto_now_add=True)
