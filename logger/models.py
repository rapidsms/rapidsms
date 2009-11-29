#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models, connection
from django.db.backends.util import typecast_timestamp
from django.core.exceptions import ValidationError
from reporters.models import *


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
    connection = models.ForeignKey(PersistantConnection, null=True, related_name="incoming_messages")
    reporter   = models.ForeignKey(Reporter, null=True, related_name="incoming_messages")
    received   = models.DateTimeField(auto_now_add=True)
    prep = "from"


class OutgoingMessage(MessageBase):
    connection = models.ForeignKey(PersistantConnection, null=True, related_name="outgoing_messages")
    reporter   = models.ForeignKey(Reporter, null=True, related_name="outgoing_messages")
    sent       = models.DateTimeField(auto_now_add=True)
    prep = "to"


def combined_message_log(reporter):

    # this wacky sql allows us to fetch a single queryset
    # containing both incoming and outgoing messages, which
    # we can display in a single paginated block. it's taken
    # (sort-of) from the messaging app, which provides a lot
    # of overlapping functionality that should be abstracted
    sql = """select
              "in", inc.id, inc.received, inc.text
              from logger_incomingmessage as inc
              where inc.reporter_id=%s
            union all select
              "out", out.id, out.sent, out.text
              from logger_outgoingmessage as out
              where out.reporter_id=%s
            order by inc.received desc""" %\
        (reporter.pk, reporter.pk)

    # fetch the blob of messages
    cursor = connection.cursor()
    cursor.execute(sql)

    # (from messaging/models.py)
    # TODO: return a paginatable iterator by overloading the Django
    # QuerySet with the contents of this query, optionally adding
    # a LIMIT statement to slice BEFORE hitting the database
    return cursor.fetchall()


def combined_message_log_row(row):

    # order of fields output by combined_message_log:
    #   [0] direction     [1] message_id
    #   [2] message_date  [3] message_text

    return {
        "direction": row[0],
        "pk":        row[1],
        "date":      typecast_timestamp(row[2]),
        "text":      row[3] }
