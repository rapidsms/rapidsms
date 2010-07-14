#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from ..models import Connection
from .base import BackendBase

from ..utils.modules import try_import
irclib = try_import('irclib')


class Backend(BackendBase):

    def __init__(self, *args, **kwargs):
        BackendBase.__init__(*args, **kwargs)

        if irclib is None:
            raise ImportError(
                "The rapidsms.backends.irc engine is not available, " +
                "because 'irclib' is not installed.")

    def configure(self, host="irc.freenode.net", port=6667,
                        nick=None, channels=["#rapidsms"], *kwargs):
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
