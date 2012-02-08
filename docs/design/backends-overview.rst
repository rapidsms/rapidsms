Backends are the way RapidSMS interacts with external messages. Backends receive messages from external sources and delivers messages from Applications to external sources.

By default, RapidSMS responds to messages using the same backend on which it received the message. So emails coming in through the Emailbackend will go out through the Emailbackend, and messages received through a GSM Modem will go out through the same GSM modem. This is just the default though; you can manually re-route messages in code.

Backends are configured in settings.py and when RapidSMS is installed there are no backends configured. Backends are composed of a "backend name" and a dictionary. The only required key in the dictionary is the "Engine" which is a python module path. Other keys in the dictionary are used for configuration. Backends are deliberately similar to the Django projects database structure

and an example GSM backend would look like this::

    "Zain": {
        "ENGINE": "rapidsms.backends.gsm",
        "PORT": "/dev/ttyUSB1"
    },

Note that multiple backends can use the same engine. So you could plug 3 modems into your machine and run each of them at the same time using RapidSMS.

A useful backend to configure after installing RapidSMS is the "bucket" backend. This is a testing backend that is used by the message tester.
::

    "message_tester": {
        "ENGINE": "rapidsms.backends.bucket"
    }

To add that to your RapidSMS install paste it between in the `INSTALLED_BACKENDS` section of setting.py::

    INSTALLED_BACKENDS = {
    }

turns into::

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.backends.bucket"
        }
    }

Backends That Ship with RapidSMS
==================================

Backends that come with the new version of RapidSMS include:

* `bucket backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/bucket.py>`_
* `email backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/email.py>`_
* `gsm backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/gsm.py>`_
* `irc backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/irc.py>`_
* `smpp backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/smpp.py>`_
* `http backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/http.py>`_
* `kannel backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/kannel.py>`_

Each of these is known to work with the new version of RapidSMS.

Writing your own backend
==========================

bucket backend is a good example of the most barebones backend you can write (the 'hello world' of backends, if you will). Backends should extend BackendBase and implement a few functions:

* Configure (optional)
* Receive
* Send

`Receive`'s main job is to call `self.router.incoming_message(msg)`, in order to dispatch any messages received from the outside world to the RapidSMS router.

Send is called by the RapidSMS router in order to order to dispatch any messages received from the router to the outside world.
