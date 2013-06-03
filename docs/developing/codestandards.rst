.. _coding-standards:

Coding standards and best practices
************************************

We follow these practices when developing RapidSMS code:

#. Work on a branch off the ``develop`` branch.

#. Follow `PEP8 style conventions <http://www.python.org/dev/peps/pep-0008/>`_.
   Use 4 spaces instead of tabs.

#. Run the :ref:`PEP 8 adherence tool <pep-eight-adherence>`.

#. Use CapitalizedCase for class names, underscored_words for method names.

#. Code using ``os.path`` must be Windows and 'NIX friendly. For example,
   don't use backslashes (``\``) as path separators.

#. Be sure every class and method has docstrings.

#. Use :ref:`Python logging <logging>` whenever an error or exception occurs.
   Optionally include debug-level logging.

#. Write a test which shows that the bug was fixed or that the feature works as
   expected.

#. Run the :ref:`test_suite` to make sure nothing unexpected
   broke. We only accept pull requests with passing tests.

#. Write new or update existing :ref:`documentation <writing-documentation>`
   to describe the changes you made.

#. Add the change to the release notes document for the next release. The
   release notes should focus on the effects on existing users, particularly
   if it will require them to make changes.

#. Submit a pull request and get reviews before merging your changes, even
   if you have authority to merge the changes yourself.

#. Sign the
   :ref:`Contributor License Agreement <contributor-license-agreements>`.
