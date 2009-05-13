#!/usr/bin/env python
# vim: ai et sts=4 sw=4 ts=4
from apps.reporters.models import Location

KANO_PILOT_LGAS = [ 2001, 2004, 2005, 2007, 2009, 2013, 2014, 2015, 2016, 2018, 2019, 2020, 
                  2021, 2023, 2024, 2027, 2030, 2031, 2035, 2040, 2043]

if __name__ == "__main__":
    for lga in KANO_PILOT_LGAS:
        print "%d: %s" % (lga, Location.objects.get(code=lga).name)
