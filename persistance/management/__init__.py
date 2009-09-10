#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management import call_command
from django.db.models import signals


def update_backends(**kwargs):
    call_command("update_backends")

def update_apps(**kwargs):
    call_command("update_apps")


# update the backends and apps every time rapidsms
# starts, so we have an accurate representation of
# the router in the database at all times
signals.post_syncdb.connect(update_backends)
signals.post_syncdb.connect(update_apps)
