Installing RapidSMS
===================

.. note::
    RapidSMS depends on the Django_ web framework. If you're new to Django, we
    recommend reading through the `Django installation instructions`_ before
    installing RapidSMS.

The recommended way to install RapidSMS is with Pip_ (since RapidSMS is available on
PyPI_)::

    pip install rapidsms

.. _new-project:

Starting a New RapidSMS Project
...............................

.. _installing-rapidsms-project-template:

.. _rapidsms-project-template:

Installing the RapidSMS project template
----------------------------------------

If you're starting a new RapidSMS project, you can use the `RapidSMS project
template`_. The template is a `custom project template`_ for Django 1.8 and
therefore requires Django 1.8 or later to use.

To use the project template, first make sure you have the latest version of
Django installed::

    pip install "Django>=1.8,<1.9"

Now you can use the ``startproject`` management command with the ``template`` option. You just need to specify your project name at the end of the command::

    django-admin.py startproject --template=https://github.com/rapidsms/rapidsms-project-template/zipball/release-0.21.0 --extension=py,rst my_project_name

This will create a new project using the name you specified. Inside your project, you'll find a *README.rst* file with instructions to setup your project.

.. _RapidSMS project template: https://github.com/rapidsms/rapidsms-project-template
.. _custom project template: https://docs.djangoproject.com/en/1.4/releases/1.4/#custom-project-and-app-templates

.. _installing-development-version:

Installing the latest development version
-----------------------------------------

The latest development version is available in our `Git repository`_. Get it
using this shell command, which requires Git_::

    git clone https://github.com/rapidsms/rapidsms.git

You can also download `a zipped archive`_ of the development version.

.. _Pip: http://pip.openplans.org/
.. _PyPI: http://pypi.python.org/
.. _Django: https://www.djangoproject.com/
.. _Django installation instructions: https://docs.djangoproject.com/en/dev/intro/install/
.. _Git repository: https://github.com/rapidsms/rapidsms
.. _Git: http://git-scm.com/
.. _a zipped archive: https://github.com/rapidsms/rapidsms/zipball/master
