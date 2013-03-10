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
* **Backends:** :doc:`Overview <topics/backends/index>` | :doc:`Kannel <topics/backends/kannel>` | :doc:`Vumi <topics/backends/vumi>`

**The development process**

* :doc:`Settings <ref/settings>`
* :doc:`Internationalization <topics/i18n>`
* :doc:`Extending core RapidSMS models <topics/extensible-models>`
* :doc:`Front end <topics/frontend>`
* :doc:`Testing <topics/testing>`
* :doc:`Scheduling Tasks with Celery <topics/celery>`
* :doc:`Deployment <topics/deployment>`

**RapidSMS contrib applications** (:doc:`Overview <topics/contrib/index>`)

* :doc:`default <topics/contrib/default>`
* :doc:`echo <topics/contrib/echo>`
* :doc:`handlers <topics/contrib/handlers>`
* :doc:`Message Tester <topics/contrib/httptester>`
* locations
* messagelog
* :doc:`messaging <topics/contrib/messaging>`
* registration

**The RapidSMS open-source project**

* :doc:`How to get involved <internals/contributing/index>`
* :doc:`Running the RapidSMS core test suite <internals/contributing/testing>`
* :doc:`Release notes and upgrading instructions <releases/index>`
* :doc:`License <internals/contributing/license>`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
