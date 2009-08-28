#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from nodegraph.models import NodeSet
from django.core.exceptions import ValidationError
from reporters.models import *

MAX_LATIN_SMS_LEN = 160 

class MessageBase(models.Model):
    text = models.CharField(max_length=MAX_LATIN_SMS_LEN)
    # TODO save connection title rather than wacky object string?
    identity = models.CharField(max_length=150)
    backend = models.CharField(max_length=150)
    # this isn't modular
    # but it's optional and saves some ridiculous querying for smsforum frontpage
    # TODO save domain to wacky object string rather than connection title?
    # (to reduce app dependencies)
    domain = models.ForeignKey(NodeSet,null=True)
    
    def __unicode__(self):
        return u'%s (%s) %s' % (self.identity, self.backend, self.text)
    
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
        return u"%s %s" % (MessageBase.__unicode__(self), self.received)

    class Meta:
        # the permission required for this tab to display in the UI
        permissions = (
            ("can_view", "Can view message logs"),
        )
    
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
        return u"%s %s" % (MessageBase.__unicode__(self), self.sent)

    connection = models.ForeignKey(PersistantConnection, null=True, related_name="outgoing_messages")
    reporter   = models.ForeignKey(Reporter, null=True, related_name="outgoing_messages")
    sent       = models.DateTimeField(auto_now_add=True)
    prep = "to"

class CodeSet(models.Model):
    """
    An arbitrary set of codes with which messages can be tagged.
    e.g. category, state, flagged
    """
    name = models.CharField(max_length = 64, unique=True) 
    
    def __unicode__(self):
        return unicode(self.name)

class Code(models.Model):
    """
    This model holds codes which can be mapped to individual messages
    e.g. good/bad/ignore, open/inprogress/closed, flagged/not_flagged
    """
    set = models.ForeignKey(CodeSet, null=False)
    name = models.CharField(max_length = 64, unique=True) # e.g. sante, les droits humain, etc.
    slug = models.CharField(max_length = 8, unique=True) # e.g. san, dro, etc.
    
    def __unicode__(self):
        return u"%(name)s" % { 'name':self.name }

class MessageTag(models.Model):
    """
    A dynamic way of associating messages with codes without requiring that
    all messages be coded
    """
    message = models.ForeignKey(IncomingMessage)
    code = models.ForeignKey(Code)

    def __unicode__(self):
        return u"%(message)s: %(tag)s" % { 'message':self.message, 'tag':self.code }

class MessageAnnotation(models.Model):
    """
    A dynamic way of associating messages with free-form annotations
    without requiring that all messages be annotated
    """
    message = models.ForeignKey(IncomingMessage)
    text = models.CharField(max_length=255,blank=True)

    def __unicode__(self):
        return u"%(message)s: %(annotation)s" % { 'message':self.message, 'annotation':self.annotation }

