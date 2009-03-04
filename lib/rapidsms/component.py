#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Component(object):
    
    def debug(self, msg):
        if self.router: self.router.log('debug', msg)
    
    def info(self, msg):
        if self.router: self.router.log('info', msg)
        
    def warning(self, msg):
        if self.router: self.router.log('warning', msg)
    
    def error(self, msg):
        if self.router: self.router.log('error', msg)
    
    def critical(self, msg):
        if self.router: self.router.log('critical', msg)