.. RapidSMS documentation master file, created by
   sphinx-quickstart on Sun Oct 16 13:48:46 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

**Architecture**

* Overview
* :doc:`Router <topics/router>`
* Applications
* Backends
* Messages

**The development process**

* :doc:`Settings <ref/settings>`
* Extending core RapidSMS models
* Testing
* Deployment

**RapidSMS contrib applications**

* ``contrib.default``
* ``contrib.echo``
* ``contrib.export``
* ``contrib.handlers``
* ``contrib.httptester``
* ``contrib.locations``
* ``contrib.messagelog``
* ``contrib.messaging``
* ``contrib.registration``
* ``contrib.scheduler``

**The RapidSMS open-source project**

* About this documentation
* Team of core committers
* How to get involved
* :doc:`Running the RapidSMS core test suite <internals/contributing/testing>`
* Release notes and upgrading instructions


:doc:`Installation <main/installation>`

How to install RapidSMS on your computer and how to get started with community-contributed apps or developing your own.

:doc:`Rapid SMS Explained <main/rapidsms-explained>`

Various pages providing overviews, repository structures, and the technical architecture of RapidSMS. Think of this as a "RapidSMS for Dummies" type of section. A good place to peruse and learn concepts and vocabulary before digging into the code.

:doc:`RapidSMS Examples <main/rapidsms-examples>`

A few code examples of simple RapidSMS concepts.

:doc:`Sending and Receiving SMS <main/send-recv-sms>`

How to get SMS into the real world (modems, gateways, etc.)

:doc:`Differences with the new and old RapidSMS <main/differences>`

Here is a short explanation of a few of the new things that RapidSMS has for those who are used to the old RapidSMS. Also includes instructions for porting your apps to work with the latest version RapidSMS.

:doc:`Deployment <main/deployment>`

Tips and tricks for when you're ready to shove RapidSMS into the real world

:doc:`FAQ <main/faq>`

A FAQ containing Frequently Asked Questions

:doc:`Development <main/development>`

How to get involved and contribute to RapidSMS

:doc:`Testing <main/testing>`

How to run the test suite for RapidSMS

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

:doc:`i18n <misc/i18n>`

Internationalization

:doc:`Testing <misc/testing>`

Writing and running tests

:doc:`Editing <misc/editing>`

Find out how you can edit this wiki and what markup it uses

:doc:`Tutorial Videos <misc/tutorial-videos>`

Tips on recording RapidSMS tutorial videos in Linux

:doc:`Kannel Configuration <configuration/kannel>`

Configuring RapidSMS to work with the Kannel SMS gateway

:doc:`In Development <misc/indevelopment>`

A list of other repositories, all works in progress, of new apps for RapidSMS

Table of Contents
=================

.. toctree::
   releases/0.9.7.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

