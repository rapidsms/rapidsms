#!/usr/bin/env ruby
# vim: noet


require "rubygems"
require "rack"


module SMS::Backend

    # Provides a low-tech HTML webUI to inject mock SMS messages into
    # RubySMS, and receive responses. This is usually used during app
    # development, to provide a cross-platform method of simulating
    # a two-way conversation with the SMS backend(s). Note, though,
    # that there is no technical difference between the SMS::Incoming
    # and SMS::Outgoing objects created by this backend, and those
    # created by "real" incoming messages via the GSM backend.
    #
    # The JSON API used internally by this backend also be used by
    # other HTML applications to communicate with RubySMS, but that
    # is quite obscure, and isn't very well documented yet. Also, it
    # sporadically changes without warning. May The Force be with you.
    class HTTP < Base
        HTTP_PORT = 1270
        #MT_URL = "http://ajax.googleapis.com/ajax/libs/mootools/1.2.1/mootools-yui-compressed.js"
        MT_URL = "http://localhost:8000/static/http/scripts/mootools-yui-compressed.js"
        attr_reader :msg_log
        
        def initialize(port=HTTP_PORT, mootools_url=MT_URL)
            @app = RackApp.new(self, mootools_url)
            @port = port
            
            # initialize the log, which returns empty
            # arrays (new session) for unknown keys
            # to avoid initializing sessions all over
            @msg_log = {}
        end

        # Starts a thread-blocking Mongrel to serve
        # SMS::Backend::HTTP::RackApp, and never returns.
        def start
            
            # add a screen log message, which is kind of
            # a lie, because we haven't started anything yet
            uri = "http://localhost:#{@port}/"
            log ["Started HTTP Offline Backend", "URI: #{uri}"], :init
            
            # this is goodbye
            Rack::Handler::Mongrel.run(
                @app, :Port=>@port)
        end
        
        # outgoing message from RubySMS (probably
        # in response to an incoming, but maybe a
        # blast or other unsolicited message). do
        # nothing except add it to the log, for it
        # to be picked up next time someone looks
        def send_sms(msg)
            s = msg.recipient.phone_number
            t = msg.text
            
            # allow RubySMS to notify the router
            # this is a giant ugly temporary hack
            super
            
            # init the message log for
            # this session if necessary
            @msg_log[s] = []\
                unless @msg_log.has_key?(s)
            
            # add the outgoing message to the log
            msg_id = @msg_log[s].push\
                [t.object_id.abs.to_s, "out", t]
        end
        
        
        
        
        # This simple Rack application handles the few
        # HTTP requests that this backend will serve:
        #
        # GET  /             -- redirect to a random blank session
        # GET  /123456.json  -- export session 123456 as JSON data
        # GET  /123456       -- view session 123456 (actually a
        #                       static HTML page which fetches
        #                       the data via javascript+json)
        # POST /123456/send  -- add a message to session 123456
        class RackApp
            def initialize(http_backend, mootools_url)
                @backend = http_backend
                @mt_url = mootools_url
                
                # generate the html to be returned by replacing the
                # variables in the constant with our instance vars
                @html = HTML.sub(/%(\w+)%/) do
                    instance_variable_get("@#{$1}")
                end
            end
            
            def call(env)
                req = Rack::Request.new(env)
                path = req.path_info
                
                if req.get?
                    
                    # serve GET /
                    # for requests not containing a session id, generate a random
                    # new one (between 111111 and 999999) and redirect back to it
                    if path == "/"
                        while true
                        
                            # randomize a session id, and stop looping if
                            # it's empty - this is just to avoid accidentally
                            # jumping into someone elses session (although
                            # that's allowed, if explicly requested)
                            new_session = (111111 + rand(888888)).to_s
                            break unless @backend.msg_log.has_key?(new_session)
                        end
                    
                        return [
                            301, 
                            {"location" => "/#{new_session}"},
                            "Redirecting to session #{new_session}"]
                    
                    # serve GET /123456
                    elsif m = path.match(/^\/\d{6}$/)
                    
                        # just so render the static HTML content (the
                        # log contents are rendered via JSON, above)
                        return [200, {"content-type" => "text/html"}, @html]
            
                    # serve GET /123456.json
                    elsif m = path.match(/^\/(\d{6})\.json$/)
                        msgs = @backend.msg_log[m.captures[0]] || []
                        
                        return [
                            200,
                            {"content-type" => "application/json"},
                            "[" + (msgs.collect { |msg| msg.inspect }.join(", ")) + "]"]
                    
                    # serve GET /favicon.ico
                    # as if YOU'VE never wasted
                    # a minute on frivolous crap
                    elsif path == "/favicon.ico"
                        icon = File.dirname(__FILE__) + "/cellphone.ico"
                        return [200, {"content-type" => "image/x-ico"}, File.read(icon)]
                    end
                
                # serve POST /123456/send
                elsif (m = path.match(/^\/(\d{6})\/send$/)) && req.post?
                    t = req.POST["msg"]
                    s = m.captures[0]
                    
                    # init the message log for
                    # this session if necessary
                    @backend.msg_log[s] = []\
                        unless @backend.msg_log.has_key?(s)
                    
                    # log the incoming message, so it shows
                    # up in the two-way "conversation" 
                    msg_id = @backend.msg_log[s].push\
                        [t.object_id.abs.to_s, "in", t]

                    # push the incoming message
                    # into RubySMS, to distribute
                    # to each application
                    @backend.router.incoming(
                        SMS::Incoming.new(
                            @backend, s, Time.now, t))
                    
                    # acknowledge POST with
                    # the new message ID
                    return [
                        200,
                        {"content-type" => "text/plain" },
                        t.object_id.abs.to_s]
                end
                
                # nothing else is valid. not 404, because it might be
                # an invalid method, and i can't be arsed right now.
                [500, {"content-type" => "text/plain" }, "FAIL."]
            end
        end
    end
