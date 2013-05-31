.. _release-process:

===============
Release process
===============

The process for a new RapidSMS release begins when a
:ref:`release-champion` is identified for it.
The release champion's job is to organize and lead the work
to get a new release out. Any of the work identified below
could be done by anyone, under the release champion's
leadership.

The release champion starts by creating a new Github milestone
for the release, if there's not one already. It will be named
something like "v0.15.0".

There might already have been changes merged to the ``develop``
branch since the last release. The release champion should find
those closed issues and add the new milestone to them, so the
new milestone will contain all the issues that'll be in the new
release.

Then the release champion will look for existing issues, or create
new ones, that they want to include in the new release. They'll
add the new milestone to each of those issues.

The release champion should use the rapidsms-dev mailing list to
inform everyone interested in the development of RapidSMS of
the progress of the release. In particular, they should solicit
suggestions for issues that should be included in the new
release, and ask people to try out the ``develop`` branch
as changes are merged.

The release champion and :ref:`release-manager` collaborate
when it's time to ship the new release, with the release manager
responsible for final QA and the actual :ref:`release-checklist`
steps to publish a new release.
