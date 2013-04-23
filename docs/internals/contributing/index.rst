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

* Open `pull requests`_ for features and bug fixes against the
  `develop` branch.  We use the `Gitflow`_ model for our development.

* Comment on open issues and pull requests. Try the changes yourself and
  report on how well they work in the issue or pull request.

* Improve the RapidSMS :ref:`documentation <writing-documentation>` (what
  you're reading now!).

* Participate on the `rapidsms-dev`_ mailing list.

.. _Gitflow: http://nvie.com/posts/a-successful-git-branching-model/

Submitting code
---------------

#. Check for open issues or open a fresh issue in the `ticket tracker`_ to
   start   a discussion around a   feature idea or a bug. Send a message to the
   `rapidsms-dev`_ mailing list to request feedback.

#. If you're working on a large patch, we highly recommend creating a `wiki
   page`_ under the RapidSMS GitHub account. Use the wiki page to outline the
   motivation behind the patch and to document decisions made on the
   `rapidsms-dev`_ mailing list.
   `Router decoupling and HTTP message processing`_, `Bulk Messaging API`_,
   and `Scheduling`_ are good examples.

#. Fork the repository on GitHub to start making your changes (relative to the
   `develop` branch).

#. Follow the RapidSMS :ref:`coding standards <coding-standards>` and run the
   :ref:`PEP 8 adherence tool <pep-eight-adherence>`.

#. Write a test which shows that the bug was fixed or that the feature works as
   expected.

#. Run the RapidSMS :doc:`test suite <testing>` to make sure nothing unexpected
   broke. We only accept pull requests with passing tests.

#. Write new or update old documentation to describe the changes you made.

#. Add the change to the release notes document for the next release. The
   release notes should focus on the effects on existing users, particularly
   if it will require them to make changes.

#. Make sure to add yourself to `AUTHORS`_.

#. Open a pull request against the `develop` branch (see `Gitflow`_), and
   request feedback on `rapidsms-dev`_.

#. Sign the :ref:`Contributor License Agreement <contributor-license-agreements>`.

.. _coding-standards:

Coding standards and best practices
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

Using virtualenv
****************

We highly recommend using `virtualenv`_ and `virtualenvwrapper`_ to work on
RapidSMS core. These tools provide isolated Python environments, which are more
practical than installing packages system wide. They also allow installing
packages without administrator privileges. This section will outline the steps
to setup RapidSMS core so that you can edit it while working on a RapidSMS
project.

1. **Install virtualenv and virtualenvwrapper.** Use pip to install the latest
   version (and upgrade if you have an older copy):

.. code-block:: bash

    sudo pip install --upgrade virtualenv
    sudo pip install --upgrade virtualenvwrapper

Then follow the `virtualenvwrapper install docs`_ to setup your shell properly.

2. **Create a new virtual environment for RapidSMS.** Now we'll create a new
   virtual environment to isolate our development:

.. code-block:: bash

    mkvirtualenv --distribute rapidsms

3. **Install RapidSMS in development mode.** This install is done in such a
   way that changes to the RapidSMS source are immediately available in your
   project, without needing to run a build or install step after each change.
   To do this, navigate to the RapidSMS clone on your file system and use
   distribute's `develop`_ command:

.. code-block:: bash

    cd <your-rapidsms-clone>
    python setup.py develop

4. **Setup your project.** Now we can use our new virtual environment with a
   RapidSMS project to test changes and modifications. You can create a new
   project (e.g. by :ref:`installing-rapidsms-project-template`).

5. **Remember to activate your virtualenv.** If you restart or need to return
   to your virtualenv at any point, you can easily reactivate it:

.. code-block:: bash

    workon rapidsms

Now any changes made to your local RapidSMS clone will be reflected immediately
while editing your project.

Logging
*******

If you want to log in your app, just::

    import logging
    logger = logging.getLogger(__name__)

and use::

    logger.debug("msg")
    logger.critical("msg")
    logger.exception("msg")
    # etc.

All RapidSMS core logging can now be captured using the ``'rapidsms'``
root logger.  (There's not a lot of logging from the core yet, but pull
requests are welcome.)

For example, if you wanted messages from the RapidSMS
core to be written to a file `"/path/rapidsms.log"`, you could define
a new handler in the :setting:`LOGGING` setting in Django::

    LOGGING = {
        ...
        'handlers': {
            ...
            'rapidsms_file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/path/rapidsms.log',
            },
            ...
        },
        ...
    }

and then configure the ``rapidsms`` logger to send messages to it::

    LOGGING = {
        ...
        'loggers': {
            'rapidsms': {
                'handlers': ['rapidsms_file'],
                'propagate': True,
                'level': 'DEBUG',
            },
        },
        ...
    }


If you created your project with the latest `rapidsms-project-template`_
and haven't changed the settings, all rapidsms logging will be written
to `rapidsms.log` in your project directory.

.. _rapidsms-project-template: https://github.com/rapidsms/rapidsms-project-template/

.. _writing-documentation:

Writing documentation
---------------------

We believe RapidSMS needs to treat our documentation like we treat our code.
It's what you're reading now and is generally the first point of contact for
new developers. We value great, well-written documentation and aim to improve
it as often as possible. And we're always looking for help with documentation!

Getting the raw documentation
*****************************

The official documentation is available on `Read the Docs`_. This is the
compiled HTML version. However, we edit it as a collection of text files for
maximum flexibility. These files live in the top-level ``docs/`` directory of a
RapidSMS release. If you'd like to start contributing to our docs, get the
development version of RapidSMS from the source code repository
(see :ref:`installing-development-version`).

Using Sphinx
************

Before building the documentation, you must have a version of RapidSMS
installed.  See the :ref:`installing-development-version` guide for
instructions on installing RapidSMS.

We use the Sphinx__ documentation system (based on docutils__). To
build the documentation locally, you'll need to install Sphinx::

    pip install Sphinx

Then, building the HTML is easy. Just run make from the ``docs`` directory::

    make html

(or ``make.bat html`` on Windows)

To get started contributing, you'll want to read the `reStructuredText
Primer`_. After that, you'll want to read about the `Sphinx-specific markup`_
that's used to manage metadata, indexing, and cross-references.

Documentation starting points
*****************************

Typically, documentation changes come in two forms:

* **General improvements:** typo corrections, error fixes and better
  explanations through clearer writing and more examples.

* **New features:** documentation of features that have been added to the
  framework since the last release.

If you're interested in helping out, a good starting point is with the
`documentation label`_ on the GitHub issue tracker.


.. toctree::

    license
    testing
    /intro/tutorial-videos
    release-checklist
    release-process


__ http://sphinx.pocoo.org/
__ http://docutils.sourceforge.net/

.. _Read the Docs: http://rapidsms.readthedocs.org/
.. _rapidsms: http://groups.google.com/group/rapidsms
.. _rapidsms-dev: http://groups.google.com/group/rapidsms-dev
.. _#rapidsms IRC channel: irc://irc.freenode.net/rapidsms
.. _webchat: http://webchat.freenode.net?channels=rapidsms
.. _ticket tracker: https://github.com/rapidsms/rapidsms/issues?state=open
.. _pull requests: https://github.com/rapidsms/rapidsms/pulls
.. _AUTHORS: https://github.com/rapidsms/rapidsms/blob/master/AUTHORS
.. _reStructuredText Primer: http://sphinx.pocoo.org/rest.html#rst-primer
.. _Sphinx-specific markup: http://sphinx.pocoo.org/markup/index.html#sphinxmarkup
.. _documentation label: https://github.com/rapidsms/rapidsms/issues?labels=documentation&page=1&state=open
.. _Router decoupling and HTTP message processing: https://github.com/rapidsms/rapidsms/wiki/Router-decoupling-and-HTTP-message-processing
.. _Bulk Messaging API: https://github.com/rapidsms/rapidsms/wiki/Bulk-Messaging-API
.. _Scheduling: https://github.com/rapidsms/rapidsms/wiki/Scheduling
.. _wiki page: https://github.com/rapidsms/rapidsms/wiki/_pages
.. _virtualenv: http://rapidsms.readthedocs.org/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/
.. _virtualenvwrapper install docs: http://virtualenvwrapper.readthedocs.org/en/latest/install.html
.. _develop: http://packages.python.org/distribute/setuptools.html#develop-deploy-the-project-source-in-development-mode
