.. _tutorial01:

RapidSMS Tutorial Part 1
========================

In this part of the tutorial, we will:

* start a new RapidSMS project
* set up message tester
* write a minimal application that responds to a message
* demonstrate our application

Start a project
---------------

We're going to create a new Django project, using the RapidSMS project
template at `https://github.com/rapidsms/rapidsms-project-template`_.

Install Django
~~~~~~~~~~~~~~

But before we can do that, we need to have Django installed, so we can
use the Django `startproject`_ command. So we'll start by creating the
`virtualenv`_ we'll use, activating it, and installing Django into it:

.. code-block:: console
    :emphasize-lines: 1,7-8

    ~ $ virtualenv rapidsms-tut-venv
    Running virtualenv with interpreter /usr/bin/python2.7
    New python executable in rapidsms-tut-venv/bin/python2.7
    Also creating executable in rapidsms-tut-venv/bin/python
    Installing distribute...........................................................................................................................................................................................................................done.
    Installing pip................done.
    ~ $ . rapidsms-tut-venv/bin/activate
    (rapidsms-tut-venv)~ $ pip install Django
    Downloading/unpacking Django
    [...]
    Successfully installed Django
    Cleaning up...
    (rapidsms-tut-venv)~ $

Start the project
~~~~~~~~~~~~~~~~~

Now we'll use the Django `startproject`_ command, with the
RapidSMS project template:

.. code-block:: console
    :emphasize-lines: 1

    (rapidsms-tut-venv)~ $ django-admin.py startproject --template=https://github.com/rapidsms/rapidsms-project-template/zipball/master --extension=py,rst rapidsms_tut
    (rapidsms-tut-venv)~ $ cd rapidsms_tut
    (rapidsms-tut-venv)~/rapidsms_tut $ tree
    .
    ├── manage.py
    ├── rapidsms_tut
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── templates
    │   │   └── rapidsms
    │   │       └── _nav_bar.html
    │   ├── urls.py
    │   └── wsgi.py
    ├── README.rst
    └── requirements
        └── base.txt

    4 directories, 8 files
    (rapidsms-tut-venv)~/rapidsms_tut $

Install dependencies
~~~~~~~~~~~~~~~~~~~~

Install the dependencies:

.. code-block:: console
    :emphasize-lines: 1

    (rapidsms-tut-venv)~/rapidsms_tut $ pip install -r requirements/base.txt
    [... lots of output omitted ...]
    Successfully installed RapidSMS South requests django-nose django-tables2 djappsettings django-selectable nose
    Cleaning up...
    (rapidsms-tut-venv)~/rapidsms_tut $

Remove some unneeded applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The RapidSMS project template installs a number of applications by default.
Let's disable some to simplify things. In ``rapidsms_tut/settings.py``, comment
out the following lines:

