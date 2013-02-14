from rapidsms.backends.base import BackendBase
from rapidsms.backends.db.models import BackendMessage


class DatabaseBackend(BackendBase):
    """
    Simple backend that uses the database for storage. Mostly used for testing.
    """

    def send(self, id_, text, identities, context):
        kwargs = {'name': self.name, 'direction': 'O', 'text': text,
                  'message_id': id_}
        if 'external_id' in context:
            kwargs['external_id'] = context['external_id']
        for identity in identities:
            kwargs['identity'] = identity
            BackendMessage.objects.create(**kwargs)
        return True
