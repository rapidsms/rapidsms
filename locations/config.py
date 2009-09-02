#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from apps.locations.models import LocationType


# if there is only than one location type available, the main tab will
# be linked (and captioned) as if "types" does not exist -- this avoids
# having a useless notion of "types" that do nothing. otherwise, the main
# tab will be labelled "locations", and type types listed as sub-tabs
# (as usual, this is overridable by settings.py or the rapidsms ini)
title = LocationType.label().plural
tab_link = "/locations"
