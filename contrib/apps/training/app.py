import rapidsms
import threading
from training.models import *
from rapidsms.message import Message, StatusCodes
from rapidsms.connection import Connection
import time

class App (rapidsms.app.App):
    '''The training app saves error messages in a queue before they go out
       and waits for someone to either flag them as "ready to go out" or
       override the default response by adding their own.  This is meant
       to be used in trainings, to provide live feedback via SMS''' 
    
    PRIORITY = "last"
    
    
    def ajax_GET_pending_count(self, params):
    	
    	# returns JUST the number of messages in waiting, which
    	# indicates whether anyone is waiting for attention
    	return MessageInWaiting.objects.filter(status="P").count()
    
    
    def ajax_GET_pending(self, params):

        # return all of the messages in waiting,
        # each of which contain their responses
        return MessageInWaiting.objects.filter(status="P")
    
    
    def ajax_POST_accept(self, params, form):
        msg = MessageInWaiting.objects.get(pk=int(form["msg_pk"]))
        
        # there might be one response, or there
        # might be many -- make it iterable
        responses = form.get("responses", [])
        if not type(responses) == list:
            responses = [responses]

        for resp in responses:
            
            # if this response was present in the original
            # set, and remains unchanged, just "confirm" it
            originals = msg.responses.filter(text=resp, type="O")
            if len(originals):
                originals[0].type = "C"
                originals[0].save()
            
            # this response is new, or changed!
            # create a new ResponseInWaiting object
            else:
                ResponseInWaiting(
                    originator=msg,
                    text=resp,
                    type="A").save()
        
        # find any remaining original responses, which
        # were removed in the webui, and delete them
        msg.responses.filter(type="O").delete()
        
        # mark the incoming message as "handled", so
        # it will be picked up by the responder_loop
        msg.status = "H"
        msg.save()
        
        # TODO: send something more useful
        # back to the browser to confirm
        return True




    def start (self):
        """Configure your app in the start phase."""
        # Start the Responder Thread -----------------------------------------
        
        self.info("[responder] Starting up...")
        # interval to check for responding (in seconds)
        response_interval = 10
        # start a thread for responding
        responder_thread = threading.Thread(
                target=self.responder_loop,
                args=(response_interval,))
        responder_thread.daemon = True
        responder_thread.start()
        
    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def cleanup (self, message):
        if (self._requires_action(message)):
            # create the message in waiting object and response
            # in waiting objects for this, and assume someone will
            # deal with them.  
            # This app should never be running in a production environment
            # unless someone is very carefully tracking the incoming messages
            self.info("Queueing up %s for further handling" % message)
            in_waiting = MessageInWaiting.from_message(message)
            in_waiting.save()
            for response in message.responses:
                resp_in_waiting = ResponseInWaiting.objects.create(type='O', originator=in_waiting,text=response.text)
            
            # blank out the responses, they will be sent by the responder thread
            # after moderation
            message.responses = []

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass

    
    def _requires_action(self, message):
        # this message requires action if and only if
        # 1. No response is indicated "ok"
        #   "ok" by any app should override any other errors 
        # 2. Some message is indicated "app error" or "generic errror"
        #   "none" is the default, and we haven't updated every app to correctly
        #   say "ok" on real responses, so only do this for known errors
        to_return = False
        for response in message.responses:
            if response.status == StatusCodes.OK:
                return False
            elif response.status == StatusCodes.APP_ERROR or response.status == StatusCodes.GENERIC_ERROR:
                to_return = True
        return to_return
    
    # Responder Thread --------------------
    def responder_loop(self, seconds=10):
        self.info("Starting responder...")
        while True:
            # look for any new handled messages
            # in the database, and send the responses
            for msg_in_waiting in MessageInWaiting.objects.filter(status="H"):
                self.info("Responding to %s.", msg_in_waiting)
                for response in msg_in_waiting.responses.all():
                    self.info("Response: %s.", response)
                    # only send confirmed or added responses
                    if response.type != "O":
                        db_connection = msg_in_waiting.get_connection()
                        if db_connection is not None:
		                      db_backend = db_connection.backend
		                      # we need to get the real backend from the router 
		                      # to properly send it 
		                      real_backend = self.router.get_backend(db_backend.slug)
		                      if real_backend:
		                          connection = Connection(real_backend, db_connection.identity)
		                          response_msg = Message(connection, response.text)
		                          self.router.outgoing(response_msg)
		                      else:
		                          # TODO: should we fail harder here?  This will permanently
		                          # disable responses to this message which is bad.  
		                          self.error("Can't find backend %s.  Messages will not be sent")
                # mark the original message as responded to
                msg_in_waiting.status="R"
                msg_in_waiting.save()
            # wait until it's time to check again
            time.sleep(seconds)

