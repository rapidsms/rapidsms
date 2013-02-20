#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from djtables import Table, Column


def _edit_link(cell):
    return reverse(
        "contact_edit",
        args=[cell.row.pk])


def _identities(cell):
    return ', '.join([x.identity for x in cell.object.connection_set.all()])


class ContactTable(Table):
    name = Column(link=_edit_link)
    identity = Column(value=_identities, sortable=False)

    class Meta:
        order_by = 'name'
