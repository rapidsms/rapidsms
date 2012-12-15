RapidSMS 1.0 Roadmap
====================

This document describes the high level goals and schedule for releasing RapidSMS 1.0. It was originally created by Colin Copeland and Tobias McNulty in collaboration with UNICEF Innovation. However, the document is open to the greater RapidSMS community for discussion, comments, and other feedback.

Design Philosophies
-------------------

* **Encourage community involvement.** New and long term RapidSMS users should feel welcomed in the community. Introductory materials, such as tutorials and how-to documentation, should be written to help beginners. Standards and design patters should be in place to make the development environment more consistent.
* **Be more Django-like.** RapidSMS is, for the most part, a set of Django applications with a message processing component. RapidSMS should be packaged like every other Django app and follow the communities best practices.
* **Improve test coverage.** Every good Python package should provide a robust test suite for coverage and regression testing. New core code should always include tests before being merged into master.
* **Write better documentation.** The RapidSMS project should provide consistent and readable documentation. The documentation should be written in a maintainable format (ReST) and we should aim to improve it as often as possible.
* **Batteries included.** The bar needs to be raised for the contrib applications. RapidSMS should provide you with enough tools out of the box to hit the ground running.
* **Guidelines for maintenance and scaling.** Deployment examples and best practices should be provided to ease the transition to hosted environments.

Roadmap
-------

===========  ===========
   Month      Focus
===========  ===========
July         Develop roadmap and plan
August       Improve test suite against core
September    Improve and cleanup documentation
October      Encourage ongoing developer participation in RapidSMS itself
November     Clean up core and prepare for v1.0 release
December     Provide community blessed way to package and distribute pluggable RapidSMS apps
January      Optimize core for scaling
February     Revamp RapidSMS website
March        Build extensible implementations of key RapidSMS core / contrib apps 
April        Release 1.0
May          Create and document RapidSMS deployment methods
===========  ===========

Develop roadmap and plan
************************

* Conduct assessment of RapidSMS code and community
* Begin developing community document outlining strategy and workplan for 1.0 release
* Survey 3rd-party integration points and discuss plan for core modification
* Delivery: End of month 1

Improve test suite against core
*******************************

* Setup and maintain Jenkins CI for RapidSMS
* Set standard for test coverage
* Set the precedent for including unit tests both in projects and RapidSMS itself
* Delivery: End of month 2

Improve and cleanup documentation
*********************************

* Write documentation for existing core functionality
* Installation instructions
* Configuration and deployment instructions
* Take down or redirect links to old documentation
* Delivery: End of month 3

Encourage ongoing developer participation in RapidSMS itself
************************************************************

* Define a structured way to contribute to RapidSMS and how to help out
* Designate roles (“Release manager”) & encourage individuals to champion features
* Organize RapidSMS development sprints
* Delivery: End of month 4

Clean up core and prepare for v1.0 release
******************************************

* Push development of new router
* Cleanup and document built-in backends
* Determine release schedule that focuses on releasing early and often
* Set release date for 1.0 and create publicity for the release
* UNICEF Deliverables:
    * Provide list of existing RapidSMS projects and apps
* Delivery: End of month 5

Provide community blessed way to package and distribute pluggable RapidSMS apps
*******************************************************************************

* Identify existing apps and projects that would be good candidates for packaging
* Survey the community on the list for such apps
* Provide documentation for packaging apps and distributing to community
* Provide guidelines for making apps extensible
* Build small apps as examples using proposed packaging guidelines
* Provide support  packaging using the provided examples, test coverage and documentation
* Identify overlap of different projects, e.g., two apps that do group management
* UNICEF Deliverables:
    * Sign off on new website design and functionality
    * Server for RapidSMS website
* Delivery: End of month 6

Optimize core for scaling
*************************

* Load testing of message handling and routing functionality
* Identify bottlenecks and create plans for improving performance
* Write documentation for users intending to operate RapidSMS at scale
* Work with Evan to integrate 3rd party service providers like Vumi
* Delivery: End of month 7

Revamp RapidSMS website
***********************

* Highlight high level stories of current installations with pictures and maps
* Provide a page to track 3rd party reusable apps and backends
* Blog syndication (community page)
* Migrate existing content to new platform
* Begin marketing new release
* UNICEF Deliverables:
    * Information gathering and content writing for featured case studies on website
* Delivery: End of month 8

Build extensible implementations of key RapidSMS core / contrib apps
********************************************************************
* scheduler
* locations
* groups
* Delivery: End of month 9

Release 1.0
***********

* Write a tutorial similar to the Django tutorial for beginners
* Finish documentation for new core features
* Write release notes for v1.0
* Finish development on outstanding core features and bugs
* Delivery: End of month 10

Create and document RapidSMS deployment methods
***********************************************

* Review and analyze cloud hosting providers
* Write comprehensive deployment documentation for chosen providers
* Provide instructions and scripts to deploy project in a few simple steps
* Delivery: End of month 11
