#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


# for most commands we will drop straight through this script into the
# standard django-admin.py -- but if we're creating a project, we are
# going to... (wait for it...) monkeypatch our command into sys.modules,
# and trick django into calling it instead of its own! hahaha!
#
# ...but seriously, django provides no way of doing this via management
# commands, since we're spawning a new project here, and django doesn't
# know to look in the rapidsms package for commands yet.

import sys
import rapidsms.management.commands.startproject
import django.core.management.commands.startproject

sys.modules['django.core.management.commands.startproject'] =\
    rapidsms.management.commands.startproject


# straight from the django-admin.py script.

if __name__ == "__main__":
    from django.core import management
    management.execute_from_command_line()
