Instructions for using an App that is not a contrib app in RapidSMS
=====================================================================

These tutorials are for the current active development branch RapidSMS of the core: http://github.com/rapidsms/rapidsms-core-dev

If you have additional apps (other than those already added by the default configuration in settings.py):

1 - clone or copy each of your apps' directories in your project directory alongside manage.py, settings.py, etc. For example::

    cd myproject
    git clone git://github.com/myuser/my-rapidsms-app.git myapp
    git clone git://github.com/myfriend/herapp.git


2 - edit settings.py and add your apps to the installed apps and add tabs for your apps, if applicable::

    INSTALLED_APPS = [

        # the essentials.
        "django_nose",
        "djtables",
        "rapidsms",

        # common dependencies (which don't clutter up the ui).
        "rapidsms.contrib.handlers",
        "rapidsms.contrib.ajax",

        # enable the django admin using a little shim app (which includes
        # the required urlpatterns), and a bunch of undocumented apps that
        # the AdminSite seems to explode without.
        "django.contrib.sites",
        "django.contrib.auth",
        "django.contrib.admin",
        "django.contrib.sessions",
        "django.contrib.contenttypes",
        "rapidsms.contrib.djangoadmin",
    
        # the rapidsms contrib apps.
        "rapidsms.contrib.default",
        "rapidsms.contrib.export",
        "rapidsms.contrib.httptester",
        "rapidsms.contrib.locations",
        "rapidsms.contrib.messagelog",
        "rapidsms.contrib.messaging",
        "rapidsms.contrib.registration",
        "rapidsms.contrib.scheduler",
        "rapidsms.contrib.search",
        "rapidsms.contrib.echo",
    
        "myapp",
        "herapp",
    ]


2.1 - I also needed to do the following (which may or may not be 'correct')::

    touch __init__.py


3 - Then, in the root of your project directory, sync the database. You'll need to sync your database each time you add an app::

    ./manage.py syncdb

(Note: Windows users might not see manage.py. You can use ./rapidsms instead.)

Alternate instructions for using Apps that are not contrib apps in RapidSMS
=============================================================================

1a - create an 'apps' directory in your project directory alongside manage.py, settings.py, etc. Clone individual app repositories into your apps directory::

    cd myproject
    mkdir apps
    cd apps
    git clone git://github.com/myuser/my-rapidsms-app.git myapp
    git clone git://github.com/myfriend/herapp.git

1b - clone http://github.com/rapidsms/rapidsms-community-apps-dev alongside manage.py, settings.py, etc as a directory called apps::

    cd myproject
    git clone git://github.com/rapidsms/rapidsms-community-apps-dev.git apps


2 - patch your manage.py script to add your apps directory to your pythonpath, for example (http://gist.github.com/516020)::

    #!/usr/bin/env python
    # vim: ai ts=4 sts=4 et sw=4

    import sys, os

    from django.core.management import execute_manager
    import settings


    if __name__ == "__main__":
        project_root = os.path.abspath(
            os.path.dirname(__file__))

        for dir in ["apps"]:
            path = os.path.join(project_root, dir)
            sys.path.insert(0, path)

        sys.path.insert(0, project_root)
        execute_manager(settings)

3 - edit settings.py and add desired apps to INSTALLED_APPS and add tabs, if desired, in `RAPIDSMS_TABS`

4 - Then, in the root of your project directory, sync the database. You'll need to sync your database each time you add an app::

    ./manage.py syncdb

(Note: Windows users might not see manage.py. You can use ./rapidsms instead.)
