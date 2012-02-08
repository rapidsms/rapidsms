Eclipse Configuration
======================

Configuring Eclipse on Windows XP for RapidSMS

Intro
--------

These instructions explain how to install RapidSMS on Windows XP with Eclipse

Install Eclipse
------------------

The following packages are required to complete the install:
* Java JDK
* Eclipse (Java EE for Web Developers)
* Install PyDev plugin for Eclipse: http://pydev.org/updates

Change your tab-key to four spaces. This must be done in two places in your preferences:

1. Under General->Editors->Text Editors: set displayed tab width to '4' and check the box that says 'Insert spaces for tabs'
1. Under PyDev->Editor: set tab length to '4' and check the box that says 'Replace tabs with spaces when typing?'

Change your newlines from windows style to Unix:

1. Under General->Workspace set 'New text file line delimiter' to Unix.

Install additional required and useful packages
--------------------------------------------------

* Install Python (>= 2.5, but < 3)
* Install Python dependencies. So Far, this includes

    * pytz http://pytz.sourceforge.net/: Python TimeZone libraries
    * simplejson http://pypi.python.org/pypi/simplejson

* Django http://www.djangoproject.com/.

You will also need at least one of the following database systems:

* mysql-server: The MySQL database server and python-mysqldb: Python library access to MySQL
* PostGRES-server: a PostGRES database server and psycopg2: Python library for PostGRES
* python-pysqlite2: Support for Sqlite3 in Python

(I know, the numbering is confusing, but pysqlite2 is for Sqlite3)

Note
^^^^^

Currently SQLite should be used for development and testing only. The multi-process nature of RapidSMS does not interact stably enough with SQLite for use in production.

The following packages are OPTIONAL but useful to have, though you can leave them out if you want to create a minimal system and avoid downloading any more packages than you absolutely need:

* sqlite3: a command line program for accessing sqlite3 databases. If you use Sqlite3 as the datastore for RapidSMS, you will want this for debugging.
* sqlite3-doc: documentation for sqlite3 tool.

Install version control software
-------------------------------------

[Git]: version control for RapidSMS

Once you have installed git, you want to prevent Windows from polluting linux files with extraneous carriage returns. Do this by typing::

    $ git config --global core.autocrlf input

You should see a file called ".gitconfig" appear in your home directory with this setting inside of it.

Installing RapidSMS
--------------------

Go to :doc:`Installation <../installation>` for more info

Working with the code in Eclipse
---------------------------------

Go to the preferences/properties in Eclipse to set the pyDev python executable. It should be pretty self explanatory/automagical to find the right python interpreter.

In your workspace, It's easiest to make a new pydev project that's blank.

Do a git clone of the rapidsms project in that project directory, or just move the clone you just did into it
refresh your eclipse view to display the new files (by right-clicking on the folder in eclipse navigator and selecting 'refresh')

pydev should then pick up that you added all those files.

Right click on the projects and you'll need to add entries to your PYTHONPATH for each project. This is to tell pydev how to do code completion and refactoring linkages.

Project source folders you need to set are::


    <project root>/apps
    <project root>/lib
    <project root>/lib/rapidsms
    <project root>/lib/rapidsms/webui


copy <project root>/rapidsms/rapidsms.ini to local.ini. This will now be your local settings for running HQ.

In the database block of the ini file set the database preferences you want and the connection information.

If using mysql or postgres, make a new database with the name you set in the local.ini. Django can create tables, but is unable to make databases for mysql and postgres.

Running the Code
------------------

Sync the db
^^^^^^^^^^^^

cd into the project root/rapidsms directory::

    $ python manage.py syncdb


The syncdb will make all the tables and also bootstrap some initial configuration which includes some default users for some multiple site configuration.

* this will autogenerate the tables you need for the apps you've enabled
* this will add new tables if you add new apps
* this will not alter tables if you make model changes

Run the server
^^^^^^^^^^^^^^^
::

    $ python manage.py runserver

to run the debug server, do a python manage.py runserver, this will by default run the local django server on port localhost:8000

to get it to be visible to others in you LAN, do a python manage.py 0.0.0.0:<port>
run the route process::


    $ python manage.py runrouter


Getting PyDev to debug
------------------------

You'll need to make a pydev run configuration
For most django tasks, you should have everything run off the manage.py of the project you want to debug.
Right click on manage.py and do "debug as... --> Open Debug Dialog" to create a new debug configruation. Use either 'Python Run' or "Python Unittest"

The default settings should be ok on the first tab.
in the Arguments tab, put in your manage.py parameter you want to do. To run the server you need to put "runserver --noreload" and your breakpoints should get hit whenever you hit your app in a browser.

Note 1: the "--noreload" flag is MANDATORY if you want your breakpoints to be hit
Subnote 1: this means Django won't auto-reload for you, so you have to stop and restart debugging any time you make changes.

Note 2: If you still aren't hitting breakpoints it's possible you're running multiple instances of your server. Fix this by killing all python.exe processes and starting debugging again.

Other options:
* test
* test <appname>
* etc...

Working Directory -> select <workspace>/hq/django-hq
After that, breakpoints you define should work!

Test your install
------------------

Test RapidSMS
^^^^^^^^^^^^^^^
::

    $ ./rapidsms syncdb
    $ ./rapidsms route &
    $ ./rapidsms runserver &

Now open a browser and connect to http://localhost:8000

You should see a RapidSMS dashboard.

PyGSM
-------

Install the python-serial library to communicate with PyGSM
You can use the built-in hyperterminal for debugging (similar to Ubuntu's minicom/picocom)

Cloning PyGSM code from GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have selected your fork, you can do the following to clone it (copy it) to your local machine::

    $ cd /usr/local
    $ sudo git clone git://github.com/rapidsms/pygsm.git pygsm


Compile and install PyGSM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ cd /usr/local/pygsm
    $ sudo python setup.py install

Test PyGSM
^^^^^^^^^^^^^

PyGSM includes a small demo program that will connect to a modem and respond to incoming SMSs.

The program is called pygsm_demo and it takes as arguments:

The port the modem is connected to. E.g. COM12

Modem configuration settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To find out what port the modem is connected to, go to Windows Device Manager (open by right-clicking on My Computer -> Properties -> Device Manager -> Ports and select the one that is attached to your modem/phone).

The following will run the demo connecting to a MultiTech modem on /dev/ttyUSB0::

    $ pygsm_demo COM12 baudrate=115200 rtscts=1

While running, the demo will show all the commands it is sending the modem. Output will look something like::

    pyGSM Demo App
      Port: /dev/ttyUSB0
      Config: {'baudrate': '115200', 'rtscts': '1'}

    Connecting to GSM Modem...
       debug Booting
       debug Connecting
       write 'ATE0\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CMEE=1\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+WIND=0\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CSMS=1\r'
        read '\r\n'
        read '+CSMS: 1,1,1\r\n'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CMGF=0\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CNMI=2,2,0,0,0\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CMGL=0\r'
        read '\r\n'
        read 'OK\r\n'
    Waiting for incoming messages...
       write 'AT\r'
        read '\r\n'
        read 'OK\r\n'
       write 'AT+CMGL=0\r'
        read '\r\n'
        read 'OK\r\n'
