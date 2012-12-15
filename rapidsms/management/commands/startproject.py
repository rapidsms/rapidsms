#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
import shutil
from django.core.management.base import CommandError, LabelCommand
from rapidsms.utils.modules import try_import
import rapidsms



# this is mostly copy/pasted from django. unfortunately, the copy
# mechanism had to be replaced, since django hard-codes some paths.

class Command(LabelCommand):
    help = "Creates a RapidSMS project in the current directory."
    args = "[projectname]"
    label = 'project name'

    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, project_name, **options):
        if try_import(project_name) is not None:
            raise CommandError(
                "%r conflicts with the name of an existing Python module and cannot be used as a project name. Please try another name." %
                project_name)

        src_dir = os.path.join(rapidsms.__path__[0], "skeleton", "project")
        shutil.copytree(src_dir, project_name, ignore=shutil.ignore_patterns('*.pyc'))
