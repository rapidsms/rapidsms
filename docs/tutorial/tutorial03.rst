.. _tutorial03:

RapidSMS Tutorial Part 3
========================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ

So far, nothing we've done really requires Django. Let's create a RapidSMS
application that uses Django's abilities to store data.

We'll create an extremely simple voting application. It will understand
two messages: ``VOTE <choice>`` will add a vote for the specified
choice, and ``RESULTS`` will respond with the current number of votes
for each choice.

(Please notice that this application is more appropriate for a group
to choose a place to go to lunch than for anything serious. It makes no
attempt whatsoever to enforce any of the controls a real election would
need.)

Create the application
----------------------

Create a new Django application. Let's call it "voting":

.. code-block:: console

    $ python manage.py startapp voting


The models
----------

This application is so simple that we'll only need one model. We'll
call it ``Choice``, and there will be one instance for each possible
choice. Each record will contain the name of the choice and the number
of votes for it so far.

.. code-block:: python

    # voting/models.py
    from django.db import models

    class Choice(models.Model):
        name = models.CharField(max_length=40, unique=True)
        votes = models.IntegerField(default=0)

Application Design
------------------

Even a simple application like this can demonstrate a important design
principle for RapidSMS applications.

Instead of adding to a candidate's vote count each time a vote arrived,
we could instead have created a Vote model and stored a record of each vote.
That seems like a little simpler way to handle an incoming vote.

However, if we did that, whenever we needed the results we would have to
query every record in our database to count up the votes for each choice.
There are SQL queries that can simplify doing that, but the database still
has to look at every record. And the next time we wanted the results, we'd
have to do that again.

We're better off doing a little more processing on each
message, if that can save us a lot of work later on.

Admin
-----

We'll want to use the Django admin to set up our choices. Typically you would
need to make a few simple changes to your project's ``urls.py``, but the
RapidSMS project template has already done that for us. So all we need to
do is add ``admin.py`` to our application:

.. code-block:: python

    # voting/admin.py
    from django.contrib import admin

    from .models import Choice

    admin.site.register(Choice)


The results handler
-------------------

Let's start with the simpler message to handle, ``RESULTS``. This is
easily implemented as a RapidSMS keyword handler. Let's create a file
``handlers.py`` to contain our handlers, and write a handler that responds
with the current votes.

.. code-block:: python

    # voting/handlers.py

    from rapidsms.contrib.handlers import KeywordHandler

    from .models import Choice


    class ResultsHandler(KeywordHandler):
        keyword = "results"

        def help(self):
            """help() gets invoked when we get the ``results`` message
            with no arguments"""
            # Build the response message, one part per choice
            parts = []
            for choice in Choice.objects.all():
                part = "%s: %d" % (choice.name, choice.votes)
                parts.append(part)
            # Combine the parts into the response, with a semicolon after each
            msg = "; ".join(parts)
            # Respond
            self.respond(msg)

        def handle(self, text):
            """This gets called if any arguments are given along with
            ``RESULTS``, but we don't care; just call help() as if they
            passed no arguments"""
            self.help()

If the choices are "Moe", "Larry", and "Curly", the response to a
``RESULTS`` message might look like ``Moe: 27; Larry: 15; Curly: 98``.

The vote handler
----------------

The ``VOTE`` message is slightly more work. If we receive ``VOTE xxxx``
where xxx is one of the choices (case-insensitive), we want to increment
the votes for choice ``xxx`` and respond telling the user that their
vote has been counted. If we receive any other message starting with ``VOTE``,
we'll respond with some help to tell them how the command works and what
the choices are.

.. code-block:: python

    # voting/handlers.py (continued)
    from django.db.models import F

    class VoteHandler(KeywordHandler):
        keyword = "vote"

        def help(self):
            """Respond with the valid commands.  Example response:
            ``Valid commands: VOTE <Moe|Larry|Curly>``
            """
            choices = "|".join(Choice.objects.values_list('name', flat=True))
            self.respond("Valid commands: VOTE <%s>" % choices)

        def handle(self, text):
            text = text.strip()
            # look for a choice that matches the attempted vote
            try:
                choice = Choice.objects.get(name__iexact=text)
            except Choice.DoesNotExist:
                # Send help
                self.help()
            else:
                # Count the vote. Use update to do it in a single query
                # to avoid race conditions.
                Choice.objects.filter(name__iexact=text).update(votes=F('votes')+1)
                self.respond("Your vote for %s has been counted" % text)

Settings
--------

We need to add our Django app to :setting:`INSTALLED_APPS` and our
handlers to :setting:`RAPIDSMS_HANDLERS`:

.. code-block:: python
    :linenos:
    :emphasize-lines: 4,11-12

    INSTALLED_APPS = (
       [...]
        # RapidSMS
        "voting",
       [...]
        "rapidsms.contrib.default",  # Must be last
    )

    RAPIDSMS_HANDLERS = [
        [...]
        "voting.handlers.ResultsHandler",
        "voting.handlers.VoteHandler",
        [...]
    ]

Update database
---------------

We've added a new model, so we need to update our database to
include it:

.. code-block:: console

    $ python manage.py syncdb
    Syncing...
    Creating tables ...
    Creating table voting_choice
    [... rest of output omitted ...]

Create some choices
-------------------

Now it's time to start our application and create some choices to vote
for.

.. code-block:: console

    $ python manage.py runserver
    Validating models...

    0 errors found
    May 07, 2013 - 08:28:44
    Django version 1.5.1, using settings 'rapidsms_tut.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Go to http://127.0.0.1:8000/admin/voting/choice/, login as the superuser
you created in part 1 of the tutorial, and you should be able to add some
choices.

Vote
----

Let's start by checking that there are no votes. Go to the message tester
application (http://127.0.0.1:8000/httptester/) and send the message
``RESULTS``. You should see a response showing no votes, something like
this::

    05/07/2013 8:30 a.m.	349911«	Moe: 0; Larry: 0; Curly: 0
    05/07/2013 8:30 a.m.	349911»	RESULTS

(Recall that the messages are shown in reverse order.)

Now let's cast a vote. Send ``VOTE Moe`` and you should see something
like::

    05/07/2013 8:32 a.m.	349911«	Your vote for Moe has been counted
    05/07/2013 8:32 a.m.	349911»	VOTE Moe

and if you check the results again::

    05/07/2013 8:33 a.m.	349911«	Moe: 1; Larry: 0; Curly: 0
    05/07/2013 8:33 a.m.	349911»	RESULTS


Continue with :ref:`tutorial04`.
