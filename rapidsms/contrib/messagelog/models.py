#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from rapidsms.models import Contact, Connection


@python_2_unicode_compatible
class Message(models.Model):
    INCOMING = "I"
    OUTGOING = "O"
    DIRECTION_CHOICES = (
        (INCOMING, "Incoming"),
        (OUTGOING, "Outgoing"),
    )

    contact = models.ForeignKey(Contact, blank=True, null=True)
    connection = models.ForeignKey(Connection, blank=True, null=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES)
    date = models.DateTimeField()
    text = models.TextField()

    def save(self, *args, **kwargs):
        """
        Verifies that one (not both) of the contact or connection fields
        have been populated (raising ValidationError if not), and saves
        the object as usual.
        """
        if self.contact is None and self.connection is None:
            raise ValidationError("A valid (not null) contact or connection "
                    "(but not both) must be provided to save the object.")
        elif self.connection and self.contact and \
                (self.contact != self.connection.contact):
            raise ValidationError("The connection and contact you tried to "
                    "save did not match! You need to pick one or the other.")

        if self.connection and self.connection.contact is not None:
            # set the contact here as well, even if they didn't
            # do it explicitly. If the contact's number changes
            # we still might want to know who it originally came
            # in from.
            self.contact = self.connection.contact
        super(Message, self).save(*args, **kwargs)

    @property
    def who(self):
        """Returns the Contact or Connection linked to this object."""
        return self.contact or self.connection

    def __str__(self):
        # crop the text (to avoid exploding the admin)
        text = self.text if len(self.text) < 60 else "%s..." % self.text[0:57]
        direction = "to" if self.direction == self.INCOMING else "from"
        return "%s (%s %s)" % (text, direction, self.who)
