RapidSMS
========

RapidSMS is a free and open source framework for building interactive SMS
applications, which integrates tightly with `Django`_ to provide a rich
reporting interface. It was created by the Innovation Team at `UNICEF`_, and is
under development by `the RapidSMS Team`_.

.. image::
   https://github.com/rapidsms/rapidsms/actions/workflows/tox.yaml/badge.svg?branch=develop
   :alt: Build Status
   :target: https://github.com/rapidsms/rapidsms/actions

.. image::
   https://readthedocs.org/projects/rapidsms/badge
   :alt: Documentation
   :target: http://rapidsms.readthedocs.org/

.. _Django: http://djangoproject.com
.. _UNICEF: http://unicef.org
.. _the RapidSMS Team: http://github.com/rapidsms


Features
--------

- A framework for processing text messages through a series of phases.
- Support for sending and receiving messages from pluggable backends, including `Kannel`_.
- A swappable routing architecture with support for background processing with `Celery`_.
- Built-in commonly used apps in ``rapidsms.contrib``, including ``registration.``

.. _Kannel: http://www.kannel.org/
.. _Celery: http://www.celeryproject.org/


Installation
------------

RapidSMS is best installed via `PyPI`_. To install the latest version, run::

  $ pip install rapidsms

.. _PyPI: http://pypi.python.org/pypi/RapidSMS
.. _GitHub: http://github.com/rapidsms/rapidsms


Dependencies
------------

* `djappsettings <http://pypi.python.org/pypi/djappsettings>`_
* `django-tables2 <https://pypi.python.org/pypi/django-tables2>`_
* `django-selectable <http://pypi.python.org/pypi/django-selectable>`_
* `requests <https://pypi.python.org/pypi/requests/>`_


Documentation
-------------

Documentation on using RapidSMS is available on
`Read The Docs <http://readthedocs.org/docs/rapidsms/>`_.


License
-------

RapidSMS is released under the BSD License. See the
`LICENSE <https://github.com/rapidsms/rapidsms/blob/master/LICENSE>`_ file for
more details.


Contributing
------------

If you think you've found a bug or are interested in contributing to this
project, check out `RapidSMS on Github <https://github.com/rapidsms/rapidsms>`_.
A full contributing guide can be found in the `online documentation
<http://rapidsms.readthedocs.org/en/latest/community/joining.html>`_.
