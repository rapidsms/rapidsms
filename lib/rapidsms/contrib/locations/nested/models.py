import mptt

from rapidsms.contrib.locations.models import Location

mptt.register(Location, parent_attr='tree_parent')
