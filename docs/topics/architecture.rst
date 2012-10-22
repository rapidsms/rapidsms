RapidSMS Architecture Overview
==============================

.. image:: /_static/rapidsms-architecture.png
    :width: 100 %

Summary
-------

The goal of the core repository is to provide a relatively stable codebase that
provides developers with features that will be used by almost everyone. It is
meant to be small, stable and not change much. It provides the router, common
backends and the webUI.

Additionally it provides extensible models such as "contact," an abstract way
to represent a person who has one or more phone numbers. This is the "Contacts"
app. App writers can extend this model in their own apps to encapsulate their
specific metadata without interfering with the data of other apps and allowing
the code to be reusable. As many apps can use contact as users would like.
