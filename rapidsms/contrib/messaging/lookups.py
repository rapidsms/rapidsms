#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.models import Contact

from selectable.base import ModelLookup
from selectable.registry import registry


class ContactLookup(ModelLookup):
    """Contacts with a Connection."""
    model = Contact
    filters = {
        'connection__isnull': False,
    }
    search_fields = ('name__icontains',)

    def get_item_value(self, item):
        return self.get_item_label(item)

    def get_item_label(self, item):
        if not item.name:
            return item.default_connection.identity
        return '{0} ({1})'.format(item.name, item.default_connection.identity)

registry.register(ContactLookup)
