#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import BaseHTTPServer
import random
import re
import urllib, urllib2
from datetime import datetime

def _uni(str):
    """
    Make inbound a unicode str
    Decoding from utf-8 if needed

    """
    try:
        return unicode(str)
    except:
        return unicode(str,'utf-8')

def _str(uni):
    """
    Make inbound a string
    Encoding to utf-8 if needed

    """
    try:
        return str(uni)
    except:
        return uni.encode('utf-8')

class RapidBaseHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''The base handler for use in the http backends.  This is a
       simple extension of the python builtin handlers with
       logging capabilities and a utility method for responding
       to incoming requests.'''

    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(_str(msg))

    
class HttpHandler(RapidBaseHttpHandler):
    '''The original http handler, used by the httptester app.
       URLS are /PhoneNumber/Message'''
    
    msg_store = {}
    
    def do_GET(self):
        # if the path is just "/" then start a new session
        # and redirect to that session's URL
        if self.path == "/":
            session_id = random.randint(100000, 999999)
            self.send_response(301)
            self.send_header("Location", "/%d/" % session_id)
            self.end_headers()
            return
        
        # if the path is of the form /integer/blah 
        # send a new message from integer with content blah
        send_regex = re.compile(r"^/(\d+)/(.*)")
        match = send_regex.match(self.path)
        if match:
            # send the message
            session_id = match.group(1)
            text = _str(match.group(2))
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if HttpHandler.msg_store.has_key(session_id) and len(HttpHandler.msg_store[session_id]):
                    resp=_str("{'phone':'%s', 'message':'%s'}" % (session_id, HttpHandler.msg_store[session_id].pop(0).replace("'", r"\'")))
                    self.wfile.write(resp)
                return
            
            # get time
            received = datetime.utcnow()
            # leave Naive!
            # received.replace(tzinfo=pytz.utc)
            
            msg = self.server.backend.message(
                session_id, 
                urllib.unquote(text),
                date=received
                )

            self.server.backend.route(msg)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_str("{'phone':'%s', 'message':'%s'}" % (session_id, urllib.unquote(text).replace("'", r"\'"))))
            return
            
        return
        
    def do_POST(self):
        # TODO move the actual sending over to here
        return
    
    @classmethod
    def outgoing(klass, msg):
        '''Used to send outgoing messages through this interface.'''
        #self.log_message("http outgoing message: %s" % message)
        # the default http backend just stores outgoing messages in
        # a store and provides access to them via the JSON/AJAX 
        # interface
        if HttpHandler.msg_store.has_key(msg.connection.identity):
            HttpHandler.msg_store[msg.connection.identity].append(_str(msg.text))
        else:
            HttpHandler.msg_store[msg.connection.identity] = []
            HttpHandler.msg_store[msg.connection.identity].append(_str(msg.text))
                
class MTechHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the mtech gateway, for use in Nigeria'''
    def do_GET(self):
        querystart = self.path.find("?")
        if querystart == -1:
            self.respond(500, "Must specify parameters in the URL!")
            return
        
        query_params = map((lambda t: t.split("=")), self.path[querystart + 1:].split("&"))
        
        self.accept_message(query_params)
        
        
    def do_POST(self):
        if self.rfile:
            content_len = int(self.headers["Content-Length"])
            data = self.rfile.read(content_len)
            params = map((lambda t: t.split("=")), data.split("&"))
            self.accept_message(params)
    
    def accept_message(self, params):
        # parameters are: 
        # text=message%20body
        # from=2347067277331
        # sent=200904091443.21
        # mtech_received=200904091444.48
        # operator_received=200904091444.4
        
        text = None
        sender = None
        date = None
        for key,val in params:
            if key == "text":
                # TODO watch out because urllib.unquote will blow up on unicode text 
                text = _str(text)
                text = urllib.unquote(val)
                text = _uni(text)
            elif key == "from":
                sender = val
            elif key == "sent":
                date = datetime.strptime(val, "%Y%m%d%H%M.%S")
        
        if text and sender: 
            # respond with the number and text 
            msg = self.server.backend.message(text, sender, date)
            self.server.backend.route(msg)
            self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, _str(text)))
            return
        else:
            self.respond(500, "You must specify a valid number and message")
            return

    def outgoing(self, message):
        '''An HttpHandler for the mtech gateway, for use in Nigeria'''
        self.log_message("Mtech outgoing message: %s" % message)


