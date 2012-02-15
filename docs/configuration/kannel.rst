===============================
Setting up RapidSMS with Kannel
===============================

`Kannel <http://www.kannel.org/>`_ is a free and opensource SMS gateway that can 
be configured for use with RapidSMS.  While in-depth Kannel configuration is
outside the scope of this documentation, it's possible to configure Kannel to
connect directly to USB or serial GSM modems as well as third party HTTP or SMPP
gateways.  For more information about the connections Kannel supports (what
Kannel calls an "SMS Center" or "SMSC"), see the in-depth 
`Kannel user guide <http://www.kannel.org/userguide.shtml>`_ and refer to 
"Chapter 6. Setting up a SMS Gateway".

The following guide will help you setup Kannel on Ubuntu to talk to a single GSM
modem and RapidSMS installation.

Installing Kannel
=================

A ``kannel`` package is included with Ubuntu, so installation is very easy::

    sudo apt-get install kannel

By default in Ubuntu, Kannel starts a WAP gateway but does not start the SMS
gateway.  To change this behavior, first stop Kannel::

    sudo service kannel stop

Now, edit ``/etc/default/kannel`` and uncomment the line starting with
``START_SMSBOX``. If you won't be using the WAP gateway (if you don't know what
that is you probably won't be), you can also disable it by commenting out
``START_WAPBOX=1``. **Note:** Simply setting START_WAPBOX=0 will not disable it;
you must comment out the line::

    sudo vim /etc/default/kannel # or use your favorite editor

Finally, start Kannel again (note it will say "Starting WAP gateway" even if it's
only starting the SMS gateway)::

    sudo service kannel start

You can check that it's running by looking at ``ps ax | grep kannel``.  You
should see something like this::

    2446 ?        Ss     0:00 /usr/sbin/run_kannel_box --pidfile /var/run/kannel/kannel_bearerbox.pid --no-extra-args /usr/sbin/bearerbox -v 4 -- /etc/kannel/kannel.conf
    2447 ?        Sl     0:00 /usr/sbin/bearerbox -v 4 -- /etc/kannel/kannel.conf
    2460 ?        Ss     0:00 /usr/sbin/run_kannel_box --pidfile /var/run/kannel/kannel_smsbox.pid --no-extra-args /usr/sbin/smsbox -v 4 -- /etc/kannel/kannel.conf

Setting up the fake SMSC for testing
====================================

Kannel includes support for a Fake SMSC which can be useful during setup for
testing both Kannel and RapidSMS.  The relevant utility is included in the
``kannel-extras`` package::

    sudo apt-get install kannel-extras

To make things simpler, we'll first setup Kannel and RapidSMS to work with a
Fake SMSC, and then attempt to connect it to a USB modem.

Configuring Kannel for the first time
-------------------------------------

