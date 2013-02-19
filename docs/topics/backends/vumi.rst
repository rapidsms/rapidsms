.. _vumi_configuration:

=============================
Setting up RapidSMS with Vumi
=============================

`Vumi <http://vumi.org/>`_ is a free and opensource super scalable messaging
platform written in Python. Vumi can connect to third party gateways via
protocols list HTTP and SMPP. Please read `Vumi's documentation
<http://vumi.readthedocs.org/en/latest/>`_ for additional information.

The following guide will help you setup Vumi on Ubuntu to talk to a SMPP
simulator and RapidSMS installation.

Using an SMPP simulator
=======================

For local development, it's easy to setup an SMPP simulator for testing
purposes. Vumi suggests using `SMPPSim <http://www.seleniumsoftware.com/user-
guide.htm#intro>`_. SMPPSim is a testing utility which mimics the behavior of
the Short Message Peer to Peer Protocol (SMPP) based Short Message Service
Center (SMSC).

.. note::

    SMPPSim requires Java. Please install Java before proceeding with these
    instructions.

To download SMPPSim, run the following commands::

    wget http://www.seleniumsoftware.com/downloads/SMPPSim.tar.gz
    tar zxf SMPPSim.tar.gz

SMPPSim runs on port 80 by default. Let's set this to a higher port to make it
easier to run without superuser privileges. Open ``conf/smppsim.props`` and
change the ``HTTP_PORT`` line to::

    HTTP_PORT=8080

You can use the provided shell scripts to start SMPPSim::

    chmod +x startsmppsim.sh
    ./startsmppsim.sh

Now visit `http://localhost:8080 <http://localhost:8080>`_ to use SMPPSim's web
interface. You'll use this interface to create mobile-originated (MO) messages
to send to Vumi.

Installing and setting up Vumi for the first time
=================================================

Clone the Vumi `GitHub repository <https://github.com/praekelt/vumi>`_::

    git clone git@github.com:rapidsms/vumi.git  # TODO: set to official Vumi repo when pull request has been merged
    cd vumi
    git checkout feature/issue-302-rapidsms-relay  # TODO: remove once merged into master

Install Vumi's Python dependencies::

    pip install requirements.pip

Setup the proper RabbitMQ user/vhost using the provided utility script::

    sudo ./utils/rabbitmq.setup.sh

Create ``config/rapidsms.yaml`` using the following configuration::

    smpp_transport:
      transport_name: "transport" 
      system_id: smppclient1  # username
      password: password      # password
      host: localhost         # the host to connect to
      port: 2775              # the port to connect to

    rapidsms_relay:
      transport_name: 'transport'
      rapidsms_url: "http://127.0.0.1:8000/backend/vumi-fake-smsc/"
      web_path: "/send/"
      web_port: 9000
      send_to:
        default:
          transport_name: 'transport'

    workers:
      smpp_transport: vumi.transports.smpp.SmppTransport
      rapidsms_relay: vumi.application.rapidsms_relay.RapidSMSRelay

This configures a Vumi ``SmppTransport`` to communicate to SMPPSim and a
VUMI ``RapidSMSRelay`` to communicate to RapidSMS.

Now we can start Vumi using our config file::

    twistd -n start_worker --worker-class vumi.multiworker.MultiWorker --config config/rapidsms.yaml


Adding a backend for the fake SMSC to RapidSMS
==============================================

Now that Vumi is installed and configured correctly, adding support for the
Vumi backend to your existing RapidSMS project is not difficult.  To begin,
simply add the following to your existing ``INSTALLED_BACKENDS`` configuration
in your ``settings.py`` file::

    INSTALLED_BACKENDS = {
        # ...
        # other backends, if any
        "vumi-fake-smsc" : {
            "ENGINE":  "rapidsms.backends.vumi.VumiBackend",
            "sendsms_url": "http://127.0.0.1:9000/send/",
        },
    }

Next, you need to add an endpoint to your ``urls.py`` for the newly created
backend.  You can do this like so::

    from django.conf.urls.defaults import *
    from rapidsms.backends.vumi.views import VumiBackendView
    
    urlpatterns = patterns('',
        # ...
        url(r"^backend/vumi-fake-smsc/$",
            VumiBackendView.as_view(backend_name="vumi-fake-smsc")),
    )

You can make the Django URL pattern whatever you like, but the convention is to
make it ``backend/`` followed by the name of your backend (from the settings
file) and a final ``/``.

Now, you should be able to start RapidSMS like so::

    ./manage.py runserver

That's it! Now you can use SMPPSim to send mobile-originated (MO) messages
through Vumi to RapidSMS.

Authentication
==============

If you've enabled basic authentication on the Vumi side, you can configure the Vumi backend with a username and password:

.. code-block:: python
   :emphasize-lines: 5,6

    INSTALLED_BACKENDS = {
        "vumi-fake-smsc" : {
            "ENGINE":  "rapidsms.backends.vumi.VumiBackend",
            "sendsms_url": "http://127.0.0.1:9000/send/",
            "sendsms_user": "username",
            "sendsms_pass": "password",
        },
    }