class End2EndHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the End2End mobile gateway'''  
    
    # This is the format of the post string
    # http://www.ihredomain.de/smsparser.cgi?snr=%2B491721234567&dnr=%2B491781234567&smsc=%2b491722170000&msg=Anfrage+per+SMS&tdif=15&nc=62F270
    # snr: originator address code
    # dnr: number of the solicited SMS-Inbound port
    # smsc: number of the employed short message service center (optional)
    # msg: short message text
    # tdif: difference between actual time and timestamp of message
    # nc: Networkcode MCC/MNC (optional)
    
    param_text = "msg"
    param_sender = "snr"
    
    outgoing_url = "http://gw1.promessaging.com/sms.php"
    backup_outgoing_url = "http://gw2.promessaging.com/sms.php"
    # id (customer identification number)
    # pw (password)
    # dnr (recipient code)
    # snr (originator code)
    # ddt (deferred delivery time)
    # test flag indicating test mode (SMS will not be send out) (0 or 1)
    # msg (for transporting a text-message)
    outgoing_params = {"id" : "please", 
                       "pw" : "fix", 
                       "snr" : "me", 
                       }
    param_text_outgoing = "msg"
    param_dst_outgoing = "dnr"
    param_sender_outgoing = "snr"


    def do_GET(self):
        params = get_params(self)
        self.handle_params(params)
        
    def do_POST(self):
        params = post_params(self)
        self.handle_params(params)
        
    def handle_params(self, params):
        if not params:
            self.respond(500, "Must specify parameters in the URL!")
            return
        else:
            # parameters are: 
            text = None
            sender = None
            date = None
            for param in params:    
                if param[0] == End2EndHandler.param_text:
                    # TODO watch out because urllib.unquote 
                    # will blow up on unicode text 
                    text = urllib.unquote(param[1])
                elif param[0] == End2EndHandler.param_sender:
                    # TODO watch out because urllib.unquote 
                    # will blow up on unicode text 
                    sender = urllib.unquote(param[1])
                # TODO: deal with timestamps
            if text and sender: 
                # messages come in from end2end with + instead of spaces, so
                # change them
                text = " ".join(text.split("+"))
                # route the message
                msg = self.server.backend.message(sender, text, date)
                self.server.backend.route(msg)
                # respond with the number and text 
                # only really useful for testing
                self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, text))
                return
            else:
                self.respond(500, "You must specify a valid number and message")
                return

    @classmethod
    def outgoing(klass, message):
        klass.backend.debug("End2End outgoing message: %s" % message)
        params = End2EndHandler.outgoing_params.copy()
        params[End2EndHandler.param_text_outgoing] = message.text
        params[End2EndHandler.param_dst_outgoing] = message.connection.identity
        print params
        lines = []
        success = False
        response = ""
        for url in [End2EndHandler.outgoing_url, End2EndHandler.backup_outgoing_url]:
             
            try:
                response = urllib2.urlopen(End2EndHandler.outgoing_url, urllib.urlencode(params))
                for line in response:
                    if "-ERR" in line:
                        # fail
                        klass.backend.error("Error from gateway %s:\n%s" % (url, line))
                        continue
                # we didn't fail if we made it out
                success = True
                # stop looping over the urls on the first success
                break
            except Exception, e:
                klass.backend.error("problem submitting to: %s" % url)
                klass.backend.error("Exception is: %s" % e)
        if success:
            lines.insert(0,"Success!")
        else:
            lines.insert(0,"Error!")
        
        klass.backend.debug("Got response: %s" % "\n".join(response))
        
        
def get_params(handler):
    '''Pulls the parameters from a query string and returns them in
       a dictionary'''
    querystart = handler.path.find("?")
    if querystart == -1:
        return
    return map((lambda t: t.split("=")), handler.path[querystart + 1:].split("&"))

def post_params(handler):
    '''Pulls the parameters from the body of a POST and returns them
       in a dictionary'''
    if handler.rfile:
        content_len = int(handler.headers["Content-Length"])
        data = handler.rfile.read(content_len)
        return map((lambda t: t.split("=")), data.split("&"))
