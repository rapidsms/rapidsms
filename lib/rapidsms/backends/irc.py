import irclib

import rapidsms
from rapidsms.message import Message

class Backend(rapidsms.backends.Backend):
    def __init__(self, router, host="irc.freenode.net", port=6667,
                 nick="rapidsms", channels=["#rapidsms"]):
        rapidsms.backends.Backend.__init__(self,router)
        self.type = "IRC"
        self.host = host
        self.port = port
        self.nick = nick
        self.channels = channels

        self.irc = irclib.IRC()
        self.irc.add_global_handler("privmsg", self.privmsg)
        self.irc.add_global_handler("pubmsg", self.pubmsg)
        
    def run (self):
        self.info("Connecting to %s as %s", self.host, self.nick)
        self.server = self.irc.server()
        self.server.connect(self.host, self.port, self.nick)

        for channel in self.channels:
            self.info("Joining %s on %s", channel, self.host)    
            self.server.join(channel)

        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                self.outgoing(msg)
            self.irc.process_once(timeout=1.0)

        self.info("Shutting down...")
        self.server.disconnect()

    def outgoing (self, msg):
        try:
            channel = msg.irc_channel
        except AttributeError:
            channel = self.channels[0]
        if channel:
            target = channel
        else:
            target = msg.caller
        response = "%s: %s" % (msg.caller, msg.text)
        self.info("sending to %s: %s", target, response)
        self.server.privmsg(target, response)

    def pubmsg (self, connection, event):
        self.info("%s -> %s: %r", event.source(), event.target(), event.arguments())
        try:
            nick, txt = map(str.strip, event.arguments()[0].split(":"))
        except ValueError:
            return # not for me
        nick = nick.split("!")[0]
        if nick == self.nick:
            self.info("routing public message from %s", event.source())
            caller = event.source().split("!")[0]
            msg = self.message(caller, txt)
            msg.irc_channel = event.target()
            self.route(msg)

    def privmsg (self, connection, event):
        self.info("%s -> %s: %r", event.source(), event.target(), event.arguments())
        if event.target() == self.nick:
            self.info("routing private message from %s", event.source())
            caller = event.source().split("!")[0]
            msg = self.message(caller, event.arguments()[0])
            msg.irc_channel = caller
            self.route(msg)
