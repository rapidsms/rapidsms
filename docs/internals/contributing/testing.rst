Running the RapidSMS core test suite
====================================

RapidSMS uses `nose <http://pypi.python.org/pypi/nose/>`_ to run its test suite
and provides several configuration options and entry points for continuous
integration. The unit tests can be run in the current python environment or
automated to run in several environments and can include coverage reports.

Quickstart
----------

.. note::

    The RapidSMS core test suite includes some tests that depend on
    `django-celery`_ 3.0+. If you install the requirements file listed below,
    all tests should pass properly.

The easiest way to run the unit tests in a new install is to run the following
from the project root::

    python setup.py develop
    pip install -r tests/requirements/dev.txt
    python run_tests.py --settings=tests.default

The settings found in the /tests/default.py module are intended as the default
settings file for running tests. You can tell the test runner what settings
file to use with the --settings flag or by setting your
``DJANGO_SETTINGS_MODULE`` environment variable.

Coverage
--------

To see code coverage while running the tests, you can use the supplied
``coverage`` settings file::

    python run_tests.py --settings=tests.coverage

.. _pep-eight-adherence:

PEP 8 Style Guidelines Adherence
--------------------------------

RapidSMS adheres to the Python `PEP 8
<http://www.python.org/dev/peps/pep-0008/>`_ style guidelines for all Python
source outside of the ``docs/`` directory.  As such, please check your code
against the PEP 8 specification by using the ``pep8`` linting tool in your
RapidSMS directory before submitting patches for review::

    pep8 --count --statistics --exclude=scheduler,locations,ajax ./rapidsms/

Testing multiple environments
-----------------------------

RapidSMS uses `Tox <http://tox.readthedocs.org/en/latest/index.html>`_ to run
the test suite in a variety of environments. You can test all environments
together or specific ones::

    tox                 # all environments
    tox -e py26-1.4.X   # only test using Python 2.6 and Django 1.4

The available environments are:

 * ``py26-1.3.X`` - Test using Python 2.6 and Django 1.3.X
 * ``py26-1.4.X`` - Test using Python 2.6 and Django 1.4.X
 * ``py26-trunk`` - Test using Python 2.6 and Django master
 * ``py27-1.3.X`` - Test using Python 2.7 and Django 1.3.x
 * ``py27-1.4.X`` - Test using Python 2.7 and Django 1.4.x
 * ``py27-trunk`` - Test using Python 2.7 and Django master
 * ``docs`` - Test buliding docs

You can also add additional environments or change other parts of the
configuration in your local copy of the tox.ini by following the `tox
configuration specification
<http://tox.readthedocs.org/en/latest/config.html>`_ docs.

Using setup.py
--------------

Your ``DJANGO_SETTINGS_MODULE`` must be set in order for the test suite using
setup.py. Running the following will install test dependencies and run the unit
tests in one step, but without the option of a coverage report::

    export DJANGO_SETTINGS_MODULE=tests.default
    python setup.py test

.. _django-celery: http://pypi.python.org/pypi/django-celery
