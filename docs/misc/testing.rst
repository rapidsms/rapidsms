Instructions running the RapidSMS automated tests
===================================================

It's not currently possible to test RapidSMS outside of a project. So, if you haven't already, follow the instructions on the Installation page to get setup with a project.

RapidSMS requires django_nose to run its tests, so ensure that it's installed and up to date. This may happen automatically if you use pip or easy_install to install RapidSMS.
::

    pip install --upgrade django-nose


In the settings.py file in your project directory, ensure your TEST_RUNNER is configured to use django_nose::

    TEST_RUNNER = "django_nose.NoseTestSuiteRunner"


Next, you can run all of the RapidSMS tests by typing::

    ./manage.py test rapidsms

Note that this runs all of the RapidSMS tests. When using django_nose, the argument to ./manage.py test is a package name, not an application name. This means Nose will find all tests under the "rapidsms" package.

Apart from standard python and django tests, we used to have an SMS testing framework, which is currently being updated to work with the latest version of RapidSMS.

Writing tests for your apps
==============================

You can write integration tests for your applications by using the TestScript framework. Just create a tests.py file in your app directory. Any TestCase that extends TestScript can take advantage of the assertInteraction method to test outgoing messages and their responses.

The string passed to assertInteraction is parsed into a script that is executed against the RapidSMS router. Each line which contains a > is interpreted as an incoming message from the number to the left of the >. Each line which contains a < represents a response from RapidSMS to the number to the left of the <.

Here is an example test case for the registration application::

    import unittest
    from rapidsms.tests.scripted import TestScript

    class TestRegister(TestScript):

        def testRegister(self):
            self.assertInteraction("""
                8005551212 > register as someuser
                8005551212 < Thank you for registering, as someuser!
            """)
