#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from djangotables import Table, Column
from rapidsms.models import Contact


class ContactTable(Table):
    alias    = Column()
    name     = Column()
    identity = Column()

    class Meta:
        order_by = 'alias'
