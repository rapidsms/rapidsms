.. _rapidsmsdev:

Getting the code for development
================================

Here's how you can get the RapidSMS source code and make changes to it.

Git
---

The RapidSMS project uses `Git`_ to manage its source code. If you're not
familiar with Git already, you'll find it useful knowledge for more than
working on RapidSMS. Git is an incredibly popular source control tool, and
there is a huge amount of documentation on the net ranging from introductory
tutorials to in-depth reference material.

Clone the repository
--------------------

Clone the RapidSMS source repository from Github:

.. code-block:: console

    $ git clone git://github.com/rapidsms/rapidsms.git
    Cloning into 'rapidsms'...
    remote: Counting objects: 25262, done.
    remote: Compressing objects: 100% (8696/8696), done.
    remote: Total 25262 (delta 15920), reused 24482 (delta 15498)
    Receiving objects: 100% (25262/25262), 5.20 MiB | 1.09 MiB/s, done.
    Resolving deltas: 100% (15920/15920), done.

You'll now have a new ``rapidsms`` subdirectory containing the code.

Environment
-----------

Install virtualenv and virtualenvwrapper (see :ref:`using-virtualenv`).

Change into the ``rapidsms`` directory:

.. code-block:: console

    $ cd rapidsms
    $


Create a virtual environment to work in and activate it:

.. code-block:: console

    $ mkvirtualenv --no-site-packages rapidsms
    ...
    $

Master branch
-------------

The default branch in the RapidSMS repository is ``develop``, because
that's the branch used when working on new features for an upcoming
release, and so most developers use it a lot.

But let's switch to the stable branch, ``master``, for now, so we can
run the tests and verify that we have things set up right.

.. code-block:: console

    $ git checkout master
    Branch master set up to track remote branch master from origin.
    Switched to a new branch 'master'
    $

Requirements
------------

Install RapidSMS's requirements using distribute's `develop`_ command:

.. code-block:: console

    $ python setup.py develop
    [lots of output omitted]
    $

.. _develop: http://packages.python.org/distribute/setuptools.html#develop-deploy-the-project-source-in-development-mode

Tests
-----

Verify that everything is okay by running RapidSMS's tests.

.. code-block:: console

    $ tox
    [lots of output omitted]
    ____________________________________________ summary _____________________________________________
      py26-1.4.X: commands succeeded
      py26-1.5.X: commands succeeded
      py26-trunk: commands succeeded
      py27-1.4.X: commands succeeded
      py27-1.5.X: commands succeeded
      py27-trunk: commands succeeded
      congratulations :)
    $

This takes a while the first time -- over 8 minutes on my computer.
But after that, the environments are already set up and it'll run much faster.
On my computer, subsequent tests take less than 30 seconds.

The code on the RapidSMS master branch should always pass the tests.
If anything fails, review these instructions, and if they still fail,
ask on IRC or the rapidsms-dev mailing list.

Work on a branch
----------------

When you're ready to start making changes, you'll want to create a new
branch. You have a choice to base your branch on the ``master`` or
``develop`` branch. The tip of the ``master`` branch is always the latest
released code. It's stable, but does not include any changes currently
under development for the next release.

The ``develop`` branch contains changes that are ready for the next release.
It should also be pretty stable, because all changes are developed on other
branches and not merged into ``develop`` until they appear to be ready, but
there's a bit more chance of there being something broken in ``develop``.

It's probably a good idea to base your branch on ``develop`` if possible,
because if you work from master, there might be changes already in develop
that your work won't take into account.

.. _Git: http://git-scm.com/
