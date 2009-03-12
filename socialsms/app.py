#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
from rapidsms.message import Message
from rapidsms.parsers.keyworder import * 

class App(rapidsms.app.App):

    kw = Keyworder()

    def start(self):
        self.people = {}
        self.backends = {}
        self.groups = {}

    def parse(self, message):
        pass 

    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                except Exception, e:
                    # nothing was found, use default handler
                    self.debug('No keyworder match')
            else:
                self.debug('App has not instantiated Keyworder as kw')
        except Exception, e:
            self.error(e) 


    def outgoing(self, message):
        pass 


    def __identify(self, message, task=None):
        # if the caller is not yet identified, then
        # send a message asking them to do so, and
        # stop further processing
        if not self.people.has_key(message.caller):
            err = "You must identify yourself"
            if task: 
                err += " before %s" % (task)
                message.respond(err)
        
        return self.people[message.caller]


    # everything that we pass around (identities and
    # group names, for now) must be short and upper,
    # to keep things simple for texters
    def __slug(self, str):
        return str[:10].upper()
    
    
    # slugize a string, and check that it's a
    # valid (already existing) group name
    def __group(self, str):
        grp = self.__slug(str)
        if not self.groups.has_key(grp):
            err = "There is no %s group" % (grp)
            #raise CallerError(err)
        return grp
    
    
    # HELP
    @kw("help")
    def help(self, message):
        message.respond([
            "join <GROUP>",
            "leave <GROUP>",
            "identify <NAME>",
            "list my groups",
            "list groups",
            "list members of <GROUP>",
            "<GROUP> <MESSAGE>"])
    
    
    # LIST GROUPS
    @kw("list (my )?groups")
    def list_groups(self, message, my_groups=None):
        group_names = []
        
        # collate groups to list into a
        # flat list of slugized names
        for g in self.groups.keys():
            member = message.caller in self.groups[g]
            
            # include this group if we are listing ALL
            # groups, OR we are already a member of it
            # (also add a star to denote groups
            # which the caller is a member of)
            if member or not my_groups:
                if not my_groups and member: g += "*"
                group_names.append(g)
        
        # if there is nothing to return, then abort
        if not len(group_names):
            if my_groups: message.respond("You are not a member of any groups")
            else:         message.respond("No groups have been created yet")
            
        else:
            # return a list of [your|all] groups
            capt = my_groups and "Your groups" or "Groups"
            msg = "%s: %s" % (capt, ", ".join(group_names))
            message.respond(msg) 
    
    # LIST MEMBERS OF <GROUP>
    @kw("list members of (letters)")
    def list_members_of_group(self, message, grp):
        ident = self.__identify(message, "making queries")
        grp = self.__group(grp)
        # collate the names of the members of this group
        # with a very ugly list comprehension, and send
        # TODO this doesnt work now that identify takes
        # messages rather than callers
        #member_names = [self.__identify(p) for p in self.groups[grp]]
        #msg = "Members of %s: %s" % (grp, ", ".join(member_names))
        #message.respond(msg) 
        message.respond('Sorry, this feature is not currently available')
    
    # JOIN <GROUP>
    @kw("join (letters)")
    def join(self, message, grp):
        ident = self.__identify(message, "joining groups")
        grp = self.__slug(grp)
        
        # create the group if it
        # doesn't already exist
        if not self.groups.has_key(grp):
            self.groups[grp] = []
        
        # is the caller already in this group?
        if message.caller in self.groups[grp]:
            err = "You are already a member of the %s group" % (grp)
            message.respond(err)
            
        else:
            # join the group and notify
            self.groups[grp].append(message.caller)
            msg = "You have joined the %s group" % grp
            message.respond(msg) 
    
    # LEAVE <GROUP>
    @kw("leave (letters)")
    def leave(self, message, grp):
        grp = self.__group(grp)
        
        # callers can only send messages to groups which they are members of
        if not message.caller in self.groups[grp]:
            err = "You are not a member of the %s group" % (grp)
            message.respond(err)
        
        self.groups[grp].remove(message.caller)
        msg = "You have left the %s group" % grp
        message.respond(msg) 
    
    # IDENTIFY <NAME>
    @kw("identify (letters)", "my name is (letters)", "i am (letters)")
    def identify(self, message, name):
        name = self.__slug(name)
        self.backends[message.caller] = message.backend
        self.people[message.caller] = name
        reply = 'Your name is now "%s"' % name
        message.respond(reply)

    # <GROUP> <MESSAGE>
    @kw("(letters) (.+)")
    def to_group(self, message, grp, rest):
        ident = self.__identify(message, "posting")
        grp = self.__group(grp)
        
        # check that the caller is a member of
        # the group to which we are broadcasting
        if not message.caller in self.groups[grp]:
            err = "You are not a member of the %s group" % (grp)
            message.respond(err)
        
        # keep a log of broadcasts
        self.info("Sending to group: %s" % grp)
        
        # iterate every member of the group we are broadcasting
        # to, and queue up the same message to each of them
        msg = "[%s] %s: %s" % (grp, ident, rest)
        for dest in self.groups[grp]:
            if dest != message.caller:
                Message(self.backends[dest], dest, msg).send()
        
        # notify the caller that his/her message was sent
        people = len(self.groups[grp]) - 1
        msg = "Your message was sent to the %s group (%d people)" % (grp, people)
        message.respond(msg) 
