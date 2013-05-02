.. _deployment:

Provisioning Servers & Deploying Your Project
=============================================

*Provisioning* are the steps required to prepare a server for a RapidSMS
project installation. *Deployment* is the process of continually syncing code
to a production environment as changes are made and tested in a development
environment.

RapidSMS projects can easily be installed in many ways.
     Provisioning & Deployment are a large topics, contain many right answers and are largely dependent on your application requirements. Our goal is not to provide the best solution or a configuration that will work on any project. We only want to provide you with the proper resources to make the best decisions.

Document sane defaults.
    While there are many installation methods, there's a common denominator of best practices that all production RapidSMS sites should follow (don't use DEBUG = True). We will document a concise list of best practices.

Example templates.
    There are many options to consider: a bare metal server, cloud VM, platform as a service (PaaS). We don't want to bless any single particular method, but we believe that linking to sample configurations for a small subset of these will provide a solid foundation and starting point for deploying your own application.

We can look at the overall production installation process in four parts:

* Deciding where to run your application - :ref:`deploy_planning`.
* Preparing the server(s) to run your application - :ref:`provisioning`.
* Deployiong and updating your application to the server(s) - :ref:`deploying`.
* Scaling up when your server can't handle the traffic anymore - :ref:`scaling`.

When deploying RapidSMS, you might also need to consider
:ref:`telecom`.

.. note::

    Even if you don't read anything else, the main things are:

    * Stop using runserver and switch over to Apache or your real server of choice.
    * Use a real database (not SQLite)
    * Turn off :setting:`DEBUG`!
    * Follow the guidelines in :ref:`provision_what`.

    You can find community-contributed examples on the `GitHub wiki
    <https://github.com/rapidsms/rapidsms/wiki/Deployment-Examples>`_.

Outline
-------

.. toctree::

    planning
    virtual-machines
    paas
    provisioning
    provision_how
    provision_what
    deploying
    scaling
    telecom
