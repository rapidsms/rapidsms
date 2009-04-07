#!/usr/bin/env python
from distutils.core import setup

setup(
    name = "rapidsms",
    version = "0.1.0",
    maintainer = "RapidSMS development community",
    maintainer_email = "rapidsms@googlegroups.com",
    description = "A framework for building messaging applications",
    url = "http://rapidsms.org/",
    package_dir = {'': 'lib'},
    packages = ['rapidsms', 'spomsky'],
    package_data = {'rapidsms': ['skeleton/project/*.ini']},
    scripts = ["server.py"],
    long_description = """
RapidSMS is a Free and Open Source framework for developing short message-based
applications.

  * RapidSMS is a messaging development framework, in the same way that
    Django or Rails are web development frameworks.

  * RapidSMS is designed to do the heavy lifting for you. You implement your
    application logic, and RapidSMS takes care of the rest.

  * RapidSMS is designed specifically to facilitate building applications
    around mobile SMS.

  * ... but it supports pluggable messaging backends, including IRC and HTTP,
    and more are possible (e.g. email).

  * RapidSMS is Open Source and is written in Python.

  * RapidSMS integrates with Django, allowing you to easily develop web-based
    views of your messaging app.

  * RapidSMS is designed to scale efficiently.

  * RapidSMS provides (or will eventually provide) core support for message
    parsing, i18n, and more.
"""
)
