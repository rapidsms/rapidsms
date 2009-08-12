#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from django.db import connection
from django.db.backends.util import typecast_timestamp
from reporters.models import PersistantConnection, PersistantBackend, Reporter
from datetime import datetime

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


def combined_message_log(reporters=None):
    """Returns a list of IncomingMessage and OutgoingMessage objects, sorted by
       date (decending; most recent first) and (optionally) filtered to only
       contain messages linked to _reporters_, which can be a list of Reporter
       objects or integer primary keys.

       This may seem very complicated for something so inefficient, but
       the output can be made lazy, once that becomes a priority, without
       compromising the sorting or normalization."""


    def __rep_pk(reporter):
        """Casts a Reporter to an int by returning its primary
           key, returns an int as-is, or raises TypeError for
           any other input. Use this to validate _reporters_!"""

        if isinstance(reporter, Reporter):
            return reporter.pk

        elif isinstance(reporter, int):
            return reporter

        else:
            raise TypeError(
                "not a Reporter or int: %s" %\
                    (reporter))


    # start with all incoming messages (we might add a
    # filter later). note that we're pulling out just
    # enough information about reporters to build a
    # Reporter instance without hitting the db again
    incoming_sql = """select
                          "in", inc.id, inc.received, inc.text,
                          rep1.id, rep1.first_name, rep1.last_name,
                          be1.id, be1.title, be1.slug, con1.id, con1.identity

                        from messaging_incomingmessage as inc
                        left join reporters_reporter as rep1
                          on inc.reporter_id=rep1.id
                        left join reporters_persistantconnection as con1
                          on inc.connection_id=con1.id
                        left join reporters_persistantbackend as be1
                          on con1.backend_id=be1.id"""
    
    # same thing, except rather more convoluted, since
    # outgoing messages can have more than one recipient
    outgoing_sql = """select
                          "out", outgoing.id, outgoing.sent, outgoing.text,
                          rep2.id, rep2.first_name, rep2.last_name,
                          be2.id, be2.title, be2.slug, con2.id, con2.identity

                        from messaging_outgoingmessage as outgoing
                        left join messaging_recipient as rcp
                          on outgoing.id=rcp.outgoing_message_id
                        left join reporters_reporter as rep2
                          on rcp.reporter_id=rep2.id
                        left join reporters_persistantconnection as con2
                          on rcp.connection_id=con2.id
                        left join reporters_persistantbackend as be2
                          on con2.backend_id=be2.id"""


    # if one or more reporters were passed
    # in, we will return _only their_ messages
    if reporters is not None:

        # cast all _reporters_ to their primary keys.
        # __rep_pk will raise TypeError if any are invalid
        ids = [
            __rep_pk(rep)
            for rep in reporters]

        if len(ids):

            # build an sql-ish list of the reporters that
            # we're fetching: (1,2,3). we already know that
            # "ids" only contains ints, so no need to escape
            flat_ids = ",".join(map(str, ids))

            # add filters to both parts of the statement
            incoming_sql += " where inc.reporter_id in (%s)" % (flat_ids)
            outgoing_sql += " where rcp.reporter_id in (%s)" % (flat_ids)


    # grab both incoming and outgoing messages from the database at
    # once, so we can sensibly paginate the output (later) without
    # fetching everything and manually intersecting the rows.
    
    # NOTE: the following line had to be commented out and changed
    # to the below to run in mysql.  I have not tested the new version
    # so this may break on sqlite.
    # sql = incoming_sql + " union all " + outgoing_sql + " order by inc.received desc"
    sql = incoming_sql + " union all " + outgoing_sql + " order by received desc"
    cursor = connection.cursor()
    cursor.execute(sql)


    # TODO: return a paginatable iterator by overloading the Django
    # QuerySet with the contents of this query, optionally adding
    # a LIMIT statement to slice BEFORE hitting the database
    return cursor.fetchall()


def __combined_message_log_row(row):
    reporter = None
    connection = None

    # order of fields output by combined_message_log:
    #   [0] direction           [1] message_id      [2] message_date
    #   [3] message_text        [4] reporter_id     [5] reporter_first_name
    #   [6] reporter_last_name  [7] backend_id      [8] backend_title
    #   [9] backend_slug       [10] connection_id  [11] connection_identity


    # if this message is linked to a reporter, create a Reporter object
    # (so we can call the  methods like full_name) without hitting the
    # database each time. note that not all fields were fetched, so the
    # object won't work fully, but enough to display it
    if row[4] is not None:
        reporter = Reporter(
            first_name=row[5],
            last_name=row[6],
            pk=row[4])

    # likewise for a backend+connection, if this message isn't
    # linked to a reporter. combined_message_log can't filter
    # by connections (yet), but they must be displayed
    if row[7] is not None:
        backend = PersistantBackend(
            title=row[8],
            slug=row[9],
            id=row[7])

        connection = PersistantConnection(
            backend=backend,
            identity=row[11],
            id=row[10])

    # If the date object is already a datetime, don't bother
    # casting it.  Otherwise do.
    casted_date = row[2]
    if not isinstance(casted_date, datetime):
        casted_date = typecast_timestamp(row[2])
    return {
        "direction":  row[0],
        "pk":         row[1],
        "date":       casted_date,
        "text":       row[3],
        "reporter":   reporter,
        "connection": connection }
