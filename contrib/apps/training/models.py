#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from reporters.models import Reporter, PersistantConnection

# TODO: better name
class MessageInWaiting(models.Model):
    '''A message in waiting for a response.'''
    STATUS_TYPES = (
        ('P', 'Pending'), # the message has been received, but not handled
        ('H', 'Handled'), # the message has been handled by the user but not sent
        ('S', 'Sent'), # the message has been sent
    )
    
    # we need either a reporter or a connection to respond
    # TODO: this should be a dual-non-null key if that is possible
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    time = models.DateTimeField()
    incoming_text = models.CharField(max_length=160)
    status = models.CharField(max_length=1, choices=STATUS_TYPES)
    
    @classmethod
    def from_message(klass, msg):
        return klass(
            incoming_text=msg.text,
            time=msg.date,
            status="P",
            
            # link the message to the reporter
            # or connection, whichever we have
            **msg.persistance_dict)
    
    def get_connection(self):
        if self.reporter:
            return self.reporter.connection()
        return self.connection
    
    def __unicode__(self):
        return self.incoming_text
    
    def __json__(self):
	    return {
		    "pk":         self.pk,
		    "text":       self.incoming_text,
		    "reporter":   self.reporter,
		    "connection": self.connection,
		    "responses":  list(self.responses.all()) }


# TODO: better name    
class ResponseInWaiting(models.Model):
    
    '''The responses to send to the messages in waiting'''
    RESPONSE_TYPES = (
        ('O', 'Original'), # the original response - as decided by RapidSMS.  These won't go out unless they are confirmed 
        ('C', 'Confirmed'), # an original response that is to be sent out as-is
        ('A', 'Added'), # when we want to send our own messages back
        ('R', 'Responded') # when messages in the messageinwaiting model has been responded to
    )
    
    # TODO: better name - what is the antonym of response?
    originator = models.ForeignKey(MessageInWaiting, related_name="responses")
    text = models.CharField(max_length=160)
    type = models.CharField(max_length=1, choices=RESPONSE_TYPES)
    
    def __unicode__(self):
        return self.text

    def __json__(self):
	    return {
		    "pk":   self.pk,
		    "text": self.text,
		    "type": self.get_type_display() }


class Template(models.Model):
    """This model provides a place for efficient users of the
       Training WebUI to store canned responses to common errors."""
    key  = models.CharField(max_length=1, unique=True)
    text = models.CharField(max_length=160, unique=True)

    def __unicode__(self):
        return self.text
    
    class Meta:
        verbose_name = "Template"
