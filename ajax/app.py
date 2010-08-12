#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import cgi
import urlparse
import traceback
from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from django.utils.simplejson import JSONEncoder
from django.db.models.query import QuerySet
from rapidsms.apps.base import AppBase
from rapidsms.conf import settings


class App(AppBase):
    """
    This App does nothing by itself. It exists only to serve other Apps,
    by providing an easy (and standard) way for them to communicate
    between their WebUI and RapidSMS App object.

    When RapidSMS starts, this app starts an HTTPServer (port 8001 as
    default, but configurable via settings.py) in a worker thread, and
    watches for any incoming HTTP requests matching */app/method*. These
    requests, along with their GET parameters and POST data, are passed
    on to the named app.

    Examples::

    method  URL             app   method             args
    ======  ===             ===   ======             ====
    GET     /food/toast     food  ajax_GET_toast     { }
    POST    /food/waffles   food  ajax_POST_waffles  { }, { }
    POST    /food/eggs?x=1  food  ajax_POST_eggs     { "x": [1] }, { }

    Any data that is returned by the handler method is JSON encoded, and
    sent back to the WebUI in response. Since RapidSMS includes jQuery
    with every view, this makes it very easy for apps to query their
    running App object for state. See the _httptester_ for an example.

    But wait! AJAX can't cross domains, so a request to port 8001 from
    the WebUI won't work! This is handled by the WebUI bundled with this
    app, that proxies all requests to /ajax/(.+) to the right place, on
    the server side. I cannot conceive of a situation where this would
    be a problem - but keep it in mind, and don't forget to prepend
    "/ajax/" to your AJAX URLs.
    """


    class Server(ThreadingMixIn, HTTPServer):
        pass


    class MyJsonEncoder(JSONEncoder):
        def default(self, o):

            # if this object has its own JSON serializer, use it
            if hasattr(o, "__json__"):
                return o.__json__()

            elif type(o) == QuerySet:
                return list(o)

            # otherwise, revert to the usual behavior
            return JSONEncoder.default(self, o)


    class RequestHandler(BaseHTTPRequestHandler):
        def _find_app(self, name):
            for app in self.server.app.router.apps:
                if app.name == name:
                    return app

        def _charset(self, str):
            """
            Extract and return the charset argument from an HTTP
            content-type header, or None if it was not found.
            """

            x = str.split("charset=", 1)
            return x[1] if(len(x) == 2) else None


        # handle GET and POST with the same method
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

                # otherwise, write the raw response. it doesn't make
                # much sense to have error messages encoded as JSON.
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
            # any other path format will return an http 404 error, for
            # the time being. GET parameters are optional.
            url = urlparse.urlparse(self.path)
            path_parts = url.path.split("/")

            # abort if the url didn't look right
            if len(path_parts) != 3:
                str_ = "Malformed URL: %s" % url
                self.server.app.warning(str_)
                return response(404, str_)

            # resolve the first part of the url into an app (via the
            # router), and abort if it wasn't valid
            app_name = path_parts[1]
            app = self._find_app(app_name)
            if (app is None):
                str_ = "Invalid app: %s" % app_name
                self.server.app.warning(str_)
                return response(404, str_)

            # same for the request name within the app
            meth_name = "ajax_%s_%s" % (self.command, path_parts[2])
            if not hasattr(app, meth_name):
                str_ = "Invalid method: %s.%s" %\
                    (app.__class__.__name__, meth_name)
                self.server.app.warning(str_)
                return response(404, str_)

            # everything appears to be well, so call the  target method,
            # and return the response (as a string, for now)
            try:
                method = getattr(app, meth_name)
                args   = [cgi.parse_qs(url.query)]

                # for post requests, we'll also need to parse the form
                # data and hand it along to the method
                if self.command == "POST":
                    content_type = self.headers["content-type"]
                    form = {}

                    # parse the form data via the CGI lib. this is a
                    # horrible mess, but supports all kinds of encodings
                    # that we may encounter. (multipart, in particular.)
                    storage = cgi.FieldStorage(
                        fp = self.rfile, 
                        headers = self.headers,
                        environ = {
                            "REQUEST_METHOD": "POST",
                            "CONTENT_TYPE": content_type })

                    # extract the charset from the content-type header,
                    # which should have been passed along in views.py
                    charset = self._charset(content_type)

                    # convert the fieldstorage object into a dict, to
                    # keep it simple for the handler methods. TODO: make
                    # this a util, if it's useful elsewhere.
                    for key in storage.keys():

                        # convert each of the values with this key into
                        # unicode, respecting the content-type that the
                        # request _claims_ to be currently encoded with
                        val = [
                            unicode(v, charset)
                            for v in storage.getlist(key)]

                        # where possible, store the values as singular,
                        # to avoid CGI's usual post["id"][0] verbosity
                        form[key] = val[0] if(len(val) == 1) else val

                    args.append(form)

                self.server.app.debug(
                    "Calling %s.%s with args: %s" %
                    (app.__class__.__name__, meth_name, args))

                output = method(*args)

                self.server.app.debug("Response: %s" % output)
                return response(200, output)

            # something raised during the request, so return a useless
            # http error to the requester
            except Exception, err:
                self.server.app.warning(traceback.format_exc())
                return response(500, unicode(err), False)

        # this does nothing, except prevent the incoming http requests
        # from being echoed to the screen (which screws up the log)
        def log_request(*args):
            pass


    def start(self):

        # create the webserver, through which the AJAX requests from the
        # WebUI will arrive (via utils.py)
        self.server = self.Server((
            settings.AJAX_PROXY_HOST,
            settings.AJAX_PROXY_PORT),
            self.RequestHandler)

        # allow the server to call back the app
        self.server.app = self

        # start the server in a separate thread, and daemonize it to
        # prevent it from hanging once the main thread terminates
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
