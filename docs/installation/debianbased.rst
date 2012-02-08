Installing RapidSMS in Debian Based Linux for development
===========================================================

Steps 1-3 are optional -- virtualenv makes it easier to keep a tidy python environment for development. If you are not familiar with virtualenv, learn more here: http://pypi.python.org/pypi/virtualenv

1 - Install virtualenv and pip (optional)
------------------------------------------
::

    $ sudo apt-get install python-virtualenv python-pip


2 - Create a virtual environment (optional)
--------------------------------------------
::

    $ virtualenv --no-site-packages my_rapidsms_env


3 - Activate the virtual environment (optional)
------------------------------------------------
::

    $ source my_rapidsms_env/bin/activate

4 - Install RapidSMS
---------------------
::

    $ pip install rapidsms


5 - Create a new project
-------------------------
::

    $ rapidsms-admin.py startproject myproject
    $ cd myproject


Optionally configure, then spawn the database::


    $ python manage.py syncdb


6 - Start the development server
---------------------------------
::

    $ python manage.py runserver


7 - Start the message router 
-----------------------------
(in another window OR use GNU Screen -- don't forget to activate the virtualenv in your second window)::

    $ python manage.py runrouter


To stop the RapidSMS message router, press `ctrl-C`
