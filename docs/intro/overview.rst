RapidSMS Overview
=================

.. image:: /_static/phone.jpg
    :align: center

RapidSMS is a free and open-source framework for dynamic data collection,
logistics coordination and communication, leveraging basic short message
service (SMS) mobile phone technology. It can be used by anyone and because one
size does not fit all and no two projects are exactly the same, RapidSMS is
easily customized to meet the specific needs of the project and is scalable at
an enterprise level. It is currently being utilized by large multilateral
organizations (such as the United Nations), development professionals (such as
the Earth Institute at Columbia University), and small NGOs and CBOs (such as
Tostan).

RapidSMS is written in `Python`_ and `Django`_ and is a *framework* for building
highly customized applications. While there are increasingly more and more
pre-configured applications being created for RapidSMS, most projects will
continue to benefit from applications designed specifically to meet the need
and demands of their stakeholders.

RapidSMS at a glance
--------------------

The goal of this section is to give you enough technical specifics to
understand how RapidSMS works, but this isn’t intended to be a tutorial or
reference. When you're ready to start a project, you can :doc:`install RapidSMS
<install/index>` and begin writing your own custom applications.

As a quick example, here's how we might create a simple application, written in
Python, that replies 'pong' after receiving the message 'ping':

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    from rapidsms.apps.base import AppBase

    class PingPong(AppBase):

        def handle(self, msg):
            """Respond to 'ping' messages with 'pong'"""
            if msg.text == 'ping':
                msg.respond('pong')
                return True
            return False

This is just the surface
------------------------

This has been only a quick overview of RapidSMS's functionality.  The next
obvious steps are for you to :doc:`install RapidSMS <install/index>`, read the
tutorial and :doc:`join the community <../internals/contributing/index>`.
Thanks for your interest!

.. _Python: http://python.org/
.. _Django: https://www.djangoproject.com/
