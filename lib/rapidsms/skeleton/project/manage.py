#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management import execute_manager
import settings


if __name__ == "__main__":
    execute_manager(settings)
