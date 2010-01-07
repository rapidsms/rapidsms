#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management import call_command
from ..rapidsms.router import router


def update_persistance(**kwargs):
    call_command("update_backends", verbosity=0)
    call_command("update_apps", verbosity=0)


# the app and backend configuration can change at any
# time, but it doesn't really matter until the router
# is reloaded, so synchronize everyting during startup
router.pre_start.connect(
    update_persistance)
