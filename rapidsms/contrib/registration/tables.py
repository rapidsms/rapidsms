#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.models import Contact
import django_tables2 as tables


class ContactTable(tables.Table):
    identities = tables.Column(empty_values=(), orderable=False)
    id = tables.LinkColumn('registration_contact_edit',
                           args=[tables.utils.A('pk')])

    class Meta:
        model = Contact
        order_by = ('id')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }

    def render_identities(self, value, record):
        return ', '.join([x.identity for x in record.connection_set.all()])
