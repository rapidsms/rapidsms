#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
from models import *

class App(rapidsms.app.App):
    def start(self):
        self.callers = {}
    
    def configure(self, last_message="There are no more questions.", **kwargs):
        self.last_message = last_message
    
    def handle(self, msg):
        
        # if this caller doesn't have a "question" attribute,
        # they're not currently answering a question tree, so
        # just search for triggers and return
        if not msg.caller in self.callers:
            try:
                self.callers[msg.caller] =\
                    Tree.objects.get(trigger=msg.text).root_question
            
            # no trigger found? no big deal. the
            # message is probably for another app
            except Tree.DoesNotExist:
                return False
        
        # the caller is part-way though a question
        # tree, so check their answer and respond
        else:
            try:
                q = self.callers[msg.caller]
                answer = Answer.objects.get(
                    previous_question=q,
                    trigger=msg.text)
            
            # not a valid answer, so remind
            # the user of the valid options.
            except Answer.DoesNotExist:
                answers = Answer.objects.filter(previous_question=q)
                flat_answers = ", ".join([ans.trigger for ans in answers])
                msg.respond('"%s" is not a valid answer. Pick one of: %s' % (msg.text, flat_answers))
                return True
            
            # if this answer has a response, send it back to the user
            # before doing anything else. this means that they might
            # receive two messages (this, and the next question), but
            # avoids having to concatenate them.
            if answer.response:
                msg.respond(answer.response)
            
            # advance to the next question, or remove
            # this caller's state if there are no more
            if answer.next_question:
                self.callers[msg.caller] =\
                    answer.next_question
                
            else:
                del self.callers[msg.caller]
                
                # sent the LAST_MESSAGE to end the conversation,
                # unless the last question triggered a response
                if not answer.response:
                    msg.respond(self.last_message)
        
        # if there is a next question ready to ask
        # (and this includes THE FIRST), send it along
        if msg.caller in self.callers:
            q = self.callers[msg.caller]
            msg.respond(q.text)
            self.info(q.text)
        
        # if we haven't returned long before now, we're
        # long committed to dealing with this message
        return True
