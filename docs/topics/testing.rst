Testing RapidSMS Applications
=============================

Automated testing is an extremely useful tool and, therefore, we recomend
writing tests for all RapidSMS applications and projects. Tests provide a way
to repeatedly ensure that your code functions as expected and that new code
doesn't break existing functionality.

This document outlines the tools and best practices for writing RapidSMS tests.

Prerequisites
-------------

A RapidSMS test is written using standard Python and Django testing utilities.
If you're unfamiliar with these concepts, please take a moment to read through
the following links:

* Python's `unittest <http://docs.python.org/library/unittest.html>`_ module
* Django's `Testing <https://docs.djangoproject.com/en/dev/topics/testing/>`_ documentation, including:
    * `Writing tests <https://docs.djangoproject.com/en/dev/topics/testing/#writing-tests>`_
    * `Running tests <https://docs.djangoproject.com/en/dev/topics/testing/#running-tests>`_
    * `Testing tools <https://docs.djangoproject.com/en/dev/topics/testing/#testing-tools>`_

Additionally, since much of RapidSMS is Django-powered, these docs will not
cover testing standard Django aspects (views, models, etc.), but rather focus
on the areas unique to RapidSMS itself, specifically messaging and the router.

.. _what-to-test:

What To Test
************

Let's start with an example. Say you've written a quiz application,
``QuizMe``, that will send a question if you text the letter ``q`` to
RapidSMS::

    You: q
    RapidSMS: What color is the ocean? Answer with 'q ocean <answer>'
    You: q ocean red
    RapidSMS: Please try again!
    You: q ocean blue
    RapidSMS: Correct!

Additionally, if no questions exist, the application will inform you::

    You: q
    RapidSMS: No questions exist.

While the application is conceptually simple, determining what and how to test
can be a daunting task. To start, let's look a few areas that we could test:

* **Message parsing.** How does the application know the difference between ``q`` and ``q ocean blue``? Will it be confused by other input, like ``q   ocean   blue`` or ``quality``?
* **Workflow.** What happens when there aren't any questions in the database?
* **Logic testing.** Is the answer correct?

How to test these aspects is another question. Generally speaking, it's best
practice, and conceptually the easiest, to test the smallest units of your
code. For example, say you have a function to test if an answer is correct::

    class QuizMeApp(AppBase):

        def check_answer(self, question, answer_text):
            """Return if guess is correct or not"""

            guess = answer_text.lower()
            answer = question.correct_answer.lower()
            return guess == answer

Writing a test that uses ``check_answer`` directly will verify the correctness
of that function alone. With that test written, you can write higher level
tests knowing that ``check_answer`` is covered and will only fail if the logic
changes inside of it.

The following sections describe the various methods and tools to use for
testing your RapidSMS applications.

Testing Methods
---------------

.. _general-testing:

General Testing
***************

RapidSMS provides a suite of test harness tools, but the most flexible and
natural tool is ``MockBackendRouter``. ``MockBackendRouter`` extends from
``CustomRouter``, which allows you to specify the router and backends to use
for each test. ``MockBackendRouter`` takes this a step further to setup a test
backend that can be examined during the testing process.

.. class:: CustomRouter

    .. attribute:: router_class

        String to override :setting:`RAPIDSMS_ROUTER` during testing. Defaults to ``'rapidsms.router.blocking.BlockingRouter'``.

    .. attribute:: backends

        Dictionary of backends to use during testing.

.. class:: MockBackendRouter

    .. attribute:: backends

        Defaults to ``{'mockbackend': {'ENGINE': backend.MockBackend}}``.

    .. attribute:: outbox

        The list of outgoing messages sent through ``mockbackend``.

    .. method:: clear()

        Manually empty the outbox of ``mockbackend``.

    .. method:: receive(text, backend_name='mockbackend', identity=None, connection=None, fields=None)

        A wrapper around the ``receive`` API that defaults to using ``mockbackend``. See :ref:`receiving-messages`.

    .. method:: send(text, backend_name='mockbackend', identity=None, connection=None)

        A wrapper around the ``send`` API that defaults to using ``mockbackend``. See :ref:`sending-messages`.

Examples
~~~~~~~~

Outbox Testing
^^^^^^^^^^^^^^

``MockBackendRouter`` provides full access to analyze sent messages. For
example, if you want to make sure the proper response was sent after receiving
a message, you can use the ``outbox`` property::

    from django.test import TestCase
    from rapidsms.tests.harness.base import MockBackendRouter

    class QuizMeGeneralTest(MockBackendRouter, TestCase):

        def test_no_questions(self):
            """Outbox should contain a message explaining no questions exist"""

            self.receive('q', identity='1112223333')
            self.assertEqual(self.outbox[0].text, 'No questions exist.')

