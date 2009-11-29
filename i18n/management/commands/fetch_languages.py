#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import urllib2
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Fetches a list of all language codes and descriptions from IANA"
    SRC = "http://www.iana.org/assignments/language-subtag-registry"


    def _chunk(self, chunk):
        """Parses a "chunk" of key/value pairs into a dict:

             a: Alpha       { "a": "Alpha",
             b: Beta   -->    "b": "Beta",
             g: Gamma         "g": "Gamma" }

           This is ugly, and should probably be reimplemented as a real parser,
           but I suspect it'll be a one off, so I don't particularly care."""

        lines = chunk.split("\n")
        output = {}
        
        for line in lines:
            x = line.split(":", 1)

            if len(x) == 2:
                key = x[0].lower() # normalize the key
                val = x[1].strip() # strip leading spaces
                output[key] = val

        return output


    def handle_noargs(self, **options):
        output = {}

        try:
            f = urllib2.urlopen(self.SRC)
            data = f.read()
            f.close()

        # abort if anything went
        # bang. what error handling?
        except Exception, err:
            return err

        # iterate the huge fortune-file-style
        # language registry one chunk at at time
        for chunk in data.split("%%"):
            d = self._chunk(chunk.strip())

            # we're only interested in the actual
            # language definitions; skip the rest
            if d.get("type", None) != "language":
                continue

            # store just the relevant bits
            output[d["subtag"]] = d["description"]

        # print a dictionary, ready to be pasted
        # into a python source somewhere
        print "LANGUAGES = {"
        print ",\n".join([
            '    "%s": "%s"' % (key ,output[key])
            for key in sorted(output.keys())])
        print "}"
