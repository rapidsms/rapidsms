.. _release-checklist:

RapidSMS Release Checklist
==========================
This is a checklist for releasing a new version of RapidSMS.

This is intended for someone who has been designated the
:ref:`release-manager`,
the person responsible for making an official release of RapidSMS.

For a higher-level overview of the whole release cycle, see the
:ref:`Release Process <release-process>`.

Git branches
------------

RapidSMS uses the
`Git Flow <http://nvie.com/posts/a-successful-git-branching-model/>`_
process for development. The two branches of concern at release time are:

* **master** - always has the most recently released code. Each release is
  tagged ``vX.X.X``.
* **develop** - contains the code under development for the next release

So technically, what makes a new release is merging ``develop`` to ``master``
and tagging it.  Of course, we don't want to do that until we're ready.

Required permissions
--------------------

You'll need the following authorizations to make a release:

Github
    push to the `rapidsms repository <https://github.com/rapidsms/rapidsms>`_
PyPI
    push updates to the `rapidsms package <https://pypi.python.org/pypi/RapidSMS>`_
Read the Docs
    change the configuration for RapidSMS

If you need any of these authorizations:

* create any of the accounts you don't have
* send an email to rapidsms-dev@googlegroups.com and ask for someone to give
  you the needed authorizations. Be sure to include your userid for each
  account.

Release checks
--------------

All the following checks should be verified before continuing:

* ``master`` merged to ``develop`` to be sure any hotfixes are included
* Version number in ``rapidsms/__init__.py`` updated
* `Next` version number in ``rapidsms/docs/conf.py`` updated
* New release labeled as current in ``rapidsms/docs/releases`` in
  ``index.rst``, ``this-release.rst``, and ``roadmap.rst``
* Previous release not labeled as current in ``rapidsms/docs/releases`` in
  ``index.rst``, ``prev-release.rst``, and ``roadmap.rst``.
* Create a ``release-X.X.X`` branch (based off ``master``) in the RapidSMS
  `project template repository`_. Make sure to update ``README.rst`` as well.
* Update project template command line in ``intro/install/index.rst`` to point
  to the RapidSMS project template release branch.
* All git issues for this release's milestone have been resolved.  (closed or
  moved to another milestone)
* All tests pass against the ``develop`` branch.  Look for a passing build
  on `Travis <https://travis-ci.org/rapidsms/rapidsms/>`_ of the tip commit
  on the ``develop`` branch.
* A distribution tarball can be built with ``python setup.py sdist``, it can
  be installed with pip, has the right version, and works when installed.
  (SUGGEST HOW TO TEST AN INSTALLED RAPIDSMS)

Release steps
-------------

Take these steps to release the new version:

* Make a fresh clone of the repo:

.. code-block:: bash

    git clone git@github.com:rapidsms/rapidsms.git
    cd rapidsms

* Checkout master:

.. code-block:: bash

    git checkout master

* Merge develop into master:

.. code-block:: bash

    git merge develop

* Run the tests locally. (This assumes you have tox on your path. Create a
  new virtualenv and install it if needed.) The tests must pass before
  proceeding.

.. code-block:: bash

    tox

* Create a new tag:

.. code-block:: bash

    git tag -a vX.X.X

* Push the merged master branch and tag to github:

.. code-block:: bash

    git push origin master --tags

* While Travis is testing the pushed branch, compose a release announcement.

Here's a template that can be used for release announcements. You can copy
the summary from the release notes:

    Subject: RapidSMS X.X.X Released

    I'm excited to announce the release of
    `RapidSMS X.X.X <https://rapidsms.readthedocs.org/en/vX.X.X/releases/X.X.X.html>`_!
    Here's a quick summary:

    * **Major change or feature 1:** *one-line explanation*
    * **Major change or feature 2:** *one-line explanation*
    * ...

    You can find the full list of changes and upgrade guide in the
    `RapidSMS X.X.X Release Notes <https://rapidsms.readthedocs.org/en/vX.X.X/releases/X.X.X.html>`_.

    I'd like to give special thanks to Tom, Dick, and Harry for their work
    on this release. *[EXPAND ON THAT].*

    More help is always welcome. If you're interested, you can read the
    `contributing guide <http://rapidsms.readthedocs.org/en/vX.X.X/internals/contributing/index.html>`_.

    The next release will be *Y.Y.Y* and will focus on *FILL IN MAJOR GOALS
    FOR Y.Y.Y.*

    As always, if you have any questions or issues, please feel free to
    post them to this list or ask in the #rapidsms IRC channel on
    `Freenode <http://freenode.net/>`_. Bugs can be reported on
    `Github <https://github.com/rapidsms/rapidsms>`_.

* Verify that Travis tests have passed for the pushed master

* Push the new version to `PyPI <http://docs.python.org/3/distutils/packageindex.html>`_:

  .. code-block:: bash

        python setup.py sdist upload

* Add the new version to the tags that Read the Docs should build

* Email the release announcement to rapidsms@googlegroups.com and
  rapidsms-dev@googlegroups.com

Start Next Release
------------------

Back on the ``develop`` branch, we can now start on the next release:

* Merge ``master`` to ``develop`` to make sure we're starting from the same
  code that's currently released (there might have been merge conflicts or
  something during the release process).
* Update the version in ``rapidsms/__init__.py`` and the next version in
  ``rapidsms/docs/conf.py``.
* Start a new release notes document in ``rapidsms/docs/release``. Use the
  previous release's document as a template. Be sure
  to label it at the top as under development.
* Update ``rapidsms/docs/release/index.rst`` to mark the next release as
  under development.
* Create a new Github milestone with the next release number, e.g.
  "v0.15.0", so that developers can start targeting work for the
  next release.

Now we can start merging features intended for the next release. Review
`Git Flow <http://nvie.com/posts/a-successful-git-branching-model/>`_
for more about how to use git branches while developing.

.. _project template repository: https://github.com/rapidsms/rapidsms-project-template/
