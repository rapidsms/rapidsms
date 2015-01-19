#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import pytz
from datetime import datetime
from six import string_types


def empty_str(in_str):
    """
    Simple helper to return True if the passed
    string reference is None or '' or all whitespace

    """
    if in_str is not None and not isinstance(in_str, string_types):
        raise TypeError('Arg must be None or a string type')

    return in_str is None or \
        len(in_str.strip()) == 0


def to_naive_utc_dt(dt):
    """
    Converts a datetime to a naive datetime (no tzinfo)
    as follows:

    if inbound dt is already naive, it just returns it

    if inbound is timezone aware, converts it to UTC,
    then strips the tzinfo

    """
    if not isinstance(dt, datetime):
        raise TypeError('Arg must be type datetime')

    if dt.tzinfo is None:
        return dt

    return dt.astimezone(pytz.utc).replace(tzinfo=None)


def to_aware_utc_dt(dt):
    """
    Convert an inbound datetime into a timezone
    aware datetime in UTC as follows:

    if inbound is naive, uses 'tzinfo.localize' to
    add utc tzinfo. NOTE: Timevalues are not changed,
    only difference in tzinfo is added to identify this
    as a UTC tz aware object.

    if inbound is aware, uses 'datetime.astimezone'
    to convert timevalues to UTC and set tzinfo to
    utc.

    """
    if not isinstance(dt, datetime):
        raise TypeError('Arg must be type datetime')

    if dt.tzinfo is None:
        return pytz.utc.localize(dt)

    return dt.astimezone(pytz.utc)


def timedelta_as_minutes(td):
    """
    Returns the value of the entire timedelta as
    integer minutes, rounded down

    """
    return timedelta_as_seconds(td) / 60


def timedelta_as_seconds(td):
    '''
    Returns the value of the entire timedelta as
    integer seconds, rounded down

    '''
    return td.days * 86400 + td.seconds
