#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests(options, args):
    if django.VERSION > (1, 7):
        # http://django.readthedocs.org/en/latest/releases/1.7.html#standalone-scripts
        django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=int(options.verbosity),
                             interactive=options.interactive,
                             failfast=False)
    if not args:
        args = ['rapidsms']
    failures = test_runner.run_tests(args)
    sys.exit(failures)


def main():
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
    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment. "
                     "Set it or use --settings.")
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']
    run_tests(options, args=args)


if __name__ == '__main__':
    main()
