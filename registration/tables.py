#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from djangotables import Table, Column
from rapidsms.models import Contact


def _edit_link(cell):
    return reverse(
        "registration_edit",
        args=[cell.row.pk])


class ContactTable(Table):
    alias    = Column(link=_edit_link)
    name     = Column()
    identity = Column()

    class Meta:
        order_by = 'alias'
