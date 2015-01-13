Testing RapidSMS Applications
=============================

Automated testing is an extremely useful tool and, therefore, we recommend
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

RapidSMS provides a suite of test harness tools. Below you'll find a collection
of :py:class:`django.test.TestCase` extensions to make testing your RapidSMS applications easier.

.. _rapidtest:

RapidTest
~~~~~~~~~

The :py:class:`~rapidsms.tests.harness.RapidTest` class provides a simple test environment to analyze sent and
received messages. You can inspect messages processed by the router and, if
needed, see if messages were delivered to a special backend, ``mockbackend``.
Let's take a look at a simple example::

    from rapidsms.tests.harness import RapidTest

    class QuizMeStackTest(RapidTest):

        def test_no_questions(self):
            """Outbox should contain message explaining no questions exist"""
            self.receive('q', self.lookup_connections('1112223333')[0])
            self.assertEqual(self.outbound[0].text, 'No questions exist.')

In this example, we want to make sure that texting ``q`` into our application
will return the proper message if no questions exist in our database. We use
``receive`` to communicate to the router and ``lookup_connections`` to create a
``connection`` object to bundle with the message. Our app will respond with a
special message, ``No questions exist``, if the database isn't populated, so we
inspect the ``outbound`` property to see if it contains the proper message
text. That's it! With just a few lines we were able to send a message through
the entire routing stack and verify the functionality of our application.

.. autoclass:: rapidsms.tests.harness.RapidTest
    :members:


Database Interaction
^^^^^^^^^^^^^^^^^^^^

:py:class:`~rapidsms.tests.harness.RapidTest` provides flexible means to check application state, including
the database. Here's an example of a test that examines the database after
receiving a message::

    from rapidsms.tests.harness import RapidTest
    from quizme.models import Question, Answer

    class QuizMeGeneralTest(RapidTest):

        def test_question_answer(self):
            """Outbox should contain question promt and answer should be recorded in database"""

            Question.objects.create(short_name='ocean',
                                    text="What color is the ocean?",
                                    correct_answer='Blue')
            msg = self.receive('q ocean blue', self.lookup_connections('1112223333')[0])
            # user should receive "correct" response
            self.assertEqual(self.outbound[0].text, 'Correct!')
            # answer from this interaction should be stored in database
            answer = Answer.objects.all()[0]
            self.assertTrue(answer.correct)
            self.assertEqual(msg.connection, answer.connection)


Application Logic
*****************

If you have application logic that doesn't depend on message processing
directly, you can always test it independently of the router API. RapidSMS
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
The app is constructed with :py:class:`~rapidsms.router.test.TestRouter` and tests ``is_quiz`` with various
types of input.

This method is useful for testing specific, low-level components of your
application. Since the routing architecture isn't loaded, these tests will
also execute very quickly.

Scripted Tests
**************

You can write high-level integration tests for your applications by using the
:py:class:`~rapidsms.tests.harness.TestScript` framework.
:py:class:`~rapidsms.tests.harness.TestScript`
allows you to write message *scripts*
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
:py:class:`~rapidsms.tests.harness.TestScript` or
:py:class:`~rapidsms.tests.harness.TestScriptMixin`
to get access to
:py:meth:`~rapidsms.tests.harness.TestScriptMixin.runScript`::

    from rapidsms.tests.harness import TestScript
    from quizme.app import QuizMeApp
    from quizme.models import Question

    class QuizMeScriptTest(TestScript):
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

.. autoclass:: rapidsms.tests.harness.TestScript
    :members:

.. autoclass:: rapidsms.tests.harness.TestScriptMixin
    :members:

.. class:: rapidsms.tests.harness.scripted.TestScriptMixin

    Full name of :py:class:`rapidsms.tests.harness.TestScriptMixin`.


Test Helpers
************

Below you'll find a list of mixin classes to help ease unit testing. Most of
these mixin classes are used by the RapidSMS test classes for convenience, but
you can also use these test helpers independently if needed.


CreateDataMixin
~~~~~~~~~~~~~~~

The ``CreateDataMixin`` class can be used with standard ``TestCase`` classes to
make it easier to create common RapidSMS models and objects. For example::

    from django.test import TestCase
    from rapidsms.tests.harness import CreateDataMixin

    class ExampleTest(CreateDataMixin, TestCase):

        def test_my_app_function(self):
            contact1 = self.create_contact()
            contact2 = self.create_contact({'name': 'John Doe'})
            connection = self.create_connection({'contact': contact1})
            text = self.random_string()
            # ...

.. autoclass:: rapidsms.tests.harness.CreateDataMixin
    :members:

.. class:: rapidsms.tests.harness.base.CreateDataMixin

    Full name for :py:class:`rapidsms.tests.harness.CreateDataMixin`.

CustomRouterMixin
~~~~~~~~~~~~~~~~~

The ``CustomRouterMixin`` class allows you to override the :setting:`RAPIDSMS_ROUTER` and :setting:`INSTALLED_BACKENDS` settings. For example:

.. code-block:: python

    from django.test import TestCase
    from rapidsms.tests.harness import CustomRouterMixin

    class ExampleTest(CustomRouterMixin, TestCase)):

        router_class = 'path.to.router'
        backends = {'my-backend': {'ENGINE': 'path.to.backend'}}

        def test_sample(self):
            # this test will use specified router and backends
            pass

.. autoclass:: rapidsms.tests.harness.CustomRouterMixin
    :members:


.. class:: rapidsms.tests.harness.router.CustomRouterMixin

    Full name for :py:class:`rapidsms.tests.harness.CustomRouterMixin`.


TestRouterMixin
~~~~~~~~~~~~~~~

``TestRouterMixin`` extends CustomRouterMixin and arranges for tests
to use the :py:class:`rapidsms.router.test.TestRouter`.

.. autoclass:: rapidsms.tests.harness.TestRouterMixin
    :members:

    .. attribute:: apps

        A list of app classes to load, rather than ``INSTALLED_APPS``, when the
        router is initialized.


.. class:: rapidsms.tests.harness.router.TestRouterMixin

    Full name for :py:class:`rapidsms.tests.harness.TestRouterMixin`.


TestRouter
~~~~~~~~~~

The ``TestRouter`` can be used in tests. It saves all messages for later
inspection by the test.

.. autoclass:: rapidsms.router.test.TestRouter
    :members:


DatabaseBackendMixin
~~~~~~~~~~~~~~~~~~~~

The ``DatabaseBackendMixin`` helps tests to use the DatabaseBackend.

.. autoclass:: rapidsms.tests.harness.DatabaseBackendMixin
    :members:


LoginMixin
~~~~~~~~~~

.. autoclass:: rapidsms.tests.harness.LoginMixin
    :members:

.. class:: rapidsms.tests.harness.base.LoginMixin

    Full name for :py:class:`rapidsms.tests.harness.LoginMixin`.

Django TestCase
~~~~~~~~~~~~~~~

Some of these classes inherit from:

.. class:: django.test.testcases.TestCase

which is the full name for :py:class:`django.test.TestCase`.
