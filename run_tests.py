#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
import sys

from coverage import coverage

from django import VERSION
from django.conf import settings
from django.test.utils import get_runner


def run_tests(options, args, ci=False):
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=int(options.verbosity),
                             interactive=options.interactive,
                             failfast=False)
    if 'test' in args:
        args.remove('test')  # Sometimes we get the 'test' string as an arg.
    if not args:
        # In Django through 1.5, test runner arguments are applabel, applabel.TestCase, or
        # applabel.TestCase.test_method.
        # Starting in Django 1.6, arguments cannot be applabels (unless the app label just
        # happens to also be the Python path).  Args are Python dotted paths, or you can specify
        # a directory name to look for test*.py under that directory.
        if VERSION >= (1, 6):
            args = ['rapidsms/']  # Look in this directory tree for test*.py files

            # Work around a circular import problems starting in 1.6 by
            # importing this ahead of time.  (HACK, I don't know why this is happening
            # but this gets past it.)
            from rapidsms.tests.harness import backend

        else:
            # We only want to test rapidsms apps
            rapidsms_apps = [app for app in settings.INSTALLED_APPS if app.startswith('rapidsms')]
            # Insert the app labels for the rapidsms apps in INSTALLED_APPS - that's
            # the LAST part of the Python path.
            args = [app.split('.')[-1] for app in rapidsms_apps]

    cov = None
    if ci:
        cov = coverage()
        cov.start()

    failures = test_runner.run_tests(args)

    if cov and not failures:
        cov.stop()
        cov.report()

    sys.exit(failures)


def main():
    # It's useful to see the version - there have been bugs installing the right Django from tox.ini
    print("Django version: %s" % (VERSION,))

    from optparse import OptionParser
    usage = "%prog [options] [module module module ...]"
    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--verbosity', action='store', dest='verbosity',
                      default=1, type='choice', choices=['0', '1', '2', '3'],
                      help='Verbosity level; 0=minimal output, 1=normal '
                           'output, 2=all output')
    parser.add_option('--noinput', action='store_false', dest='interactive',
                      default=True,
                      help='Tells Django to NOT prompt the user for input of '
                           'any kind.')
    parser.add_option('--settings',
                      help='Python path to settings module, e.g. '
                           '"myproject.settings". If this isn\'t provided, '
                           'the DJANGO_SETTINGS_MODULE environment variable '
                           'will be used.')
    parser.add_option('--ci', action='store_true', dest='ci',
                      default=False,
                      help='Run tests with CI environment. You can also set CI env var.'
                           'Mainly this turns on coverage.')
    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment. "
                     "Set it or use --settings.")
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']
    ci = options.ci or os.environ.get('CI', False)
    run_tests(options, ci=ci, args=args)


if __name__ == '__main__':
    main()
