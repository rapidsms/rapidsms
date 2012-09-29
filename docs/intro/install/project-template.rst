RapidSMS project template
=========================

If you're starting a new RapidSMS project, you can use the `RapidSMS project
template`_. The template is a `custom project template`_ for Django 1.4 and
therefore requires Django 1.4 or later to use.

To use the project template, first make sure you have the latest version of
Django installed::

    pip install Django>=1.4

Now you can use the ``startproject`` management command with the ``template`` option. You just need to specify your project name at the end of the command::

    django-admin.py startproject --template=https://github.com/rapidsms/rapidsms-project-template/zipball/master --extension=py,rst my_project_name

This will create a new project using the name you specified. Inside your project, you'll find a *README.rst* file with instructions to setup your project.

.. _RapidSMS project template: https://github.com/rapidsms/rapidsms-project-template
.. _custom project template: https://docs.djangoproject.com/en/1.4/releases/1.4/#custom-project-and-app-templates
