#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import cgi, urlparse, traceback
from simplejson import JSONEncoder
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class App(rapidsms.app.App):
    """This app has no docstring!"""
    
    class Server(ThreadingMixIn, HTTPServer):
        pass
    
    
    class MyJsonEncoder(JSONEncoder):
        def default(self, o):
            
            # if this object has its own preference
            # for JSON serialization, prioritize that
            if hasattr(o, "__json__"):
                return o.__json__()
            
            # otherwise, revert to the usual behavior
            return JSONEncoder.default(self, o)

    
    class RequestHandler(BaseHTTPRequestHandler):
        def __find_app(self, name):
            
            # inspect the name of each active app,
            # returning as soon as we find a match
            for app in self.server.app.router.apps:
                if app.name.lower() == name.lower():
                    return app
            
            # no app by that
            # name was found
            return None
        
        # handle both GET and POST with
        # the same method
        def do_GET(self):  return self.process()
        def do_POST(self): return self.process()
        
        def process(self):
            def response(code, output):
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.end_headers()
                
                # send back every response as JSON -- even the
                # errors -- to avoid having to check the mime
                # type of the output before displaying it.
                json = App.MyJsonEncoder().encode(output)
                self.wfile.write(json)
                
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
                params = urlparse.parse_qs(url.query)
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
            except:
                self.server.app.warning(traceback.format_exc())
                return response(500, traceback.format_exc())
        
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
