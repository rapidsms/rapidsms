#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import re
import __builtin__

class App(rapidsms.app.App):
    class Session (dict):
        def __init__ (self, *args, **kwargs):
            self.cleanup()
            dict.__init__(self, *args, **kwargs)

        def prepare (self, temps):
            self.temps = temps

        def cleanup (self):
            self.temps = {}

        def __getitem__ (self, key):
            if key in self.temps:
                return self.temps[key]
            if hasattr(__builtin__, key):
                return getattr(__builtin__, key)
            if key not in self:
                self[key] = None
            return dict.__getitem__(self,key)

    def configure (self, cfg="apps/ezsms/ezsms.cfg"):
        self.file = cfg

    def start(self):
        self.sessions = {}
    
    def parse(self, msg):
        if msg.connection.identity not in self.sessions:
            self.sessions[msg.connection.identity] = self.Session()
    
    def handle(self, msg):
        sections = self.load()
        self.debug("available: %r", sections.keys())
        cmd = text = args = None
        for section in sections.keys():
            regex = re.compile(section, re.I)
            match = re.search(regex, msg.text)
            if match:
                cmd = section
                text = re.sub(regex, "", msg.text).strip()
                args = match.groups()
                break
        if not cmd: return
        if not args: args = filter(None, text.split())
        self.debug("cmd: %s, args: %r", cmd, args)
        session = self.sessions[msg.connection.identity]
        session.prepare({
            'caller': msg.connection.identity,
            'text': text,
            'args': args,
            'respond': msg.respond,
            'info': self.info,
            'debug': self.debug,
        })
        self.debug("session before: %r", sorted(session.keys()))
        try:
            code = compile(sections[cmd], cmd, 'exec')
            eval(code, globals(), session)
        except Exception, e:
            self.error("%s section raised %r", cmd, e)
        finally:
            session.cleanup()
        self.debug("session after: %r", sorted(session.keys()))

    def load (self):
        cfg = file(self.file)
        sections = {}
        current = None
        indent = 0
        for line in cfg.readlines():
            if re.match("\s*#",line): continue #comment
            heading = re.match(r"^(\S[^:]+):$", line)
            if heading:
                current = heading.group(1).strip()
                sections[current] = ""
                indent = 0
                continue
            if current:
                if indent == 0 and line.strip() != "":
                    while line[indent].isspace():
                        indent += 1
                sections[current] += line[indent:]
        return sections
