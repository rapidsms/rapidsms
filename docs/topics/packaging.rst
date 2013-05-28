.. _packaging:

Packaging your RapidSMS application for re-use
==============================================

If you'd like others to be able to use your application, you'll want to
package it and publish it on `PyPI`_.

You will package and publish your RapidSMS application in the same way you
would any other Django application. Django provides excellent documentation
on `packaging your Django app`_, so we won't try to write the same thing
here.

We recommend using at least the following classifiers on your package::

    Framework :: Django
    Topic :: Communications
    Topic :: Software Development :: Libraries :: Python Modules

You'll also need to give your package a license that allows others to
use it. RapidSMS uses the `BSD license`_ and we recommend it if you don't
have a strong preference for another license.

.. _BSD license: http://opensource.org/licenses/BSD-3-Clause
.. _packaging your Django app: https://docs.djangoproject.com/en/dev/intro/reusable-apps/
.. _PyPI: http://guide.python-distribute.org/contributing.html#pypi-info
