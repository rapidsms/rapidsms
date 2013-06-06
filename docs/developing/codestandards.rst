.. _coding-standards:

Coding standards and best practices
************************************

We follow these practices when developing RapidSMS code:

#. Work on a branch off the ``develop`` branch.

#. Follow `PEP8 style conventions <http://www.python.org/dev/peps/pep-0008/>`_.
   Use 4 spaces instead of tabs.

   * To learn more about writing 'pythonic' code, check out
     The Hitchhiker's Guide To Python's `Code Style guide <http://docs.python-guide.org/en/latest/writing/style.html>`_

   * Tip: `Configure your development environment for python <http://docs.python-guide.org/en/latest/dev/env.html>`_
     to make your life a bit easier.

#. Run the :ref:`PEP 8 adherence tool <pep-eight-adherence>`.

#. Use CapitalizedCase for class names, underscored_words for method names.

#. Code using ``os.path`` must be Windows and 'NIX friendly. For example,
   don't use backslashes (``\``) as path separators.

#. Be sure every class and method has `docstrings <http://docs.python-guide.org/en/latest/writing/documentation.html#code-documentation-advice>`_.

#. Use :ref:`Python logging <logging>` whenever an error or exception occurs.
   Optionally include debug-level logging.

#. Write a `test <http://docs.python-guide.org/en/latest/writing/tests.html>`_
   which shows that the bug was fixed or that the feature works as expected.

#. Run the :ref:`test_suite` to make sure nothing unexpected
   broke. We only accept pull requests with passing tests.

#. Write new or update existing :ref:`documentation <writing-documentation>`
   to describe the changes you made.

#. Add the change to the `release notes <https://github.com/rapidsms/rapidsms/tree/develop/docs/releases>`_
   document for the next release. The release notes should focus on the effects
   on existing users, particularly if it will require them to make changes.

#. Submit a `pull request <https://help.github.com/articles/using-pull-requests>`_
   and get reviews before merging your changes, even if you have authority to
   merge the changes yourself.

#. Sign the
   :ref:`Contributor License Agreement <contributor-license-agreements>`.
