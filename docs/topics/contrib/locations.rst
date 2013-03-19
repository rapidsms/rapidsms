==========================
rapidsms.contrib.locations
==========================

.. module:: rapidsms.contrib.locations

.. warning::

    The fate of ``rapidsms.contrib.locations`` is currently up for debate in
    the RapidSMS community. It has been updated to run in RapidSMS v0.12.0+,
    but not all functionality is supported. If you're interested in
    contributing to Locations, please see this `message thread
    <https://groups.google.com/d/msg/rapidsms/oBQiDFNmKAc/hDKVD4C4AucJ>`_.

Locations allows you to easily map custom locations and points in your i
RapidSMS project.

.. _locations-installation:

Installation
============

1. The `locations` contrib application depends on `djtables
   <https://pypi.python.org/pypi/djtables>`_ to display data. You can install
   `djtables` using pip:

.. code-block:: bash

    pip install djtables

2. Add ``"rapidsms.contrib.locations"`` and ``"djtables"`` (if not already
   present) to :setting:`INSTALLED_APPS` in your settings file::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.locations",
        "djtables",
        ...
    ]

3. Add `locations` URLs to your urlconf::

    urlpatterns = patterns("",
        ...
        (r"^locations/", include("rapidsms.contrib.locations.urls")),
        ...
    )

4. Create database tables for the `locations` models:

.. code-block:: bash

    $ python manage.py syncdb

5. If wanted, add a navigation item to your ``rapidsms/_nav_bar.html`` template:

.. code-block:: html

    {% load url from future %}
    <li><a href="{% url "locations" %}">Map</a></li>

.. _locations-usage:

Usage
=====

Locations will auto-generate a map and editing interface for any models that
inherit from `rapidsms.contrib.locations.models.Location`. For example, say
you had an application called `cities` with a `City` model:

.. code-block:: python

    # example file: cities/models.py

    from django.db import models
    from rapidsms.contrib.locations.models import Location

    class City(Location):
        name = models.CharField(max_length=100)

        class Meta(object):
            app_label = "cities"
            verbose_name_plural = "cities"

To use Locations, you'd add `cities` to your installed apps:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "cities",
        ...
    ]

Create the necessary database tables:

.. code-block:: bash

    $ python manage.py syncdb

Now visit the Map tab in your browser to see the `City` model.
