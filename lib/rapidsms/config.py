#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, sys, log
from ConfigParser import SafeConfigParser
from utils.modules import try_import


def to_list (item, separator=","):
    return filter(None, map(lambda x: str(x).strip(), item.split(separator)))


class LazyAppConf(object):
    """RapidSMS apps can provide an optional config.py, which is like a per-app
       version of Django's settings.py. The settings defined there are available
       to both the RapidSMS router and the Django WebUI. This class acts very
       much like a dict, but doesn't build the app config until it's really
       required (much like a Django QuerySet).

       This is almost completely useless, except it allows us to prepare the
       Config opject (full of LazyAppConf instances) while building the Django
       settings (rapidsms.djangoproject.settings), _and_ allow app configs to hit
       the database. If the configs were regular (eager) dicts, Django would refuse
       to hit the database, because "You haven't set the DATABASE_ENGINE setting
       yet".
       
       Unfortunately, for Python2.5 compatibility, this must be cast to a real
       dict before being iterated or passed as **kwargs."""

    def __init__(self, config, app_name):
        self.app_name = app_name
        self.config = config
        self._cache = None

    def _dict(self):
        if self._cache is None:
            self._cache = self.config.app_section(self.app_name)
        return self._cache

    # not strictly necessary, but avoids logging the useless
    # "Added app: <rapidsms.config.LazyAppConf object at 0x......c>"
    def __repr__(self):
        return repr(self._dict())

    # these two methods are enough to cast to a dict in
    # python 2.5. in python 2.6, use collections.mapping.
    def keys(self):
        return self._dict().keys()

    def __getitem__(self, key):
        return self._dict()[key]


class Config (object):
    def __init__ (self, *paths):
        self.parser = SafeConfigParser()

        # read the configuration, and store the list of
        # config files which were successfully parsed
        self.sources = self.parser.read(paths)
        
        self.raw_data = {}
        self.normalized_data = {}
        self.data = {}
        
        # first pass: read in the raw data. it's all strings, since
        # ConfigParser doesn't seem to decode unicode correctly (yet)
        for sn in self.parser.sections():
            items = self.parser.items(sn)
            self.raw_data[sn] = dict(items)
        
        # second pass: cast the values into int or bool where possible
        # (mostly to avoid storing "false", which evaluates to True)
        for sn in self.raw_data.keys():
            self.normalized_data[sn] = {}
            
            for key, val in self.raw_data[sn].items():
                self.normalized_data[sn][key] = \
                    self.__normalize_value(val)
        
        # third pass: iterate the normalized data, creating a
        # dict (self.data) containing the "real" configuration,
        # which may include things (magic, defaults, etc) not
        # present in the raw_data or normalized_data
        for sn in self.normalized_data.keys():
            section_parser = "parse_%s_section" % (sn)
            
            # if this section has a special parser, call
            # it with the raw data, and store the result
            if hasattr(self, section_parser):
                self.data[sn] = \
                    getattr(self, section_parser)(
                        self.normalized_data[sn])
            
            # no custom section parser, so
            # just copy the raw data as-is
            else:
                self.data[sn] =\
                    self.normalized_data[sn].copy()


    def __normalize_value (self, value):
        """Casts a string to a bool, int, or float, if it looks like it
           should be one. This is a band-aid over the ini format, which
           assumes all values to be strings. Examples:
           
           "mudkips"              => "mudkips" (str)
           "false", "FALSE", "no" => False     (bool)
           "true", "TRUE", "yes"  => True      (bool)
           "1.0", "0001.00"       => 1.0       (float)
           "0", "0000"            => 0         (int)"""
        
        # shortcut for string boolean values
        if   value.lower() in ["false", "no"]: return False
        elif value.lower() in ["true", "yes"]: return True
        
        # attempt to cast this value to an int, then a float. (a sloppy
        # benchmark of this exception-catching algorithm indicates that
        # it's faster than checking with a regexp)
        for func in [int, float]:
            try: func(value)
            except: pass
        
        # it's just a str
        # (NOT A UNICODE)
        return value


    def lazy_app_section (self, name):
        return LazyAppConf(self, name)


    def app_section (self, name):

        # fetch the current config for this app
        # from raw_data (or default to an empty dict),
        # then copy it, so we don't alter the original
        data = self.raw_data.get(name, {}).copy()

        # "type" is ONLY VALID FOR BACKENDS now. it's not [easily] possible
        # to run multple django apps of the same type side-by-side, so i'm
        # raising here to avoid confusion (and allow apps to be lazy loaded)
        if "type" in data:
            raise Exception(
                'The "type" option is not supported for apps. It does ' +\
                'nothing, since running multple apps of the same type ' +\
                'is not currently possible.')

        # load the config.py for this app, if possible
        config = try_import("%s.config" % name)
        if config is not None:

            # copy all of the names not starting with underscore (those are
            # private or __magic__) into this component's default config,
            # unless they're already present (ini overrides config.py)
            for var_name in dir(config):
                if not var_name.startswith("_"):
                    if not var_name in data:
                        data[var_name] = getattr(config, var_name)

        # return the component with the additional
        # app-specific data included.
        return data


    def backend_section (self, name):

        # fetch the current config for this backend
        # from raw_data (or default to an empty dict),
        # then copy it, so we don't alter the original
        data = self.raw_data.get(name, {}).copy()

        # although "name" and "type" are deliberately distinct (to enable multiple
        # backends of the same type to run concurrently), it's cumbersome to have
        # to provide a type every single time, so default to the name
        if not "type" in data:
            data["type"] = name

        return data


    def parse_rapidsms_section (self, raw_section):
        
        # "apps" and "backends" are strings of comma-separated
        # component names. first, break them into real lists
        app_names     = to_list(raw_section.get("apps",     ""))
        backend_names = to_list(raw_section.get("backends", ""))
        
        # run lists of component names through [app|backend]_section,
        # to transform into dicts of dicts containing more meta-info
        return { "apps":     dict((n, self.lazy_app_section(n)) for n in app_names),
                 "backends": dict((n, self.backend_section(n)) for n in backend_names) }


    def parse_log_section (self, raw_section):
        output = {"level": log.LOG_LEVEL, "file": log.LOG_FILE}
        output.update(raw_section)
        return output


    def __getitem__ (self, key):
        return self.data[key]
        
    def has_key (self, key):
        return self.data.has_key(key)
    
    __contains__ = has_key
