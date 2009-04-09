#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import date, datetime
from strings import ENGLISH as STR

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import rapidsms
from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.parsers.keyworder import * 

# import poll-specific models as p because
# poll has a Message class of its own...
import models as p
import graph
import utils

class App(rapidsms.app.App):

    # lets use the Keyworder parser!
    kw = Keyworder()

    def parse(self, message):
        self.handled = False 


    def handle(self, message):
        try:
            if hasattr(self, "kw"):
                try:
                    # attempt to match tokens in this message
                    # using the keyworder parser
                    func, captures = self.kw.match(self, message.text)
                    func(self, message, *captures)
                    # short-circuit handler calls because 
                    # we are responding to this message
                    return self.handled 
                except Exception, e:
                    # TODO only except NoneType error
                    # nothing was found, use default handler
                    self.incoming_entry(message)
                    return self.handled 
            else:
                self.debug("App does not instantiate Keyworder as 'kw'")
        except Exception, e:
	    # TODO maybe don't log here bc any message not meant
	    # for this app will log this error
	    #
            # self.error(e) 
	    pass


    def outgoing(self, message):
        pass 

    # HELP
    @kw("help")
    def help(self, message):
        message.respond([
            "subscribe",
            "unsubscribe"])
    
    
    def __get(self, model, **kwargs):
        try:
            # attempt to fetch the object
            return model.objects.get(**kwargs)
        
        # no objects or multiple objects found (in the latter case,
        # something is probably broken, so perhaps we should warn)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None

    # SUBSCRIBE ---------------------------------------------------------------
    
    kw.prefix = ["subscribe", "join"]

    @kw.blank()
    @kw("(whatever)")
    def subscribe(self, message, blah=None):
        r, created = p.Respondant.subscribe(str(message.connection))
        
        # acknowledge with an appropriate message
        if created: message.respond(STR["subscribe"])
        else: message.respond(STR["resubscribe"])
    
    
    # UNSUBSCRIBE -------------------------------------------------------------
    
    kw.prefix = ["unsubscribe", "leave", "stop", "exit"]

    @kw.blank()
    @kw("(whatever)")
    def unsubscribe(self, message, blah=None):
        r, created = p.Respondant.unsubscribe(message.connection)
        message.respond(STR["unsubscribe"])
	self.handled = True

    # SUBMIT AN ANSWER --------------------------------------------------------

    def incoming_entry(self, message):
        # make a poll.Message out of the rapidsms.models.Message
        # because utils.parse_message expects a poll.Message
        mess = p.Message.objects.create(is_outgoing=False,\
            connection=str(message.connection), text=message.text)

        # ensure that the caller is subscribed
        r, created = p.Respondant.subscribe(str(message.connection))
        # if no question is currently running, then
        # we can effectively ignore the incoming sms,
        # but should notify the caller anyway
        ques = p.Question.current()
        if ques is None: 
	    message.respond(STR["no_question"])
	    self.handled = True
        
        # try to parse the message
        # pass along the rapidsms.models.Message.backend with the
        # poll.Message object so that parse_message can check that
        # the respondant is subscribed
        parsed = utils.parse_message(mess, ques)

        # send an appropriate response to the caller
        if parsed:  
            graph.graph_entries(ques)
            message.respond(STR["thanks"])
	    self.handled = True

        else:       
	    message.respond(STR["thanks_unparseable"])
	    self.handled = True

	# BROADCAST FUNCTIONS ----------------------------------------------------------
	
	def broadcast_question(question):

		# gather active respondants
		respondants = p.Respondant.objects.filter(is_active=True)
		sending = 0

		# message to be blasted
		broadcast = question.text

		# unless this is a free text question,
		# add the answer choices to the broadcast message
		if question.type != 'F':
			answers = p.Answer.objects.filter(question=question.pk)
			for a in answers:
				broadcast = broadcast + '\n ' + a.choice + ' - ' + a.text

		# blast the broadcast message to our active respondants
		# and increment the counter
		for r in respondants:
			r.connection.backend.send(r.connection.identity, broadcast)
			sending += 1
			self.info('[broadcaster] Blasted to %d of %d numbers...' % (sending, len(respondants)))

		# save number broadcasted to db
		question.sent_to = sending
		question.save()

		return '[broadcaster] Blasted %s to %d numbers with %d failures' % \
				(broadcast, sending, (len(respondants) - sending))


	def broadcaster(seconds=60, wake_hour=8, sleep_hour=21):
		self.info("Starting Broadcaster...", "init")
		while True:
			
			# only broadcast while people are awake. otherwise, we'll be sending
			# people messages at 12:01AM, which probably won't go down so well
			hour = time.localtime()[3]
			if wake_hour < hour < sleep_hour:
				
				# if the current question has not been sent,
				# broadcaster will broadcast it
				q = p.Question.current()
				if q:
				
					# if this question hasn't been 'sent_to' anyone yet,
					# we can assume that it should be broadcast now
					if not q.sent_to:
						self.info("Broadcasting new question")
						broadcast_question(q)
					
					# already sent, so we have nothing to do
					# i don't think we really need to log this...
					#else: app.log("Current question was already broadcast")
					else: pass
				
				# when in production, there should probably ALWAYS
				# be an active question; otherwise, anyone texting
				# in will receive an error -- so highlight this
				# as a warning in the screen log
				else: self.info("No current question", "warn")
			
			# we are outside of waking hours, so do nothing
			else:
				self.info("Broadcast disabled from %d:00 to %d:00" %\
						(sleep_hour, wake_hour))
			
			# wait until it's time
			# to check again (60s)
			time.sleep(seconds)

	# BROADCAST THREAD -------------------------------------------------------------

	self.info("[broadcaster] Starting up...")

	# interval to check for broadcasting (in seconds)
	broadcast_interval = 30
	# start a thread for broadcasting
	thread.start_new_thread(broadcaster, (broadcast_interval,))
