import warnings

from django.test import TestCase
from rapidsms.tests.harness.scripted import TestScript as TestScriptMixin


class TestScript(TestScriptMixin, TestCase):
    
    def startRouter(self):
        warnings.warn("startRouter is deprecated and will be removed in a future "
                      "release.  Please, see the release notes.", DeprecationWarning, stacklevel=2)
        self.clear() # make sure the outbox is clean
    
    def stopRouter(self):
        warnings.warn("stopRouter is deprecated and will be removed in a future "
                      "release.  Please, see the release notes.", DeprecationWarning, stacklevel=2)
