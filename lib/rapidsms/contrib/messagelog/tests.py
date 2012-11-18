#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase
from rapidsms.tests.harness.base import CreateDataMixin
import rapidsms.contrib.messagelog.app


class MessageLogTest(CreateDataMixin, TestCase):
    def test_messagelog(self):
        """Make sure Django 1.4 timezone aware datetimes don't disrupt _log"""

        app = rapidsms.contrib.messagelog.app.App(None)
        # Invoke _log, make sure it doesn't blow up regardless of Django
        # version. See issue #171 for more details.
        contact = self.create_contact()
        app._log('I', {'contact': contact}, "text")
