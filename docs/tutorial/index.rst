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

* :ref:`tutorial01`: Start a new RapidSMS project. Set up message tester. Write a minimal app that responds to a message. Put it through its paces.

* :ref:`tutorial02`: Configure the default app with a custom response. Recreate the minimal app from step 1, this time using a handler. Demonstrate keyword and pattern handlers.

* :ref:`tutorial03`: It's probably time to actually send and receive messages to telephones. Tropo has free development accounts and there's a Tropo backend at https://github.com/caktus/rapidsms-tropo. Walk through adding that to the project. Set up a Tropo development account. Demo the test app from step 2, this time using real messages.


4?) It'd be great to include a really simple web report too -- perhaps just some summary figures and a
    simple line chart of incoming responses.

5?) You should also add a virtualbox+vagrant installation option


MORE NOTES:

* Try to show an example where we're storing data from the text messages, but the data is modeled differently than just a thinly veiled list of the messages.  E.g. have a real patient model and update its data. (but... keep it simple!)


Start with :ref:`tutorial01`.

.. toctree::
    :hidden:

    tutorial01
    tutorial02
    tutorial03

.. _Django tutorial: https://docs.djangoproject.com/en/dev/intro/tutorial01/