The easiest way to get Kannel working with RapidSMS is to start with a sample
Kannel configuration.  To get started, copy and paste the following into
``/etc/kannel/kannel.conf``, replacing everything currently in the file (make
a backup first if you'd like)::

    # CONFIGURATION FOR USING SMS KANNEL WITH RAPIDSMS
    #
    # For any modifications to this file, see Kannel User Guide 
    # If that does not help, see Kannel web page (http://www.kannel.org) and
    # various online help and mailing list archives
    #
    # Notes on those who base their configuration on this:
    #  1) check security issues! (allowed IPs, passwords and ports)
    #  2) groups cannot have empty rows inside them!
    #  3) read the user guide

    include = "/etc/kannel/modems.conf" 

    #---------------------------------------------
    # CORE
    #
    # There is only one core group and it sets all basic settings
    # of the bearerbox (and system). You should take extra notes on
    # configuration variables like 'store-file' (or 'store-dir'),
    # 'admin-allow-ip' and 'access.log'

    group = core
    admin-port = 13000
    smsbox-port = 13001
    admin-password = CHANGE-ME
    status-password = CHANGE-ME
    admin-deny-ip = "*.*.*.*"
    admin-allow-ip = "127.0.0.1"
    box-deny-ip = "*.*.*.*"
    box-allow-ip = "127.0.0.1"
    log-file = "/var/log/kannel/bearerbox.log"
    log-level = 0

    #---------------------------------------------
    # SMSC CONNECTIONS
    #
    # SMSC connections are created in bearerbox and they handle SMSC specific
    # protocol and message relying. You need these to actually receive and send
    # messages to handset, but can use GSM modems as virtual SMSCs

    # Here is a sample SMSC for use with the /usr/lib/kannel/test/fakesmsc command

    group = smsc
    smsc = fake
    smsc-id = FAKE
    port = 10000
    connect-allow-ip = 127.0.0.1

    #---------------------------------------------
    # SMSBOX SETUP
    #
    # Smsbox(es) do higher-level SMS handling after they have been received from
    # SMS centers by bearerbox, or before they are given to bearerbox for delivery

    group = smsbox
    bearerbox-host = 127.0.0.1
    sendsms-port = 13013
    sendsms-chars = "0123456789 +-"
    log-file = "/var/log/kannel/smsbox.log"
    log-level = 0
    access-log = "/var/log/kannel/smsbox-access.log"
    reply-couldnotfetch = "Your message could not be processed at this time.  Please try again later. (err=couldnotfetch)"
    reply-requestfailed = "Your message could not be processed at this time.  Please try again later. (err=requestfailed)"
    reply-couldnotrepresent = "Your message could not be processed at this time.  Please try again later. (err=couldnotrepresent)"
    http-request-retry = 3
    http-queue-delay = 10

    # SEND-SMS USERS
    #
    # These users are used when Kannel smsbox sendsms interface is used to
    # send PUSH sms messages, i.e. calling URL like
    # http://kannel.machine:13013/cgi-bin/sendsms?username=tester&password=foobar...

    # This is the username and password that RapidSMS uses to deliver SMSes to
    # Kannel.  It must also set the 'smsc' variable in the query string, so that
    # Kannel knows which SMSC to use to route the message.

    group = sendsms-user
    username = rapidsms
    password = CHANGE-ME
    user-deny-ip = "*.*.*.*"
    user-allow-ip = "127.0.0.1;"

    #---------------------------------------------
    # SERVICES
    #
    # These are 'responses' to sms PULL messages, i.e. messages arriving from
    # handsets. The response is based on message content. Only one sms-service is
    # applied, using the first one to match.

    # The 'ping-kannel' service let's you check to see if Kannel is running,
    # even if RapidSMS is offline for some reason.

    group = sms-service
    keyword = ping-kannel
    text = "Kannel is online and responding to messages."

    # There should be always a 'default' service. This service is used when no
    # other 'sms-service' is applied.  These relay incoming messages from any
    # configured SMSCs to the appropriate HTTP backend URLs in RapidSMS.
    # By setting 'accepted-smsc', we are assured that messages are routed to
    # the appropriate backend in RapidSMS.

    group = sms-service
    keyword = default
    catch-all = yes
    accepted-smsc = FAKE
    # don't send a reply here (it'll come through sendsms):
    max-messages = 0
    get-url = http://127.0.0.1:8080/?id=%p&text=%a&charset=%C&coding=%c

You'll notice the file includes a file called ``modems.conf`` at the top.  You
can copy this file from where Ubuntu installed it as follows::

    sudo cp /usr/share/doc/kannel/examples/modems.conf /etc/kannel/

Next, restart Kannel to reload the new configuration::

    sudo service kannel restart

When you look at the process list (``ps ax | grep kannel``), you should see a
4th process for the smsbox now started, like so::

    3231 ?        Ss     0:00 /usr/sbin/run_kannel_box --pidfile /var/run/kannel/kannel_bearerbox.pid --no-extra-args /usr/sbin/bearerbox -v 4 -- /etc/kannel/kannel.conf
    3232 ?        Sl     0:00 /usr/sbin/bearerbox -v 4 -- /etc/kannel/kannel.conf
    3243 ?        Ss     0:00 /usr/sbin/run_kannel_box --pidfile /var/run/kannel/kannel_smsbox.pid --no-extra-args /usr/sbin/smsbox -v 4 -- /etc/kannel/kannel.conf
    3245 ?        Sl     0:00 /usr/sbin/smsbox -v 4 -- /etc/kannel/kannel.conf

You can further test that Kannel is running by using the fake SMSC (used only
for testing) to use the "ping-kannel" service that we included in the
Kannel configuration above::

    /usr/lib/kannel/test/fakesmsc -m 1 "123 789 text ping-kannel"

On the last line of the output you should see the message that was sent by the
``ping-kannel`` service, e.g.::

    INFO: Got message 1: <789 123 text Kannel is online and responding to messages.>

Press Control-C to kill the ``fakesmsc`` command and return to the prompt.

Adding a backend for the fake SMSC to RapidSMS
----------------------------------------------

Now that Kannel is installed and configured correctly, adding support for the
Kannel backend to your existing RapidSMS project is not difficult.  To begin,
simply add the following to your existing ``INSTALLED_BACKENDS`` configuration
in your ``settings.py`` file::

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.backends.bucket",
        },
        # other backends, if any
        "kannel-fake-smsc" : {
            "ENGINE":  "rapidsms.backends.kannel",
            "host": "127.0.0.1",
            "port": 8080,
            "sendsms_url": "http://127.0.0.1:13013/cgi-bin/sendsms",
            "sendsms_params": {"smsc": "FAKE",
                               "from": "123", # not set automatically by SMSC
                               "username": "rapidsms",
                               "password": "CHANGE-ME"}, # or set in localsettings.py
            "coding": 0,
            "charset": "ascii",
            "encode_errors": "ignore", # strip out unknown (unicode) characters
        },
    }

