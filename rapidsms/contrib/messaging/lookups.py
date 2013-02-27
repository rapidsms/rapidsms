#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.models import Contact

from selectable.base import ModelLookup
from selectable.registry import registry


class ContactLookup(ModelLookup):
    model = Contact
    search_fields = ('name__icontains',)
registry.register(ContactLookup)
