mHealth Interoperability Survey
===============================

Stemming from our discussions at the Rwanda mHealth System Design Workshop, this brief survey outlines the possible integration points between RapidSMS and various mHealth open source projects.

OpenMRS
-------

Open Medical Record System (OpenMRS) is a software platform and a reference application which enables design of a customized medical records system with no programming knowledge.

* `Website <http://openmrs.org/>`_, `Developers Portal <http://openmrs.org/help/>`_
* Date created: 2004
* Architecture: Java/MySQL
* Features: Patient database with detailed visit history and metrics.
* RapidSMS Interoperability:
    * API: Internal Java API? 
    * Patient backend? via MySQL?

Vumi/praekelt
-------------

A super-scalable conversation engine for the delivery of SMS.

* `Website <http://www.vumi.org/>`_, `Developers Portal <http://vumi.readthedocs.org/en/latest/index.html>`_
* Architecture: Python
* Features: Message sending framework. Can write Vumi-level applications for deeper integration. Can be used as a hosted service?
* RapidSMS Interoperability
    * Backend: https://github.com/rapidsms/rapidsms/tree/feature/vumi-backend

DHIS
----

The District Health Information System (DHIS) 2 is a tool for collection, validation, analysis, and presentation of aggregate statistical data, tailored (but not limited) to integrated health information management activities.

* `Website <http://www.dhis2.org/>`_, `Developers Portal <http://www.dhis2.org/development>`_
* Date created: 2008
* Architecture: Java frameworks, such as the Spring Framework, Hibernate, Struts2, Maven, and JUnit.
* Features: Data analysis and aggregation tool. Mapping features.
* RapidSMS Interoperability
    * API: "Rich Web API" - REST?
    * Probably easiest to push data to DHIS2.
    * Idea: Django app to model DHIS2 data structures and push on demand.

MOTECH
------

The MOTECH Suite is a set of Open Source technology components from a consortium of partners who have recognized that their complementary software efforts can address the core needs of mHealth.

* `Website <http://www.motechproject.org/>`_
* Date created: 2008
* Architecture: MOTECH is a modular, event driven system written in Java. 
* Features: A framework with built in support for SMS registration, IVR, scheduled messages, reports.
* RapidSMS Interoperability
    * REST API?
