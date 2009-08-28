#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from django.core.exceptions import ValidationError
from apps.reporters.models import *


class MessageBase(models.Model):
    text = models.TextField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Verifies that one (not both) of the reporter and connection fields
           have been populated (raising ValidationError if not), and saves the
           object as usual. Note that neither field is defined in this abstract
           base class (because of the distinct related_names)."""

        if (self.reporter or self.connection) is None:
            raise ValidationError(
                "A valid (not null) reporter or connection (but " +\
                "not both) must be provided to save the object")

        # all is well; save the object as usual
        models.Model.save(self, *args, **kwargs)

    @property
    def who(self):
        """Returns the Reporter or Connection linked to this object."""
        return self.reporter or self.connection

    def __unicode__(self):

        # crop the text if it's long
        # (to avoid exploding the admin)
        if len(self.text) < 60: str = self.text
        else: str = "%s..." % (self.text[0:57])

        return "%s (%s %s)" %\
            (str, self.prep, self.who)

    def __repr__(self):
        return "%s %r: %r" %\
            (self.prep, self.who, self.text)


class IncomingMessage(MessageBase):
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

    connection = models.ForeignKey(PersistantConnection, null=True, related_name="incoming_messages")
    reporter   = models.ForeignKey(Reporter, null=True, related_name="incoming_messages")
    received   = models.DateTimeField(auto_now_add=True)
    prep = "from"


class OutgoingMessage(MessageBase):
    @property
    def date(self):
        '''Same as sent''' 
        return self.sent
    
    def is_incoming(self):
        return False
    
    def __unicode__(self):
        return "%s %s" % (MessageBase.__unicode__(self), self.sent)  

    connection = models.ForeignKey(PersistantConnection, null=True, related_name="outgoing_messages")
    reporter   = models.ForeignKey(Reporter, null=True, related_name="outgoing_messages")
    sent       = models.DateTimeField(auto_now_add=True)
    prep = "to"
