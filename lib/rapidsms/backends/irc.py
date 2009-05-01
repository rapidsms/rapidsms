import irclib

import rapidsms
from rapidsms.message import Message
from rapidsms.connection import Connection

class Backend(rapidsms.backends.Backend):
    def configure(self, host="irc.freenode.net", port=6667,
                        nick=None, channels=["#rapidsms"]):
        self.host = host
        self.port = port
        self.nick = self.config_requires("nick",nick)[:16] # 16 char limit for IRC nicks
        self.channels = self.config_list(channels)

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
            target = msg.connection.identity
        response = "%s: %s" % (msg.connection.identity, msg.text)
        self.info("sending to %s: %s", target, response)
        self.server.privmsg(target, response)

    def pubmsg (self, connection, event):
        self.debug("%s -> %s: %r", event.source(), event.target(), event.arguments())
        try:
            nick, txt = map(str.strip, event.arguments()[0].split(":"))
        except ValueError:
            return # not for me
        nick = nick.split("!")[0]
        if nick == self.nick:
            self.info("routing public message from %s", event.source())
            c = Connection(self, event.source().split("!")[0])
            msg = self.message(c.identity, txt)
            msg.irc_channel = event.target()
            self.route(msg)

    def privmsg (self, connection, event):
        self.debug("%s -> %s: %r", event.source(), event.target(), event.arguments())
        if event.target() == self.nick:
            self.info("routing private message from %s", event.source())
            c = Connection(self, event.source().split("!")[0])
            msg = self.message(c.identity, event.arguments()[0])
            msg.irc_channel = c.identity
            self.route(msg)