.. code-block:: diff

    --- a/rapidsms_tut/settings.py
    +++ b/rapidsms_tut/settings.py
    @@ -202,7 +202,7 @@ INSTALLED_APPS = (
         "rapidsms.contrib.messagelog",
         "rapidsms.contrib.messaging",
         "rapidsms.contrib.registration",
    -    "rapidsms.contrib.echo",
    +    # "rapidsms.contrib.echo",
         "rapidsms.contrib.default",  # Must be last
     )

    @@ -215,6 +215,6 @@ INSTALLED_BACKENDS = {
     LOGIN_REDIRECT_URL = '/'

     RAPIDSMS_HANDLERS = (
    -    'rapidsms.contrib.echo.handlers.echo.EchoHandler',
    +    # 'rapidsms.contrib.echo.handlers.echo.EchoHandler',
    +    # 'rapidsms.contrib.echo.handlers.ping.PingHandler',
     )

Set up the database
~~~~~~~~~~~~~~~~~~~

The default settings in the RapidSMS project template use SQLite as the
database. You should *never* use SQLite in production, but we'll leave it
configured here for simplicity.

Initialize our database. First we use `syncdb`_. Go ahead and create
a superuser when prompted:

.. code-block:: console
    :emphasize-lines: 1,16-17
    :linenos:

    (rapidsms-tut-venv)~/rapidsms_tut $ python manage.py syncdb
    Syncing...
    Creating tables ...
    Creating table auth_permission
    Creating table auth_group_permissions
    Creating table auth_group
    Creating table auth_user_groups
    Creating table auth_user_user_permissions
    Creating table auth_user
    Creating table django_content_type
    Creating table django_session
    Creating table django_site
    Creating table django_admin_log
    Creating table south_migrationhistory

    You just installed Django's auth system, which means you don't have any superusers defined.
    Would you like to create one now? (yes/no): yes
    Username (leave blank to use 'username'):
    Email address: username@example.com
    Password:
    Password (again):
    Superuser created successfully.
    Installing custom SQL ...
    Installing indexes ...
    Installed 0 object(s) from 0 fixture(s)

    Synced:
     > django.contrib.auth
     > django.contrib.contenttypes
     > django.contrib.sessions
     > django.contrib.sites
     > django.contrib.messages
     > django.contrib.staticfiles
     > django.contrib.admin
     > django_tables2
     > selectable
     > south
     > rapidsms.contrib.handlers
     > rapidsms.contrib.httptester

    Not synced (use migrations):
     - rapidsms
     - rapidsms.backends.database
     - rapidsms.contrib.messagelog
    (use ./manage.py migrate to migrate these)
    (rapidsms-tut-venv)~/rapidsms_tut $

Then we apply migrations using `South`_'s `migrate`_ command:

.. code-block:: console
    :emphasize-lines: 1

    (rapidsms-tut-venv)~/rapidsms_tut $ python manage.py migrate
    Running migrations for rapidsms:
    [...]
     - Loading initial data for rapidsms.
    Installed 0 object(s) from 0 fixture(s)
    Running migrations for database:
    [...]
     - Loading initial data for database.
    Installed 0 object(s) from 0 fixture(s)
    Running migrations for messagelog:
    [...]
     - Loading initial data for messagelog.
    Installed 0 object(s) from 0 fixture(s)
    (rapidsms-tut-venv)~/rapidsms_tut $

Start the server
~~~~~~~~~~~~~~~~

We should now be ready to start our project. It won't do much yet,
but we can see if what we've done so far is working:

.. code-block:: console
    :emphasize-lines: 1

    (rapidsms-tut-venv)~/rapidsms_tut $ python manage.py runserver
    Validating models...

    0 errors found
    May 03, 2013 - 09:47:56
    Django version 1.5.1, using settings 'rapidsms_tut.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

And if you go to http://127.0.0.1:8000/ with a local browser, you
should see a prompt to login. Entering the userid and password you
used earlier to create a superuser should work and you'll see
RapidSMS's "Installation Successful!" page.

Message Tester
--------------

Let's take a look at one of the contributed applications that
is installed by default, Message Tester. There should be a link
to it at the top of the page, or you can just go to
http://localhost:8000/httptester/.

With Message Tester, you can manually enter and send a message
to your RapidSMS site as if it came from outside. Let's try it
out. In the Phone Number field, change our phone number to
"123456".  (The phone number doesn't really matter, but it'll
make your output match what we show here in the tutorial.)
Then in the Single Message field, enter "ping" and click
the "Send" button.

On the right side of the page, Message Tester shows the messages
sent and received, in reverse order (so the most recent message
is first). Here's what you might see:

.. code-block:: text

    05/03/2013 9:54 a.m.	123456«	Sorry, RapidSMS could not understand your message.
    05/03/2013 9:54 a.m.	123456»	ping

The "123456»" indicates that a message was sent from phone number
123456 to RapidSMS. The text of the message was "ping".

The "123456«" tells us that RapidSMS sent a message to phone number
123456. The content of that message was "Sorry, RapidSMS could not
understand your message." That shouldn't be too surprising, since
we haven't written an application yet.  But then, where did the
"Sorry" message come from? That comes from RapidSMS's
`default handler`_, which we'll learn more about later.

(If instead of the "Sorry" message, you get a response of "pong",
that just means you missed the step above of commenting out
a few lines in ``settings.py`` that the RapidSMS project
template installs by default. If you go back and make that change,
restart your app, and try again, it should work.)

A minimal application
---------------------

The :doc:`Applications Overview </topics/applications/index>`
shows a trivial RapidSMS application:

.. code-block:: python
    :linenos:

    from rapidsms.apps.base import AppBase

    class PingPong(AppBase):

        def handle(self, msg):
            if msg.text == 'ping':
                msg.respond('pong')
                return True
            return False

Let's see how we would add that to our project.

A RapidSMS app must first be a Django app, so let's create an empty Django
app.  We'll call it `tut`:

.. code-block:: console
    :emphasize-lines: 1

    (rapidsms-tut-venv)~/rapidsms_tut $ python manage.py startapp tut
    (rapidsms-tut-venv)~/rapidsms_tut $ tree tut
    tut
    ├── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py

    0 directories, 4 files
    (rapidsms-tut-venv)~/rapidsms_tut $

Now we need to add our app to Django's :setting:`INSTALLED_APPS` setting:

.. code-block:: python
    :emphasize-lines: 4

    INSTALLED_APPS = (
       [...]
        # RapidSMS
        "tut",
       [...]
        "rapidsms.contrib.default",  # Must be last
    )

Our RapidSMS app class must be in a file named ``app.py`` in our
Django application's directory, so create a file ``rapidsms_tut/tut/app.py``
and paste the code from above. Here's what it should look like when you're
done:

.. code-block:: console

    (rapidsms-tut-venv)~/rapidsms_tut $ cat tut/app.py
    from rapidsms.apps.base import AppBase

    class PingPong(AppBase):

        def handle(self, msg):
            if msg.text == 'ping':
                msg.respond('pong')
                return True
            return False
    (rapidsms-tut-venv)~/rapidsms_tut $

Try our application
-------------------

Now, let's start our project again and try it out. Start Django as before,
go to the Message Tester app, and send a message containing "ping"
(exactly, it must be all lower-case).  Instead of "RapidSMS could not
understand your message", this time your app responds "pong":

.. code-block:: text

    05/03/2013 10:49 a.m.	123456«	pong
    05/03/2013 10:49 a.m.	123456»	ping

You can find a brief explanation of how this app works in the
:doc:`Applications Overview </topics/applications/index>`.

Continue with :ref:`tutorial02`.

.. _https://github.com/rapidsms/rapidsms-project-template: https://github.com/rapidsms/rapidsms-project-template
.. _default handler: http://rapidsms.readthedocs.org/en/latest/topics/contrib/default.html
.. _migrate: http://south.readthedocs.org/en/latest/commands.html#migrate
.. _South: http://south.readthedocs.org/en/latest/
.. _startproject: https://docs.djangoproject.com/en/dev/ref/django-admin/#startproject-projectname-destination
.. _syncdb: https://docs.djangoproject.com/en/dev/ref/django-admin/#syncdb
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
