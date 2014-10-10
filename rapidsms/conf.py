#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

"""
This module wraps `djappsettings`_, a helper which provides per-app
default settings for RapidSMS apps. This makes it much easier to create
reusable apps, while remaining 100% backwards-compatible with Django's
``django.conf.settings`` object. To support this, apps should include a
``settings.py`` module containing their default settings, which can be
overriden by the project author in the top-level ``settings.py``.

.. _djappsettings: http://github.com/adammck/djappsettings
"""

try:
    from djappsettings import settings
except:
    from django.conf import settings  # noqa
