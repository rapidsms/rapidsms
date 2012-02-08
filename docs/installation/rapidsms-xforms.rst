Starting a new installation of RapidSMS, XForms
=================================================

This is a brief tutorial on getting RapidSMS and XForms running out of the box. This was written on August 12th, 2011, so it is possible some things may have changed since then. If so, please track down the issues and update this document.

Why XForms?
------------

Many projects can satisfy their entire needs by using this application. It provides a simple interface for defining structured incoming messages. It has been used on multiple projects across the world and is fairly well tested. In short, it gives you a point and click interface to creating data collection systems using SMS.

Pre-requisites
-----------------

It is assumed you already have Python, pip and virtualenv installed on your system. This tutorial assumes using a terminal application either on OS X or Linux.

Tutorial
=========

Step1: Create a working directory and virtual environment
------------------------------------------------------------

First things first, we need to set up a space to work in. You should use a virtual environment to manage your Python dependencies, so we'll do that as well::

    bash
    % cd
    % mkdir rapidsms
    % cd rapidsms
    % virtualenv env
    % source env/bin/activate

Step2: Install Packages
--------------------------

Now we need to install the packages into our virtual environment. We'll be using Django 1.3, RapidSMS and RapidSMS-XForms::

    bash
    (env) % pip install rapidsms-xforms


Step3: Create our RapidSMS Project
-----------------------------------

Now we need to create our RapidSMS/Django project. RapidSMS has some specific settings required in its settings.py, so we use its admin command to start our project::

    bash
    (env) % rapidsms-admin.py startproject project


Step4: Configure your settings.py for RapidSMS-XForms
------------------------------------------------------

Installing RapidSMS-XForms involves editing your settings.py in your project directory.

Add rapidsms_xforms, eav and uni_form to your installed apps::


    INSTALLED_APPS = ( "rapidsms",
                       .. other apps, rapidsms and others ..
    
                       "eav",
                       "uni_form",
                       "rapidsms_xforms",
    )


And make similar changes to your RapidSMS tabs::

    RAPIDSMS_TABS = [
                     ("rapidsms.contrib.messagelog.views.message_log",       "Message Log"),
                     .. other tabs ..

                     ("xforms", "XForms")
    ]

Finally, also configure your login URL to match RapidSMS::

    LOGIN_REDIRECT_URL = "/"
    LOGIN_URL = "/account/login"


Step5: Configure your urls.py for RapidSMS-XForms
---------------------------------------------------

We also need to add the routes for XForms to the urls.py file in your project directory::

    urlpatterns = patterns('',
                           .. other url patterns ..
                           (r'^scheduler/', include('rapidsms.contrib.scheduler.urls')),

                           ('', include('rapidsms_xforms.urls'))
    )

Step6: Sync DB
----------------

You now need to create your database tables and initial admin user::

    (env) % python manage.py syncdb


Step7: Start the router and server
-----------------------------------

In two separate windows, start the RapidSMS router and server. Remember to activate your virtual environment first.

First start your router::

    $ cd
    $ cd rapidsms
    $ source env/bin/activate
    $ cd project
    $ python manage.py runrouter

Keep this window running, then start your server in a new terminal::

    $ cd
    $ cd rapidsms
    $ source env/bin/activate
    $ cd project
    $ python manage.py runserver


Testing your Install
======================

You should now be able to create a new XForm and test your install. Point your browser to http://localhost:8000 and click on the XForms tab. You'll be asked to log in using the admin username and password you created when running the syncdb command.

Step1: Create A New XForm
--------------------------

From here create a new form, name it 'Gas'. Set a keyword of 'gas', a description saying that it will track the gas mileage of users and leave the rest as default.

For the response set it to: Thank you for helping us track your mileage.

Step2: Create Miles and Gallons Fields
----------------------------------------

Create two new fields, one named miles, with miles as a keyword, of type Integer, and another named gallons with gallons as a keyword and of type Decimal.

Step3: Test your form
------------------------

Now we can test our form using the message tester. Click on the Message Tester tab, then enter an SMS like::

    gas 356 12.5

You should see a response from the server::

    Thank you for helping us track your mileage.

You can also now click on the XForms tab, then the results for your form to see that the data has been correctly parsed.

Step4: Experiment
--------------------

XForms has many options, you can add constraints to fields, you can change the response messages and you can make fields optional. Experiment with the different options as you see fit. You can even hook into the form submissions and alter the behavior programmatically.

Check the XForms Documentation for more details: http://nyaruka.github.com/rapidsms-xforms/