Now, you should be able to run the RapidSMS router::

    ./manage.py runrouter

And test connection using the ``echo`` app in RapidSMS (if installed in your
project)::

    /usr/lib/kannel/test/fakesmsc -m 1 "123 789 text echo hi"

You should see the message get echoed back to you on the last line::

    INFO: Got message 1: <123 123 text hi>

Adding support for a GSM Modem SMSC
===================================

This section assumes that you've already installed, configured, and setup Kannel
to use the Fake SMSC as described above.  Once you have Kannel and RapidSMS
configured, adding support for additional SMSCs (such as a GSM modem) is fairly
easy.  It also assumes that you already have a GSM modem connected to your
computer, and that you know the device location (e.g., ``/dev/ttyUSB0``) of that
modem.

Adding the GSM modem to the Kannel configuration
------------------------------------------------

Using the base configuration given above, add the following to the section 
titled "SMSC CONNECTIONS" in ``/etc/kannel/kannel.conf``, changing the
``device = /dev/ttyUSB0`` line so that it points to the right device::

    group = smsc
    smsc = at
    smsc-id = usb0-modem
    my-number = 1234
    modemtype = auto
    device = /dev/ttyUSB0

Next, add the following ``sms-service`` at the end of the file, which will
send incoming messages from the modem to RapidSMS via HTTP::

    group = sms-service
    keyword = default
    catch-all = yes
    accepted-smsc = usb0-modem
    # don't send a reply here (it'll come through sendsms):
    max-messages = 0
    get-url = http://127.0.0.1:8081/?id=%p&text=%a&charset=%C&coding=%c

Make sure to restart Kannel to reload the configuration::

    sudo service kannel restart

Adding a backend for the GSM modem to RapidSMS
----------------------------------------------

Finally, add a second Kannel backend to your ``settings.py`` which will setup
the necessary router infrastructure to send and receive messages via the
USB modem you configured above in Kannel::

    INSTALLED_BACKENDS = {
        # ...
        "kannel-usb0-smsc" : {
            "ENGINE":  "rapidsms.backends.kannel",
            "host": "127.0.0.1",
            "port": 8081,
            "sendsms_url": "http://127.0.0.1:13013/cgi-bin/sendsms",
            "sendsms_params": {"smsc": "usb0-modem",
                               "from": "+SIMphonenumber", # not set automatically by SMSC
                               "username": "rapidsms",
                               "password": "CHANGE-ME"}, # or set in localsettings.py
            "coding": 0,
            "charset": "ascii",
            "encode_errors": "ignore", # strip out unknown (unicode) characters
        },
    }

Now, the next time you call ``./manage.py runrouter``, you should see two
Kannel backends get created (one for the fake SMSC and one for the GSM modem).

Troubleshooting
===============

For help troubleshooting, please carefully review the relevant log files in
``/var/log/kannel`` as well as the output of the ``./manage.py runrouter``
command.  For additional help configuring Kannel, review the
`Kannel user guide <http://www.kannel.org/userguide.shtml>`_ or subscribe to the
`Kannel users mailing list <http://www.kannel.org/lists.shtml>`_.
