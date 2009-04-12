#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import re

class Keyworder(object):

    TOKEN_MAP = [
        ("slug",     "([a-z0-9\-]+)"),
        ("letters",  "([a-z]+)"),
        ("numbers",  "(\d+)"),
        ("whatever", "(.+)")]

    def __init__(self):
        self.regexen = []
        self.prefix = ""
        self.pattern = "^%s$"

    def prepare(self, prefix, suffix):

        # no prefix is defined, so match
        # only the suffix (so simple!)
        if prefix == "":
            str = suffix

        # we have a prefix, but no suffix,
        # so accept JUST the prefix
        elif suffix == "":
            str = prefix

        # the most common case; we have both a
        # prefix and suffix, so simpley join
        # them with a space
        else: str = prefix + " " + suffix


        # also assume that one space means
        # "any amount of whitespace"
        str = str.replace(" ", "\s+")

        # replace friendly tokens with real chunks
        # of regex, to make the patterns more readable
        for token, regex in self.TOKEN_MAP:
            str = str.replace("(%s)" % token, regex)

        return re.compile(self.pattern % str, re.IGNORECASE)

    def __call__(self, *regex_strs):
        def decorator(func):

            # make the current prefix into something
            # iterable (so multiple prefixes can be
            # specified as list, or single as string)
            prefixen = self.prefix
            if not hasattr(self.prefix, "__iter__"):
                prefixen = [self.prefix]

            # store all of the regular expressions which
            # will match this function, as attributes on
            # the function itself
            if not hasattr(func, "regexen"):
                setattr(func, "regexen", [])

            # iterate and add all combinations of
            # prefix and regex for this keyword
            for prefix in prefixen:         
                for rstr in regex_strs:
                    regex = self.prepare(prefix, rstr)
                    getattr(func, "regexen").append(regex)
                    #print "Handler: %s" % regex.pattern
                    self.regexen.append((regex, func))
            return func
        return decorator

    def match(self, sself, str):
        for pat, func in self.regexen:
            match = pat.match(str)
            if match:
                # clean up leading and trailing whitespace
                # note: match groups can be None, hence the and/or business
                groups = map(lambda x: x and x.strip() or x, match.groups())
                return (func, groups)
        # TODO proper logging??
        #print "No method called %s" % (str)

    # a semantic way to add a default
    # handler (when nothing else is matched)
    def blank(self):
        return self.__call__("")
    
    # another semantic way to add a catch-all
    # most useful with a prefix for catching
    # invalid syntax and responding with help
    def invalid(self):
        return self.__call__("(whatever)")
