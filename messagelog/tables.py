#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils.tables import Table, Column
from .models import Message


class MessagelogTable(Table):
    text      = Column("Text")
    who       = Column("To/From", sortable=False)
    date      = Column("Date", template="{{ row.date|date:'d/m/Y H:i' }}")
    direction = Column("Direction", attr="get_direction_display")

    def get_query_set(self):
        return Message.objects.all()