This example uses ``self.receive`` to pass a new message to the router. The
test then examines ``self.outbox`` to make sure the proper message was sent in
response.

Database Interaction
^^^^^^^^^^^^^^^^^^^^

``MockBackendRouter`` provides flexible means to check application state,
including the database. Here's an example of a test that examines the database
after receiving a message::

    from django.test import TestCase
    from rapidsms.tests.harness.base import MockBackendRouter
    from quizme.models import Question, Answer

    class QuizMeGeneralTest(MockBackendRouter, TestCase):

        def test_question_answer(self):
            """Outbox should contain question promt and answer should be recorded in database"""

            Question.objects.create(short_name='ocean',
                                    text="What color is the ocean?",
                                    correct_answer='Blue')
            msg = self.receive('q ocean blue', identity='1112223333')
            # user should receive "correct" response
            self.assertEqual(self.outbox[0].text, 'Correct!')
            # answer from this interaction should be stored in database
            answer = Answer.objects.all()[0]
            self.assertTrue(answer.correct)
            self.assertEqual(msg.connection, answer.connection)


Application Logic
*****************

If you have application logic that doesn't depend on message processing
directly, you can always test it indepdently of the router API. RapidSMS
applications are just Python classes, so you can construct your app inside of
your test suite. For example::

    from django.test import TestCase
    from rapidsms.router.test import TestRouter
    from quizme.app import QuizMeApp

    class QuizMeLogicTest(TestCase):

        def setUp(self):
            # construct the app we want to test with the TestRouter
            self.app = QuizMeApp(TestRouter())

        def test_inquiry(self):
            """Messages with only the letter "q" are quiz messages"""

            self.assertTrue(self.app.is_quiz("q"))

        def test_inquiry_whitespace(self):
            """Message inquiry whitespace shouldn't matter"""

            self.assertTrue(self.app.is_quiz(" q "))

        def test_inquiry_skip(self):
            """Only messages starting with the letter q should be considered"""

            self.assertFalse(self.app.is_quiz("quantity"))
            self.assertFalse(self.app.is_quiz("quality 50"))

This example tests the logic of ``QuizMeApp.is_quiz``, which is used to
determine whether or not the text message is related to the quiz application.
The app is constructed with ``TestRouter`` and tests ``is_quiz`` with various
types of input.

This method is useful for testing specific, low-level components of your
application. Since the routing architecture isn't loaded, these tests will
also execute very quickly.

Scripted Tests
**************

You can write high-level integration tests for your applications by using the
``TestScript`` framework. ``TestScript`` allows you to write message *scripts*
(akin to a movie script), similar to our example in the :ref:`what-to-test`
section above::

    You: q
    RapidSMS: What color is the ocean? Answer with 'q ocean <answer>'
    You: q ocean blue
    RapidSMS: Correct!

The main difference is the syntax::

    1112223333 > q
    1112223333 < What color is the ocean? Answer with 'q ocean <answer>'
    1112223333 > q ocean blue
    1112223333 < Correct!

The script is interpreted like so:

* **number > message-text**
    * Represents an incoming message from **number** whose contents is **message-text**
* **number < message-text**
    * Represents an outoing message sent to **number** whose contents is **message-text**

The entire script is parsed and executed against the RapidSMS router.

Example
~~~~~~~

To use this functionality in your test suite, you simply need to extend from
``TestScript`` to get access to ``runScript``::

    from django.test import TestCase
    from rapidsms.tests.harness.scripted import TestScript
    from quizme.app import QuizMeApp
    from quizme.models import Question

    class QuizMeScriptTest(TestScript, TestCase):
        apps = (QuizMeApp,)

        def test_correct_script(self):
            """Test full script with correct answer"""

            Question.objects.create(short_name='ocean',
                                    text="What color is the ocean?",
                                    correct_answer='Blue')
            self.runScript("""
                1112223333 > q
                1112223333 < What color is the ocean? Answer with 'q ocean <answer>'
                1112223333 > q ocean blue
                1112223333 < Correct!
            """)

This example uses ``runScript`` to execute the interaction against the RapidSMS
router. ``apps`` must be defined at the class level to tell the test suite
which apps the router should load. In this case, only one app was required,
``QuizMeApp``.

This test method is particularly useful when executing high-level integration
tests across multiple RapidSMS applications. However, you're limited to the
test script. If you need more fined grained access, like checking the state of
the database in the middle of a script, you should use :ref:`general-testing`.
