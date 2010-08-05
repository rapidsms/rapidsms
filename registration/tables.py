#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from djtables import Table, Column
from rapidsms.models import Contact


def _edit_link(cell):
    return reverse(
        "registration_edit",
        args=[cell.row.pk])

def _any_identity(cell):
    if cell.object.connection_set.count() > 0:
        return cell.object.connection_set.all()[0].identity

class ContactTable(Table):
    name     = Column(link=_edit_link)
    identity = Column(value=_any_identity)

    class Meta:
        order_by = 'name'
