.. _tutorial04:

RapidSMS Tutorial Part 4
========================

In this part of the tutorial, we'll show one way to move beyond the
message tester to send and receive text message with real phones.

Online Providers
----------------

A common way to connect your RapidSMS application to the telephone
system is to use an online service. Typically such a service will
provide an HTTP interface that lets you send messages, and a phone
number that can receive messages. When a message is received, the
service will deliver it to your application via HTTP request as
well.

Tropo
-----

For this example we'll use `Tropo`_. There's a `Tropo RapidSMS backend`_ we
can use, and if you're in the United States, you can get a free developer
account that includes a phone number and enough free messages to try out
the service. Tropo also has service in the rest of North America and
western Europe, though the free developer account is not available.
If you're outside Tropo's service area, you'll have to use another
provider, but hopefully this tutorial will still show you the basics
of how using an online provider works.

Get an account
--------------

To create a Tropo account, go to https://www.tropo.com/account/register.jsp
and fill in the form.

Create an app at Tropo
----------------------

Go to https://www.tropo.com/applications/ and create a new WebAPI application.
Configure it as follows:

Tropo WebAPI Application Name:
    Anything you like; this only appears on the Tropo site and is not
    needed in your RapidSMS app.
What URL powers voice calls to your app?
    We don't need this, but it cannot be blank. We recommend just copying the
    messaging URL you enter into the next field.
What URL powers SMS/messaging calls to your app?
    This is a URL that Tropo will make requests to when interacting with
    your app.  You can use something like
    ``https://yourhost.example.com/tropo``.  We'll talk more about this
    when we get to configuration.
Phone Numbers:
    You'll need a ``Voice & Messaging`` phone number. Your app will
    receive text messages at this number, and will use this number as
    the source number when sending messages.  Click ``Add a new
    phone number`` if needed.  After adding this number, make a note
    of it.

    You can ignore the other phone numbers.
Outbound tokens:
    Voice:
        You can ignore this token.
    Messaging:
        Click on this token string to display a popup window where you can
        copy the entire token. Save it for later.  Click the close button in
        the upper right of the window.

Click the ``Update Application`` button to save your settings.


Install the backend
-------------------

Add the Tropo RapidSMS backend to your requirements by editing
``requirements/base.txt``:

.. code-block:: text
    :emphasize-lines: 4

    Django>=1.5,<1.6
    RapidSMS==0.14.0
    South==0.7.6
    rapidsms-tropo>=0.2.0

Then use pip to install it:

.. code-block:: console

    $ pip install -r requirements/base.txt

That will pull in a few dependencies of rapidsms-tropo.


Configure RapidSMS and the backend
----------------------------------

You'll need to add or change a few settings in your application.

:setting:`INSTALLED_APPS`:
    Add "rtropo" to :setting:`INSTALLED_APPS`.
:setting:`INSTALLED_BACKENDS`:
    Add a new entry to :setting:`INSTALLED_BACKENDS`
    for the Tropo backend to talk to your Tropo account.
    It will look something like this:

.. code-block:: python

    INSTALLED_BACKENDS = {
        ...,
        "my-tropo-backend": {
            "ENGINE": "rtropo.outgoing.TropoBackend",
            'config': {
                # Your Tropo application's outbound token for messaging
                'messaging_token': '(some long hex string)',
                # Your Tropo application's voice/messaging phone number (including country code)
                'number': '+1-555-555-1212',
            },
        },
    }

URLs:
    Add a URL definition for the messaging URL that you configured in
    your Tropo app on the Tropo site.  It should call the Tropo
    backend's view for receiving messages (``rtropo.views.message_received``),
    and pass the name of the backend you used in :setting:`INSTALLED_BACKENDS`.
    The URL pattern should match the URL you configured at Tropo, like this:

.. code-block:: python

    from rtropo.views import message_received

    urlpatterns = patterns('',
        ...,
        url(r'^tropo/',
            message_received,
            kwargs={'backend_name': 'my-tropo-backend'}),
        ...
    )

Try it out
----------

Start your app, send a text message to your phone number at Tropo,
and you should get a response from your app, probably the typical
"RapidSMS could not understand your message" unless you've changed
it.

Troubleshooting
---------------

If you don't get a response, first check your application's logs for
errors and if you find any, follow them up. If you don't find any, or
you fix them and try again and still don't get a response, then you'll
want to methodically work through the steps your message and its
response have to take and check things out.

Did Tropo get your text?
........................

Tropo has an excellent debugging tool. When you're logged in to their site,
you'll see a link near the top right, "Application Debugger". Follow that
link and you'll see a window which will show voluminous logging information.

The window starts out empty, so once you have it open, send a new
message to your Tropo number and see what shows up. If nothing does,
then Tropo didn't get your message. Go back to your application settings
on the Tropo site and check the phone number again, then double-check
you're not misdialing it when you send the message.

Did Tropo call your site?
.........................

We should be able to tell from the logs in the Tropo application debugger
what Tropo did with the message. The window automatically scrolls to the
end, so scroll back up to the top.  Then start scanning the log messages.

Hopefully after 10 or 20 messages have gone by, you'll see something like
this:

    #TROPO#: Found hostedCloudDnsApplicationInfo [_url=https://hostname.example.com/tropo/, _type=tropo-web, _account=NNNNN, _userName=XXXXXX, _appId=NNNNN, _odf=cusd, _serviceId=NNNNNN, _platform=NNN][endpoint=NNNNNNNNN]

That tells you that Tropo matched the incoming message to your application.
Double-check the URL there.

Was Tropo's call to your site successful?
.........................................

