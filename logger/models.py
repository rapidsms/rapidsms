#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django
from django.db import models


class MessageBase(models.Model):
    text = models.CharField(max_length=140)
    # TODO save connection title rather than wacky object string?
    identity = models.CharField(max_length=150)
    backend = models.CharField(max_length=150)
    
    def __unicode__(self):
        return "%s (%s) %s" % (self.identity, self.backend, self.text)
    
    class Meta:
        abstract = True
    
    
class IncomingMessage(MessageBase):
    received = models.DateTimeField(auto_now_add=True)
    
    # Helper methods to allow this object to be treated similar
    # to the outgoing message, e.g. if they are in the same list
    # in a template
    @property
    def date(self):
        '''Same as received''' 
        return self.received
    
    def is_incoming(self):
        return True
    
    def __unicode__(self):
        return "%s %s" % (MessageBase.__unicode__(self), self.received)  

class OutgoingMessage(MessageBase):
    sent = models.DateTimeField(auto_now_add=True)
    
    @property
    def date(self):
        '''Same as sent''' 
        return self.sent
    
    def is_incoming(self):
        return False
    
    def __unicode__(self):
        return "%s %s" % (MessageBase.__unicode__(self), self.sent)  
