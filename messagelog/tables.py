#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils.tables import Table, Column, DatetimeColumn
from .models import Message


class MessagelogTable(Table):
    text      = Column("Text")
    who       = Column("To/From", sortable=False)
    direction = Column("Direction", attr="get_direction_display")
    date      = DatetimeColumn("Date", format="d/m/Y H:i")

    def get_query_set(self):
        return Message.objects.all()
