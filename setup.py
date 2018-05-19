import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    with open(filepath) as f:
        return f.read()


setup(
    name="RapidSMS",
    version=__import__('rapidsms').__version__,
    license="BSD",

    install_requires=[
        "requests>=1.2.0",
        "django-tables2==1.21.*",
        "djappsettings>=0.4.0",
        "django-selectable>=0.7.0",
        "six",
    ],

    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={
        '': ['*.pyc']
    },

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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
    ],
)
