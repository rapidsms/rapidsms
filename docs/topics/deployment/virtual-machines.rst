.. _virtual machines:

=============================
Deploying to Virtual Machines
=============================

Deploying a Django app to a virtual machine from a provider
on the Internet is a popular choice. You get complete control over
the system as if you were using your own hardware, but don't have to
worry about any hardware-related problems like disk failures,
providing reliable power, getting a good network connection, etc.

Using a VM over the Internet
----------------------------

The experience is similar with most VM providers. After setting up an
account, you can create a new VM and select which of a number of
installed operating system images it is created with. The provider
will (in essence) install that operating system, configure the
system to communicate over their network, and set up a way for you
to login to the system.

Typically for our purposes, you'd install a server Linux image,
with command line access only. Once you're logged in, you can do anything
on the system that you could do while logged into your own hardware
with a command line interface.

It's always possible to make a mistake when changing the system
configuration and end up not able to login over the network anymore.
The better providers give you an alternate way to get into your
system so you can correct that yourself. With other providers, you
might have to make a support request and wait for someone to fix it
manually, perhaps with an additional charge.

Choosing a provider
-------------------

There are many providers of VMs on the Internet. Amazon is probably
the biggest. Others like Linode and Rackspace are also popular.

There are two main considerations when choosing a VM provider,
reliability and connectivity/location. Reliability is the most
important - if your system isn't running, whether it is well-connected
to the Internet is moot. Some providers publish uptime statistics
or offer service level guarantees, or you could just go with one
of the biggest, best-known providers.

Location is another criterion. If your users are accessing your app
over the web, they'll likely get better response times if the server
is at least on the same continent as they are (though not always).

Cost is always a factor, but it should not be the overriding criterion.
There are some very low-priced VM providers, but typically they run many
more VMs on the same hardware so that performance is poor, and they offer
poor or no service.

Here are a few of the most popular VM providers:

* `Amazon EC2`_ has `nine regions`_: US East (Northern Virginia), US West (Oregon), US West (Northern California), EU (Ireland), Asia Pacific (Singapore), Asia Pacific (Tokyo), Asia Pacific (Sydney), South America (Sao Paulo), and AWS GovCloud.
* Linode_ has six data centers: Tokyo, London, Newark, Atlanta, Dallas, and Fremont.
* Rackspace_ doesn't appear to have information on their web site about their locations.

.. _Amazon EC2: http://aws.amazon.com/ec2/
.. _nine regions: http://aws.amazon.com/about-aws/globalinfrastructure/
.. _Linode: http://www.linode.com/tour/
.. _Rackspace: http://www.rackspace.com/cloud/servers/overview_b/