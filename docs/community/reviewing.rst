.. _reviewing:

Reviewing pull requests
=======================

Everyone is welcome to comment on pull requests. If you're deeply
familiar with the RapidSMS code, you might spot a fundamental problem.
But if not, you still can look for smaller-scale bugs, typos,
style issues, better algorithms, etc.

The :ref:`coding-standards` are a good checklist when reviewing
pull requests. All pull requests are expected to comply with our
coding standards.

Check out the code from the pull request's branch and try running
it locally. Make sure the tests pass on your system; it might be different
from the submitter's system. Try other things; even if all the tests pass,
there might be things we forgot to write a test for, or couldn't.

See if your own app still works when using the modified RapidSMS.
Sometimes different apps use RapidSMS in different ways.

If you are on :ref:`core-team`, you're encouraged to review pull
requests and if they look acceptable, merge them to the ``develop``
branch. Or if the submitter is another core team member, add a
``ship it!`` comment and let them do the merging.

In any case, please try to be polite in your comments, and give the
submitter the benefit of the doubt. Before clicking to submit your
comment, think about how you would feel if someone made that comment
about your code.

One good policy when writing review comments is to always refer to
the code, never to the submitter.  Remember that what we're reviewing
is the code, not the person. For example, instead of saying
"you didn't check for None", you might instead say "the method
is missing a check for None".
