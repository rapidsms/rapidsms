#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from djangotables import Table, Column
from .models import Message


class MessageTable(Table):

    # this is temporary, until i fix ModelTable!
    contact = Column()
    connection = Column()
    direction = Column()
    date = Column()
    text = Column()

    class Meta:
        #model = Message
        #exclude = ['id']
        order_by = '-date'
