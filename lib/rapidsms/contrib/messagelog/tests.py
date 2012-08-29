#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.conf import settings
import rapidsms.contrib.messagelog.app


def test_messagelog():
    app = rapidsms.contrib.messagelog.app.App()
    # Invoke _log, make sure it doesn't blow up regardless of Django version
    app._log('I', {}, "text")
