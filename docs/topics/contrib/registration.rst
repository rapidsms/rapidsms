=============================
rapidsms.contrib.registration
=============================

.. module:: rapidsms.contrib.registration

The `registration` app provides a nice interface for creating, updating,
and deleting RapidSMS contacts, both on the web and via SMS messages. It is
deliberately minimal, and outside
of the core, so other apps can extend or replace it where necessary.

Installation
============

1. `registration` depends on :doc:`handlers <handlers>`, so first install
`handlers`.

2. Add ``"rapidsms.contrib.registration"`` to
:setting:`INSTALLED_APPS` in your settings file:

.. code-block:: python
    :emphasize-lines: 3

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.registration",
        ...
    ]

3. Add URLs for `registration` to your urlconf:

.. code-block:: python
    :emphasize-lines: 3

    urlpatterns = ("",
        ...
        (r"^registration/", include("rapidsms.contrib.urls")),
        ...
    )

4. (Optional) add `registration` link to the nav bar:


.. code-block:: html
    :emphasize-lines: 2

    {% load url from future %}
    <li><a href="{% url 'registration' %}">Registration</a></li>

.. _registration-usage:

Usage
=====

The `registration` app provides both web and SMS interfaces.

Web
---

At the left of each page is a set of links:

* List Contacts
* Add Contact
* Bulk Add Contacts

List Contacts is the front page.  It displays a table with the contacts.
You can click on a contact row to edit that contact. You can edit the
contact's name, language, etc., and also edit their connections near the
bottom. A blank connection form is at the bottom; add a new connection by
filling in the blank form's Backend and Identity fields and saving.  Each
existing connection has a Delete checkbox; delete a connection by checking
its checkbox and saving. You can delete a contact by clicking the Delete
Contact button at the bottom.

Add Contact goes to a blank form for adding a new contact. It works just
like the page for editing a contact.

Bulk Add Contacts allows creating many contacts at once by uploading a
.CSV file with the data. There's help on the page showing the format
that the file should have.

SMS Messages
------------

Users can use SMS messages to register themselves or change their
preferred language through the `register` app.

REGISTER
~~~~~~~~

Users can create a contact for themselves along with a connection
representing their backend and identity by sending a text message
of the form::

    REGISTER <name>

They can also use ``REG`` or ``JOIN`` as synonyms for ``REGISTER``.

LANGUAGE
~~~~~~~~

After they have registered, users can choose their preferred language
by sending a text message of the form::

    LANGUAGE <code>

They can also use ``LANG`` as a synonym for ``LANGUAGE``.

The ``<code>`` should be the international code for the language,
e.g. ``pt-BR`` for Brazilian Portuguese or ``de`` for German.
