import string
import random

from rapidsms.models import Backend, Contact, Connection
from rapidsms.log.mixin import LoggerMixin
from rapidsms.messages.outgoing import OutgoingMessage


__all__ = ('CreateDataMixin',)


UNICODE_CHARS = [unichr(x) for x in xrange(1, 0xD7FF)]


class CreateDataMixin(object, LoggerMixin):
    """Base test mixin class that provides helper functions to create data"""

    def random_string(self, length=255, extra_chars=''):
        """Generate a random string of characters."""
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def random_unicode_string(self, max_length=255):
        """Generate a random string of unicode characters."""
        output = u''
        for x in xrange(random.randint(1, max_length / 2)):
            c = UNICODE_CHARS[random.randint(0, len(UNICODE_CHARS) - 1)]
            output += c + u' '
        return output

    def create_backend(self, data={}):
        """Create and return RapidSMS backend object."""
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Backend.objects.create(**defaults)

    def create_contact(self, data={}):
        """Create and return RapidSMS contact object."""
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def create_connection(self, data={}):
        """Create and return RapidSMS connection object."""
        defaults = {
            'identity': self.random_string(10),
        }
        defaults.update(data)
        if 'backend' not in defaults:
            defaults['backend'] = self.create_backend()
        return Connection.objects.create(**defaults)

    def create_outgoing_message(self, data={}):
        """Create and return RapidSMS OutgoingMessage object."""
        defaults = {
            'template': self.random_string(10),
        }
        defaults.update(data)
        if 'connection' not in defaults:
            defaults['connection'] = self.create_connection()
        return OutgoingMessage(**defaults)
