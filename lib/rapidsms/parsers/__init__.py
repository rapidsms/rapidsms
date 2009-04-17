#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re
from keyworder import *

class Matcher:
    def __init__(self, msg, pattern_template="^%s$"):
        self.tmpl = pattern_template
        self.msg = msg

    def __getitem__(self, n):
        return self.groups[n]

    def __call__(self, *patterns):
        for pat in patterns:

            # assume that one space means
            # "any amount of whitespace"
            pat = pat.replace(" ", "\s+")

            # replace friendly tokens with real chunks
            # of regex, to make the patterns more readable
            for token, regex in Keyworder.TOKEN_MAP:
                pat = pat.replace("(%s)" % token, regex)

            # attempt to match the text of the message
            # that this object was initialized with
            # against the generated pattern
            self.match_data = re.match(
                self.tmpl % pat,
                self.msg.text,
                re.IGNORECASE)

            # if we had a match, store the groups in
            # this instance, and return true. if the
            # end of the loop is reached without any
            # match, None is returned implicitly
            if self.match_data is not None:
                self.groupdict = self.match_data.groupdict()
                self.groups = self.match_data.groups()
                return True
