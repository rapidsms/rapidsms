.. RapidSMS documentation master file, created by
   sphinx-quickstart on Sun Oct 16 13:48:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :hidden:
    :glob:

    design/*
    internals/*
    internals/contributing/*
    internals/roadmap/*
    intro/*
    intro/install/*
    ref/*
    releases/*
    topics/*
    topics/applications/*
    topics/backends/*
    topics/contrib/*
    topics/router/*
    _themes/*


RapidSMS Documentation
=======================

Release: v\ |release|. (:doc:`Installation <intro/install/index>`, :doc:`Release Notes <releases/index>`)

**Getting Started**

* :doc:`Overview <intro/overview>`
* :doc:`Installation <intro/install/index>`

**Architecture**

* :doc:`RapidSMS architecture overview <topics/architecture>`
* **Router:** :doc:`Overview <topics/router/index>` | :doc:`Messaging <topics/router/messaging>` | :doc:`DatabaseRouter <topics/router/db>` | :doc:`CeleryRouter <topics/router/celery>`
* **Applications:** :doc:`Overview <topics/applications/index>` | :doc:`Community apps <topics/applications/community>`
* **Backends:** :doc:`Overview <topics/backends/index>` | :doc:`Kannel <topics/backends/kannel>` | :doc:`Vumi <topics/backends/vumi>` | :doc:`Custom <topics/backends/custom>`

**The development process**

* :doc:`Settings <ref/settings>`
* :doc:`Internationalization <topics/i18n>`
* :doc:`Extending core RapidSMS models <topics/extensible-models>`
* :doc:`Front end <topics/frontend>` - Creating a web interface for your app
* :doc:`Testing <topics/testing>`
* :doc:`Scheduling Tasks with Celery <topics/celery>`
* :doc:`Deployment <topics/deployment>`

**RapidSMS contrib applications**

* :doc:`default <topics/contrib/default>` - Sends a pre-defined default
  response to messages that are not handled by any other application.
* :doc:`echo <topics/contrib/echo>` - A collection of two simple handlers that
  can assist you in remote debugging.
* :doc:`handlers <topics/contrib/handlers>` - Extensible classes that help you
  create RapidSMS applications quickly.
* :doc:`httptester <topics/contrib/httptester>` - Helps you test your project
  by sending fake messages to RapidSMS to see how it responds.
* :doc:`locations <topics/contrib/locations>` - Defines the `Location` model,
  which helps you map custom locations and points in your project.
* :doc:`messagelog <topics/contrib/messagelog>` - Maintains a record of all
  messages sent and received by RapidSMS.
* :doc:`messaging <topics/contrib/messaging>` - Provides a web interface
  through which you can send messages to Contacts.
* registration

**The RapidSMS open-source project**

* :doc:`How to get involved <internals/contributing/index>`
* :doc:`Running the RapidSMS core test suite <internals/contributing/testing>`
* :doc:`Release notes and upgrading instructions <releases/index>`
* :doc:`License <internals/contributing/license>`

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
