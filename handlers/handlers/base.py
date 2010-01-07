#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class BaseHandler(object):

    @classmethod
    def dispatch(cls, router, msg):
        return False

    def __init__(self, router, msg):
        self.router = router
        self.msg = msg

    def respond(self, text, **kwargs):
        return self.msg.respond(text, **kwargs)

    @classmethod
    def test(cls, text, identity=None):
        """
        Test this handler by dispatching an IncomingMessage containing
        *text*. Returns a list containing the *text* property of each
        response, in the order which they were sent.

        >>> class AlwaysHandler(BaseHandler):
        ...
        ...     @classmethod
        ...     def dispatch(cls, router, msg):
        ...         msg.respond("xxx")
        ...         msg.respond("yyy")
        ...         return True

        >>> AlwaysHandler.test('anything')
        ['xxx', 'yyy']

        Returns None if the handler ignored the message (ie, the
        `dispatch` method returned False or None).

        >>> class NeverHandler(BaseHandler):
        ...     pass

        >>> NeverHandler.test('anything') is None
        True

        This is intended to test the handler in complete isolation. To
        test the interaction between multiple apps and/or handlers, see
        the rapidsms.tests.scripted module.
        """

        # these can't be loaded until runtime,
        # since the django ORM isn't configured
        from rapidsms.models import Backend, Connection
        from rapidsms.messages import IncomingMessage

        bknd = Backend(name='mock')
        conn = Connection(backend=bknd, identity=identity)
        msg = IncomingMessage(connection=conn, text=text)

        accepted = cls.dispatch(None, msg)
        if not accepted:
            return None
        
        # just the text, for now. maybe the
        # full OutgoingMessage objects later
        return [m.text for m in msg.responses]
