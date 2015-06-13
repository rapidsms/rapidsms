from __future__ import unicode_literals
from six import unichr
from six.moves import xrange
import string
import random
from django.contrib.auth.models import User

from rapidsms.models import Backend, Contact, Connection
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage


__all__ = ('CreateDataMixin', 'LoginMixin')


UNICODE_CHARS = [unichr(x) for x in xrange(1, 0xD7FF)]


class CreateDataMixin(object):
    """Base test mixin class that provides helper functions to create data.

    No superclasses.
    """

    def random_string(self, length=255, extra_chars=''):
        """ Generate a random string of characters.

        :param length: Length of generated string.
        :param extra_chars: Additional characters to include in generated
            string.
        """
        chars = string.ascii_letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def random_unicode_string(self, max_length=255):
        """Generate a random string of unicode characters.

        :param length: Length of generated string.
        """
        output = ''
        for x in xrange(random.randint(1, max_length / 2)):
            c = UNICODE_CHARS[random.randint(0, len(UNICODE_CHARS) - 1)]
            output += c + ' '
        return output

    def create_backend(self, data={}):
        """Create and return RapidSMS backend object. A random ``name``
        will be created if not specified in ``data`` attribute.

        :param data: Optional dictionary of field name/value pairs to pass
            to the object's ``create`` method.
        """
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Backend.objects.create(**defaults)

    def create_contact(self, data={}):
        """ Create and return RapidSMS contact object. A random ``name``
        will be created if not specified in ``data`` attribute.

        :param data: Optional dictionary of field name/value pairs to
            pass to the object's ``create`` method."""
        defaults = {
            'name': self.random_string(12),
        }
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def create_connection(self, data={}):
        """ Create and return RapidSMS connection object. A random
        ``identity`` and ``backend`` will be created if not specified in
        ``data`` attribute.

        :param data: Optional dictionary of field name/value pairs
            to pass to the object's ``create`` method."""
        defaults = {
            'identity': self.random_string(10),
        }
        defaults.update(data)
        if 'backend' not in defaults:
            defaults['backend'] = self.create_backend()
        return Connection.objects.create(**defaults)

    def create_outgoing_message(self, data={}, backend=None):
        """Create and return RapidSMS OutgoingMessage object. A random
        ``template`` will be created if not specified in ``data`` attribute.

        :param data: Optional dictionary of field name/value pairs to pass
            to ``OutgoingMessage.__init__``."""
        defaults = {
            'text': self.random_string(10),
        }
        defaults.update(data)
        if 'connections' not in defaults:
            conn_kwargs = {}
            if backend:
                conn_kwargs = {'data': {'backend': backend}}
            defaults['connections'] = [self.create_connection(**conn_kwargs)]
        return OutgoingMessage(**defaults)

    def create_incoming_message(self, data={}):
        """Create and return RapidSMS IncomingMessage object."""
        defaults = {
            'text': self.random_string(10),
        }
        defaults.update(data)
        if 'connections' not in defaults:
            defaults['connections'] = [self.create_connection()]
        return IncomingMessage(**defaults)


class LoginMixin(object):
    """Helpers for creating users and logging in"""
    def login(self):
        """If not already set, creates self.username and self.password,
        otherwise uses the existing values.
        If there's not already a user with that username, creates one.
        Sets self.user to that user.
        Logs the user in.
        """
        if not hasattr(self, 'username'):
            self.username = 'fred'
        if not hasattr(self, 'password'):
            self.password = 'bob'
        if not User.objects.filter(username=self.username).exists():
            User.objects.create_user(self.username, password=self.password)
        self.user = User.objects.get(username=self.username)
        logged_in = self.client.login(username=self.username,
                                      password=self.password)
        if not logged_in:
            self.fail("LOGIN failed")
