.. _deploying:

==========================
Deploying your Application
==========================

*RapidSMS can easily be deployed in many ways*.
Deployment is a large topic, contains many right answers and is largely
dependent on your project requirements. Our goal is not to provide the
best solution or a configuration that will work on any project. We only
want to provide you with the proper resources to make the best decisions.

Non-PaaS
--------

The `Django documentation`_ provides some advice about how to run
a Django application like RapidSMS in production.

One approach you'll often see when deploying to your own hardware or
to a virtual machine is using `Fabric`_ to implement deploy
commands that a developer can use. A developer might type
``fab staging deploy`` to update the code on the staging server, or
``fab production setup_server`` to provision the production server.

PaaS
----

If you're using a PaaS, your provider takes care of setting up your
application on their servers, and will provide tools and documentation
about how to deploy your application.

Examples
--------

The RapidSMS wiki has a
`page <https://github.com/rapidsms/rapidsms/wiki/Deployment-Examples>`_
with links to examples of how people provision and deploy RapidSMS applications.

.. _Django documentation: https://docs.djangoproject.com/en/1.5/howto/deployment/
.. _Fabric: http://docs.fabfile.org/en/latest/index.html
