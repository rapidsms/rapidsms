#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import cgi, urlparse, traceback
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from django.utils.simplejson import JSONEncoder
from django.db.models.query import QuerySet


class App(rapidsms.app.App):
    """This App does nothing by itself. It exists only to serve other Apps, by
       providing an easy (and standard) way for them to communicate between their
       WebUI and RapidSMS App object.
       
       When RapidSMS starts, this app starts an HTTPServer (port 8001 as default,
       but configurable via rapidsms.ini) in a worker thread, and watches for any
       incoming HTTP requests matching */app/method*. These requests, along with
       their GET parameters and POST form, are passed on to the named app.
       
       Examples:
       
       method  URL                  app        method             args
       ======  ===                  ===        ======             ====
       GET     /breakfast/toast     breakfast  ajax_GET_toast     { }
       POST    /breakfast/waffles   breakfast  ajax_POST_waffles  { }, { }
       POST    /breakfast/eggs?x=1  breakfast  ajax_POST_eggs     { "x": 1 }, {}
       
       Any data that is returned by the handler method is JSON encoded, and sent
       back to the WebUI in response. Since the _webui_ app includes jQuery with
       every view, this makes it very easy for the WebUIs of other apps to query
       their running App object for state. See the _training_ app for an example.
       
       But wait! AJAX can't cross domains, so a request to port 8001 from the WebUI
       won't work! This is handled by the WebUI bundled with this app, that proxies
       all requests to /ajax/(.+) to the right place, on the server side. I cannot
       conceive of a situation where this would be a problem - but keep it in mind,
       and don't forget to prepend "/ajax/" to your AJAX URLs."""
    
    
    class Server(ThreadingMixIn, HTTPServer):
        pass
    
    
    class MyJsonEncoder(JSONEncoder):
        def default(self, o):
            
            # if this object has its own preference
            # for JSON serialization, prioritize that
            if hasattr(o, "__json__"):
                return o.__json__()
            
            elif type(o) == QuerySet:
                return list(o)
            
            # otherwise, revert to the usual behavior
            return JSONEncoder.default(self, o)

    
    class RequestHandler(BaseHTTPRequestHandler):
        def __find_app(self, name):
            
            # inspect the name of each active app,
            # returning as soon as we find a match
            for app in self.server.app.router.apps:
                if app.slug == name:
                    return app
            
            # no app by that
            # name was found
            return None
        
        # handle both GET and POST with
        # the same method
        def do_GET(self):  return self.process()
        def do_POST(self): return self.process()
        
        def process(self):
            def response(code, output, json=True):
                self.send_response(code)
                mime_type = "application/json" if json else "text/plain"
                self.send_header("content-type", mime_type)
                self.end_headers()
                
                if json:
                    json = App.MyJsonEncoder().encode(output)
                    self.wfile.write(json)
                
                # otherwise, write the raw response.
                # it doesn't make much sense to have
                # error messages encoded as JSON...
                else: self.wfile.write(output)
                
                # HTTP2xx represents success
                return (code>=200 and code <=299)
            
            # should look something like:
            #   /alpha/bravo?charlie=delta
            # 
            # this request will be parsed to the "bravo"
            # method of the "alpha" app, with the params:
            #   { "charlie": ["delta"] }
            #
            # any other path format will return an http404
            # error, for the time being. params are optional.
            url = urlparse.urlparse(self.path)
            path_parts = url.path.split("/")
            
            # abort if the url didn't look right
            # TODO: better error message here
            if len(path_parts) != 3:
                return response(404, "FAIL.")
            
            # resolve the first part of the url into an app
            # (via the router), and abort if it wasn't valid
            app_name = path_parts[1]
            app = self.__find_app(app_name)
            if (app is None):
                return response(404,
                    "Invalid app: %s" % app_name)
            
            # same for the request name within the app
            # (FYI, self.command returns GET, POST, etc)
            meth_name = "ajax_%s_%s" % (self.command, path_parts[2])
            if not hasattr(app, meth_name):
                return response(404,
                    "Invalid method: %s" % meth_name)
           
            # everything appears to be well, so call the
            # target method, and return the response (as
            # a string, for now)
            try:
                method = getattr(app, meth_name)
                params = urlparse.urlparse(url.query)
                args   = [params]
                
                # for post requests, we'll also need to parse
                # the form data, and hand it to the method
                if self.command == "POST":
                    form = {}
                
                    # parse the form data via the CGI lib. this is
                    # a horrible mess, but supports all kinds of
                    # encodings (multipart, in particular)
                    storage = cgi.FieldStorage(
                        fp = self.rfile, 
                        headers = self.headers,
                        environ = {
                            "REQUEST_METHOD": "POST",
                            "CONTENT_TYPE": self.headers["content-type"] })
                    
                    # convert the fieldstorage object into a dict,
                    # to keep it simple for the handler methods.
                    # TODO: maybe make this a util if it's useful
                    # elsewhere. it isn't, for the time being.
                    for key in storage.keys():
                        v = storage.getlist(key)
                        
                        # where possible, just store the values as singular,
                        # to avoid CGIs usual post["id"][0] verbosity
                        if len(v) > 1: form[key] = v
                        else:          form[key] = v[0]
                    
                    args.append(form)
                
                # call the method, and send back whatever data
                # structure was returned, serialized with JSON
                output = method(*args)
                return response(200, output)
 
            # something raised during the request, so
            # return a useless http error to the requester
            except Exception, err:
                self.server.app.warning(traceback.format_exc())
                return response(500, unicode(err), False)
        
        # this does nothing, except prevent HTTP
        # requests being echoed to the screen
        def log_request(*args):
            pass
    
    
    def configure(self, host=None, port=None):
        self.host = host
        self.port = port
    
    
    def start(self):
        # create the webserver, through which the
        # AJAX requests from the WebUI will arrive
        self.server = self.Server((self.host, self.port), self.RequestHandler)
        self.server.app = self
        
        # start the server in a separate thread, and daemonize it
        # to prevent it from hanging once the main thread terminates
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
