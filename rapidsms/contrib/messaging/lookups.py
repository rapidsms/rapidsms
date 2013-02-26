from selectable.base import ModelLookup
from selectable.registry import registry
from rapidsms.models import Contact


class ContactLookup(ModelLookup):
    model = Contact
    search_fields = ('name__icontains',)
registry.register(ContactLookup)
