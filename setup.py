#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from setuptools import setup, find_packages


setup(
    name="RapidSMS",
    version="0.10.0",
    license="BSD",

    install_requires=[
        "django-nose",
        "djtables",
        "djappsettings"
    ],

    test_requires=[
        "nose",
    ],

    scripts=["bin/rapidsms-admin.py"],

    package_dir={"": "lib"},
    packages=find_packages("lib", exclude=['*.pyc']),
    include_package_data=True,

    author="RapidSMS development community",
    author_email="rapidsms@googlegroups.com",

    maintainer="RapidSMS development community",
    maintainer_email="rapidsms@googlegroups.com",

    description="Build SMS applications with Python and Django",
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
