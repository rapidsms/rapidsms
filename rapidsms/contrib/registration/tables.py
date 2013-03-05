#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.models import Contact
import django_tables2 as tables


class ContactTable(tables.Table):
    name = tables.LinkColumn('contact_edit', args=[tables.utils.A('pk')])
    identities = tables.Column(empty_values=())

    class Meta:
        model = Contact
        exclude = ('id', )

    def render_identities(self, value, record):
        return ', '.join([x.identity for x in record.connection_set.all()])
