.. _paas:

==========================
Running on a PaaS Provider
==========================

In choosing to run a project on a PaaS provider, you are choosing simplicitiy over
ability to easily customize and transfer your installation. Each of these
companies provide a custom command line tool for automatically configuring and
deploying an application.

Choosing a provider
-------------------

There are a number of PaaS providers who support Django web applications.  Most
of these will work fine for supporting RapidSMS. It is important to consider
the availability and cost of extra services since you will be relying on the
services provided out of the box and there is little room for customization.

It should also be noted that there have been a number of PaaS solutions that
are no longer operating businesses. Since there is less portability, it is
important to consider the longevity of the provider when finalizing a decision.
Also, with respect to portability, since you are choosing to invest in a single
companies tools, the documentation and support that are provided by the company
must be vetted before deciding to go down a particular path.

Finally, another important consideration to take into account is the command
line tool provided by the PaaS provider itself. With a virtual machine, for
example, you can choose from a number of tools to put on top of the VM to help
provision a new instance while with PaaS, you are locked in to the tools decided
on by the provider.

Here's a short list of popular PaaS providers that support Django:

 * Heroku_
 * gondor.io_
 * dotCloud_

Examples
--------

The RapidSMS wiki has a
`page <https://github.com/rapidsms/rapidsms/wiki/Deployment-Examples>`_
with links to examples of how people provision and deploy RapidSMS applications.


.. _Heroku: https://devcenter.heroku.com/articles/django
.. _gondor.io: https://gondor.io/support/django/setup/
.. _dotCloud: http://docs.dotcloud.com/tutorials/python/django/
