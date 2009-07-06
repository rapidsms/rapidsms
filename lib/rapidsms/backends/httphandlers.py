#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer, SocketServer
import select
import random
import re
import urllib, urllib2
from datetime import datetime

import rapidsms
from rapidsms.message import Message

class RapidBaseHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''The base handler for use in the http backends.  This is a
       simple extension of the python builtin handlers with
       logging capabilities and a utility method for responding
       to incoming requiests.'''

    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(msg)

    
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
            text = match.group(2)
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if HttpHandler.msg_store.has_key(session_id) and len(HttpHandler.msg_store[session_id]):
                    self.wfile.write("{'phone':'%s', 'message':'%s'}" % (session_id, str(HttpHandler.msg_store[session_id].pop(0)).replace("'", r"\'")))
                return
                
            # TODO watch out because urllib.unquote will blow up on unicode text 
            msg = self.server.backend.message(session_id, urllib.unquote(text))
            self.server.backend.route(msg)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("{'phone':'%s', 'message':'%s'}" % (session_id, urllib.unquote(text).replace("'", r"\'")))
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
            HttpHandler.msg_store[msg.connection.identity].append(msg.text)
        else:
            HttpHandler.msg_store[msg.connection.identity] = []
            HttpHandler.msg_store[msg.connection.identity].append(msg.text)
                
class BernsoftHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the bernsoft gateway, for use in Kenya''' 
    
    # This is the format of the post string
    # TODO: not hard code this
    outgoing_url = "http://afritext.bernsoft.com/api/send.php?username=%(user)s&password=%(password)s&destination_number=%(to)s&message=%(text)s&thirdparty_message_id=%(id)s"
    user = "8291"
    password = "iavitst"
    
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
            # text=message%20body
            # sender=2347067277331
            # timesent=<format???>
            text = None
            sender = None
            date = None
            for param in params:
                if param[0] == "text":
                    # TODO watch out because urllib.unquote 
                    # will blow up on unicode text 
                    text = urllib.unquote(param[1])
                elif param[0] == "sender":
                    sender = param[1]
                elif param[0] == "timesent":
                    try: 
                        date = datetime.strptime(param[1], "%Y%m%d%H%M.%S")
                    except:
                        self.log_error("bad date format: %s" % param[1])
                        date = datetime.now()
            if text and sender: 
                # respond with "ok" so bernsoft knows
                # we got it correctly
                msg = self.server.backend.message(sender, text, date)
                self.server.backend.route(msg)
                self.respond(200, "OK")
                return
            else:
                self.respond(500, "You must specify a valid number and message")
                return

    @classmethod
    def outgoing(klass, message):
        klass.backend.debug("Bernsoft outgoing message: %s" % message)
        if hasattr(message, "logger_id") and message.logger_id:
            id = message.logger_id
        else:
            id = 0
        to_submit = BernsoftHandler.outgoing_url % ( { "user": BernsoftHandler.user, "password" : BernsoftHandler.password, 
                                             "to" : message.connection.identity, "text" : urllib2.quote(message.text),
                                             "id" : id})
        #self.log_message("submitting to url: %s" % to_submit)
        klass.backend.debug("submitting to url: %s" % to_submit)
        
        response = "\n".join([line for line in urllib2.urlopen(to_submit)])
        #self.log_message("Got response: %s" % response)
        klass.backend.debug("Got response: %s" % response)
        
        
        
class YoHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the yo gateway, for use in Uganda''' 
    
    # This is the format of the post string
    yo_secret = "iv-av-3vksEt" 
    param_text = "smsContent"
    param_sender = "msisdn"
    
    outgoing_url = "http://switch1.yo.co.ug/ybs_p/task.php"
    outgoing_params = {"ybsacctno" : "1000193801", 
                 "sysrid" : "5", 
                 "method" : "acsendsms", 
                 "type" : "1", 
                 "nostore" : "1", 
                 "ybs_autocreate_authorization" : "c32d86ed21921f3a2c4140ac8e65e188"
                 }
    param_text_outgoing = "sms_content"
    param_phone_outgoing = "destinations"


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
            # smsContent=message%20body
            # msisdn=2347067277331 (sender)
            text = None
            sender = None
            date = None
            for param in params:    
                if param[0] == YoHandler.param_text:
                    # TODO watch out because urllib.unquote 
                    # will blow up on unicode text 
                    text = urllib.unquote(param[1])
                elif param[0] == YoHandler.param_sender:
                    sender = param[1]
            if text and sender: 
                # respond with the number and text 
                # only really useful for testing
                
                # messages come in from yo with + instead of spaces, so
                # change them
                text = " ".join(text.split("+"))
                msg = self.server.backend.message(sender, text, date)
                self.server.backend.route(msg)
                self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, text))
                return
            else:
                self.respond(500, "You must specify a valid number and message")
                return

    @classmethod
    def outgoing(klass, message):
        klass.backend.debug("Yo outgoing message: %s" % message)
        params = YoHandler.outgoing_params.copy()
        params[YoHandler.param_text_outgoing] = urllib2.quote(message.text)
        params[YoHandler.param_phone_outgoing] = urllib2.quote(message.connection.identity)
        lines = []
        ok = False
        for line in urllib2.urlopen(YoHandler.outgoing_url, urllib.urlencode(params)): 
            if "ybs_autocreate_status=OK" in line:
                ok = True
            elif "ybs_autocreate_status=ERROR" in line:
                ok = False
            lines.append(line)
        if ok:
            lines.insert(0,"Success!")
        else:
            lines.insert(0,"Error!")
        
        klass.backend.debug("submitting to url: %s" % YoHandler.outgoing_url)
        
        response = "\n".join([line for line in lines])
        klass.backend.debug("Got response: %s" % response)
        
        
        
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
        for param in params:
            if param[0] == "text":
                # TODO watch out because urllib.unquote will blow up on unicode text 
                text = urllib.unquote(param[1])
            elif param[0] == "from":
                sender = param[1]
            elif param[0] == "sent":
                date = datetime.strptime(param[1], "%Y%m%d%H%M.%S")
        
        if text and sender: 
            # respond with the number and text 
            msg = self.server.backend.message(text, sender, date)
            self.server.backend.route(msg)
            self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, text))
            return
        else:
            self.respond(500, "You must specify a valid number and message")
            return

    def outgoing(self, message):
        '''An HttpHandler for the mtech gateway, for use in Nigeria'''
        self.log_message("Mtech outgoing message: %s" % message)

        
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
