Installing RapidSMS on Mac OS X for development
================================================

Mac OS X 10.5 and later ship with Python and setuptools. If you are using an earlier version of OS X, you may need to install setuptools following instructions found here: http://pypi.python.org/pypi/setuptools

You will also need the Mac OS X Developer Tools which is installed by the Xcode package on your OS X installation disc.

Steps 1-3 are optional -- virtualenv makes it easier to keep a tidy python environment for development. If you are not familiar with virtualenv, learn more here: http://pypi.python.org/pypi/virtualenv

Install virtualenv and pip (optional)
--------------------------------------
::

    $ sudo easy_install virtualenv
    $ sudo easy_install pip


Create a virtual environment (optional)
----------------------------------------
::

    $ virtualenv --no-site-packages my_rapidsms_env


Activate the virtual environment (optional)
--------------------------------------------
::

    $ source my_rapidsms_env/bin/activate


Install RapidSMS
------------------
::

    $ pip install rapidsms


Create a new project
-----------------------
::

    $ rapidsms-admin.py startproject myproject
    $ cd myproject


Optionally configure, then spawn the database::


    $ python manage.py syncdb


Start the development server
------------------------------
::

    $ python manage.py runserver


Start the message router 
-------------------------
(in another window OR use GNU Screen -- don't forget to activate the virtualenv in your second window)::

    $ python manage.py runrouter


To stop the RapidSMS message router, press ctrl-C

Video Instructions
===================

Here is a youtube video showing how to set up virtualenv and get things running. (Apologies for the watermark, I was using a demo version of iShowU).

http://www.youtube.com/watch?v=E1cdq8T6s4E