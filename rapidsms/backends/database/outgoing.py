#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging

from rapidsms.backends.base import BackendBase
from rapidsms.backends.database.models import BackendMessage


logger = logging.getLogger(__name__)


class DatabaseBackend(BackendBase):
    """
    Simple backend that uses the database for storage. Mostly used for testing.
    """

    def send(self, id_, text, identities, context=None):
        logger.info('Storing message: %s', text)
        context = context or {}
        kwargs = {'name': self.name, 'direction': 'O', 'text': text,
                  'message_id': id_}
        if 'external_id' in context:
            kwargs['external_id'] = context['external_id']
        for identity in identities:
            kwargs['identity'] = identity
            BackendMessage.objects.create(**kwargs)
        return True
