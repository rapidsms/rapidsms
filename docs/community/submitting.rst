.. _submitting:

Submitting changes back to the project
======================================

Here's how you can offer your changes back to the RapidSMS project,
so others can benefit from them.

(If you're a member of :ref:`core-team`, you should still follow
this process.)

See if there's support for your change
--------------------------------------

#. Check for open issues or open a fresh issue in the `ticket tracker`_ to
   start a discussion around a feature idea or a bug. Send a message to the
   `rapidsms-dev`_ mailing list to request feedback.

#. If you're working on a large patch, we highly recommend creating a `wiki
   page`_ under the RapidSMS GitHub account. Use the wiki page to outline the
   motivation behind the patch and to document decisions made on the
   `rapidsms-dev`_ mailing list.

   `Router decoupling and HTTP message processing`_, `Bulk Messaging API`_,
   and `Scheduling`_ are good examples.


Develop your change
-------------------

Write the code for your change.

Follow the RapidSMS :ref:`coding-standards`.

Sign the CLA
------------

Before your work can be accepted into the project, you'll have to
sign a
:ref:`Contributor License Agreement <contributor-license-agreements>`.

Ask for it to be added
----------------------

To ask the project to merge your changes into the official repository,
:ref:`pullrequest`.

Now what?
---------

What you'd like to happen is for someone with privileges
on the RapidSMS repository to merge your changes into the
``develop`` branch, so that they'll be included in the next
RapidSMS release.

Typically before that, there will be one or more rounds of people
making comments on your changes or asking questions to try to
improve the code.

If you don't hear anything after a few days, it's okay to ask on
the ``rapidsms-dev`` mailing list for someone to look at your pull
request.  Everyone is busy and sometimes a reminder is helpful.

Just remember that if you want your change included, you'll need to
take responsibility to convince people that it's worthwhile. And sometimes
perfectly good changes are not included in the project because they don't
appear to be useful to enough users. Every time code is added, it's a cost
to the project because it has to be maintained from then on.

You can always continue using the change in your fork, even if it's not
included in the main project.

Core team members
-----------------

If you're a member of :ref:`core-team`, there are a few small changes
to the process.

You can merge your own changes, but if possible, you should first get
another core team member to agree with them. Ask them to add a "ship it"
comment to the pull request.  After that, you can merge your changes.

It's also your prerogative to merge your own changes if no one has commented
after a few days. Just keep in mind that whatever changes you make will
contribute to your own standing in the community.

.. _Git Flow: http://nvie.com/posts/a-successful-git-branching-model/
.. _gitflow tool: https://github.com/nvie/gitflow
.. _Github: https://github.com
.. _RapidSMS repository: https://github.com/rapidsms/rapidsms
.. _ticket tracker: https://github.com/rapidsms/rapidsms/issues?state=open
.. _rapidsms-dev: http://groups.google.com/group/rapidsms-dev
.. _wiki page: https://github.com/rapidsms/rapidsms/wiki/_pages
.. _Router decoupling and HTTP message processing: https://github.com/rapidsms/rapidsms/wiki/Router-decoupling-and-HTTP-message-processing
.. _Bulk Messaging API: https://github.com/rapidsms/rapidsms/wiki/Bulk-Messaging-API
.. _Scheduling: https://github.com/rapidsms/rapidsms/wiki/Scheduling
