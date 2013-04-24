.. _deployment:

Deploying Robust Applications
=============================

*Deployment* is the process of arranging for your application to run on
a server for test or production, as opposed to running on your local
development system, where only you can use it.

RapidSMS can easily be deployed in many ways.
     Deployment is a large topic, contains many right answers and is largely dependent on your application requirements. Our goal is not to provide the best solution or a configuration that will work on any project. We only want to provide you with the proper resources to make the best decisions.

Document sane defaults.
    While there are many deployment methods, there's a common denominator of best practices that all production RapidSMS sites should follow (don't use DEBUG = True). We will document a concise list of best practices.

Example templates.
    There are many options to consider: a bare metal server, cloud VM, platform as a service (PaaS). We don't want to bless any single particular method, but we believe that linking to sample configurations for a small subset of these will provide a solid foundation and starting point for deploying your own application.

We can look at the overall deployment process in three parts:

* Deciding where to run your application - :ref:`deploy_planning`.
* Preparing the server(s) to run your application - :ref:`provisioning`.
* Installing and updating your application to the server(s) - :ref:`deploying`.

When deploying RapidSMS, you might also need to consider
:ref:`telecom`.

But even if you don't read anything else, the main things are:

* Stop using runserver and switch over to Apache or your real server of choice.
* Use a real database (not SQLite)
* Turn off :setting:`DEBUG`!

.. toctree::

    planning
    virtual-machines
    paas
    provisioning
    provision_what
    deploying
    telecom
