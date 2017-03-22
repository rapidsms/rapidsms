#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.models import Connection

from selectable.base import ModelLookup
from selectable.registry import registry


class ConnectionLookup(ModelLookup):
    model = Connection
    search_fields = ('identity__icontains', 'contact__name__icontains')

    def get_item_value(self, item):
        return self.get_item_label(item)

    def get_item_label(self, item):
        # Add an asterisk to default connections
        default = not item.contact or item == item.contact.default_connection
        if default:
            conn_name = '{0} - {1}*'.format(item.backend.name, item.identity)
        else:
            conn_name = '{0} - {1}'.format(item.backend.name, item.identity)

        if not item.contact or not item.contact.name:
            return conn_name
        return '{0} ({1})'.format(item.contact.name, conn_name)


registry.register(ConnectionLookup)
