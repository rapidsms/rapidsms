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
    topics/send-recv-sms
    intro/install/index
    topics/architecture
    topics/applications/index
    topics/backends/index
    topics/router/index
    design/apps
    topics/deployment/index
    topics/contrib/index
    internals/contributing/index
    releases/index
    internals/index

Release: v\ |release|. (:doc:`Installation <intro/install/index>`, :doc:`Release Notes <releases/index>`)

**Getting Started**

* :doc:`Overview <intro/overview>`
* :doc:`So you want to build an SMS service <topics/send-recv-sms>`
* :doc:`Installation <intro/install/index>`

**Architecture**

* :doc:`RapidSMS architecture overview <topics/architecture>`
* **Router:** :doc:`Overview <topics/router/index>` | :doc:`Messaging API <topics/router/messaging>` | :doc:`BlockingRouter <topics/router/blocking>` | :doc:`CeleryRouter <topics/router/celery>` | :doc:`DatabaseRouter <topics/router/db>`
* **Applications:** :doc:`Overview <topics/applications/index>` | :doc:`Community apps <topics/applications/community>`
* **Backends:** :doc:`Overview <topics/backends/index>` | :doc:`Kannel <topics/backends/kannel>` | :doc:`Vumi <topics/backends/vumi>` | :doc:`Database <topics/backends/database>` | :doc:`Custom <topics/backends/custom>`

**The development process**

* :doc:`Writing RapidSMS Applications <design/apps>`
* :doc:`Settings <ref/settings>`
* :doc:`Internationalization <topics/i18n>`
* :doc:`Extending core RapidSMS models <topics/extensible-models>`
* :doc:`Front end <topics/frontend>` - Creating a web interface for your app
* :doc:`Testing <topics/testing>`
* :doc:`Scheduling Tasks with Celery <topics/celery>`

**Deployment**

* :doc:`Overview <topics/deployment/index>`
* :doc:`Planning <topics/deployment/planning>`
* :doc:`Provisioning <topics/deployment/provisioning>`
* :doc:`Deploying <topics/deployment/deploying>`

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
* :doc:`registration <topics/contrib/registration>` - Provides a web interface
  for creating, updating, and deleting RapidSMS contacts.

**The RapidSMS open-source project**

* :doc:`How to get involved <internals/contributing/index>`
* :doc:`Running the RapidSMS core test suite <internals/contributing/testing>`
* :doc:`Release notes and upgrading instructions <releases/index>`
* :doc:`Release process <internals/contributing/release-process>` - The release cycle
* :doc:`Release checklist <internals/contributing/release-checklist>` - How to release a new version
* :doc:`License <internals/contributing/license>` - How RapidSMS is licensed

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
