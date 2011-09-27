from .base import BaseRouter


class BlockingRouter(BaseRouter):
    """ Simple router that blocks while sending and receiving messages """

    def incoming(self, msg):
        # process incoming phases
        super(BlockingRouter, self).incoming(msg)
        # handle message responses from within router
        for response in msg.responses:
            self.outgoing(response)

    def outgoing(self, msg):
        # process outgoing phase
        super(BlockingRouter, self).outgoing(msg)
        # send message from within router
        self.sent = self.backends[msg.connection.backend.name].send(msg)
        msg.sent = self.sent
