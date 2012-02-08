Release process
================

(based on Django's release process http://docs.djangoproject.com/en/1.2/internals/release-process)

RapidSMS uses a time-based release schedule, with minor (i.e. 1.1, 1.2, etc.) releases every six weeks, or more, depending on features.

After each previous release (and after an optional cooling-off period of a week or two), the core development team will examine the landscape and announce a timeline for the next release. Most releases will be scheduled in the 4 - 8 week range, but if we have bigger features to development we might schedule a longer period to allow for more ambitious work.

Release cycle
==============

Each release cycle will be split into three periods, each lasting roughly one-third of the cycle:

PHASE ONE: FEATURE PROPOSAL
----------------------------

The first phase of the release process will be devoted to figuring out what features to include in the next version. This should include a good deal of preliminary work on those features – working code trumps grand design.

At the end of part one, the release manager, in consultation with core developers and community members, will propose a feature list for the upcoming release. This will be broken into:

* “Must-have”: critical features that will delay the release if not finished
* “Maybe” features: that will be pushed to the next release if not finished
* “Not going to happen”: features explicitly deferred to a later release.

Anything that hasn’t got at least some work done by the end of the first third isn’t eligible for the next release; a design alone isn’t sufficient.

PHASE TWO: DEVELOPMENT
-----------------------

The second third of the release schedule is the “heads-down” working period. Using the roadmap produced at the end of phase one, we’ll all work very hard to get everything on it done.

Longer release schedules will likely spend more than a third of the time in this phase.

At the end of phase two, any unfinished “maybe” features will be postponed until the next release. Though it shouldn’t happen, any “must-have” features will extend phase two, and thus postpone the final release.

Phase two will culminate with an alpha release (e.g., 1.2.3a)

PHASE THREE: BUGFIXES
----------------------

The last third of a release is spent fixing bugs – no new features will be accepted during this time. We’ll release a beta release about halfway through (e.g., 1.2.3b), and an rc complete with string freeze (e.g., 1.2.3rc1)one week before the end of the schedule.

**Merge procedures**

* **1** - Submit your idea or suggestion to the RapidSMS mailing list for discussion (http://groups.google.com/group/rapidsms).

* **2** - Prepare a patch of your fix or feature (along with unit tests and documentation).

* **3a** - For core framework code, a core committer will apply your patch unless anyone objects. If anyone objects, the objector must submit a suitable alternate solution in order to revert your patch, or offer a convincing argument up for a vote to the other core committers. (see extended guidelines below)

* **3b** - For contrib app code, fork the contrib-app repository, apply your patch, send a pull request, and email the list with a link to your fork, a description of your functionality to be added, changed, or fixed. If you do not include adequate unit tests and documentation, your patch will not be applied.

* **3c** - For community app code, fork the app repository, apply your patch, and send pull request to the app's maintainer.

The following are the guidelines for committing code to the rapidsms core framework repository

Contributor opens an issue, or comments on an existing issue, in the rapidsms/rapidsms issue tracker requesting a merge from their fork, including

* a link to the fork to be merged or an attached patch file
* a description of the functionality to be added, changed, or fixed
* some kind of promise that the Coding Standards have been adhered to ;-)

Contributor labels the issue review. Contributor notifies the community of the pending patch via the google group. Contributor has signed the individual and/or corporate contributor license agreement (see Contributor License Agreement section below) From here the process varies depending on whether the contributor submitting the patch is a committer or not.

For committers:
=================

The patch submitter waits some amount of time determined at his/her discretion, based on the size and scope of of the changes to allow any interested other developers to review. A recommended amount of time is around a day for average-sized changes.
If there is any feedback on the patch, the submitter should address that feedback before pushing the code.
If there is no feedback, or only positive feedback, the committer runs tests and pushes the patch on his/her own.

For non committers:
=====================

It is the patch submitters responsibility to nag the list until a committer can review the patch.
When the committer reviews the patch, if it looks good they notify the list that they are going to push it “in XX time”.
If there is any further feedback on the patch, the submitter or committer should address that feedback before pushing the code.

If there is no feedback, or only positive feedback, the committer runs tests and pushes the patch on his/her own.

When code is pushed, the original issue should be labeled applied, and (if appropriate) closed.

When reviewing code – things to consider:
============================================

* does the new code meet the coding standards for style, documentation, tests, etc.?
* does the new code fit with the existing architecture of the project?
* does the new code change the existing architecture or API?
* if the patch might be contentious, the reviewer should post concerns to the mailing list.
* if the patch looks like it might cause problems, the reviewer should leave constructive criticism in the issue tracker, * label the issue fixme, and respond over the mailing list.

RapidSMS code repositories
============================

Issue tracker for RapidSMS code repositories: http://github.com/rapidsms/rapidsms/issues

Core Framework
================

http://github.com/rapidsms/rapidsms-core-dev

All commits to the core framework are automatically tested by Hudson: http://harmonia.caktusgroup.com/job/rapidsms

Contrib Apps
===============

http://github.com/rapidsms/rapidsms-contrib-apps-dev

Community Apps
===============

http://github.com/rapidsms/rapidsms-community-apps-dev

Handy guide for adding your app to pypi: http://blog.nyaruka.com/adding-a-django-app-to-pythons-cheese-shop-py

Coding standards
=================

All code should be styled according to PEP 8 (http://www.python.org/dev/peps/pep-0008/)

Indent each level four spaces. Be sure to use spaces, and not tabs.

Add the following two lines to the beginning of your files to automatically configure many text editors (VI, Emacs) to do this automatically::

    #!/usr/bin/env python
    # vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


If you are using Eclipse for development, please read the :doc:`Eclipse Configuration <../configuration/eclipseconfiguration>`

Use CapitalizedCase for class names, underscored_words for method names.

Name a yourapp’s templatetags ‘yourapp-tags’. Other templatetags (not specific to an app) should not have the -tags suffix (e.g., ‘pagination’ instead of ‘pagination-tags’).

Code using os.path must be Windows and 'NIX friendly.

For example, check for a file using `os.path.join('foo','bar')` instead of `'foo/bar'`

Be sure every class and method has docstrings.

All code must work in Python 2.5 and above.

All merges to the main RapidSMS trunk must include the following

Documentation
================

Unit tests, if the merge adds or changes functionality in the core
API classes and methods should be marked as such. (How?)
The names and arguments to API methods must not be changed within a major version.

Additional arguments may be added to API methods within a major version if a default is provided.

Contributor License Agreement
===============================

`RapidSMS Individual Contributor License Agreement <https://spreadsheets.google.com/viewform?formkey=dGtKTGU1bWkwU1ctOEpkdENhaVQ5YkE6MA>`_

`View individual contributors <http://spreadsheets.google.com/pub?key=tkJLe5mi0SW-8JdtCaiT9bA&output=html>`_

`RapidSMS Corporate Contributor License Agreement <https://spreadsheets.google.com/viewform?formkey=dGJPeFh5NTV6NlJjclg1cFRKUFVsQmc6MA>`_

`View corporate contributors <http://spreadsheets.google.com/pub?key=tbOxXy55z6RcrX5pTJPUlBg&output=html>`_