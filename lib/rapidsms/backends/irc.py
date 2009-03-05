from backend import Backend
from rapidsms.message import Message

class Irc(Backend):
    def __init__(self, router, host="irc.freenode.net", port=6667,
                 nick="rapidsms", channels=["#rapidsms"]):
        super(Backend,self).__init__(router)
        self.host = host
        self.port = port
        self.nick = nick
        self.channels = channels

        self.irc = irclib.IRC()
        self.irc.add_global_handler("privmsg", self.privmsg)
        
    def run (self):
        self.server = irc.server()
        self.server.connect(self.host, self.port, self.nick)
        for channel in channels:
            self.server.join(channel)

        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                # oops we have to throw the message away
            self.irc.process_once(timeout=1.0)

    def privmsg (self, connection, event):
        self.info("%s -> %s: %r", event.source, event.target, event.arguments)
        try:
            nick, txt = map(str.strip, event.arguments[0].split(":"))
        except ValueError:
            nick, txt = None, event.arguments[0]
        if event.target == self.nick or nick == self.nick:
            self.info("routing message from %s", event.source)
            msg = self.message(event.source, txt)
            msg.irc_event = event
            self.route(msg)

