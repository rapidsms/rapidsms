.. _contributing-fix:

Contributing a fix
==================

This example outlines how to use distribute, pip, and virtualenv to fix
and submit a patch to RapidSMS.

To begin, let's say we have a RapidSMS project, myproject, that's running
rapidsms==0.15.0 installed using pip. During development, we discover a
bug or want to add a feature to RapidSMS. How do we submit a patch?

First, fork the `rapidsms repository`_ on GitHub. All future changes will be
pushed here for RapidSMS core devs to review.

Next, we'll need to remove rapidsms==0.15.0 from our virtual environment
and install our forked version for testing. Uninstalling is easy with pip::

    ~/myproject$ workon project
    (project)~/myproject$ pip uninstall rapidsms

To install a version for testing, clone your forked rapidsms repository::

    (project)~/myproject$ cd ~
    (project)~$ git clone git@github.com:username/rapidsms.git rapidsms-fork
    (project)~$ cd rapidsms-fork
    (project)~/rapidsms-fork$

Bug fixes are almost always included in a later release, so it's a good
idea to make your fix against the branch that contains the current code for
the next release, the ``develop`` branch.  Check out the ``develop``
branch::

    (project)~/rapidsms-fork$ git checkout develop

Install forked RapidSMS in development mode. Note that your own project's
virtualenv is still active, so this will install RapidSMS for your project
to use::

    (project)~/rapidsms-fork$ python setup.py develop

Now any changes made to rapidsms-fork will immediately be available in
myproject. Further, you can run the RapidSMS test suite from your project::

    (project)~/myproject$ ./manage.py test rapidsms

We'll fix and write tests for the bug in rapidsms-fork, and push the
changes back to your rapidsms fork on GitHub. Before making any changes,
make sure to create a branch first, based on the ``develop`` branch::

    (project)~/rapidsms-fork$ git checkout -b my-fix
    ... make changes ...
    (project)~/rapidsms-fork$ git add [files to commit]
    (project)~/rapidsms-fork$ git commit

Push your changes up to your fork on github::

    (project)~/rapidsms-fork/$ git push -u origin my-fix

Now go to the github page for your fork. Near the top middle, you should see
a big button saying "Pull Request".  Click that button to start creating a
pull request. Change the base repo to ``rapidsms/rapidsms``, the base
branch to ``develop``, the head repo to ``username/rapidsms``, and the
head branch to your fix branch ``myfix``.

View "Files Changed" and make sure your pull request contains only your
fix, and your fix looks good. If you see a lot of unrelated changes, check
the base and head repositories and branches again.

If everything looks good, go back to "New Pull Request". Enter a
good description of the bug you're fixing and how your pull request fixes it.
If the bug has an issue in github, you should link to it using the #NNN
format.  (E.g. "This pull request is a fix for #123.")

Click the "Send Pull Request" button at the bottom right of the description
box to create the pull request.

.. _rapidsms repository: https://github.com/rapidsms/rapidsms.git