Keep scanning down the logs, paying particular attention to
lines with your URL in them, and you should eventually find
Tropo sending a request to your application. It might look
like this:

    #TROPO#: Sending TropoML Payload on Tropo-Thread-3b43948e921da539a358747c389567a8 [url=http://host.example.com/tropo/]: {"session":{"id":"3b43948e921da539a358747c389567a8","accountId":"NNNNN","timestamp":"2013-05-17T15:44:08.724Z","userType":"HUMAN","initialText":"MYMESSAGE","callId":"(hex string)","to":{"id":"15555551212","name":null,"channel":"TEXT","network":"SMS"},"from":{"id":"15555551212","name":null,"channel":"TEXT","network":"SMS"},"headers":{(a whole lot of SIP headers omitted here}}}

If the application failed to handle the request, that might be followed
shortly by something like this:

    #TROPO#: Received non-2XX status code on Tropo-Thread-163cd6755723938b4b19003576b16212 [url=http://home.example.com/tropo/, code=500]

That indicates that the request got a response status code of 500
from your app. If you see this, you'll have to go back to your app
and add more logging or find another way to determine what's going
wrong when Tropo calls your app.

What you'd like to see instead would be a log message like this:

    #TROPO#: Received new TropoML document on Tropo-Thread-5312f2c74f36e1421622564e18c1c297: {"tropo": [{"hangup": {}}]}

That shows the rapidsms-tropo backend responded to Tropo with a little
Tropo program, as it should.

Did your site call Tropo back?
..............................

In order to send a response, your site has to make a call to Tropo,
then Tropo calls your site back, and finally your site responds to
that request with the command to send the response message. (This
convoluted workflow seems to be unique to Tropo; with most other
providers, your site just calls the provider and sends the command
to send a message.)

This will all show up in the debug log as well.  To confuse the
issue, this flow might overlap with the previous flow - your
site might call Tropo while still in the middle of handling
the request from Tropo.  However, you can distinguish the
two calls by looking at the ``SessionID`` column in the debugger.
The first part of that is just the line number in the log window,
but the second part identifies the session, and will be different
on the messages associated with a different call.

Here's a message indicating your site has called Tropo:

    #TROPO#: HTTPDriver.doGet(): action = create

And further down with the same session ID, you should see
another message showing Tropo calling your app again:

	#TROPO#: Sending TropoML Payload on Tropo-Thread-5acf02a5867a557bd6b31212f47a5c56 [url=http://home.example.com:9123/tropo/]: {"session":{"id":"5acf02a5867a557bd6b31212f47a5c56","accountId":"NNNNN","timestamp":"2013-05-17T16:54:54.307Z","userType":"NONE","initialText":null,"callId":null,"parameters":{(contents omitted)}}}

Keep looking for the same session ID to see if this was successful.
Eventually you should see something like:

    #TROPO#: Received new TropoML document on Tropo-Thread-5acf02a5867a557bd6b31212f47a5c56: {"tropo": [{"message": {"to": "15555551212", "say": {"value": "Sorry, RapidSMS could not understand your message."}, "from": "+15555551212", "network": "SMS", "channel": "TEXT"}}]}

This is the rapidsms-tropo backend telling Tropo to send a message
"Sorry, RapidSMS could not understand your message.".

Did Tropo send the response message?
....................................

Continue following the log messages for the same session.
Searching for the text of the response message might be
helpful. You're looking for a log message showing Tropo
delivering the message externally. It might look
like this:

    #MRCP#: (o)ANNOUNCE rtsp://10.6.69.204:10074/synthesizer/ RTSP/1.0\r\nCseq: 3\r\nSession: 1368809694451-15745b70-b9b143c0-00000585\r\nContent-Type: application/mrcp\r\nContent-Length: 397\r\n\r\nSPEAK 141650001 MRCP/1.0\r\nKill-On-Barge-In: false\r\nSpeech-Language: im\r\nVendor-Specific-Parameters: IMified-Network=SMS;IMified-From=+15555551212;IMified-Bot-Key=88A17A15-CCC1-404B-806434AD47E4B442;IMified-User=tel:+15555551212\r\nContent-Type: application/synthesis+ssml\r\nContent-Length: 103\r\n\r\n<?xml version="1.0" encoding="UTF-8"?><speak>Sorry, RapidSMS could not understand your message.</speak> #[1368809694451-15745b70-b9b143c0-00000585][10.6.69.204:10074][10.6.69.204:59469][4602a1bcfe5482f8b25066886e8a7496][456902][77104]

Most of that we can ignore, bug we should see our phone numbers and the text message.
After that, we should see another log message showing the response, hopefully
successful:

    #MRCP#: (i)RTSP/1.0 200 OK\r\nSession: 1368809694451-15745b70-b9b143c0-00000585\r\nCseq: 3\r\nContent-Type: application/mrcp\r\nContent-Length: 38\r\n\r\nMRCP/1.0 141650001 200 IN-PROGRESS\r\n\r\n #[1368809694451-15745b70-b9b143c0-00000585][10.6.69.204:10074][10.6.69.204:59469][4602a1bcfe5482f8b25066886e8a7496][456902][77104]

Again, we can ignore most of that, but "200 OK" is a good sign.

Next steps
----------

Continue reading the documentation. There's a lot of useful information.
Some of it you might want to skim for now, but it'll give you an idea
of what RapidSMS can do, and where to look for more details when you're ready
to try new things.

.. _Tropo: https://www.tropo.com/
.. _Tropo RapidSMS backend: https://pypi.python.org/pypi/rapidsms-tropo/
