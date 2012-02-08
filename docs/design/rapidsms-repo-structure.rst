The source code of RapidSMS is freely available at github, a community using the common and popular distributed version control system git(created by Linus Torvalds himself, the author of the Linux kernel).

http://github.com/rapidsms

The Core
==========

Goal
------

The goal of the core repository is to provide a relatively stable codebase that provides developers with features that will be used by almost everyone. It is meant to be small, stable and not change much. It provides the router, common backends and the webUI.

Additionally it provides extensible models such as "contact," an abstract way to represent a person who has one or more phone numbers. This is the "Contacts" app. App writers can extend this model in their own apps to encapsulate their specific metadata without interfering with the data of other apps and allowing the code to be reusable. As many apps can use contact as users would like.

Commit Rights
---------------

Core commit rights are limited to core committers. However anyone can submit a patch that can be committed by a core committer. Core committers are long term members of the community that have demonstrated a solid understanding of the codebase, high coding standards, participated in the community and submitted at least two patches that were accepted into the core.

URL
-----

http://github.com/rapidsms/rapidsms

Contributed Apps
==================

Goal
------

The goal of the contributed apps repository is to provide a place for applications that are designed to be reusable and solve common problems to live. All applications in this repository must be sufficiently abstract so they can be used for any deployment.

Some apps and interfaces in the contrib repository include:

The Locations App: Locations uses the model "location," an abstract way for app authors to attach metadata to geographic points and includes a WebUI to display them on a map. It is designed to be extensible by other apps so it is reusable.

Messaging Interface: There is a messaging API that provides a simple way for users of the web interface to send messages to contacts. It allows app authors to create message-able objects, for example a school could be assigned contacts which would allow a message to be sent from the web interface to all the teachers in the school.

Handlers: Handlers a slimmer alternative to apps, instead of 1 app with 10 patterns, one should write 10 handlers.
keywordhandler provides a simple prefix interface
patternhandler provides a regex interface
basehandler makes it easy to write more handlers
echo app is an app that is merely a container for a handler that echos a message. It is a good example to look at to see how handlers work.

Locations
^^^^^^^^^^^
Locations provide a flexible framework for dealing with adminstrative boundaries, water points, health facilities, schools, or anything else that is tied to the data being collected and it's physical location on a map. More information about how to configure locations to fit your project's needs can be found on the Locations page.

Commit Rights
---------------

The contrib apps are part of the core, and commit rights are the same.

URL
-----

https://github.com/rapidsms/rapidsms/tree/master/lib/rapidsms/contrib

Community Apps
================

Goal
-----

This is where all deployment specific apps will live. Community members can use them as a template for their own apps, experiment with new ideas, or find an app that may provide the features they need for their deployments.

Commit Rights
---------------
Commit rights to this repository will be given to anyone who asks.

URL
-----
http://github.com/rapidsms/rapidsms-community-apps-dev