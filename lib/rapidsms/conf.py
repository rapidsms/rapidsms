#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

# django-app-settings should be included as a submodule or a dependency,
# but we shouldn't *require* it. if it's not available, silently fall
# back to djano. apps should `from rapidsms.conf import settings`.
try: from djangoappsettings import settings
except: from django.conf import settings
