#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

#import sys, os

from django.core.management import execute_manager
import settings


if __name__ == "__main__":
#    project_root = os.path.abspath(
#        os.path.dirname(__file__))

#    path = os.path.join(project_root, "apps")
#    sys.path.insert(0, path)

#    sys.path.insert(0, project_root)
    execute_manager(settings)
