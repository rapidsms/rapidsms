Testing RapidSMS Applications
=============================

Automated testing is an extremely useful tool and, therefore, we recomend writing tests for all RapidSMS applications and projects. Tests provide a way to repeatedly ensure that your code functions as expected and that new code doesn't break existing functionality.

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

What To Test
************

Let's start with an example. Say you've written a quiz application, ``QuizMe``, that will send a question if you text the letter ``q`` to RapidSMS::

    You: q
    RapidSMS: What color is the ocean? Answer with 'q ocean <answer>'
    You: q ocean red
    RapidSMS: Please try again!
    You: q ocean blue
    RapidSMS: Correct!

Additionally, if no questions exist, the application will inform you::

    You: q
    RapidSMS: No questions exist.

While the application is conceptually simple, determining what and how to test can be a daunting task. To start, let's look a few areas that we could test:

* **Message parsing.** How does the application know the difference between ``q`` and ``q ocean blue``? Will it be confused by other input, like ``q   ocean   blue`` or ``quality``?
* **Workflow.** What happens when there aren't any questions in the database?
* **Logic testing.** Is the answer correct?

How to test these aspects is another question. Generally speaking, it's best practice, and conceptually the easiest, to test the smallest units of your code. For example, say you have a function to test if an answer is correct::

    class QuizMeApp(AppBase):

        def check_answer(self, question, answer_text):
            """Return if guess is correct or not"""

            guess = answer_text.lower()
            answer = question.correct_answer.lower()
            return guess == answer

Writing a test that uses ``check_answer`` directly will verify the correctness of that function alone. With that test written, you can write higher level tests knowing that ``check_answer`` is covered and will only fail if the logic changes inside of it.

The following sections describe the various methods and tools to use for testing your RapidSMS applications.

Testing Methods
---------------

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
