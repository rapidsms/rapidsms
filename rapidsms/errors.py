#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class MessageSendingError(Exception):
    """
    This exception is raised when an outgoing message cannot be sent.
    Where possible, a more specific exception should be raised, along
    with a descriptive message.
    """
    def __init__(self, message='An error occurred during sending.', failed_identities=None):
        # list of failed identities can optionally be attached
        self.failed_identities = failed_identities or []
        super(MessageSendingError, self).__init__(message)


class NoRouterError(MessageSendingError):
    """
    This exception is raised when no Router is available to send an
    outgoing message. This usually means that it is being sent from the
    webui process(es), which is not currently possible in RapidSMS.
    """


class NoConnectionError(MessageSendingError):
    """
    This execption is raised when a Contact cannot be messaged because
    they do not have any Connections.
    """
