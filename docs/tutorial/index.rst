.. _tutorial_overview:

RapidSMS Tutorial
=================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ

This tutorial will walk you through the creation of a simple RapidSMS
application.

We assume that you are familiar with Django, at least the material in the
`Django tutorial`_. If you haven't worked through that before, please start
there, then come back here when you feel comfortable with the concepts
there.


Outline
-------

* :doc:`Part 1 <tutorial01>`: Start a new RapidSMS project. Set up message tester. Write a minimal app that responds to a message. Put it through its paces.

* :doc:`Part 2 <tutorial02>`: Configure the default app with a custom response. Recreate the minimal app from step 1, this time using a handler. Demonstrate keyword and pattern handlers.

* :doc:`Part 3 <tutorial03>`: It's probably time to actually send and receive messages to telephones. Tropo has free development accounts and there's a Tropo backend at https://github.com/caktus/rapidsms-tropo. Walk through adding that to the project. Set up a Tropo development account. Demo the test app from step 2, this time using real messages.

  Sounds great. I really like the idea of walking through adding a functional backend for testing, but I'm not sure that tropo will work for folks outside of north america and europe -- https://www.tropo.com/docs/scripting/international_dialing_sms.htm

  I don't know much about the reach of Twilio or Clickatell (say there is testing for up to 10 messages, but it looks like a web form where one just sends a message). Perhaps if we reached out to them and suggest a testing sandbox for at least up to 10 messages.

4?) It'd be great to include a really simple web report too -- perhaps just some summary figures and a
    simple line chart of incoming responses.

5) You should also add a virtualbox+vagrant installation option


Start with :doc:`Part 1 <tutorial01>`.

.. toctree::
    :hidden:

    tutorial01
    tutorial02
    tutorial03

.. _Django tutorial: https://docs.djangoproject.com/en/dev/intro/tutorial01/
