#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms import tables
from .models import Message


class MessagelogTable(tables.Table):
    text      = tables.Column("Text")
    who       = tables.Column("To/From", sortable=False)
    direction = tables.Column("Direction")
    date      = tables.Column("Date")

    def get_query_set(self):
        return Message.objects.all()
