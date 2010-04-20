#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms import tables
from rapidsms.models import Contact


# add an 'identity' column, which is a bit naughty, since a contact can
# have many of them -- but that's an implementation detail, and rarely
# comes up in practice. it's useful enough to be inconsistent here.
def _identity(row):
    identities = row.data.connection_set.values_list('identity', flat=True)
    return identities[0] if identities else None


class ContactTable(tables.ModelTable):
    identity = tables.Column(data=_identity)

    class Meta:
        model = Contact
        exclude = ['id']
        order_by = 'alias'
