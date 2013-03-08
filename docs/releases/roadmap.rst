================
RapidSMS Roadmap
================

Below you'll find a rough outline of planned milestones and releases for
RapidSMS. For a list of official releases, please see the :doc:`index`.


New RapidSMS website
--------------------

* *Expected release date:* May, 2013

**Goals**

* Revamp `RapidSMS website <http://www.rapidsms.org/>`_ with new design
* Highlight high level stories of current installations with pictures and maps
* Provide a page to track 3rd party reusable apps and backends
* Blog syndication (community page)
* Migrate existing content to new platform


v1.0.0
------

* *Expected release date:* April, 2013

**Goals**

* Write a tutorial similar to the Django tutorial for beginners
* Finish documentation for new core features
* Write release notes for v1.0
* Finish development on outstanding core features and bugs


v0.14.0
-------
* **Scheduling and deployment**
* *Expected release date:* March, 2013
* `GitHub Milestone <https://github.com/rapidsms/rapidsms/issues?milestone=6&page=1&state=open>`_

**Goals**

* Update scheduling architecture based on community `proposal <https://github.com/rapidsms/rapidsms/wiki/Scheduling>`_
* Review and analyze cloud hosting providers
* Write comprehensive deployment documentation for chosen providers
* Provide instructions and scripts to deploy project in a few simple steps


v0.13.0 - Next Release
----------------------
* **Bulk messaging**
* *Expected release date:* March, 2013
* `GitHub Milestone <https://github.com/rapidsms/rapidsms/issues?milestone=5&page=1&state=open>`_


**Goals**

* Load testing of message handling and routing functionality
* Identify bottlenecks and create plans for improving performance
* Write documentation for users intending to operate RapidSMS at scale
* Integrate 3rd party service providers like Vumi
* Implement the `Bulk Messaging API`_
* Finalize and merge the `Vumi backend pull request`_


v0.12.0
-------
* **Bootstrap and contrib update**
* *Expected release date:* March, 2013
* `GitHub Milestone <https://github.com/rapidsms/rapidsms/issues?milestone=4&page=1&state=open>`_


**Goals**

* Use `Twitter Bootstrap`_ in core, based on the community proposal
* Update contrib applications to meet base standard as per this `review <https://groups.google.com/forum/#!topic/rapidsms-dev/34AOL5S0Xr8>`_


v0.11.0
-------
* **PEP8 and testing**
* *Release date:* December 31, 2012
* :doc:`0.11.0`
* `GitHub Milestone <https://github.com/rapidsms/rapidsms/issues?milestone=2&page=1&state=open>`_

**Goals**

* Update and simplify test harness
* Add coverage/PEP8 usage guide and documentation


v0.10.0
-------
* **New routing**
* *Date released:* November 23, 2012
* :doc:`0.10.0`
* `GitHub Milestone <https://github.com/rapidsms/rapidsms/issues?milestone=1>`_

**Goals**

* Introduce new-routing architecture
* Improve documentation


v0.9.6a
-------
* *Date released:* October 19, 2010
* :doc:`0.9.6`


.. _Bulk Messaging API: https://github.com/rapidsms/rapidsms/wiki/Bulk-Messaging-API
.. _Vumi backend pull request: https://github.com/rapidsms/rapidsms/pull/230
.. _Twitter Bootstrap: https://github.com/rapidsms/rapidsms/wiki/Twitter-Bootstrap
