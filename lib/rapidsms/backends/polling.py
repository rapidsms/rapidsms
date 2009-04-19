#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time
from rapidsms.backends import Backend
from rapidsms.message import Message
from utilities.dbmessagelog.httplog.models import * 
from datetime import datetime

class Backend(Backend):
    def configure(self, interval=2, timeout=10):
        self.interval = interval
        self.timeout = timeout

    def run(self):
        while self.running:

            # look for any new incoming messages
            # in the database, and route them
            for incoming_msg in IncomingMessage.objects.filter(status="R"):
                incoming_msg.status = "H"
                incoming_msg.save()
                msg = self.message(incoming_msg.phone, incoming_msg.text, incoming_msg.time)
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
                    countdown -= timestep
                    time.sleep(timestep)

                # mark the message, so we don't
                # receive it again next time
                if msg.processed:
                    incoming_msg.status = "P"
                    incoming_msg.save()

                else:
                    # TODO: should we do anything other than warn, here?
                    #self.warn("Router timed out while processing incoming message")
                    pass 
            # wait a few seconds
            # before polling again
            time.sleep(self.interval)

    def send(self, msg):
        outgoing = OutgoingMessage(
            phone = msg.connection.identity,
            time = datetime.now(),
            text = msg.text,
            status = "R"
        )
        outgoing.save()
        try: 
            # if this is a response then we we need a handle 
            # to the original message we are responding to.
            # As a first pass, assume that there is only one message
            # per person in the "handle" phase and we just look it 
            # up in the db
            original_msg = IncomingMessage.objects.get(status="H", phone=msg.connection.identity)
            original_msg.responses.add(outgoing)
            original_msg.save()
        except IncomingMessage.DoesNotExist:
            # this might just be a standard outgoing message 
            # so don't do anything special
            pass
        
        