RapidSMS
========

RapidSMS is a free and open source framework for building interactive SMS applications, which integrates tightly with `Django`_ to provide a rich reporting interface. It was created by the Innovation Team at `UNICEF`_, and is under development by `the RapidSMS Team`_.

.. _Django: http://djangoproject.com
.. _UNICEF: http://unicef.org
.. _the RapidSMS Team: http://github.com/rapidsms


Please Note
===========

1) The very old RapidSMS codebase (AKA Tusker) that was living in `rapidsms <http://github.com/rapidsms/rapidsms>`_ **has been moved** to `rapidsms/rapidsms-legacy <http://github.com/rapidsms/rapidsms-legacy>`_. If your clone or fork is still in use, you should update your repository's remote/origin.

2) The combined repository of the contents of `rapidsms-core-dev <http://github.com/rapidsms/rapidsms-core-dev>`_ and `rapidsms-contrib-apps-dev <http://github.com/rapidsms/rapidsms-contrib-apps-dev>`_ **has replaced** the old codebase in `rapidsms <http://github.com/rapidsms/rapidsms>`_.

3) The ``search`` and ``training`` apps that were in `rapidsms-contrib-apps-dev <http://github.com/rapidsms/rapidsms-contrib-apps-dev>`_ **have been removed** and are now submodules of `rapidsms-community-apps-dev <http://github.com/rapidsms/rapidsms-community-apps-dev>`_.

4) The `rapidsms-core-dev <http://github.com/rapidsms/rapidsms-core-dev>`_ and `rapidsms-contrib-apps-dev <http://github.com/rapidsms/rapidsms-contrib-apps-dev>`_ repositories **will remain unchanged** until the 1.0 release, but should now be considered deprecated.

5) The PyPi package will now install from `rapidsms <http://github.com/rapidsms/rapidsms>`_.

  This note will be removed from this README once RapidSMS 1.0 arrives.


Installing
==========

RapidSMS is best installed via `PyPi`_. To install the latest stable-ish version::

  $ pip install rapidsms

Alternatively, to install the development version from `GitHub`_::

  $ pip install git+git://github.com/rapidsms/rapidsms.git#egg=RapidSMS

The RapidSMS project skeleton is identical to the Django project skeleton, with a few of our settings added. To quickly spawn a new project, we've bundled a wrapper around django-admin.py::

  $ rapidsms-admin.py startproject myproject

The ``runrouter`` management command starts the router, sends and receives SMS (and other short messages) via the configurable backends::

  $ python manage.py runrouter

.. _PyPi: http://pypi.python.org/pypi/RapidSMS
.. _GitHub: http://github.com/rapidsms/rapidsms


Getting Help
============

The current documentation is at http://rapidsms.readthedocs.org/. For community policies and ongoing dicussions, you can also take a look at `the RapidSMS wiki`_, but you may find more useful information on `the mailing list` for the time being.

.. _the RapidSMS wiki: http://docs.rapidsms.org
.. _the mailing list: http://groups.google.com/group/rapidsms


Dependencies
============

* `Python <http://python.org>`_
* `Django <http://djangoproject.com>`_
* `django-nose <http://pypi.python.org/pypi/django-nose>`_
* `djappsettings <http://pypi.python.org/pypi/djappsettings>`_
* `djtables <http://pypi.python.org/pypi/djtables>`_


License
=======

RapidSMS is free software, available under the BSD license.


Bugs
====

Please file bugs on `the RapidSMS issue tracker`_, and/or submit a pull request.

.. _the RapidSMS issue tracker: http://github.com/rapidsms/rapidsms/issues
