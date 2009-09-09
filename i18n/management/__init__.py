#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management import call_command
from django.db.models import signals


def update_languages(**kwargs):
    call_command("update_languages")

def update_tokens(**kwargs):
    call_command("update_tokens")


# update the languages and tokens after the database is
# built, so we don't have to type the commands every time,
# but can still do so at a later time if necessary
signals.post_syncdb.connect(update_languages)
signals.post_syncdb.connect(update_tokens)