end

SMS::Backend::HTTP::HTML = <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>RubySMS Virtual Device</title>
        <script id="mt" type="text/javascript" src="%mt_url%"></script>
        <style type="text/css">
            
            /* remove m+p from most elements,
             * without resetting form elements */
            body, h1, #log, #log li, form {
                margin: 0;
                padding: 0;
            }
            
            body {
                line-height: 1;
                font: 8pt sans-serif;
                background: #eef;
                padding: 2em;
            }
            
                body.framed {
                    background: transparent;
                    padding: 0;
                }
                
                body.framed #wrapper {
                    position: absolute;
                    width: 100%;
                    bottom: 0;
                    left: 0;
                    
                }
            
            #wrapper div {
                padding: 0.5em;
                background: #33a7d2;
            }
            
                h1 {
                    font-size: 100%;
                    color: #fff;
                }
                
                #log {
                    height: 14em;
                    overflow-y: scroll;
                    font-family: monospace;
                    background: #fff;
                    margin: 0.5em 0;
                }
            
                    #log li {
                        line-height: 1.4;
                        list-style: none;
                        white-space: pre;
                        padding: 0.5em;
                    }
                    
                        #log li.in {
                            color: #888;
                            border-top: 1px dotted #000;
                        }
                            
                            /* don't show the divider
                             * at the top of the log */
                            #log li:first-child.in {
                                border-top: 0; }
                        
                        #log li.out {
                            color: #000;
                            background: #f8f8f8;
                        }
                        
                        /* messages prior to the latest
                         * are dim, to enhance readability */
                        #log li.old {
                            border-top: 0;
                            color: #ddd;
                        }
                        
                        #log li.error {
                            color: #f00;
                        }
                    
                form { }
                    
                    form input {
                        -moz-box-sizing: border-box;
                        width: 100%;
                    }
        </style>
    </head>
    <body>
        <div id="wrapper">
            <div>
                <h1>RubySMS Virtual Device</h1>
            
                <ul id="log">
                </ul>
            
                <form id="send" method="post">
                    <input type="text" id="msg" name="msg" />
                    <!--<input type="submit" value="Send" />-->
                </form>
            </div>
        </div>
        
        <script type="text/javascript">
            /* if mootools wasn't loaded (ie, the internet at this shitty
             * african hotel is broken again), just throw up a warning */
            if(typeof(MooTools) == "undefined") {
                var err = [
                    "Couldn't load MooTools from: " + document.getElementById("mt").src,
                    "This interface will not work without it, because I'm a lazy programmer. Sorry."
                ].join("\\n");
                document.getElementById("log").innerHTML = '<li class="error">' + err + '</li>';

            } else {
                window.addEvent("domready", function() {
                    
                    /* if this window is not the top-level
                     * window (ie, it has been included in
                     * an iframe), then add a body class
                     * to style things slightly differently */
                    if (window != top) {
                        $(document.body).addClass("framed");
                    }
                    
                    // extract the session id from the URI
                    var session_id = location.pathname.replace(/[^0-9]/g, "");
            
                    /* for storing the timeout, so we
                     * can ensure that only one fetch
                     * is running at a time */
                    var timeout = null;
                    
                    // the scrolling message log
                    var log = $("log");
            
                    /* function to be called when it is time
                     * to update the log by polling the server */
                    var update = function(msg_id) {
                        $clear(timeout);
                        
                        new Request.JSON({
                            "method": "get",
                            "url": "/" + session_id + ".json",
                            "onSuccess": function(json) {
                                var dimmed_old = false;
                                
                                json.each(function(msg) {
                                    var msg_id = "msg-" + msg[0];
                                    
                                    /* iterate the items returned by the JSON request, and append
                                     * any new messages to the message log, in order of receipt */
                                    if ($(msg_id) == null) {
                                    
                                        /* before adding new messages, add a class
                                         * to the existing messages, to dim them */
                                        if (!dimmed_old) {
                                            log.getElements("li").addClass("old");
                                            dimmed_old = true;
                                        }
                                        
                                        /* create the new element, and inject it into
                                         * the log (msg[1] contains "in" or "out"). */
                                        new Element("li", {
                                            "text": ((msg[2] == "") ? "<blank>" : msg[2]),
                                            "class": msg[1],
                                            "id": msg_id
                                        }).inject(log);
                                    }
                                });
                                
                                /* if the update function was called in response
                                 * to an outgoing message (via the #send.onComplete
                                 * event, below), a msg_id will have been returned
                                 * by the POST request. this msg should now be in
                                 * the log, so scroll to it, so we can quickly see
                                 * the response */
                                if (msg_id != null) {
                                    var msg_el = $("msg-" + msg_id);
                                    if (msg_el != null) {
                                        
                                        log.scrollTo(0, msg_el.getPosition(log)["y"]);
                                    }

                                /* if it was called independantly, just scroll to
                                 * the bottom of the log (Infinity doesn't work!) */
                                } else {
                                    log.scrollTo(0, 9999);
                                }
                                
                                /* call again in 30 seconds, to check for
                                 * unsolicited messages once in a while */
                                timeout = update.delay(30000);
                            }
                        }).send();
                    };
            
                    /* when a message is posted via AJAX,
                     * reload the load to include it */
                    $("send").set("send", {
                        "url": "/" + session_id + "/send",
                        "onComplete": update
                
                    /* submit the form via ajax,
                     * and cancel the full-page */
                    }).addEvent("submit", function(ev) {
                        this.send();
                        ev.stop();
                        
                        /* clear the text entry field to
                         * make way for the next message */
                        $("msg").value = "";
                    });
                    
                    /* update the log now, in case there
                     * is already anything in the log */
                    update();
                });
            }
        </script>
    </body>
</html>
EOF
