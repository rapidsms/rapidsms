.. RapidSMS documentation master file, created by
   sphinx-quickstart on Sun Oct 16 13:48:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RapidSMS Documentation
=======================

.. This toctree is not displayed, but it controls the navigation order
   through the documentation (next/previous etc).

.. It MUST therefore be kept in the same order as the displayed contents
   below, or it will be very confusing.
   Some of these are links to pages that have their own .toctree's,
   which will be worked into the overall navigation correctly by
   Sphinx, so we don't need to include all the subpages here.

.. toctree::
    :maxdepth: 2
    :hidden:

    intro/overview
    intro/install/index
    tutorial/index
    topics/help
    topics/architecture
    topics/applications/index
    topics/backends/index
    topics/router/index
    topics/virtualenv
    ref/settings
    topics/i18n
    topics/extensible-models
    topics/frontend
    topics/logging
    topics/testing
    topics/celery
    topics/packaging
    topics/deployment/index
    developing/index
    community/index
    topics/contrib/index
    releases/index
    internals/index
    license

Release: v\ |release|. (:doc:`Installation <intro/install/index>`, :doc:`Release Notes <releases/index>`)

**Getting Started**

* :doc:`Overview <intro/overview>`
* :doc:`Installation <intro/install/index>`
* :doc:`Tutorial <tutorial/index>`
* :doc:`Getting help <topics/help>`
* :doc:`Release notes and upgrading instructions <releases/index>`

**Architecture**

* :doc:`RapidSMS architecture overview <topics/architecture>`
* **Router:** :doc:`Overview <topics/router/index>` | :doc:`Messaging API <topics/router/messaging>` | :doc:`BlockingRouter <topics/router/blocking>` | :doc:`CeleryRouter <topics/router/celery>` | :doc:`DatabaseRouter <topics/router/db>`
* **Applications:** :doc:`Overview <topics/applications/index>` | :doc:`Community apps <topics/applications/community>`
* **Backends:** :doc:`Overview <topics/backends/index>` | :doc:`Kannel <topics/backends/kannel>` | :doc:`Vumi <topics/backends/vumi>` | :doc:`Database <topics/backends/database>` | :doc:`Custom <topics/backends/custom>`

**The development process**

* :doc:`Virtual environments <topics/virtualenv>`
* :doc:`Settings <ref/settings>`
* :doc:`Internationalization <topics/i18n>`
* :doc:`Extending core RapidSMS models <topics/extensible-models>`
* :doc:`Front end <topics/frontend>` - Creating a web interface for your app
* :doc:`Logging <topics/logging>`
* :doc:`Testing <topics/testing>`
* :doc:`Scheduling Tasks with Celery <topics/celery>`
* :doc:`Packaging a RapidSMS application for re-use <topics/packaging>`

**Provisioning & Deploying Your Project**

* :doc:`Overview <topics/deployment/index>`
* :doc:`Planning <topics/deployment/planning>`
* :doc:`Provisioning <topics/deployment/provisioning>`
* :doc:`Deploying <topics/deployment/deploying>`
* :doc:`Scaling <topics/deployment/scaling>`

**The RapidSMS open-source project**

* :ref:`developing-rapidsms`
* :ref:`rapidsms-community`
* :ref:`License <rapidsms-license>` - How RapidSMS is licensed

**RapidSMS contrib applications**

* :doc:`default <topics/contrib/default>` - Sends a pre-defined default
  response to messages that are not handled by any other application.
* :doc:`echo <topics/contrib/echo>` - A collection of two simple handlers that
  can assist you in remote debugging.
* :doc:`handlers <topics/contrib/handlers>` - Extensible classes that help you
  create RapidSMS applications quickly.
* :doc:`httptester <topics/contrib/httptester>` - Helps you test your project
  by sending fake messages to RapidSMS to see how it responds.
* :doc:`messagelog <topics/contrib/messagelog>` - Maintains a record of all
  messages sent and received by RapidSMS.
* :doc:`messaging <topics/contrib/messaging>` - Provides a web interface
  through which you can send messages to Contacts.
* :doc:`registration <topics/contrib/registration>` - Provides a web interface
  for creating, updating, and deleting RapidSMS contacts.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
