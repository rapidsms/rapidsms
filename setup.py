#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name="RapidSMS",
    version=__import__('rapidsms').__version__,
    license="BSD",

    install_requires=[
        "django-nose==1.1",
        "django-tables2==0.13.0",
        "djappsettings==0.1.0",
        "django-selectable==0.7.0",
    ],

    test_requires=[
        "nose==1.2.1",
    ],

    scripts=["bin/rapidsms-admin.py"],

    packages=find_packages(exclude=['*.pyc']),
    include_package_data=True,

    author="RapidSMS development community",
    author_email="rapidsms@googlegroups.com",

    maintainer="RapidSMS development community",
    maintainer_email="rapidsms@googlegroups.com",

    description="Build SMS applications with Python and Django",
    long_description=read_file('README.rst'),
    url="http://github.com/rapidsms/rapidsms",
    test_suite="run_tests.main",
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
)
