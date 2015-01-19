#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import logging
import warnings
import copy
from collections import defaultdict
from six import string_types

from django.db.models.query import QuerySet

from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.backends.base import BackendBase
from rapidsms.apps.base import AppBase
from rapidsms.conf import settings
from rapidsms.errors import MessageSendingError


logger = logging.getLogger(__name__)


class BlockingRouter(object):
    """Base RapidSMS router implementation."""

    #: Incoming router phases processed in the order in which they're defined.
    incoming_phases = ("filter", "parse", "handle", "default", "cleanup")
    #: Outgoing router phases processed in the order in which they're defined.
    outgoing_phases = ("outgoing",)

    def __init__(self, *args, **kwargs):
        self.apps = []
        self.backends = {}
        apps = kwargs.pop('apps', settings.INSTALLED_APPS)
        backends = kwargs.pop('backends', settings.INSTALLED_BACKENDS)
        for name in apps:
            try:
                self.add_app(name)
            except Exception:
                logger.exception("Failed to add app to router.")
        for name, conf in backends.items():
            parsed_conf = copy.copy(conf)
            engine = parsed_conf.pop('ENGINE')
            self.add_backend(name, engine, parsed_conf)

    def add_app(self, module_name):
        """
        Add RapidSMS app to router. Installed apps will be notified of
        incoming and outgoing messages. If ``module_name`` is a Django app,
        the method looks in ``app_name.app`` for an ``AppBase`` subclass to
        use.

        :param module_name: ``AppBase`` object or dotted path to RapidSMS app.
        :returns: ``AppBase`` object if found, otherwise ``None``.
        """
        if isinstance(module_name, string_types):
            cls = AppBase.find(module_name)
        elif issubclass(module_name, AppBase):
            cls = module_name
        if not cls:
            return None
        app = cls(self)
        self.apps.append(app)
        return app

    def get_app(self, module_name):
        """
        Access installed app by name.

        :param module_name: Dotted path to RapidSMS app.
        :returns: ``AppBase`` object if found, otherwise ``None``.
        """
        cls = AppBase.find(module_name)
        if cls is None:
            return None
        for app in self.apps:
            if type(app) == cls:
                return app
        raise KeyError("The %s app was not found in the router!" % module_name)

    def add_backend(self, name, module_name, config=None):
        """
        Add RapidSMS backend to router. Installed backends will be used to
        send outgoing messages.

        :param name: Name of backend.
        :param module_name: :class:`BackendBase <rapidsms.backends.base.BackendBase>`
                            object or dotted path to backend class.
        :returns: :class:`BackendBase <rapidsms.backends.base.BackendBase>`
                  object if found, otherwise a ``ValueError`` exception
                  will be raised.
        """
        if isinstance(module_name, string_types):
            cls = BackendBase.find(module_name)
        elif issubclass(module_name, BackendBase):
            cls = module_name
        if not cls:
            raise ValueError('No such backend "%s"' % module_name)
        config = self._clean_backend_config(config or {})
        backend = cls(self, name, **config)
        self.backends[name] = backend
        return backend

    @staticmethod
    def _clean_backend_config(config):
        """
        Return ``config`` (a dict) with the keys downcased. (This is
        intended to make the backend configuration case insensitive.)
        """

        return dict([
            (key.lower(), val)
            for key, val in config.items()
        ])

    def receive_incoming(self, msg):
        """
        All inbound messages will be routed through ``receive_incoming``
        by :func:`send <rapidsms.router.send>`. ``receive_incoming`` is
        typically overridden in child routers to customize incoming message
        handling.

        :param msg: :class:`IncomingMessage <rapidsms.messages.incoming.IncomingMessage>` object
        """
        self.process_incoming(msg)

    def process_incoming(self, msg):
        """
        Process message through incoming phases and pass any generated
        responses to :func:`send <rapidsms.router.send>`. Called by
        ``receive_incoming``.

        :param msg: :class:`IncomingMessage <rapidsms.messages.incoming.IncomingMessage>` object
        """
        from rapidsms.router import send
        continue_processing = self.process_incoming_phases(msg)
        if continue_processing:
            for msg_context in msg.responses:
                send(**msg_context)

    def process_incoming_phases(self, msg):
        """
        Route message through each phase and installed app.

        :param msg: :class:`IncomingMessage <rapidsms.messages.incoming.IncomingMessage>` object
        :returns: ``True`` if inbound processing should continue.
        """
        # Note: this method can't ever return False, but some subclass might
        # override it and use that feature.
        logger.info("Incoming (%s): %s", msg.connections, msg.text)

        try:
            for phase in self.incoming_phases:
                logger.debug("In %s phase", phase)

                if phase == "default":
                    if msg.handled:
                        logger.debug("Skipping phase")
                        break

                for app in self.apps:
                    logger.debug("In %s app", app)
                    handled = False

                    func = getattr(app, phase)
                    handled = func(msg)

                    # during the _filter_ phase, an app can return True
                    # to abort ALL further processing of this message
                    if phase == "filter":
                        if handled is True:
                            logger.warning("Message filtered")
                            raise StopIteration

                    # during the _handle_ phase, apps can return True
                    # to "short-circuit" this phase, preventing any
                    # further apps from receiving the message
                    elif phase == "handle":
                        if handled is True:
                            logger.debug("Short-circuited")
                            # mark the message handled to avoid the
                            # default phase firing unnecessarily
                            msg.handled = True
                            break

                    elif phase == "default":
                        # allow default phase of apps to short circuit
                        # for prioritized contextual responses.
                        if handled is True:
                            logger.debug("Short-circuited default")
                            break

        except StopIteration:
            pass

        return True

    def send_outgoing(self, msg):
        """
        All outbound messages will be routed through ``send_outgoing``
        by :func:`receive <rapidsms.router.receive>`. ``send_outgoing`` is
        typically overridden in child routers to customize outgoing message
        handling.

        :param msg: :class:`OutgoingMessage <rapidsms.messages.outgoing.OutgoingMessage>` object
        """
        self.process_outgoing(msg)

    def process_outgoing(self, msg):
        """Process message through outgoing phases and pass to backend(s)."""
        logger.info("Outgoing: %s", msg)
        continue_sending = self.process_outgoing_phases(msg)
        if continue_sending:
            self.backend_preparation(msg)

    def process_outgoing_phases(self, msg):
        """Process message through outgoing phases and apps."""
        for phase in self.outgoing_phases:
            logger.debug("Out %s phase", phase)
            continue_sending = True
            # call outgoing phases in the opposite order of the incoming
            # phases, so the first app called with an incoming message
            # is the last app called with an outgoing message
            for app in reversed(self.apps):
                logger.debug("Out %s app", app)
                try:
                    func = getattr(app, phase)
                    continue_sending = func(msg)
                except Exception:
                    logger.exception("Error while processing outgoing phase.")
                # during any outgoing phase, an app can return False to
                # abort ALL further processing of this message
                if continue_sending is False:
                    logger.warning("Message cancelled")
                    return False
        msg.processed = True
        return True

    def backend_preparation(self, msg):
        """
        Prepare message for backend processing. This includes grouping
        connections by backend and calling send_to_backend() with each group.
        """
        context = msg.extra_backend_context()
        grouped_identities = self.group_outgoing_identities(msg)
        for backend_name, identities in grouped_identities.items():
            try:
                self.send_to_backend(backend_name, msg.id, msg.text,
                                     identities, context)
            except MessageSendingError:
                # This exception has already been logged in send_to_backend.
                # The blocking router doesn't have a mechanism to handle
                # errors, so we simply pass here and continue routing messages.
                pass

    def group_outgoing_identities(self, msg):
        """Return a dictionary of backend_name -> identities for a message."""
        grouped_identities = defaultdict(list)
        if isinstance(msg.connections, QuerySet):
            backend_names = msg.connections.values_list('backend__name',
                                                        flat=True)
            for backend_name in backend_names.distinct():
                identities = msg.connections.filter(backend__name=backend_name)
                identities = identities.values_list('identity', flat=True)
                grouped_identities[backend_name].extend(list(identities))
        else:
            for connection in msg.connections:
                backend_name = connection.backend.name
                identity = connection.identity
                grouped_identities[backend_name].append(identity)
        return grouped_identities

    def send_to_backend(self, backend_name, id_, text, identities, context):
        """Send message context to specified backend."""
        try:
            backend = self.backends[backend_name]
        except KeyError:
            msg = "Router is not configured with the %s backend" % backend_name
            logger.exception(msg)
            raise MessageSendingError(msg)
        try:
            backend.send(id_=id_, text=text, identities=identities,
                         context=context)
        except Exception:
            msg = "%s encountered an error while sending." % backend_name
            logger.exception(msg)
            raise MessageSendingError(msg)

    def new_incoming_message(self, text, connections, class_=IncomingMessage,
                             **kwargs):
        """
        Create and return a new incoming message. Called by
        :func:`send <rapidsms.router.send>`. Overridable by child-routers.

        :param text: Message text
        :param connections: List or QuerySet of ``Connection`` objects
        :param class_: Message class to instaniate
        :returns: :class:`IncomingMessage <rapidsms.messages.incoming.IncomingMessage>` object.
        """
        return class_(text=text, connections=connections,
                      **kwargs)

    def new_outgoing_message(self, text, connections, class_=OutgoingMessage,
                             **kwargs):
        """
        Create and return a new outgoing message. Called by
        :func:`receive <rapidsms.router.receive>`. Overridable by child-routers.

        :param text: Message text
        :param connections: List or QuerySet of ``Connection`` objects
        :param class_: Message class to instaniate
        :returns: :class:`OutgoingMessage <rapidsms.messages.outgoing.OutgoingMessage>` object.
        """
        return class_(text=text, connections=connections, **kwargs)

    def incoming(self, msg):
        """Legacy support for Router.incoming() -- Deprecated"""
        msg = "Router.incoming is deprecated. Please use receive_incoming."
        warnings.warn(msg, DeprecationWarning)
        self.receive_incoming(msg)

    def outgoing(self, msg):
        """Legacy support for Router.outgoing() -- Deprecated"""
        msg = "Router.outgoing is deprecated. Please use send_outgoing."
        warnings.warn(msg, DeprecationWarning)
        self.send_outgoing(msg)
