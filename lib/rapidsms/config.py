#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import ConfigParser


def to_list (item):
    return filter(None,map(lambda x: unicode(x).strip(), item.split(",")))

class Config (object):
    def __init__(self, *paths):
        self.parser = ConfigParser.ConfigParser()
        self.data   = {}
        self.parser.read(paths)
        for section in map(unicode, self.parser.sections()):
            data = {}
            for option in self.parser.options(section):
                data[option] = self.parser.get(section, option)
            if hasattr(self, section):
                data = getattr(self, section)(data)
            self.data[section] = data

    def load_apps (self, apps):
        app_classes = []
        for app_name in apps:
            app_module_str = "apps.%s.app" % (app_name)
            app_module = __import__(app_module_str, {}, {}, [''])
            app_classes.append(app_module.App)
        return app_classes

    def load_backends (self, backends):
        backend_classes = []
        for backend_name in backends:
            backend_module_str = "rapidsms.backends." + backend_name
            backend_module = __import__(backend_module_str, {}, {}, [''])
            backend_class = getattr(backend_module, backend_name.capitalize())
            backend_classes.append(backend_class)
        return backend_classes

    def rapidsms (self, data):
        app_classes = self.load_apps(to_list(data["apps"]))
        backend_classes = self.load_backends(to_list(data["backends"]))
        return { "apps": app_classes,
                 "backends": backend_classes }

    def __getitem__(self, key):
        return self.data[key]
        
    def has_key(self, key):
        return self.data.has_key(key)
