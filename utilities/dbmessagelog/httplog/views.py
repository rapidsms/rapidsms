#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
import time
import logging
import urllib, urllib2
from datetime import datetime

from models import *

def api(request, url, timeout=30, interval=.5):
    # support parameters from either posts or gets
    if request.method == 'POST':
        dict = request.POST
    else: 
        dict = request.GET
    
    # this is the format we are expecting from mtech.  
    # ?text=message body&from=2347067277331&sent=unix-time
    # so parse the params out from the url
    
    text = dict.get("text")
    date_string = dict.get("sent")
    phone = dict.get("from")
    if text and phone:
        # make sure we url decode the body
        text = urllib.unquote(text)
        
        # try to parse out the date from what was passed in
        # but default to now() if anything goes wrong
        if date_string:
            try:
                date = datetime.fromtimestamp(int(date_string))
            except Exception:
                date = datetime.now()
        else:
            date = datetime.now()
            
        # save the message to the incoming db queue
        msg = IncomingMessage.objects.create(phone=phone, text=text, time=date, status="R")
        
        # wait for a while for the message to be processed by rapid sms
        handled = False
        countdown = timeout
        while not handled and countdown > 0:
            msg = IncomingMessage.objects.get(id = msg.id)
            if msg.processed:
                # aha!  rapidsms has set this flag and finished processing
                handled = True
                break
            else:
                # wait a short time before checking
                # again, to avoid pegging the cpu
                countdown -= interval
                #print "sleeping... %s" % countdown
                time.sleep(interval)
        
        # it was successfully handled by rapid sms
        # gather any responses and put them in the response body
        if handled:
            # get a list of the replies we want to send
            # and concatenate them, or respond with a 
            # generic success message
            responses = [response.text for response in msg.responses.all()]
            if responses:
                response_text = ". ".join(responses)
            else: 
                response_text = "Thanks for your message!"
            
            # mark the message as processed
            msg.status = "P"
            msg.save()
            
            # send the response messages in the body of the
            # http response 
            return HttpResponse(response_text)
        else:
            logging.warn("Router timed out while processing incoming message")
            
            # set the status to timeout, in case we 
            # want to differentiate these later 
            msg.status = "T"
            msg.save()
            # respond with a generic partial error message
            return HttpResponse("Thanks for your message.  We are having technical difficulties preventing us from responding properly, but we got it.")
    else:
        # we can't handle something if we don't have a number or a body
        # todo: something better than this?
        return HttpResponse("Must set a phone number and a message body!  You sent phone: %s, body: %s" %(phone,text))
