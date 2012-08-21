Testing
=======

RapidSMS uses `nose <http://pypi.python.org/pypi/nose/>`_ to run its test suite and provides several configuration options and entry points for continuous integration. The unit tests can be run in the current python environment or automated to run in several environments and can include coverage reports.

Quickstart
==========

The python module ``run_tests.py`` is provided as the simplest method of running the test suite. The test suite can also be run by executing ``python setup.py test``, which installs the test dependencies and runs this module. The dependencies in pip-requires.txt will need to be installed with ``pip install -r pip-requires.txt`` for run_tests.py to run properly.

The settings found in the /tests/ci.py module are intended as the default settings file for running tests. You can tell the test runner to use this settings file by using the --settings flag as in: ``./run_tests.py --settings=tests.ci``. You can also set your DJANGO_SETTINGS_MODULE environment variable equal to tests.ci and omit this flag.

Testing Multiple Environments
=============================
RapidSMS uses `Tox <http://tox.readthedocs.org/en/latest/index.html>`_ to run the test suite in a variety of environments. The environments included in the tox.ini file are:

 * `py2.6-1.3` - Test using Python 2.6 and Django 1.3.x
 * `py2.6-1.4` - Test using Python 2.6 and Django 1.4.x
 * `py2.7-1.3` - Test using Python 2.7 and Django 1.3.x
 * `py2.7-1.4` - Test using Python 2.7 and Django 1.4.x

You can run any of the environments listed above using: ``tox -e <name>``. Using ``tox`` on its own runs the test suite against each of these environments.

You can also add additional environments or change other parts of the configuration in your local copy of the tox.ini by following the `tox configuration specification <http://tox.readthedocs.org/en/latest/config.html>`_ docs.

Continuous Integration and Coverage Reports
===========================================
If desired, the test suite can produce a Cobertura coverage report for use with continuous integration software.
Setting the environment variable CI to 1 before running the test suite with produce a coverage report in the coverage.xml file.
For example, the following produces a coverage.xml file and prints a coverage report for the test suite in the current environment:

	``CI=1; ./run_tests.py``

If you are using tox, this environment variable is set to 1 automatically.