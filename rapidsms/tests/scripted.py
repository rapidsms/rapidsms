import warnings

from rapidsms.tests.harness import TestScript as TestScriptMixin


class TestScript(TestScriptMixin):

    def startRouter(self):
        warnings.warn("startRouter is deprecated and will be removed in a "
                      "future release.  Please, see the release notes.",
                      DeprecationWarning, stacklevel=2)
        self.clear()  # make sure the outbox is clean

    def stopRouter(self):
        warnings.warn("stopRouter is deprecated and will be removed in a "
                      "future release.  Please, see the release notes.",
                      DeprecationWarning, stacklevel=2)
