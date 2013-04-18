.. _vumi-backend:
.. _vumi_configuration:

=============================
Setting up RapidSMS with Vumi
=============================

`Vumi <http://vumi.org/>`_ is a free and open source super scalable messaging
platform written in Python. Vumi can connect to third party gateways via
protocols like HTTP and SMPP. Please read `Vumi's documentation
<http://vumi.readthedocs.org/en/latest/>`_ for additional information.

The following guide will help you setup Vumi on Ubuntu to talk to a SMPP
simulator and RapidSMS installation.

.. _vumi-smppsim:

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

.. note::

    As of this writing, the RapidSMS/Vumi integration is planned for merge into
    an official Vumi release, but currently resides in the
    ``feature/issue-302-rapidsms-relay`` Vumi branch. When complete, we
    will update this documentation accordingly.

Clone the Vumi `GitHub repository <https://github.com/praekelt/vumi>`_::

    git clone git@github.com:praekelt/vumi.git
    cd vumi
    git checkout feature/issue-302-rapidsms-relay

Install Vumi's Python dependencies::

    pip install -r requirements.pip

Setup the proper RabbitMQ user/vhost using the provided utility script::

    sudo ./utils/rabbitmq.setup.sh

Create ``config/rapidsms.yaml`` using the following configuration:

.. code-block:: yaml

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
                from_addr: '1234' # not set automatically by SMSC

    workers:
        smpp_transport: vumi.transports.smpp.SmppTransport
        rapidsms_relay: vumi.application.rapidsms_relay.RapidSMSRelay

This configures a Vumi ``SmppTransport`` to communicate to 
:ref:`SMPPSim <vumi-smppsim>` and a Vumi ``RapidSMSRelay`` to communicate to 
RapidSMS. While not required for this setup, you'll need to set ``from_addr`` 
to your phone number if using a real SMSC.

Now we can start Vumi using our config file::

    twistd -n start_worker --worker-class vumi.multiworker.MultiWorker --config config/rapidsms.yaml


Adding a backend for the fake SMSC to RapidSMS
==============================================

Now that Vumi is installed and configured correctly, adding support for the
Vumi backend to your existing RapidSMS project is not difficult.  To begin,
simply add the following to your existing :setting:`INSTALLED_BACKENDS`:

.. code-block:: python
    :emphasize-lines: 4-7

    INSTALLED_BACKENDS = {
        # ...
        # other backends, if any
        "vumi-fake-smsc": {
            "ENGINE":  "rapidsms.backends.vumi.VumiBackend",
            "sendsms_url": "http://127.0.0.1:9000/send/",
        },
    }

Next, you need to add an endpoint to your ``urls.py`` for the newly created
backend.  You can do this like so:

.. code-block:: python
    :emphasize-lines: 2,6-7

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

Vumi can be protected with basic authentication. To enable it on the Vumi side,
create a ``passwords`` directive in the ``rapidsms_relay`` configuration:

.. code-block:: yaml
    :emphasize-lines: 10-11

    rapidsms_relay:
        transport_name: 'transport'
        rapidsms_url: "http://127.0.0.1:8000/backend/vumi-fake-smsc/"
        web_path: "/send/"
        web_port: 9000
        send_to:
            default:
                transport_name: 'transport'
                from_addr: '1234' # not set automatically by SMSC
        vumi_username: 'username'
        vumi_password: 'password'

Then you can update :setting:`INSTALLED_BACKENDS` with ``sendsms_user`` and
``sendsms_pass``:

.. code-block:: python
   :emphasize-lines: 5-6

    INSTALLED_BACKENDS = {
        "vumi-fake-smsc": {
            "ENGINE":  "rapidsms.backends.vumi.VumiBackend",
            "sendsms_url": "http://127.0.0.1:9000/send/",
            "sendsms_user": "username",
            "sendsms_pass": "password",
        },
    }
