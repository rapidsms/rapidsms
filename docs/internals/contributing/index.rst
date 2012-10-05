Contributing to RapidSMS
========================

We're always excited to welcome new volunteers to the RapidSMS project. As it
keeps growing, we need more people to help others and contribute back to the
community. As soon as you learn RapidSMS, you can contribute in many ways:

* Join the `rapidsms`_ mailing list and answer questions. This users list, the
  primary RapidSMS mailing list, is used to ask and answer questions, help work
  through bugs, and discuss general RapidSMS topics.

* Join the `rapidsms-dev`_ mailing list. This list is used to discuss RapidSMS
  core and active country projects. This ranges from new RapidSMS features
  to large scale RapidSMS deployments in Zambia. If you're interested in any of
  this, please join the conversation!

* Join the `#rapidsms IRC channel`_ on Freenode and answer questions. By
  explaining RapidSMS to other users, you're going to learn a lot about the
  framework yourself. You can use the `webchat`_ client for this too.

And, of course, you can help out by working *on* RapidSMS.

* Report bugs in our `ticket tracker`_.

* Open `pull requests`_ for features and bug fixes.

* Comment on open issues and pull requests.

* Improve the RapidSMS documentation (what you're reading now!).

* Participate on the `rapidsms-dev`_ mailing list.

Submitting code
---------------

* Check for open issues or open a fresh issue in the `ticket tracker`_ to start
  a discussion around a   feature idea or a bug. Send a message to the
  `rapidsms-dev`_ mailing list to request feedback.

* Fork the repository on GitHub to start making your changes (relative to the
  master branch).

* Follow the RapidSMS :ref:`coding standards <coding-standards>`.

* Write a test which shows that the bug was fixed or that the feature works as
  expected.

* Run the RapidSMS :doc:`test suite <testing>` to make sure nothing unexpected 
  broke. We only accept pull requests with passing tests.

* Write new or update old documentation to describe the changes you made.

* Make sure to add yourself to AUTHORS.

* Send a pull request and request feedback on `rapidsms-dev`_. 

.. _coding-standards:

Coding standards and best practicies
************************************

#. Follow `PEP8 style conventions <http://www.python.org/dev/peps/pep-0008/>`_.
   Use 4 spaces instead of tabs.

#. Use CapitalizedCase for class names, underscored_words for method names.

#. Code using ``os.path`` must be Windows and 'NIX friendly. For example, check
   for a file using `os.path.join('foo','bar')` instead of `'foo/bar'`

#. Be sure every class and method has docstrings.

#. Add the following two lines to the beginning of your files to automatically
   configure many text editors (VI, Emacs) to do this automatically::

    #!/usr/bin/env python
    # vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

.. _rapidsms: http://groups.google.com/group/rapidsms
.. _rapidsms-dev: http://groups.google.com/group/rapidsms-dev
.. _#rapidsms IRC channel: irc://irc.freenode.net/rapidsms
.. _webchat: http://webchat.freenode.net?channels=rapidsms
.. _ticket tracker: https://github.com/rapidsms/rapidsms/issues?state=open
.. _pull requests: https://github.com/rapidsms/rapidsms/pulls
