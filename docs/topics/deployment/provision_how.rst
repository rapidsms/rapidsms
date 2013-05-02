.. _provision_how:

Ways to Provision
-----------------

Manual provisioning
...................

You can provision manually, installing things as you discover
you need them, and tweaking the configuration until things work.
This is often how people's development systems end up getting
provisioned.

If you take careful notes as you provision manually, then the
next time you have to do it, you can follow the notes and
do it much more quickly and with fewer errors. You
can also share the notes so your co-workers can benefit.

Scripting
.........

The next step is putting the provisioning commands into a script
of some kind. Typically this is when you have to start worrying
more about what platform you're working on. For example,
the commands to
install packages on Debian-based Linuxes are different from those
on Redhat or Gentoo-based Linuxes, so your script either needs to
assume some base platform, or it suddenly gets a lot more complicated.

At this level, you can use tools like `Fabric`_ to help
organize your provisioning commands into tasks and execute
them remotely. However, Fabric does not help with issues
of provisioning like how to install a package or create a user.

For an example of this, you might look at the Django project
template offered by Caktus. Its `fabfile`_, with the help
of `Argyle`_, does provisioning on Ubuntu systems. You can see
explicit commands to do things like create symbolic links and
change ownership of files.

Provisioning tools
..................

After doing that for a while, you'll probably wish there were some
tools you could use to save you from having to understand
every detail of setting up your system, and how administering
your Ubuntu system is different from a Redhat system.

You might start with something like `Blueprint`_. It takes a
different approach than most of the other tools we'll mention.
With Blueprint, instead of writing a specification for what
provisioning needs to be done, you run a Blueprint tool on
a system that you've provisioned already
and it records the state of the system: which packages have
been added to the defaults, which configuration files have
been changed or added and what their contents are, etc.

Then Blueprint provides multiple ways to recreate that provisioned
system, including generating a shell script that will do it,
or exporting a set of configuration files for several other
provisioning tools such as  `Puppet`_ and `Chef`_.
There's a lot of flexibility and room to finetune how Blueprint
works; this is just the surface.

Beyond Blueprint there are tools like `Chef`_, `Puppet`_, or `SaltStack`_.
These provide full languages in which to specify how many systems
should be configured, and tools to apply and maintain the
configurations. The cost of this power, of course, is complexity.
Getting one of these provisioning tools installed and learning
to use it will require a large investment of time.

Examples
........

The RapidSMS wiki has a
`page <https://github.com/rapidsms/rapidsms/wiki/Deployment-Examples>`_
with links to examples of how people provision and deploy RapidSMS applications.


Recommendations on Implementing Provisioning
............................................

Unfortunately, there's no simple solution to implementing
repeatable provisioning. Provisioning is a very complicated
task.

Tools can help, but you still need a pretty detailed knowledge
of system administration to make it work right.

One consideration is how large your problem is. For people who have
to manage more than a dozen or so systems, a full-featured tool
like `Chef`_ or `Puppet`_ is essential, and the time spent learning
it thoroughly will be repaid many times over.

If you only have a few Django apps, and they're fairly conventional
in terms of provisioning requirements, you should consider
a :ref:`PaaS <paas>`. They handle the provisioning for you. The
monthly bills will be higher, but your costs in time spent getting
provisioning working and keeping it working will be much lower.

If your needs fall somewhere in the middle, or funding isn't available
for a PaaS, then you'll need to consider your needs and your level of
expertise, try out some of the available approaches, and make the
best decision you can.  The `RapidSMS mailing list`_ is a good resource;
you can present your situation there and ask for advice.



.. _Argyle: https://pypi.python.org/pypi/argyle/
.. _Blueprint: http://devstructure.com/blueprint/
.. _Chef: http://www.opscode.com/chef/
.. _fabfile: https://github.com/caktus/django-project-template/blob/master/fabfile.py
.. _Fabric: http://docs.fabfile.org/en/latest/index.html
.. _Heroku: https://www.heroku.com/
.. _Puppet: https://puppetlabs.com/
.. _RapidSMS mailing list: http://groups.google.com/group/rapidsms
.. _SaltStack: http://saltstack.com/
.. _Vagrant: http://vagrantup.com/
