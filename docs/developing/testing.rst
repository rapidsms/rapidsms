.. _test_suite:

RapidSMS core test suite
========================

We expect all new and changed code to include tests for the new or changed
behavior. Having as complete a set of tests as possible is important so
we can have confidence that when we make a change in one place, we haven't
broken something else.

RapidSMS provides several configuration options and entry points for continuous
integration. The unit tests can be run in the current python environment or
automated to run in several environments and can include coverage reports.

Quickstart
----------

The easiest way to run the unit tests in a new install is to run the following
from the project root::

    pip install tox
    tox

The settings found in the /tests/default.py module are intended as the default
settings file for running tests. This will also build the docs, run flake8, look
for missing migrations, and run coverage.

.. _pep-eight-adherence:

PEP 8 Style Guidelines Adherence
--------------------------------

RapidSMS adheres to the Python `PEP 8
<http://www.python.org/dev/peps/pep-0008/>`_ style guidelines for all Python
source outside of the ``docs/`` directory.  As such, please check your code
against the PEP 8 specification by using the ``flake8`` linting tool in your
RapidSMS directory before submitting patches for review::

    flake8

Note that the ``tox`` command above also will do this.

Testing multiple environments
-----------------------------

RapidSMS uses `Tox <http://tox.readthedocs.org/en/latest/index.html>`_ to run
the test suite in a variety of environments. You can test all environments
together or specific ones::

    tox                 # all environments
    tox -e py34-dj19   # only test using Python 3.4 and Django 1.9

See the ``tox.ini`` file for a list of the available environments.

You can also add additional environments or change other parts of the
configuration in your local copy of the ``tox.ini`` by following the `tox
configuration specification
<http://tox.readthedocs.org/en/latest/config.html>`_ docs.
