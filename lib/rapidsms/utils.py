#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import pytz
from datetime import datetime

def empty_str(in_str):
    """
    Simple helper to return True if the passed
    string reference is None or '' or all whitespace

    """
    return in_str is None or \
        len(in_str.strip())==0

def to_naive_utc_dt(dt):
    if dt.tzinfo is None:
        return dt

    return dt.astimezone(pytz.utc).replace(tzinfo=None)

def to_aware_utc_dt(dt):
    if dt.tzinfo is None:
        return pytz.utc.localize(dt)

    return dt.astimezone(pytz.utc)

