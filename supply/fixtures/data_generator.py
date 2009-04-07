#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import random
import string
import sys
import os


def generate_data(args):
    '''Generates some test data and outputs it to a file.  This allows you to specify
    The number of items to generate, and the length of each item.  Items are chosen randomly
    from upper and lowercase letters'''
    totalcount = int(args[1])
    for count in args[2:]:
        filename = os.path.join(os.path.dirname(__file__), "%s-%s.txt" % (totalcount, count ))
        textoutput = open(filename, 'w')
        jsonfilename = os.path.join(os.path.dirname(__file__), "%s-%s.json" % (totalcount, count ))
        jsonoutput = open(jsonfilename, 'w')
        jsonoutput.write("[\n")
        first = True
        for i in range(1, totalcount + 1):
            chars = "".join( [random.choice(string.letters) for i in xrange(int(count))] )
            textoutput.write(chars + "\n")
            if first:
                first = False
            else:
                # the last writes the previous comma and newline
                jsonoutput.write(",\n")
            #json must generate data that looks like this:
            #{"model": "supply.LocationType","pk": <ID>,"fields": {"name": "<VALUE>"}},
            jsonoutput.write(' {"model": "supply.LocationType","pk": %s,"fields": {"name": "%s"}}' % (i, chars))
        jsonoutput.write("\n]")
  
        

if __name__ == "__main__":
    generate_data(sys.argv)


    