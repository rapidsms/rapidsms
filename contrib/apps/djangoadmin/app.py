#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App(rapidsms.app.App):
    '''Do nothing. This app is for django integration only and
       has no sms functionality. This file and class exist only
       so the router does not print an error messsage.'''
       #TODO find a more sensible way of allowing non-sms apps
    pass
