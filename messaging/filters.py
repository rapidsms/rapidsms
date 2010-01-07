#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import itertools


def builtins():
    return []


callbacks = []
def register(callback):
    """
    title=country, district, group, role, etc
    callback=called during render to return an iterable
    """

    callbacks.append(callback)


def fetch():
    """
    """

    x = []
    for func in callbacks:
        for filter in func():
            x.append(filter)

    return x


