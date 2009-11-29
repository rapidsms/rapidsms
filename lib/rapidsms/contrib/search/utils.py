#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import django


DELIMITER = re.compile(r"([\s,]+)")


def _searchable_models(models=None):
    """
    Returns an array of the *models* which implement the __search__ API. If
    *models* is omitted (or None), all installed models are checked.
    """

    if models is None:
        models = django.db.models.loading.get_models()

    return filter(
        lambda x: hasattr(x, "__search__"),
        models)


def _slice(text):
    return DELIMITER.split(text)


def _is_delimiter(text):
    """
    Returns true if *text* looks like a delimiter.

    >>> _is_delimiter("x")
    False

    >>> _is_delimiter(", ")
    True
    """
    return DELIMITER.match(text) is not None


def _dice(terms):
    """
    Returns the elements of iterable *terms* in tuples of every possible length
    and range, without changing the order. This is useful when parsing a list of
    undelimited terms, which may span multiple tokens. For example:

    >>> _dice(["a", "b", "c"])
    [('a', 'b', 'c'), ('a', 'b'), ('b', 'c'), ('a',), ('b',), ('c',)]
    """

    # remove all of the terms that look like delimiters
    terms = filter(lambda x: _is_delimiter(x) == False, terms)

    y = []
    for n in range(len(terms), 0, -1):
        for m in range(0, len(terms)-(n-1)):
            y.append(tuple(terms[m:m+n]))

    return y


def _filter_tuples(diced_str, to_remove):
    """
    Returns *diced_str* with all of the tuples containing any elements of the
    *to_remove* iterable filtered out. This is used to drop search terms from
    the diced_str once they've been matched. For example:

    # start with the output of the _dice doctest
    >>> p = [('a', 'b', 'c'), ('a', 'b'), ('b', 'c'), ('a',), ('b',), ('c',)]

    >>> _filter_tuples(p, ("a"))
    [('b', 'c'), ('b',), ('c',)]

    >>> _filter_tuples(p, ("b", "c"))
    [('a',)]
    """

    # true if the tupl does not contain
    # any of the elements in *to_remove*
    def _func(tupl):
        for x in to_remove:
            if x in tupl:
                return False

        return True

    return filter(_func, diced_str)


def _remove_double_delimiters(slices):
    """
    >>> _remove_double_delimiters(["a", " ", "b", " ", "c"])
    ['a', ' ', 'b', ' ', 'c']
    
    >>> _remove_double_delimiters(["a", " ", " ", "b"])
    ['a', ' ', 'b']
    
    >>> _remove_double_delimiters(["a", " ", " ", "b", " ", " ", " ", "c"])
    ['a', ' ', 'b', ' ', 'c']
    """

    l = len(slices)
    was_del = None
    output = []

    for n in range(0, l):
        slice = slices[n]
        is_del = _is_delimiter(slice)

        # skip this slice if it's a leading or trailing delimiter,
        # or both this AND the previous were delimiters. note that
        # the was_del flag is not rest, so any number of joined
        # delimiters will be ignored until some meat is found
        if is_del and (n==0 or n==(l-1) or was_del):
            continue

        was_del = is_del
        output.append(slice)

    return output


def _find(searchable_models, tupls):
    """
    # start with the output of the _dice doctest
    >>> p = [('a', 'b', 'c'), ('a', 'b'), ('b', 'c'), ('a',), ('b',), ('c',)]

    >>> class MockModel_A(object):
    ...
    ...     def __repr__(self):
    ...         return "<MM:A>"
    ...
    ...     @classmethod
    ...     def __search__(cls, terms):
    ...       if terms == ("a",):
    ...           return cls()

    >>> _find([MockModel_A], p)
    ([<MM:A>], [('b', 'c'), ('b',), ('c',)])

    >>> class MockModel_BC(object):
    ...
    ...     def __repr__(self):
    ...         return "<MM:BC>"
    ...
    ...     @classmethod
    ...     def __search__(cls, terms):
    ...       if terms == ("b", "c"):
    ...           return cls()

    >>> _find([MockModel_BC], p)
    ([<MM:BC>], [('a',)])

    >>> _find([MockModel_A, MockModel_BC], p)
    ([<MM:BC>, <MM:A>], [])
    """

    for perm in tupls:
        for model in searchable_models:
            found = model.__search__(perm)
            if found is not None:

                # this tuple was a match! filter all of the
                # tuples that contain the used terms, and
                # recurse to search with the remainder
                other_finds, unused_tupls = _find(
                    searchable_models,
                    _filter_tuples(
                        tupls,
                        perm))

                # return all search results and remaining tuples
                return ([found] + other_finds, unused_tupls)

    # no results. return all of the permutations
    # that we received, because none were used
    return ([], tupls)


def find_objects(text, models=None):
    return _find(
        _searchable_models(models),
        _dice(_slice(text)))[0]


def extract_objects(text, models=None):
    """
    Returns something awesome.

    # start with the output of the _dice doctest
    >>> p = [('a', 'b', 'c'), ('a', 'b'), ('b', 'c'), ('a',), ('b',), ('c',)]

    >>> class MockModel_D(object):
    ...
    ...     def __repr__(self):
    ...         return "<MM:D>"
    ...
    ...     @classmethod
    ...     def __search__(cls, terms):
    ...       if terms == ("d",):
    ...           return cls()

    >>> extract_objects("a b c d e", [MockModel_D])
    ([<MM:D>], 'a b c e')

    >>> extract_objects("aa d bb d cc d ee", [MockModel_D])
    ([<MM:D>], 'aa bb cc ee')
    """

    slices = _slice(text)
    diced = _dice(slices)
    
    objects, unused_tupls = _find(
        _searchable_models(models),
        diced)
    
    unused_slices = [
        slice for slice in slices
        if _is_delimiter(slice)
        or (slice,) in unused_tupls
    ]

    # rebuild the original text, with the parts that
    # we've used removed as cleanly as i can manage
    unused_text = "".join(_remove_double_delimiters(
        unused_slices))

    return objects, unused_text


if __name__ == "__main__":
    import doctest
    doctest.testmod()
