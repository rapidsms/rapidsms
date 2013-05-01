.. _deploy_planning:

========================================
Planning for a Provisioning & Deployment
========================================

There are three major types of hosting: application physical servers, hosted virtual machines, and platform as a service providers. Though running and maintaining a physical server has become less common recently, there are still RapidSMS installation situations where this is the best options. For example, there are times when a physical cellular modem is the best solution for sending and receiving SMS messages in a region. In this case, it can make sense to have a physical server plugged into a modem where the modem has service.

+-----------------+--------------+----------------+--------------------+------------------+-----------------+
|                 | **Low Cost** | **Simplicity** | **Physical Modem** | **Customizable** | **Portability** |
+-----------------+--------------+----------------+--------------------+------------------+-----------------+
| Physical Server |         ✗    |         ✗      |                ✓   |     ✓            |     ✓           |
+-----------------+--------------+----------------+--------------------+------------------+-----------------+
| Hosted VM       |         ✓    |         ✗      |                ✗   |     ✓            |     ✗           |
+-----------------+--------------+----------------+--------------------+------------------+-----------------+
| PaaS            |         ✗    |         ✓      |                ✗   |     ✗            |     ✗           |
+-----------------+--------------+----------------+--------------------+------------------+-----------------+

Shared and dedicated :doc:`virtual machines </topics/deployment/virtual-machines>` (VMs) are becoming more and more common. In this hosting environment, the server and network configuration and maintenance are the responsibility of the hosting company. Maintaining a physical computer means worrying about RAM and hard drive failures, but this is not the case with VMs. Beyond this, many VM providers are providing APIs which make it possible to programmatically create a new server with an API request to the VM hosting provider. Once the VM has started, you are still responsible for installing an operating system and configuring all of the various software packages and services.

Further along on the spectrum of hosting providers are Platform as a Service (PaaS) providers. These providers not only provide an API for turning on a new server, but their servers come fully configured out of the box with a number of running services or access to shared services. For example, you will not need to install and configure your own web server, database server, or queue server. Each provider has its own simple web site and command line tool that help you create new services and deploy your application either from a software repository or your development system. Typically in this environment, you pay per service rather than per server.

As you travel up the spectrum from physical server to PaaS you typically get less maintenance at the cost of a higher price and reduced flexibility in your configuration. Furthermore, when you start using a PaaS, your deployment workflows will become specific to that PaaS. That is, the command line tools that you use to deploy your application will only work with that single provider. This reduces the portability of your configuration and locks you into one provider. Also, the reduced flexibility means that you won’t have total control over the versions of software installed on your server and won’t be able to install custom services. PaaS providers are typically more expensive than VM providers since they provide an extra layer of abstractions above the bare virtual hardware. But, if your application can be supported by a PaaS provider, it means not having to worry about security upgrades and initial installation for services.
