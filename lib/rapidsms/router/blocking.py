import copy

from django.conf import settings

from .base import BaseRouter


class BlockingRouter(BaseRouter):
    """ Simple router that blocks while sending and receiving messages """

    def __init__(self, *args, **kwargs):
        """
        Apps and backends are added manually to the blocking backend.
        """
        apps = kwargs.pop('apps', settings.INSTALLED_APPS)
        backends = kwargs.pop('backends', settings.INSTALLED_BACKENDS)
        super(BlockingRouter, self).__init__(*args, **kwargs)
        for name in apps:
            try:
                self.add_app(name)
            except Exception as e:
                self.exception(e)
        for name, conf in backends.iteritems():
            parsed_conf = copy.copy(conf)
            engine = parsed_conf.pop('ENGINE')
            self.add_backend(name, engine, parsed_conf)
        self.start()  # legacy

    def receive_incoming(self, msg):
        # process incoming phases
        super(BlockingRouter, self).receive_incoming(msg)
        # handle message responses from within router
        for response in msg.responses:
            self.send_outgoing(response)
