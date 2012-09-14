.. RapidSMS documentation master file, created by
   sphinx-quickstart on Sun Oct 16 13:48:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :hidden:
    :glob:

    configuration/*
    design/*
    examples/*
    installation/*
    internals/*
    internals/contributing/*
    internals/roadmap/*
    main/*
    messaging/*
    misc/*
    ref/*
    releases/*
    topics/*
    topics/backends/*


RapidSMS Documentation
=======================

RapidSMS is a free and open-source framework for dynamic data collection, logistics coordination and communication, leveraging basic short message service (SMS) mobile phone technology. It is written in Python and uses Django.

* **Website**: http://www.rapidsms.org/

* **Documentation**: http://rapidsms.readthedocs.org/

* **Code**: http://github.com/rapidsms/rapidsms

* **Google Group**: http://groups.google.com/group/rapidsms

* **Youtube Channel**: http://www.youtube.com/user/rapidsmsdev

* **RapidSMS IRC Channel archives**: http://irc.rapidsms.org (#RapidSMS also accessible via browser at http://webchat.freenode.net/)

Destinations
=============

**Getting Started**

* :doc:`Overview <intro/overview>`
* :doc:`Installation <intro/install>`
* Tutorial

**Architecture**

* Overview
* **Router:** :doc:`Overview <topics/router>` | :doc:`Messaging <topics/messaging>`
* Applications
* **Backends:** :doc:`Overview <topics/backends/index>` | :doc:`Kannel <topics/backends/kannel>` | :doc:`Vumi <topics/backends/vumi>` | :doc:`3rd Party <topics/backends/3rd-party>`

**The development process**

* :doc:`Settings <ref/settings>`
* :doc:`Internationalization <topics/i18n>`
* :doc:`Extending core RapidSMS models <topics/extensible-models>`
* :doc:`Testing <topics/testing>`
* :doc:`Deployment <topics/deployment>`

**RapidSMS contrib applications**

* default
* echo
* export
* :doc:`handlers <topics/contrib/handlers>`
* httptester
* locations
* messagelog
* messaging
* registration
* scheduler

**The RapidSMS open-source project**

* About this documentation
* Team of core committers
* :doc:`How to get involved <internals/contributing/release-process>`
* :doc:`GitHub group and repositories <internals/contributing/repository>`
* :doc:`Running the RapidSMS core test suite <internals/contributing/testing>`
* Release notes and upgrading instructions

:doc:`Rapid SMS Explained <main/rapidsms-explained>`

Various pages providing overviews, repository structures, and the technical architecture of RapidSMS. Think of this as a "RapidSMS for Dummies" type of section. A good place to peruse and learn concepts and vocabulary before digging into the code.

:doc:`FAQ <main/faq>`

A FAQ containing Frequently Asked Questions

RapidSMS Apps
============== 

One day soon, all usable RapidSMS apps will be found or linked to from the following repositories:

* http://github.com/rapidsms/rapidsms-contrib-apps-dev (optional apps, restricted committers)

* http://github.com/rapidsms/rapidsms-community-apps-dev (optional apps, open committers)

* http://github.com/nyaruka/rapidsms-xforms (interactive form builder)

Misc
=====

:doc:`PyCharm License <misc/pycharm-license>`

How to get RapidSMS's open source license for PyCharm, JetBrains Python/Django IDE.





:doc:`Editing <misc/editing>`

Find out how you can edit this wiki and what markup it uses

:doc:`Tutorial Videos <misc/tutorial-videos>`

Tips on recording RapidSMS tutorial videos in Linux

:doc:`In Development <misc/indevelopment>`

A list of other repositories, all works in progress, of new apps for RapidSMS

Table of Contents
=================

.. toctree::
   releases/0.10.0.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

