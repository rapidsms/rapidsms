#!/usr/bin/env python

# RapidSMS setup.py -- adapted from Django's with our heartfelt thanks
from distutils.core import setup
from distutils.command.build_py import build_py as _build_py
from distutils.command.install import INSTALL_SCHEMES
import os
import sys
import commands

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.join(os.path.dirname(__file__), "lib")
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)

for dirpath, dirnames, filenames in os.walk(root_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Dynamically calculate the version based on get_rapidsms_version()
# ... this way releases automagically get shipped with the version
# stored in the git tag, and installations (whether from releases or not)
# are tagged with a reasonably exact git version.
#
sys.path = ["lib"] + sys.path
version = __import__("rapidsms").get_rapidsms_version()

class build_py (_build_py):
    def run (self):
        _build_py.run(self)
        if version == "unknown":
            print "RapidSMS version unknown! Is git in your path?"
        else:
            vstring = "VERSION = '%s'" % version 
            vfilename = os.path.join(self.build_lib,
                        "rapidsms", "__version__.py")
            vfile = file(vfilename, "w")
            print >>vfile, vstring
            print "setting %s in %s" % (vstring, vfilename)

setup(
    name = "rapidsms",
    version = version,
    maintainer = "RapidSMS development community",
    maintainer_email = "rapidsms@googlegroups.com",
    description = "A framework for building messaging applications",
    url = "http://rapidsms.org/",
    package_dir = {'': 'lib'},
    packages = packages,
    # data_files = data_files,
    package_data = {'rapidsms': ['skeleton/project/*.ini',
                                 'skeleton/project/manage.py']},
    scripts = ["rapidsms"],
    cmdclass={'build_py': build_py},
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
