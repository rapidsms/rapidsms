Installing RapidSMS
===================

.. note::
    RapidSMS depends on the Django_ web framework. If you're new to Django, we
    recommend reading through the `Django installation instructions`_ before
    installing RapidSMS.

The recommended way to install RapidSMS is with Pip_ (since it's available on
PyPi_)::

    pip install rapidsms

The latest development version is available in our `Git repository`_. Get it
using this shell command, which requires Git_::

    git clone https://github.com/rapidsms/rapidsms.git

You can also download `a zipped archive`_ of the development version.

.. _Pip: http://pip.openplans.org/
.. _PyPi: http://pypi.python.org/
.. _Django: https://www.djangoproject.com/
.. _Django installation instructions: https://docs.djangoproject.com/en/dev/intro/install/
.. _Git repository: https://github.com/rapidsms/rapidsms
.. _Git: http://git-scm.com/
.. _a zipped archive: https://github.com/rapidsms/rapidsms/zipball/master

Installation Guides
------------------

Typically, you'll either create a new RapidSMS project or add RapidSMS to an
existing project. Please follow the guides below for more information:

* :doc:`New RapidSMS project template <project-template>`
* :doc:`Adding RapidSMS to an existing Django project <existing-django-project>`
