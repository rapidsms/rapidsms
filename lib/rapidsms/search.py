#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import django


SPLIT_RE = re.compile(r"[\s,]+", re.I)


def _slice(str):
    return SPLIT_RE.split(str)


def _dice(x):
    """Returns the elements of iterable _x_ in tuples of every possible
       length and range, without changing the order. This is useful when
       parsing a list of undelimited terms, which may span multiple tokens.
       For example (note the decreasing length of the tuples):
       >>> _dice(["a", "b", "c"])
       [("a", "b", "c"),  ("a", "b"), ("b", "c"),  ("a"), ("b"), ("c")]"""

    y = []
    for n in range(len(x), 0, -1):
        for m in range(0, len(x)-(n-1)):
            y.append(tuple(x[m:m+n]))

    return y


def _searchable_models():
    """Returns an array of every model which implements the __search__ API."""

    return filter(
        lambda o: hasattr(o, "__search__"),
        django.db.models.loading.get_models())


def find_objects(models, str, intersect_with_searchable=True):
    models = set(models)
    found = []

    # usually we will intersect with _searchable_, since
    # it won't work if the __search__ method isn't present
    if intersect_with_searchable:
        models = models & set(_searchable_models())

    # since the terms are undelimited, we'll have to figure out what
    # the sender means by brute force. smash the terms string into all
    # of it's possible combinations, and pass every one to every model
    # that is followable and implements the __search__ API
    for combo in _dice(_slice(str)):
        for model in models:
            obj = model.__search__(None, combo)
            if obj is not None:
                found.append(obj)

    return found
