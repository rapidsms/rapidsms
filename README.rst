RapidSMS
========

RapidSMS is a free and open source framework for building interactive SMS applications, which integrates tightly with `Django`_ to provide a rich reporting interface. It was created by the Innovation Team at `UNICEF`_, and is under development by `the RapidSMS Team`_.

.. _Django: http://djangoproject.com
.. _UNICEF: http://unicef.org
.. _the RapidSMS Team: http://github.com/rapidsms


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
