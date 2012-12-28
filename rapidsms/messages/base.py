#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import copy
from django.conf import settings
from django.utils.translation.trans_real import translation


class MessageBase(object):
    def __init__(self, connections, text, msg_kwargs=None,
                 language=settings.LANGUAGE_CODE, fields=None):
        self.connections = connections
        self._text = text
        # save original text for future reference
        self.raw_text = copy.copy(self._text)
        self.msg_kwargs = msg_kwargs
        self.parts = [(self._text, self.msg_kwargs)]
        self.language = language
        self.fields = fields or {}
        # a message is considered "unprocessed" until rapidsms has
        # dispatched it to all apps.
        self.processed = False
        # a message can be marked "handled" by any app, which will
        # short-circuit the default phase in the router.
        self.handled = False

    def __unicode__(self):
        return self.text

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.text)

    def append(self, template, **kwargs):
        self.parts.append((template, kwargs))

    def _render_part(self, template, **kwargs):
        t = translation(self.language)
        tmpl = t.gettext(template)
        return tmpl % kwargs

    # @property
    # def text(self):
    #     return unicode(" ".join([
    #         self._render_part(template, **kwargs)
    #         for template, kwargs in self._parts
    #     ]))

    @property
    def connection(self):
        return self.connections[0]

    @property
    def contact(self):
        return self.connections[0].contact

    @property
    def peer(self):
        """
        Return the identity (eg. a phone number, email address, irc
        nickname) on the other end of this message. But you shouldn't
        use this method. It only seems to encourage people to ignore the
        distinction between backends and identities, and create fields
        like "mobile_number", which is all kinds of wrong.
        """

        return self.connections[0].identity
