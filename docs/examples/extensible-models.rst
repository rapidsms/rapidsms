Intro
========

This is a brief summary of some sandbox work to better understand Extensible Models. This is "not" a page on how to make extensible models, the Contact model in the rapid core is a fine example of that. This is intended to be a detailed example of how to set up your folder structure and stay sane while extending an Extensible Model.

Initial Setup
----------------

For this sandbox we'll be extending the Contact model in three separate apps, to see what exactly happens at the DB level. I started with a clean install of rapid, and then created three apps with creative names::

    $ python manage.py startapp testextensions_main
    $ python manage.py startapp testextensions_clash

The folder structure for each of these is the same::

    testextensions_main/models.py
    testextensions_main/extensions
    testextensions_main/extensions/rapidsms
    testextensions_main/extensions/rapidsms/contact.py
    testextensions_main/extensions/rapidsms/__init__.py
    testextensions_main/extensions/__init__.py
    testextensions_main/tests.py
    testextensions_main/views.py
    testextensions_main/__init__.py

These are all fairly dumb apps for the sake of this example, so only contact.py has any pertinent content::

    from django.db import models

    class TestContact(models.Model):
        is_used = models.BooleanField(default=True)

        class Meta:
            abstract = True


The folder structure here is very important: we're extending the Contact model, within the rapidsms app. So the modeule where our extension class exists "must" be myapp/extensions/rapidsms/contact.py. The name of the class itself, TestContact, is unimportant, however it "must" be abstract. Any abstract models within this module will have their attributes added to the base Contact class.

In testextensions_clash, I used the same exact TestContact model (it also has a boolean is_used attribute).

Initially, I started with a clean install of rapidsms, without any of these sample apps in the INSTALLED_APPS under settings. I did this to demonstrate how one might add a new app to an already-running instance, pulling in new extensions to an existing model.

Extension Experiments
-----------------------

Firstly, installing south and placing all the Extensible Models under version control makes it easy to automatically add columns as you pull in new apps that extend them (if you aren't using it already).
::

    $ easy_install south

You will likely want to change the place where the 'migrations' folder exists within your project (http://south.aeracode.org/docs/settings.html#setting-south-migration-modules), otherwise it'll place them directly with in rapidsms/lib (probably not a Good Idea). In my settings.py, I added::


    SOUTH_MIGRATION_MODULES = {
        'rapidsms': 'testextensions_main.migrations',
    }

Now we place rapidsms under migration control, but this command doesn't create any tables.
::

    $ python manage.py schemamigration rapidsms --initial
     + Added model rapidsms.Backend
     + Added model rapidsms.App
     + Added model rapidsms.Contact
     + Added model rapidsms.Connection
    Created 0001_initial.py. You can now apply this migration with: ./manage.py migrate rapidsms

This creates all tables except the core rapidsms tables::

    $ python manage.py syncdb
    Creating table ...
    ...
    Synced:
     > south
     > rapidsms.contrib.handlers
     > django.contrib.sites
     > django.contrib.auth
     > django.contrib.admin
     > django.contrib.sessions
     > django.contrib.contenttypes
     > rapidsms.contrib.locations
     > rapidsms.contrib.messagelog
     > rapidsms.contrib.scheduler
     > testextensions_clash

    Not synced (use migrations):
     - rapidsms


The following creates the rapidsms tables (migration-controlled)::

    $ python manage.py migrate
     - Migrating forwards to 0001_initial.
     > rapidsms:0001_initial

We'll now have a rapidsms_contact table with the following structure::

    CREATE TABLE "rapidsms_contact" (
        "id" integer NOT NULL PRIMARY KEY,
        "name" varchar(100) NOT NULL,
        "language" varchar(6) NOT NULL
    );
    
Now we can demonstrate a few things, the first of which is how to pull in a new app with extensions and automatically update the contact db. At this point, I added my app, testextensions_main to the INSTALLED_APPS in settings.py::

    $ python manage.py schemamigration rapidsms --auto

     + Added field is_used on rapidsms.Contact
     Created 0002_auto__add_field_contact_is_used.py. You can now apply this migration with: ./manage.py migrate rapidsms

    $ python manage.py migrate rapidsms

     - Migrating forwards to 0002_auto__add_field_contact_is_used.
     > rapidsms:0002_auto__add_field_contact_is_used


Steps 6 and 7 auto-magically added my additional column to the contacts table!
::

    CREATE TABLE "rapidsms_contact" (
        "is_used" bool NOT NULL DEFAULT True,
        "id" integer PRIMARY KEY,
        "language" varchar(6),
        "name" varchar(100));

For anyone more knowledgeable of the way ExtensibleBase works, this may not be as big a deal, but for me the implications were pretty exciting...provided that one keeps the extensible models under migration control, you can add new apps after your initial deployment, extending these models with more and more columns as you go...

As a final demonstration, just to show one (unsurprising) limitation of extensible models is that two apps cannot extend the same model with a column of the same name. Let's add testextensions_clash to the INSTALLED_APPS to see what happens::

    $ python manage.py schemamigration rapidsms --auto

    Nothing seems to have changed.

Hmmm...interesting! We have two extensions that are both wanting to add the same column, and south sees them as having no problems. It merges these two concepts together (which could be desired or a really Bad Thing, depending on what you're wanting).

Blow away the database, remove south support, and just trying syncing the db the regular way, with both _main and _clash apps installed::

      $ python manage.py syncdb
      Syncing...
      Creating table south_migrationhistory
      Creating table rapidsms_backend
      Creating table rapidsms_app
      Creating table rapidsms_contact
      Traceback (most recent call last):
       ......
    File "/home/david/Projects/CoreDevRapid/env/lib/python2.6/site-packages/Django-1.2.1-py2.6.egg/django/db/backends/sqlite3/base.py", line 200, in execute
      return Database.Cursor.execute(self, query, params)
      django.db.utils.DatabaseError: duplicate column name: is_used
    ```
    
In this case the clash is identified and in fact impossible to create.
    
Conclusions
--------------
    
South provides an easy way to add new attributes to ExtensibleModels, within an already-deploayed instance of RapidSMS.

Depending on your needs, south-managed migrations and regular syncdb offer different behaviors for attribute clashes with extensible models used by two separate apps. In either case, if two groups within the community are working on apps that extend the same model (and that both use one another's apps), they should probably be coordinating regularly when adding attributes, to be sure there are no clashes, and to determine which attributes should be brought into the base class.
