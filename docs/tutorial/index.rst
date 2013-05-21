.. _tutorial_overview:

RapidSMS Tutorial
=================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ

This tutorial will walk you through the creation of a simple RapidSMS
application.

RapidSMS builds on the Django web development frameowork.
We assume that you are familiar with Django, at least the material in the
`Django tutorial`_. If you haven't worked through that before, please start
there, then come back here when you feel comfortable with the concepts
there.

Outline
-------

* :ref:`tutorial01`: Start a new RapidSMS project. Set up message tester.
  Write a minimal app that responds to a message. Put it through its paces.

* :ref:`tutorial02`: Configure the default app with a custom response.
  Demonstrate keyword and pattern handlers.

* :ref:`tutorial03`: Make a RapidSMS app that uses Django to store and update
  data.

* :ref:`tutorial04`: It's probably time to actually send and receive
  messages to telephones. Tropo has free development accounts and there's
  a Tropo backend at https://github.com/caktus/rapidsms-tropo. Walk through
  adding that to the project. Set up a Tropo development account. Demo
  the test app from step 2, this time using real messages.

Start with :ref:`tutorial01`.

.. toctree::
    :hidden:

    tutorial01
    tutorial02
    tutorial03
    tutorial04

.. _Django tutorial: https://docs.djangoproject.com/en/dev/intro/tutorial01/
