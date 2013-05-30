.. _release-process:

===============
Release process
===============

The process for a new RapidSMS release begins when
a member of :ref:`core-team` decides it's
time for one and volunteers to serve as Release Manager for the new
release.

The Release Manager's job is to organize and lead the work
to get a new release out. Other people can help with any part
of the process, so anywhere in this document we say "Release Manager",
you can consider it to say "Release Manager or another person acting
under the leadership of the Release Manager".

The Release Manager starts by creating a new Github milestone
for the release, if there's not one already. It will be named
something like "v0.15.0".

There might already have been changes merged to the ``develop``
branch since the last release. The Release Manager should find
those closed issues and add the new milestone to them, so the
new milestone will contain all the issues that'll be in the new
release.

Then the Release Manager will look for existing issues, or create
new ones, that he wants to include in the new release. He'll
add the new milestone to each of those issues.

The Release Manager should use the rapidsms-dev mailing list to
inform everyone interested in the development of RapidSMS of
the progress of the release. In particular, he should solicit
suggestions for issues that should be included in the new
release, and ask people to try out the ``develop`` branch
as changes are merged.

When the Release Manager decides that all the changes he thinks
should be in the new release are ready, he
should ask on the rapidsms-dev mailing list whether
anyone objects to creating a new release from the current ``develop``
branch. If no one objects after a day or two, the Release Manager
can proceed to make a new release by following the
:ref:`release-checklist`.
