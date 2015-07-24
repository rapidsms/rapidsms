#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils.encoding import python_2_unicode_compatible

from rapidsms.utils.modules import import_class


@python_2_unicode_compatible
class BackendBase(object):
    """Base class for outbound backend functionality."""

    @classmethod
    def find(cls, module_name):
        """
        Helper function to import backend classes.

        :param module_name: Dotted Python path to backend class name
        :returns: Imported class object
        """
        return import_class(module_name, cls)

    def __init__(self, router, name, **kwargs):
        self.router = router
        self.name = name

        self._config = kwargs
        self.configure(**kwargs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<backend: %s>" % self.name

    def configure(self, **kwargs):
        """
        Configuration parameters from :setting:`INSTALLED_BACKENDS` will
        be passed here after the router is instantiated. You can override
        this method to parse your configuration.
        """
        pass

    def send(self, id_, text, identities, context=None):
        """
        Backend sending logic. The router will call this method for each
        outbound message. This method must be overridden by sub-classes.
        Backends typically initiate HTTP requests from within this method.

        If multiple ``identities`` are provided, the message is intended for
        all recipients.

        Any exceptions raised here will be captured and logged by the router. If
        messages to some identities failed while others succeeded, you can
        provide that information back to the router by adding a list of the
        identities which failed in a ``failed_identities`` parameter on the
        exception. If you do provide that parameter, then the router should assume
        that all identities *not* listed in ``failed_identities`` were successfully
        sent.

        :Example:

        .. code-block:: python

         def send(self, id_, text, identities, context):
             failures = []
             for identity in identities:
                 result = send_my_message(identity, text, context)
                 if result == 'failed':
                     failures.append(identity)
             if failures:
                 msg = '%d messages failed.' % len(failures)
                 raise MessageSendingError(msg, failed_identities=failures)

        :param id\_: Message ID
        :param text: Message text
        :param identities: List of identities
        :param context: Optional dictionary with extra context provided by router to backend
        """
        # subclasses should override this
        raise NotImplementedError()

    @property
    def model(self):
        """
        The model attribute is the RapidSMS model instance with this
        backend name. A new backend will automatically be created if
        one doesn't exist upon accessing this attribute.
        """
        from rapidsms.models import Backend
        backend, _ = Backend.objects.get_or_create(name=self.name)
        return backend
