RapidSMS
========

RapidSMS is a free and open source framework for building interactive SMS applications, which integrates tightly with `Django`_ to provide a rich reporting interface. It was created by the Innovation Team at `UNICEF`_, and is under development by `the RapidSMS Team`_.

.. _Django: http://djangoproject.com
.. _UNICEF: http://unicef.org
.. _the RapidSMS Team: http://github.com/rapidsms


PLEASE NOTE
===========

1) the old rapidsms codebase (aka tusker) that has been living in http://github.com/rapidsms/rapidsms HAS BEEN MOVED to http://github.com/rapidsms/rapidsms-legacy -- if your clone or fork is still in use, you should update your repository's remote/origin


2) a COMBINED repository of the contents of http://github.com/rapidsms/rapidsms-core-dev and http://github.com/rapidsms/rapidsms-contrib-apps-dev HAS REPLACED the old codebase in http://github.com/rapidsms/rapidsms

('search' and 'training' apps that were in http://github.com/rapidsms/rapidsms-contrib-apps-dev HAVE BEEN REMOVED and are now submodules of http://github.com/rapidsms/rapidsms-community-apps-dev)

3) http://github.com/rapidsms/rapidsms-core-dev and http://github.com/rapidsms/rapidsms-contrib-apps-dev WILL REMAIN UNCHANGED until the 1.0 release but should now be considered DEPRECATED.


4) pypi package will now install from http://github.com/rapidsms/rapidsms

Installing
==========

RapidSMS is best installed via `PyPi`_::

  $ pip install rapidsms

.. _PyPi: http://pypi.python.org/pypi/RapidSMS


The RapidSMS project skeleton is identical to the Django project skeleton, with a few of our settings added. To quickly spawn a new project, we've bundled a wrapper around django-admin.py::

  $ rapidsms-admin.py startproject myproject


The ``runrouter`` management command starts the router, sends and receives SMS (and other short messages) via the configurable backends::

  $ python manage.py runrouter


Getting Help
============

Right now, RapidSMS isn't very well documented. We're working on that on `the RapidSMS wiki`_, but you may find more useful information on `the mailing list` for the time being.

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

Please file bugs on `GitHub`_.

.. _GitHub: http://github.com/rapidsms/rapidsms-core-dev/issues

