Install RapidSMS in an existing Django Project
================================================


1. Add RapidSMS to your project's requirements.  You
can install it with pip::

    $ pip install rapidsms

or add it to your requirements file or setup.py.

2. Add RapidSMS to your :setting:`INSTALLED_APPS`::

    INSTALLED_APPS = [
        ...,
        'rapidsms',
        ...
    ]

3. Choose and configure a :ref:`RapidSMS router <router-choice>`.

4. Continue with the documentation for :ref:`writing RapidSMS applications <writing-apps>`.
