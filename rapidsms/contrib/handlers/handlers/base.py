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

    def respond_error(self, text, **kwargs):
        return self.msg.error(text, **kwargs)

    @classmethod
    def test(cls, text, identity=None):
        """
        Test this handler by dispatching an IncomingMessage containing
        ``text``, as sent by ``identity`` via a mock backend. Return a
        list containing the ``text`` property of each response, in the
        order which they were sent.::

            >>> class AlwaysHandler(BaseHandler):
            ...
            ...     @classmethod
            ...     def dispatch(cls, router, msg):
            ...         msg.respond("xxx")
            ...         msg.respond("yyy")
            ...         return True

            >>> AlwaysHandler.test('anything')
            ['xxx', 'yyy']

        Return False if the handler ignored the message (ie, the
        ``dispatch`` method returned False or None).

            >>> class NeverHandler(BaseHandler):
            ...     pass

            >>> NeverHandler.test('anything')
            False

        This is intended to test the handler in complete isolation. To
        test the interaction between multiple apps and/or handlers, see
        the rapidsms.tests.scripted module.
        """

        # avoid setting the default identity to "mock" in the signature,
        # to avoid exposing it in the public API. it's not important.
        if identity is None:
            identity = "mock"

        # models can't be loaded until the django ORM is ready.
        from rapidsms.models import Backend, Connection
        from rapidsms.messages import IncomingMessage

        # spawn a mock backend for each handler, to allow multiple tests
        # to interact with one another without overlapping.
        if not hasattr(cls, "_mock_backend"):
            cls._mock_backend = Backend.objects.create(
                name="mock_%d" % id(cls))

        conn, created = Connection.objects.get_or_create(
            backend=cls._mock_backend,
            identity=identity)

        msg = IncomingMessage(
            connection=conn,
            text=text)

        accepted = cls.dispatch(None, msg)
        return [m['text'] for m in msg.responses]\
            if accepted else False
