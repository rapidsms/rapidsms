#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django_tables.models import BoundModelRow
from django_tables.base import BoundRow
from django_tables import *

# i don't much like the names of these classes in django_tables, so i'm
# providing aliases here. the fact that they're "bound" is an detail
# which doesn't need to be exposed by the public API.
ModelRow = BoundModelRow
Row = BoundRow
