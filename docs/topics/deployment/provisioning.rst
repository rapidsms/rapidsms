.. _provisioning:

============
Provisioning
============

Provisioning is making sure the systems where you're going to run
your RapidSMS site are ready to deploy to. After a
system is installed, typically you need to create users,
grant permissions, and install and configure tools such as a database, a
web server, a cache, a message broker, etc.

Another way to look at it is that provisioning is things you only need to do
once per system, like installing a database server, while deploying includes
the things you have to do separately for each app or site you deploy, like
creating a virtual environment for it.

You might also look at provisioning as all the things you
have to do for yourself if you're not using a PaaS to host
your site.

Above all else, you want your provisioning to be repeatable. Use tools
to automate it so that you don't waste a lot of time tracking down problems
that turn out to be the result of a missing package on one server, or
an incorrect configuration, or incorrect file permission, and
so forth.

Having automated provisioning can also be very useful to be able to easily
provision new systems. For example, you can set up a new test system, or add
another staging server, or another production server.

We're going to look at two aspects of provisioning:

* :ref:`provision_how`
* :ref:`provision_what`
