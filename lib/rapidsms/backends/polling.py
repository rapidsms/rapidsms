#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time
from rapidsms.backends import Backend
from rapidsms.message import Message


class Backend(Backend):
    def configure(self, interval=2, timeout=10):
        self.interval = interval
        self.timeout = timeout

    def run(self):
        while self.running:

            # look for any new incoming messages
            # in the database, and route them
            for msg in IncomingMessage.objects.filter(processed=False):
                msg = self.message(msg.sender, msg.text, msg.date)
                self.route(msg)

                # pause until the msg.processed
                # flag is set, to indicate that
                # rapidsms is done with it
                timestep = 0.5
                countdown = self.timeout
                while countdown > 0:
                    if msg.processed:
                        break

                    # wait a short time before checking
                    # again, to avoid pegging the cpu
                    countdown -= timeout
                    time.sleep(timeout)

                # mark the message, so we don't
                # receive it again next time
                if msg.processed:
                    msg.processed = True
                    msg.save()

                else:
                    # TODO: should we do anything other than warn, here?
                    self.warn("Router timed out while processing incoming message")

            # wait a few seconds
            # before polling again
            time.sleep(self.interval)

    def send(self, msg):
        OutgoingMessage(
            sender = msg.connection.identity,
            date = time.time(),
            text = msg.text
        ).save()
